class InformationExtractor:
    def __init__(self, ollama_generate):
        self.ollama_generate = ollama_generate

    def extract_information(self, information, sentence):
        # Prepare the prompt for information extraction
        prompt = f"You are an information extraction model. Extract {information} from this sentence: {sentence}. Return only 'None' if suitable information is not provided."
        
        # Get the generated content from OllamaGenerate
        response = self.ollama_generate.get_generated_content(prompt)
        
        # Return the extracted information
        return "No information extracted" if 'None' in response  else response.strip()