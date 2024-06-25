from langchain.embeddings import HuggingFaceEmbeddings
import json
import sys


class embedder:
    def __init__(self, embedding_model: str = "all-MiniLM-l6-v2", verbose: bool = True):
        self.verboseprint = print if verbose else lambda *a: None
        try:
            self.model_name = embedding_model
            self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model)

            self.verboseprint(
                f"EMBEDDER: Embedder initialized successfully with configuration: embedding_model = {self.model_name}"
            )
        except Exception as e:
            self.verboseprint(
                f"EMBEDDER: Embedder initialization failed. Error:{str(e)}"
            )

    def embed_texts(self, texts: list) -> list:
        """Generates the embeddings for the given list of texts."""

        try:
            embedding_vectors = [self.embedding_model.embed_query(text) for text in texts]
            return embedding_vectors
        except Exception as e:
            self.verboseprint(f"EMBEDDER: Embed query failed. Error:{str(e)}")
            return []