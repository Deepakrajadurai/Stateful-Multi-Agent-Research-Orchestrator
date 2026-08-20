import json
import os
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    from langchain_chroma import Chroma

from config import CHROMA_PATH, EMBED_MODEL, OLLAMA_BASE_URL

def get_embeddings_model():
    try:
        import requests
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
        if resp.status_code == 200:
            try:
                from langchain_community.embeddings import OllamaEmbeddings
                return OllamaEmbeddings(model=EMBED_MODEL, base_url=OLLAMA_BASE_URL)
            except Exception:
                pass
    except Exception:
        pass

    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    except Exception:
        from langchain_huggingface import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_documents() -> list[Document]:
    doc_file = os.path.join(ROOT_DIR, "1_data", "jrc_documents.json")
    if not os.path.exists(doc_file):
        raise FileNotFoundError(f"Corpus file {doc_file} not found. Run fetch_jrc.py and fetch_pdfs.py first.")

    with open(doc_file, "r", encoding="utf-8") as f:
        raw_docs = json.load(f)

    docs = []
    for d in raw_docs:
        full_text = d["metadata_text"]
        if d.get("pdf_text"):
            full_text += "\n\nExtracted Report Content:\n" + d["pdf_text"]

        if len(full_text.strip()) < 100:
            continue

        docs.append(Document(
            page_content=full_text,
            metadata={
                "document_id": d["id"],
                "dataset_id": d["id"],
                "title": d["title"],
                "source": d.get("organization", "European Commission - Joint Research Centre (JRC)"),
                "category": d.get("category", "general_transport"),
                "publication_year": int(d.get("publication_year", 2023)),
                "url": d["url"],
                "tags": ", ".join(d.get("tags", [])),
            }
        ))
    return docs

def main():
    print("Loading JRC corpus documents...")
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")

    print("Splitting into fine-grained chunks for adversarial retrieval testing...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=250,
        chunk_overlap=40,
        separators=["\n\n", "\n", ". ", " "]
    )

    chunks = []
    for doc in docs:
        doc_chunks = splitter.split_documents([doc])
        for idx, chunk in enumerate(doc_chunks, 1):
            chunk.metadata["chunk_id"] = f"{doc.metadata['document_id']}_chk_{idx}"
            chunk.metadata["page"] = (idx // 2) + 1
            chunks.append(chunk)

    print(f"Created {len(chunks)} fine-grained metadata-enriched chunks")

    embeddings = get_embeddings_model()

    print(f"Embedding and storing in Chroma at {CHROMA_PATH}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print(f"Index successfully built: {len(chunks)} chunks stored at {CHROMA_PATH}")
    return vectorstore

if __name__ == "__main__":
    main()
