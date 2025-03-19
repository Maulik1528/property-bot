import requests
from bs4 import BeautifulSoup
import chromadb
import json
import time

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.client, self.collection = self.init_chroma()

    # Scrape the webpage and extract paragraph texts
    def scrape_text(self):
        print(f"Scraping: {self.url}")
        response = requests.get(self.url)
        if response.status_code != 200:
            print(f"Failed to scrape {self.url}")
            return []
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text_data = [para.get_text(strip=True) for para in paragraphs if para.get_text(strip=True)]
        print(f"Scraped {len(text_data)} paragraphs.")
        return text_data

    # Generate embedding using Ollama local API
    def generate_embedding(self, text, model="llama3.1"):
        url = "http://192.168.1.34:11435/api/embeddings"
        payload = {
            "model": model,
            "prompt": text
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            embedding = response.json()["embedding"]
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    # Store embedding into ChromaDB
    def store_embedding(self, text, embedding, doc_id):
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding]
        )
        print(f"Stored doc_id: {doc_id}")

    # Initialize local ChromaDB
    def init_chroma(self):
        client = chromadb.PersistentClient(path="./chroma_db")
        collection = client.get_or_create_collection(name="web_scrape_embeddings")
        return client, collection

    # Main pipeline
    def run(self):
        # Scrape data
        text_chunks = self.scrape_text()

        # Process each chunk
        for idx, text_chunk in enumerate(text_chunks):
            if len(text_chunk.strip()) == 0:
                continue
            print(f"Processing chunk {idx + 1}/{len(text_chunks)}")

            # Optional: Sleep to avoid rate-limiting Ollama (if needed)
            time.sleep(1)

            # Generate embedding
            embedding = self.generate_embedding(text_chunk)
            if embedding:
                self.store_embedding(text_chunk, embedding, doc_id=f"doc_{idx}")
        print("All data stored and ChromaDB persisted!")

# Example usage
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Natural_language_processing"
    scraper = WebScraper(url)
    scraper.run()
