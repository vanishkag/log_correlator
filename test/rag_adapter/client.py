import sys
from adapter import Adapter
import pandas as pd


def main():
    df = pd.read_csv('C:\Personal\log_correlator\Windows_2k.log_structured.csv')
    adapter_obj = Adapter(chunk_size=40, chunk_overlap=4, seperator=",")
    document = df['Content']
    chunks = adapter_obj.get_chunks(document)
    print("Chunks: ")
    print(chunks)


if __name__ == "__main__":
    main()
