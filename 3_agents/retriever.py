import sys
import time
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from state import ResearchState
from config import CHROMA_PATH, EMBED_MODEL, OLLAMA_BASE_URL

try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    from langchain_chroma import Chroma

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

def get_vectorstore():
    embeddings = get_embeddings_model()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

def retriever_node(state: ResearchState) -> ResearchState:
    start_time = time.time()
    vectorstore = get_vectorstore()
    retrieved = dict(state.get("retrieved_chunks", {}))
    trace = list(state.get("agent_trace", []))
    filters = state.get("metadata_filters", {}) or {}

    gaps = state.get("gaps_identified", [])
    is_retry = bool(gaps)

    if is_retry:
        questions_to_retrieve = gaps
        print(f"\n[RETRIEVER] Retry mode - retrieving for {len(gaps)} gaps")
    else:
        questions_to_retrieve = state.get("sub_questions", [])
        print(f"\n[RETRIEVER] First pass - {len(questions_to_retrieve)} sub-questions")

    total_chunks_retrieved = 0

    # Build Chroma metadata filter dict if provided
    chroma_filter = {}
    if filters.get("category"):
        chroma_filter["category"] = filters["category"]
    if filters.get("year"):
        chroma_filter["publication_year"] = int(filters["year"])

    filter_kw = {"filter": chroma_filter} if chroma_filter else {}

    for sq in questions_to_retrieve:
        try:
            results = vectorstore.similarity_search_with_score(sq, k=5, **filter_kw)
        except Exception as e:
            print(f"  Error performing search for '{sq}': {e}")
            results = []

        chunks = []
        for doc, score in results:
            if score < 1.6:  # Similarity threshold
                chunks.append({
                    "chunk_id": doc.metadata.get("chunk_id", f"chk_{len(chunks)}"),
                    "document_id": doc.metadata.get("document_id", ""),
                    "dataset_id": doc.metadata.get("dataset_id", ""),
                    "title": doc.metadata.get("title", ""),
                    "source": doc.metadata.get("source", "European Commission - Joint Research Centre (JRC)"),
                    "category": doc.metadata.get("category", "general_transport"),
                    "publication_year": doc.metadata.get("publication_year", 2023),
                    "page": doc.metadata.get("page", 1),
                    "url": doc.metadata.get("url", ""),
                    "content": doc.page_content,
                    "score": round(float(score), 3),
                })

        retrieved[sq] = chunks
        total_chunks_retrieved += len(chunks)
        status = f"{len(chunks)} chunks" if chunks else "sparse"
        print(f"  '{sq[:60]}...' -> {status}")

    elapsed = round(time.time() - start_time, 2)
    step_num = len(trace) + 1

    trace.append({
        "step": step_num,
        "agent": "Retriever",
        "icon": "🔎",
        "status": "SUCCESS",
        "title": "Retriever Execution" + (" (Retry Pass)" if is_retry else ""),
        "detail": f"Retrieved {total_chunks_retrieved} context chunks across {len(questions_to_retrieve)} queries with full provenance.",
        "metrics": f"{total_chunks_retrieved} sources retrieved",
        "latency_sec": elapsed,
        "timestamp": datetime.now().isoformat()
    })

    return {
        **state,
        "retrieved_chunks": retrieved,
        "gaps_identified": [],
        "agent_trace": trace
    }
