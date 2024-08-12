import sys
from embedder import embedder
import pandas as pd


if __name__ == "__main__":
    
    chunks = ['hi','my name', 'is', 'Vanishka']
    embedder_instance = embedder()
    embeddings = embedder_instance.embed_texts(chunks)
    for i, embedding in enumerate(embeddings):
        print(f"Embedding {i+1}: {embedding}")
