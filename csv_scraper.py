from langchain_community.document_loaders.csv_loader import CSVLoader
import requests
import json
import time
import chromadb
import shutil
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CSVScraper:
    def __init__(self, uploaded_file):
        self.uploaded_file = uploaded_file
        self.client, self.collection = self.init_chroma()

    # Store CSV file in the directory specified by DOCS_PATH environment variable
    def store_csv(self):
        docs_path = os.getenv("DOCS_PATH", "./docs")
        if not os.path.exists(docs_path):
            os.makedirs(docs_path)
        stored_file_path = os.path.join(docs_path, self.uploaded_file.name)
        with open(stored_file_path, "wb") as f:
            f.write(self.uploaded_file.getbuffer())
        return stored_file_path

    # Read CSV file and extract data using CSVLoader
    def read_csv(self):
        stored_file_path = self.store_csv()
        print(f"Reading CSV: {stored_file_path}")
        data = []
        try:
            loader = CSVLoader(stored_file_path)
            data = loader.load_and_split()  # Use load_and_split() instead of load()
            print(f"Extracted {len(data)} rows from CSV.")
        except Exception as e:
            print(f"Error reading CSV: {e}")
        return data

    # Generate embedding using Ollama local API
    def generate_embedding(self, text, model="llama3.1"):
        base_url = os.getenv("OLLAMA_API_URL", "http://192.168.1.34:11435")
        url = f"{base_url}/api/embeddings"
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
        chroma_db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        client = chromadb.PersistentClient(path=chroma_db_path)
        collection = client.get_or_create_collection(name="csv_embeddings")
        return client, collection

    # Main pipeline
    def run(self):
        # Read CSV data
        csv_data = self.read_csv()

        # Process each row
        for idx, row in enumerate(csv_data):
            try:
                text_chunk = json.dumps(row, default=str)  # Convert row to JSON string for embedding
            except TypeError as e:
                print(f"Error serializing row {idx}: {e}")
                continue

            if len(text_chunk.strip()) == 0:
                continue
            print(f"Processing row {idx + 1}/{len(csv_data)}")

            # Optional: Sleep to avoid rate-limiting Ollama (if needed)
            time.sleep(1)

            # Generate embedding
            embedding = self.generate_embedding(text_chunk)
            if embedding:
                self.store_embedding(text_chunk, embedding, doc_id=f"row_{idx}")
        print("All data stored in ChromaDB!")
