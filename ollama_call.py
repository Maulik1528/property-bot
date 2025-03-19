import ollama


class OllamaChat:
    def __init__(self, model="llama3.1"):
        self.model = model

    def get_ai_response(self, messages):
        # Use ollama library to get response from the specified model
        response = ollama.chat(model=self.model, messages=messages, stream=False)
        ai_response = response["message"]["content"] if response else ""
        return ai_response
