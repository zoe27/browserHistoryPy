import os
import shutil
import sqlite3
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# This file contains functions and logic to extract and process browsing history
# from the Chrome browser's SQLite database, including fetching page content
# and saving processed data to a JSON file.
# Configure logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get user home directory
user_home = os.path.expanduser("~")
logger.info(f'User Home Directory: {user_home}')

# Chrome history database path
chrome_history_path = os.path.join(user_home, 'Library/Application Support/Google/Chrome/Default/History')

# Check if file exists
if not os.path.exists(chrome_history_path):
    logger.error(f'Chrome history file not found at: {chrome_history_path}')
    exit(1)

# Copy database
temp_copy = './history_copy.db'
shutil.copy(chrome_history_path, temp_copy)
logger.info('Database copied successfully')


def fetch_page_content(url):
    start_time = time.time()
    try:
        options = Options()
        options.add_argument('--headless')
        service = Service()
        browser = webdriver.Chrome(service=service, options=options)
        browser.get(url)

        content = browser.execute_script("""
            const main = document.querySelector('main');
            const article = document.querySelector('article');
            const body = document.body;
            return (main && main.innerText) || (article && article.innerText) || (body && body.innerText) || '';
        """)

        browser.quit()
        logger.info(f'✅ Fetched {url} in {time.time() - start_time:.2f}s')
        return content.strip()
    except Exception as err:
        logger.error(f'❌ Error fetching {url}: {str(err)}')
        return ''


def process_batch(rows, output_file, batch_size=10):
    results = []
    for i, row in enumerate(rows, 1):
        start_time = time.time()
        content = fetch_page_content(row.url)
        result = {
            'url': row.url,
            'title': row.title,
            'content': content[:1000]
        }
        results.append(result)

        # Write batch to file
        if i % batch_size == 0:
            append_to_file(results, output_file)
            logger.info(f'Processed and saved batch of {batch_size} items')
            results = []

    # Write remaining items
    if results:
        append_to_file(results, output_file)
        logger.info(f'Processed and saved remaining {len(results)} items')


def append_to_file(results, filename):
    try:
        # Read existing data
        existing_data = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                existing_data = json.load(f)

        # Append new data
        existing_data.extend(results)

        # Write back to file
        with open(filename, 'w') as f:
            json.dump(existing_data, f, indent=2)
    except Exception as e:
        logger.error(f'Error writing to file: {str(e)}')


def main():
    output_file = './history_content.json'
    batch_size = 10
    page_size = 100
    processed_count = 0
    start_time = time.time()

    processed_urls = set()

    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
            processed_urls.update(item['url'] for item in existing_data)
            logger.info(f'Found {len(processed_urls)} previously processed URLs')

    db = sqlite3.connect(temp_copy)
    cursor = db.cursor()

    cursor.execute('SELECT COUNT(*) FROM urls')
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + page_size - 1) // page_size

    for page in range(total_pages):
        offset = page * page_size
        percentage = (processed_count / total_count) * 100 if total_count > 0 else 0
        logger.info(f'Progress: {processed_count}/{total_count} ({percentage:.1f}%) - Page {page + 1}/{total_pages}')

        cursor.execute('''
            SELECT url, title, last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT ? OFFSET ?
        ''', (page_size, offset))

        class HistoryRow:
            def __init__(self, url, title, last_visit_time):
                self.url = url
                self.title = title
                self.last_visit_time = last_visit_time

        rows = [HistoryRow(url, title, last_visit_time)
                for url, title, last_visit_time in cursor.fetchall()]

        rows = [row for row in rows if row.url not in processed_urls]

        if rows:
            process_batch(rows, output_file, batch_size)
            processed_count += len(rows)
            processed_urls.update(row.url for row in rows)

    db.close()
    os.remove(temp_copy)

    final_percentage = (processed_count / total_count) * 100 if total_count > 0 else 0
    logger.info(f'✅ Processing completed: {processed_count}/{total_count} ({final_percentage:.1f}%)')
    logger.info(f'Total time: {time.time() - start_time:.2f}s')


def resume_processing():
    output_file = './history_content.json'
    batch_size = 10
    page_size = 100
    processed_count = 0
    start_time = time.time()

    # Set to track processed URLs
    processed_urls = set()

    # Load existing data to populate processed_urls
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            existing_data = json.load(f)
            processed_urls.update(item['url'] for item in existing_data)
            logger.info(f'Found {len(processed_urls)} previously processed URLs')

    # Connect to database
    db = sqlite3.connect(temp_copy)
    cursor = db.cursor()

    # Get total count
    cursor.execute('SELECT COUNT(*) FROM urls')
    total_count = cursor.fetchone()[0]
    total_pages = (total_count + page_size - 1) // page_size

    for page in range(total_pages):
        offset = page * page_size
        percentage = (processed_count / total_count) * 100 if total_count > 0 else 0
        logger.info(f'Progress: {processed_count}/{total_count} ({percentage:.1f}%) - Page {page + 1}/{total_pages}')

        cursor.execute('''
            SELECT url, title, last_visit_time
            FROM urls
            ORDER BY last_visit_time DESC
            LIMIT ? OFFSET ?
        ''', (page_size, offset))

        class HistoryRow:
            def __init__(self, url, title, last_visit_time):
                self.url = url
                self.title = title
                self.last_visit_time = last_visit_time

        rows = [HistoryRow(url, title, last_visit_time)
                for url, title, last_visit_time in cursor.fetchall()]

        # Filter out already processed URLs
        rows = [row for row in rows if row.url not in processed_urls]

        if rows:
            process_batch(rows, output_file, batch_size)
            processed_count += len(rows)
            processed_urls.update(row.url for row in rows)

    db.close()
    os.remove(temp_copy)

    final_percentage = (processed_count / total_count) * 100 if total_count > 0 else 0
    logger.info(f'✅ Resume completed: {processed_count}/{total_count} ({final_percentage:.1f}%)')
    logger.info(f'Total time: {time.time() - start_time:.2f}s')




if __name__ == "__main__":
    main()