from ollama_call_chat import OllamaChat

class LanguageDetector:
    def __init__(self):
        self.ollama_chat = OllamaChat()
        self.messages = [{"role": "system", "content": "You are a language detection model. Identify the language of the given text and return only one word."}]

    def detect_language(self, text):
        # Prepare the message for language detection
        self.messages.append({"role": "user", "content": f"Detect the language of this text: {text}"})
        
        # Get the response from OllamaChat
        response = self.ollama_chat.get_ai_response(self.messages)
        
        # Append the response to the messages
        self.messages.append({"role": "assistant", "content": response})
        
        # Return the detected language
        return response.strip() if response else "Unknown"

