import subprocess
import csv
from rag_adapter.adapter import Adapter
from rag_embedder.embedder import embedder
from rag_vector_database_FAISS.vector_database import vector_database
from rag_reranker.re_ranker import ReRankerComponent

def run_powershell_script(script_path):
    """Run a PowerShell script."""
    try:
        subprocess.run(["powershell.exe", "-File", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell script: {e}")

def load_logs(file_paths):
    """Loads logs from multiple CSV files."""
    logs = []
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                logs.append(' '.join(row))  # Combine all columns into a single string for each log entry
    return logs

def parse_and_store_logs(log_file_paths):
    """Parse logs and store embeddings in the vector database."""
    # Initialize components
    adapter = Adapter(chunk_size=500, chunk_overlap=2)
    embedder_instance = embedder(embedding_model="all-MiniLM-l6-v2")
    vector_db = vector_database(name="faiss")

    # Load and preprocess logs
    logs = load_logs(log_file_paths)
    chunks = adapter.get_chunks(logs)

    # Generate embeddings
    embeddings = embedder_instance.embed_texts(chunks)

    # Store embeddings in the vector database
    metadata = {"source": "logs"}  # Adjust metadata as needed
    vector_db.insert_embeddings(embeddings, chunks, metadata)
    print("Logs parsed and stored successfully.")

def query_logs(query, top_n=None):
    """Query logs and return most relevant chunks. If top_n is None, return all chunks."""
    # Initialize components
    embedder_instance = embedder(embedding_model="all-MiniLM-l6-v2")
    vector_db = vector_database(name="faiss")
    re_ranker = ReRankerComponent(model_name="BAAI/bge-reranker-v2-m3")

    # Embed the query
    query_embeddings = embedder_instance.embed_texts([query])
    if not query_embeddings:
        raise ValueError("Embedding of the query returned an empty result.")
    
    query_embedding = query_embeddings[0]
    print(f"Query Embedding: {query_embedding}")

    # Retrieve relevant chunks for the query
    chunk_count = top_n if top_n else len(query_embedding)
    retrieved_chunks = vector_db.search_query(embedding_vector=query_embedding, chunk_count=chunk_count)

    # Remove duplicates
    unique_chunks = list(set(retrieved_chunks))

    # Re-rank retrieved chunks
    if top_n:
        re_ranked_chunks = re_ranker._rerank(model_name="BAAI/bge-reranker-v2-m3", top_n=top_n, query=query, chunks=unique_chunks)
    else:
        re_ranked_chunks = unique_chunks

    return re_ranked_chunks

# Path to the PowerShell script
powershell_script_path = r"ExportSystemLogs.ps1"

# Run the PowerShell script to export logs
run_powershell_script(powershell_script_path)

# Paths to the exported log files
log_file_paths = [
    r"SystemLog.csv",
    r"ApplicationLog.csv",
    r"SecurityLog.csv"
]

# Parse and store logs
parse_and_store_logs(log_file_paths)

# Query logs
query = "failed"
retrieved_chunks = query_logs(query)

# Print all retrieved chunks
print("All retrieved log chunks:")
for chunk in retrieved_chunks:
    print(chunk)
