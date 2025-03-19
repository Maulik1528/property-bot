class InformationExtractor:
    def __init__(self, ollama_chat):
        self.ollama_chat = ollama_chat

    def extract_information(self, information, sentence):
        # Prepare the message for information extraction
        messages = [
            {"role": "system", "content": "You are an information extraction model. Extract key information from the given sentence."},
            {"role": "user", "content": f"Extract {information} from this sentence: {sentence}"}
        ]
        
        # Get the response from OllamaChat
        response = self.ollama_chat.get_ai_response(messages)
        
        # Return the extracted information
        return response.strip() if response else "No information extracted"
