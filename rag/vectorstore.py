import chromadb
from rag.embedder import embed
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection("codebase")

def reset():
    global collection
    try:
        client.delete_collection("codebase")
    except Exception:
        pass
    collection = client.get_or_create_collection("codebase")

def add_documents(docs: list[dict]):
    if not docs:
        return
    collection.add(
        ids=[d["id"] for d in docs],
        embeddings=embed([d["text"] for d in docs]),
        documents=[d["text"] for d in docs],
        metadatas=[d.get("metadata", {}) for d in docs],
    )

def query(q: str, n=5) -> list[dict]:
    results = collection.query(query_embeddings=embed([q]), n_results=n)
    return [
        {"text": t, "metadata": m}
        for t, m in zip(results["documents"][0], results["metadatas"][0])
    ]