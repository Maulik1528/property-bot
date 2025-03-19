import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class OllamaGenerate:
    def __init__(self, model=None):
        # Use model from environment variable or default to "llama3.1"
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.base_url = os.getenv("OLLAMA_API_URL")
        self.generate_url = f"{self.base_url}api/generate"
        print(self.generate_url)

    def get_generated_content(self, prompt):
        # Use the generate_url to get generated content from the specified model
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False  # Set streaming to False
        }
        print("PAYLOAD ", payload)
        try:
            response = requests.post(self.generate_url, json=payload)
            print("resp : ", response.json())
            if response.status_code == 200:
                print("Response received: <Response [200]>")
                generated_content = response.json()["response"]
                print("Generated Content:", generated_content)
                return generated_content
            else:
                print(f"Unexpected status code: {response.status_code}")
                return ""
        except Exception as e:
            print(f"Error getting generated content: {e}")
            return ""
