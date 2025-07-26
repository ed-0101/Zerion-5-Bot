# File: app/utils/rag_engine.py

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(persist_directory="../data/chroma_store"))

embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def initialize_rag_engine():
    collection = client.get_or_create_collection(
        name="zerion5_travel_data",
        embedding_function=embedding_fn
    )
    return collection

def add_documents(collection, texts: list, metadatas: list):
    ids = [f"doc_{i}" for i in range(len(texts))]
    collection.add(documents=texts, ids=ids, metadatas=metadatas)

def query_documents(collection, query: str, top_k: int = 3):
    results = collection.query(query_texts=[query], n_results=top_k)
    return results
