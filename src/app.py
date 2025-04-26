# app.py
from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import logging
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global variables for model and index
model = None
index = None
history_data = None


def init_model():
    global model, index, history_data

    # Load model
    logger.info("Loading model...")
    start_time = time.time()
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    logger.info(f"Model loaded in {time.time() - start_time:.2f} seconds")

    # Load history data
    with open('./history_content.json', 'r') as file:
        history_data = json.load(file)

    # Generate embeddings
    logger.info("Generating embeddings...")
    start_time = time.time()
    titles = [item["title"] for item in history_data]
    embeddings = model.encode(titles)
    logger.info(f"Embeddings generated in {time.time() - start_time:.2f} seconds")

    # Build FAISS index
    logger.info("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    logger.info("Index built successfully")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.json.get('query', '')
        if not query:
            return jsonify({'error': 'Query is required'}), 400

        # Generate query embedding
        query_embedding = model.encode([query])
        D, I = index.search(np.array(query_embedding), k=5)

        # Format results with distance threshold
        threshold = 15  # Adjust this value based on testing
        results = []
        for i in range(len(I[0])):
            if D[0][i] <= threshold:  # Only include results below threshold
                item = history_data[I[0][i]]
                results.append({
                    'title': item['title'],
                    'url': item['url'],
                    'distance': float(D[0][i])
                })

        return jsonify({'results': results})
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

if __name__ == '__main__':
    init_model()
    app.run(debug=True)