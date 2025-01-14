from transformers import AutoTokenizer, AutoModelForCausalLM

class LLM:
    def __init__(self, model_name: str = "mistralai/Mistral-7B-v0.1", temperature: float = 0.3, top_p: float = 1.0, top_k: int = 50, repetition_penalty: float = 1.0, max_length: int = 512):
        try:
            self.llm = AutoModelForCausalLM.from_pretrained(model_name)
            print("Model loaded successfully.")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            print("Tokenizer loaded successfully.")
            self.temperature = temperature
            self.top_p = top_p
            self.top_k = top_k
            self.repetition_penalty = repetition_penalty
            self.max_length = max_length
        except Exception as e:
            print(f"Error loading model/tokenizer: {e}")

    def generate_text(self, input_text):
        try:
            encoded_input = self.tokenizer(input_text, return_tensors='pt')
            print("Encoded input:", encoded_input)

            if not encoded_input.input_ids.size(1):
                print("Tokenization resulted in empty input IDs.")
                return None

            encoded_output = self.llm.generate(
                input_ids=encoded_input.input_ids,
                max_length=self.max_length,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                repetition_penalty=self.repetition_penalty,
                bos_token_id=self.tokenizer.bos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
            print("Encoded output:", encoded_output)

            output_text = self.tokenizer.decode(encoded_output[0], skip_special_tokens=True)
            return output_text
        except Exception as e:
            print(f"Error during text generation: {e}")
            return None

if __name__ == "__main__":
    llm = LLM()

    prompt = "Can you help me with this error?"
    print("Prompt:", prompt)

    output = llm.generate_text(prompt)
    if output:
        print("Generated output:", output)
    else:
        print("No output generated.")
