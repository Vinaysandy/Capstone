import json
from pathlib import Path

import faiss
import numpy as np
from docx import Document
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data" / "medical_documents"
STORE_DIR = Path(__file__).resolve().parent / "faiss_index"

INDEX_FILE = STORE_DIR / "medical.index"
METADATA_FILE = STORE_DIR / "metadata.json"
MODEL_NAME = "all-MiniLM-L6-v2"


def read_document(file_path: Path) -> str:
    """Read supported document formats."""
    if file_path.suffix.lower() == ".txt":
        return file_path.read_text(encoding="utf-8")

    if file_path.suffix.lower() == ".docx":
        document = Document(file_path)
        return "\n".join(
            paragraph.text for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

    return ""


def split_text(text: str, chunk_size: int = 120, overlap: int = 20) -> list[str]:
    """Split text into small overlapping word chunks."""
    words = text.split()
    chunks = []

    for start in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[start:start + chunk_size])
        if chunk:
            chunks.append(chunk)

    return chunks


def build_vector_store() -> None:
    documents = list(DOCUMENTS_DIR.glob("*.txt")) + list(DOCUMENTS_DIR.glob("*.docx"))

    if not documents:
        raise FileNotFoundError("No .txt or .docx files found in medical_documents.")

    chunks = []
    metadata = []
    seen_chunks = set()

    for document_path in documents:
        text = read_document(document_path)

        for chunk in split_text(text):
            normalized_chunk = " ".join(chunk.lower().split())

            # Prevents repeated content from being indexed twice.
            if normalized_chunk in seen_chunks:
                continue

            seen_chunks.add(normalized_chunk)
            chunks.append(chunk)
            metadata.append({"source": document_path.name, "text": chunk})

    if not chunks:
        raise ValueError("No readable text was found in the source documents.")

    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    STORE_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))

    with METADATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print(f"Indexed {len(chunks)} unique chunks from {len(documents)} documents.")
    print(f"Index saved to: {INDEX_FILE}")


if __name__ == "__main__":
    build_vector_store()