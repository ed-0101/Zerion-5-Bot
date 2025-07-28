# File: app/utils/ollama_rag_engine_v2.py

import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document  

# Configuration
zerion_data = "../data/zerion5_visitor_guide_expanded.txt"
DATA_DIR = "../data"
CHROMA_DIR = "../data/chroma_store_ollama"
LLM_MODEL = "llama3.2"
EMBED_MODEL = "mxbai-embed-large"

# Check if documents need to be added
add_documents = not os.path.exists(CHROMA_DIR)
print(add_documents)

# Load text and split into chunks
def load_text_chunks(file_path, chunk_size):
    documents = []
    ids = []
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        filename = os.path.basename(file_path)
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        for i, chunk in enumerate(chunks):
            document = Document(
                page_content=chunk,
                metadata={
                    "chunk_index": i,
                    "source": filename
                }
            )
            documents.append(document)
            ids.append(str(i))
    return documents, ids

# Initialize Chroma vector store
vector_store = Chroma(
    collection_name="Zerion_data_collection",
    persist_directory=CHROMA_DIR,
    embedding_function=OllamaEmbeddings(model=EMBED_MODEL)
)

# Add documents to the store if needed
if add_documents:
    documents, ids = load_text_chunks(zerion_data, 500)
    print(f"Adding {len(documents)} documents to the vector store.")
    vector_store.add_documents(documents=documents, ids=ids)

# Convert the vector store into a retriever object with top-k search
retriever = vector_store.as_retriever(
    search_kwargs={"k": 5}  # Return top 5 most relevant documents
)

# Interactive QA loop
if __name__ == "__main__":
    # Load and show chunk info
    chunks, metadatas = load_text_chunks(zerion_data, 500)
    print(f"Loaded {len(chunks)} chunks from {zerion_data}")

    # Initialize LLM and QA chain
    llm = OllamaLLM(model=LLM_MODEL)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    print("\n🔍 Zerion-5 RAG QA engine is ready.\n")

    # Continuous Q&A loop
    while True:
        query = input("Ask a question (or type 'no', 'exit' to stop): ").strip().lower()
        if query in ["no", "exit", "quit"]:
            print("👋 Exiting the QA loop. Have a great day!")
            break

        response = qa_chain.invoke({"query": query})
        answer = response.get("result", "Sorry, I couldn't find an answer.")
        print(f"\n📌 Answer: {answer}\n")
