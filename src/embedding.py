from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import time
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load history data from history_content.json
with open('./history_content.json', 'r') as file:
    history_data = json.load(file)

# Load model and generate embeddings
logger.info("Starting model loading...")
start_time = time.time()
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
logger.info(f"Model loaded in {time.time() - start_time:.2f} seconds")

# Generate embeddings
logger.info("Generating embeddings...")
start_time = time.time()
titles = [item["title"] for item in history_data]
embeddings = model.encode(titles)
logger.info(f"Embeddings generated in {time.time() - start_time:.2f} seconds")

# Build FAISS index
logger.info("Building FAISS index...")
start_time = time.time()
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))
logger.info(f"Index built in {time.time() - start_time:.2f} seconds")

# Query process
query = "bad news"
logger.info(f"Processing query: {query}")
start_time = time.time()
query_embedding = model.encode([query])
D, I = index.search(np.array(query_embedding), k=5)  # Increased to show more results
search_time = time.time() - start_time
logger.info(f"Search completed in {search_time:.2f} seconds")

# Output results with URLs
logger.info("\nSearch results:")
results = [history_data[i] for i in I[0]]
for i, res in enumerate(results):
    logger.info(f"\nResult {i+1}:")
    logger.info(f"Title: {res['title']}")
    logger.info(f"URL: {res['url']}")
    logger.info(f"Distance: {D[0][i]:.4f}")