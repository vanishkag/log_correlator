#currently not giving any output

from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

class LLM: 
    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1", temperature: float = 0.3, top_p: float= 1.0, top_k:int = 50, repetition_penalty: float = 1.0, max_length: int = 512):
        self.llm = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.generation_config = GenerationConfig(
                temperature = temperature, 
                top_p = top_p, 
                top_k = top_k, 
                repetition_penalty = repetition_penalty, 
                max_length = max_length,
                bos_token_id = 1, 
                eos_token_id = 2
                )

    def generate_text(self, input_text):
        encoded_input = self.tokenizer(input_text, return_tensors= 'pt')
        encoded_output = self.llm.generate(**encoded_input, generation_config = self.generation_config)[0]
        output_text = self.tokenizer.decode(encoded_output, skip_special_tokens=True)
        return output_text
