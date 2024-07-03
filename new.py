from rag_adapter.adapter import Adapter
from rag_embedder.embedder import embedder
from rag_vector_database_FAISS.vector_database import vector_database
from rag_reranker.re_ranker import ReRankerComponent
from rag_retriever_FAISS.retriever import vector_database

def load_logs(file_path):
    """Loads logs from a file."""
    with open(file_path, 'r') as file:
        logs = file.readlines()
    return logs

def parse_and_store_logs(log_file_path):
    """Parse logs and store embeddings in the vector database."""
    # Initialize components
    adapter = Adapter(chunk_size=500, chunk_overlap=10)
    embedder_instance = embedder(embedding_model="all-MiniLM-l6-v2")
    vector_db = vector_database(name="faiss")

    # Load and preprocess logs
    logs = load_logs(log_file_path)
    chunks = adapter.get_chunks(logs)

    # Generate embeddings
    embeddings = embedder_instance.embed_texts(chunks)

    # Store embeddings in the vector database
    metadata = {"source": "logs"}  # Adjust metadata as needed
    vector_db.insert_embeddings(embeddings, chunks, metadata)
    print("Logs parsed and stored successfully.")

def query_logs(query, top_n):
    """Query logs and return top_n most relevant chunks."""
    # Initialize components
    embedder_instance = embedder(embedding_model="all-MiniLM-l6-v2")
    vector_db = vector_database(name="faiss")
    re_ranker = ReRankerComponent(model_name="BAAI/bge-reranker-v2-m3")

    # Embed the query
    query_embedding = embedder_instance.embed_texts([query])[0]

    # Retrieve relevant chunks for the query
    retrieved_chunks = vector_db.search_query(embedding_vector=query_embedding, chunk_count=top_n)

    # Re-rank retrieved chunks
    re_ranked_chunks = re_ranker._rerank(model_name="BAAI/bge-reranker-v2-m3", top_n=top_n, query=query, chunks=retrieved_chunks)

    return re_ranked_chunks

# Parse and store logs
log_file_path = "Windows_2k.log"
parse_and_store_logs(log_file_path)

# Query logs
query = "Ending "
top_chunks = query_logs(query, top_n=15)

# Print the top re-ranked chunks
print("Top relevant log chunks:")
for chunk in top_chunks:
    print(chunk)
