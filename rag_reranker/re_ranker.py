import torch
import numpy as np
from typing import List
from transformers import AutoTokenizer, AutoModel, pipeline

class ReRankerComponent:
    def __init__(self, model_name):
        self.pipe = pipeline("feature-extraction", model=model_name, truncation = True, padding = 512)
        self.supported_models = ['BAAI/bge-m3', "BAAI/bge-reranker", "BAAI/bge-large", "BAAI/bge-large-en-v1.5"]

    def _rerank(self, model_name, top_n, query, chunks, verbose = True):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.model.eval()
        self.verboseprint = print if verbose else lambda *a: None

        self.verboseprint(f"RERANKER: {self.model_name} initialized successfully!")
        if self.model_name in self.supported_models:
            query_chunk = self._encode_query(query)
            encoded_chunks = self.pipe(chunks)
            encoded_chunks = [embeds[0] for embeds in encoded_chunks]
            scores = [self._compute_scores(np.array(embeds), np.array(query_chunk)) for embeds in encoded_chunks]
            sort_indexes = np.argsort(scores).tolist()
            re_ranked_chunks = [chunks[index] for index in sort_indexes]
            return re_ranked_chunks[:top_n]

        else:
            raise ValueError("Unsupported Model.Please provide a valid model")

    def _compute_scores(self, chunk_embeddings, query_embeddings):
        dot_product = np.dot(chunk_embeddings, query_embeddings.T)
        norm_x = np.linalg.norm(chunk_embeddings)
        norm_y = np.linalg.norm(query_embeddings)
        similarity_scores = dot_product / (norm_x * norm_y)
        similarity_scores = np.mean(similarity_scores)
        return similarity_scores

    def _encode_query(self, query: str):
        encoded_query = self.tokenizer([query], padding = True, truncation = True, return_tensors = "pt", add_special_tokens=True)
        query_embeddings = self._generate_embeddings(encoded_query)
        return query_embeddings.tolist()[0]

    def _generate_embeddings(self, tokens):
        with torch.no_grad():
            model_output = self.model(**tokens)
            # Performing CLS pooling.
            sentence_embeddings = model_output[0][:, 0]

        return sentence_embeddings