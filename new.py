import pandas as pd
from datasets import Dataset, DatasetDict
from rag_embedder.embedder import Embedder
from rag_adapter.adapter import Adapter
from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration, TrainingArguments, Trainer
import os
import numpy as np

# Load your data
logs = pd.read_csv('Windows_2k.log_structured_original.csv')  # Example log file

# Example: Prepare a dataframe with 'query' and 'context'
data = {
    'query': logs['Component'],
    'context': logs['Content'],
}

# Convert to Hugging Face dataset
dataset = Dataset.from_pandas(pd.DataFrame(data))

# Split the dataset into training and test sets
split_dataset = dataset.train_test_split(test_size=0.2)

# Initialize adapter and embedder
adapter = Adapter()
embedder = Embedder()

# Chunk and embed logs
def preprocess_logs(examples):
    chunked_logs = adapter.get_chunks(examples['context'])
    embedded_logs = embedder.embed_texts(chunked_logs)
    embedding_dim = len(embedded_logs[0]) if embedded_logs else 0
    # Creating placeholders for title
    titles = [""] * len(chunked_logs)
    return {
        'title': titles,
        'text': chunked_logs,
        'embeddings': embedded_logs,
        'embedding_dim': [embedding_dim] * len(chunked_logs)  # ensure embedding_dim is a list
    }

# Apply preprocessing
preprocessed_dataset = split_dataset.map(preprocess_logs, batched=True, remove_columns=["context"])

# Save dataset without indexes
dataset_path = "dataset_path"
index_path = "index_path"

# Ensure directory exists
os.makedirs(dataset_path, exist_ok=True)
os.makedirs(index_path, exist_ok=True)

# Save dataset to disk
for split in preprocessed_dataset:
    split_dataset = preprocessed_dataset[split]
    split_dataset.save_to_disk(os.path.join(dataset_path, split))

# Reload the dataset and add FAISS index for each split
for split in preprocessed_dataset:
    split_dataset = Dataset.load_from_disk(os.path.join(dataset_path, split))
    split_dataset.add_faiss_index(column="embeddings")
    split_dataset.get_index("embeddings").save(os.path.join(index_path, f"{split}_index"))

# Load tokenizer
from transformers import RagTokenizer
tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")

# Tokenize queries
def tokenize_function(examples):
    inputs = tokenizer(examples['query'], padding="max_length", truncation=True, max_length=512)
    inputs["context_input_ids"] = examples['embeddings']
    inputs["context_attention_mask"] = [[1] * len(context) for context in examples['embeddings']]
    return inputs

# Tokenize the preprocessed dataset
tokenized_datasets = preprocessed_dataset.map(tokenize_function, batched=True)

# Ensure the query embeddings match the expected dimensionality
query_embedding_dim = np.asarray(embedder.embedding_model.embed_query("test query")).shape[-1]
for split in tokenized_datasets:
    assert tokenized_datasets[split]['embedding_dim'][0] == query_embedding_dim, \
        f"Embedding dimensionality mismatch: {tokenized_datasets[split]['embedding_dim'][0]} vs {query_embedding_dim}"

# Initialize retriever with saved dataset and index for each split
from transformers import RagRetriever, RagTokenForGeneration, TrainingArguments, Trainer

retrievers = {}
for split in tokenized_datasets:
    retrievers[split] = RagRetriever.from_pretrained(
        "facebook/rag-token-nq",
        index_name="custom",
        passages_path=os.path.join(dataset_path, split),
        index_path=os.path.join(index_path, f"{split}_index")
    )

# Initialize model and set retrievers for each split
model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq")
model.set_retriever(retrievers['train'])

# Define training arguments and trainer
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets['train'],
    eval_dataset=tokenized_datasets['test'],
)

# Train the model
trainer.train()