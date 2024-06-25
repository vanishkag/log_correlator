import sys
from rag_embedder.embedder import embedder
from rag_adapter.adapter import Adapter
import pandas as pd


if __name__ == "__main__":
    df = pd.read_csv('C:\Personal\log_correlator\Windows_2k.log_structured.csv')
    adapter_obj = Adapter(chunk_size=40, chunk_overlap=4, seperator=",")
    document = df['Content']
    chunks = adapter_obj.get_chunks(document)
    print("Chunks: ")
    print(chunks)
    embedder_instance = embedder()
    embeddings = embedder_instance.embed_texts(chunks)
    for i, embedding in enumerate(embeddings):
        print(f"Embedding {i+1}: {embedding}")
