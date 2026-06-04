import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings

DATA_PATH = "data/mentor_docs"
DB_PATH = "embeddings/faiss_index"

def load_documents():
    documents = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".txt"):
            loader = TextLoader(
                os.path.join(DATA_PATH, file),
                encoding="utf-8"
            )
            documents.extend(loader.load())
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_documents(documents)

def create_vector_db(chunks):
    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vector_db = FAISS.from_documents(chunks, embeddings)
    vector_db.save_local(DB_PATH)

def main():
    print("Loading documents...")
    documents = load_documents()

    print("Splitting documents...")
    chunks = split_documents(documents)

    print("Creating embeddings & saving to FAISS...")
    create_vector_db(chunks)

    print("✅ RAG ingestion completed successfully!")

if __name__ == "__main__":
    main()
