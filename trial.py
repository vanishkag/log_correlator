import sys
from rag_embedder.embedder import embedder
from rag_adapter.adapter import Adapter
from rag_llm_inference.inference import LLM
import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv('C:\Personal\log_correlator\output.csv')
    adapter_obj = Adapter(chunk_size=40, chunk_overlap=4, seperator=",")
    chunks = adapter_obj.get_chunks(df)
    print("Chunks: ")
    print(chunks)
