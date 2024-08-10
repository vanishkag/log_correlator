from inference import LLM

def main():
    llm = LLM()

    prompt = "Can you help me with this error?"

    output = llm.generate_text(prompt)

    print(output)

if __name__=="__main__":
    main()
