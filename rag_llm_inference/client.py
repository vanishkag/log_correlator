from inference import LLM



def main():
    llm = LLM()

    prompt = "Hello World! How are you?"

    output = llm.generate_text(prompt)

    print(output)

if __name__=="__main__":
    main()
