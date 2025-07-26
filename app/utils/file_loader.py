# File: app/utils/file_loader.py

import os
import json
import pandas as pd
from app.utils.rag_engine import add_documents, initialize_rag_engine

TEXT_FILES = [
    "app/data/zerion5_visitor_guide_expanded.txt",
    "app/data/planet_profile.txt",
    "app/data/security_protocol.md"
]

JSON_FILES = [
    "app/data/cities_and_countries.json",
    "app/data/local_travel.json"
]

CSV_FILES = [
    "app/data/hotel_directory.csv"
]

def load_and_chunk_text(file_path: str, chunk_size: int = 500):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    metadatas = [{"chunk_index": i, "source": os.path.basename(file_path)} for i in range(len(chunks))]
    return chunks, metadatas

def load_json_data(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_csv_data(file_path: str):
    return pd.read_csv(file_path)

def ingest_file():
    collection = initialize_rag_engine()
    total_chunks = 0
    for file_path in TEXT_FILES:
        chunks, metadatas = load_and_chunk_text(file_path)
        add_documents(collection, chunks, metadatas)
        total_chunks += len(chunks)
    print(f"Ingested {total_chunks} chunks from {len(TEXT_FILES)} files into the RAG collection.")

# Load structured files
json_data = {os.path.basename(f): load_json_data(f) for f in JSON_FILES}
csv_data = {os.path.basename(f): load_csv_data(f) for f in CSV_FILES}