import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
STORE_DIR = Path(__file__).resolve().parent / "faiss_index"

INDEX_FILE = STORE_DIR / "medical.index"
METADATA_FILE = STORE_DIR / "metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"


def retrieve_context(query: str, top_k: int = 3, min_score: float = 0.30) -> list[dict]:
    """Return the most relevant approved document chunks for a query."""
    if not INDEX_FILE.exists() or not METADATA_FILE.exists():
        raise FileNotFoundError(
            "RAG index not found. Run: python rag/vector_store.py"
        )

    index = faiss.read_index(str(INDEX_FILE))

    with METADATA_FILE.open("r", encoding="utf-8") as file:
        metadata = json.load(file)

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).astype("float32")

    limit = min(top_k, len(metadata))
    scores, indexes = index.search(query_embedding, limit)

    results = []

    for score, chunk_index in zip(scores[0], indexes[0]):
        if chunk_index == -1 or score < min_score:
            continue

        results.append({
            "source": metadata[chunk_index]["source"],
            "text": metadata[chunk_index]["text"],
            "score": round(float(score), 3),
        })

    return results


if __name__ == "__main__":
    question = "Can this assistant diagnose a disease?"
    results = retrieve_context(question)

    for result in results:
        print(f"\nSource: {result['source']} | Score: {result['score']}")
        print(result["text"])