import chromadb
from ollama_call_chat import OllamaChat

class RAGRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.csv_collection = self.client.get_or_create_collection(name="csv_embeddings")
        self.web_collection = self.client.get_or_create_collection(name="web_scrape_embeddings")
        self.ollama_chat = OllamaChat()

    def retrieve_documents(self, query_embedding, collection):
        # Retrieve top 5 documents based on similarity
        results = collection.query(embeddings=[query_embedding], n_results=5)
        return results

    def generate_response(self, user_input):
        # Generate embedding for the user input
        query_embedding = self.ollama_chat.generate_embedding(user_input)

        # Retrieve relevant documents from both CSV and Web collections
        csv_docs = self.retrieve_documents(query_embedding, self.csv_collection)
        web_docs = self.retrieve_documents(query_embedding, self.web_collection)

        # Combine retrieved documents
        combined_docs = csv_docs + web_docs

        # Prepare messages for OllamaChat
        messages = [
            {"role": "system", "content": "You are a retrieval-augmented generation model. Use the following documents to generate a response."},
            {"role": "user", "content": f"User input: {user_input}"}
        ]

        # Add retrieved documents to the messages
        for doc in combined_docs:
            messages.append({"role": "system", "content": f"Document: {doc['document']}"})

        # Get the response from OllamaChat
        response = self.ollama_chat.get_ai_response(messages)
        return response.strip() if response else "No relevant information found."
