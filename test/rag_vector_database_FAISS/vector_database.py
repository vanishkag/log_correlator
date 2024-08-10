from langchain_community.vectorstores import FAISS
import sys
import json
import random
import os


DB_FOLDER = "faiss_database"


class dummy_embedder:  # Langchain's vector db and embedder are tightly coupled. Giving an embedder is mandatory everywhere. Hence we give a dummy embedder class, and use search_by_vector
    def __init__(self):
        pass

    def embed_documents(self):
        return []

    def embed_query(self):
        return []


de = dummy_embedder()


class vector_database:
    def __init__(self, name: str = "faiss", verbose: bool = True):
        self.verboseprint = print if verbose else lambda *a: None
        self.name = name
        self.verboseprint(
            f"VECTOR DATABASE: Vector Database initialised successfully with  configuration: name = {self.name}"
        )
        self.db_client = None

    def insert_embeddings(
        self, embedding_list: list, chunk_list: list, metadata: dict
    ) -> bool:
        """Inserts the embeddings into the DB. returns a bool"""
        try:
            
            if os.path.exists(os.path.join(os.getcwd(), DB_FOLDER)):
                self.db_client = FAISS.load_local(DB_FOLDER, de)
                text_embedding_pairs = zip(chunk_list, embedding_list)
                metadatas = [metadata for i in range(len(chunk_list))]
                # print(metadatas)
                self.db_client.add_embeddings(
                    text_embedding_pairs,
                    metadatas,
                )
            else:
                text_embedding_pairs = list(zip(chunk_list, embedding_list))
                metadatas = [metadata for i in range(len(chunk_list))]
                self.db_client = FAISS.from_embeddings(
                    text_embedding_pairs, de, metadatas
                )

            self.verboseprint(
                f"VECTOR DATABASE: Embeddings inserted successfully. Number of embeddings = {len(embedding_list)} "
            )
            self.db_client.save_local(DB_FOLDER)
            return True
        except Exception as e:
            self.verboseprint(
                f"VECTOR DATABASE: Embeddings insertion failed. Error: {e}"
            )
            return False

    def search_query(
        self, embedding_vector: list, chunk_count: int, search_filter: dict = None
    ):
        """Searches the DB and returns the list of k most relevant chunks."""
        try:
            self.db_client = FAISS.load_local(DB_FOLDER, de)
            results = self.db_client.similarity_search_by_vector(
                embedding=embedding_vector, k=chunk_count, filter=search_filter
            )
            chunks = [doc.page_content for doc in results]
            self.verboseprint(f"VECTOR DATABASE: Search Successful. ")
            return chunks
        except Exception as e:
            self.verboseprint(f"VECTOR DATABASE: Query search failed. Error: {e}")
            return []
        