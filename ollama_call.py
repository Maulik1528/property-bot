import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OllamaChat:
    def __init__(self, model=None):
        # Use model from environment variable or default to "llama3.1"
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.base_url = os.getenv("OLLAMA_API_URL")
        self.response_url = f"{self.base_url}/api/chat"

    def get_ai_response(self, messages):
        # Use the response_url to get response from the specified model
        payload = {
            "model": self.model,
            "messages": messages
        }
        try:
            response = requests.post(self.response_url, json=payload)
            response.raise_for_status()
            ai_response = response.json()["message"]["content"] if response else ""
            return ai_response
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return ""
