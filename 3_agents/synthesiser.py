import sys
import time
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from state import ResearchState
from config import OLLAMA_MODEL, OLLAMA_BASE_URL

def get_llm():
    try:
        from langchain_community.llms import Ollama
        return Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.3)
    except ImportError:
        try:
            from langchain_ollama import OllamaLLM as Ollama
            return Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.3)
        except ImportError:
            return None

SYNTHESISER_PROMPT = """You are a research synthesis agent.

Original question: {question}

Retrieved evidence (organised by sub-question):
{evidence}

Write a comprehensive, structured answer to the original question based
ONLY on the retrieved evidence above. 

Rules:
- Cite sources by title when making specific claims
- Use section headers for each major aspect
- Note explicitly if evidence for any aspect was limited
- Do not add information beyond what is in the evidence

Answer:"""

def fallback_synthesise(question: str, retrieved_chunks: dict) -> str:
    sections = []
    sections.append(f"### Executive Summary\nBased on Joint Research Centre (JRC) empirical automotive dataset evidence for: *\"{question}\"*.")

    has_content = False
    for sq, chunks in retrieved_chunks.items():
        sections.append(f"\n#### {sq}")
        if chunks:
            has_content = True
            for c in chunks[:2]:
                title = c.get("title", "JRC Technical Report")
                year = c.get("publication_year", 2023)
                page = c.get("page", 1)
                content = c.get("content", "").strip()
                sections.append(f"- **According to {title} ({year}, Page {page})**:\n  {content[:380]}...")
        else:
            sections.append("- *Limited or sparse evidence found for this specific sub-question in the current JRC dataset index.*")

    if not has_content:
        sections.append("\n*Notice: No matching evidence chunks were retrieved from the JRC database for this query.*")

    return "\n\n".join(sections)

def synthesiser_node(state: ResearchState) -> ResearchState:
    start_time = time.time()
    print(f"\n[SYNTHESISER] Building answer from retrieved chunks...")
    trace = list(state.get("agent_trace", []))

    evidence_parts = []
    sources_used = set()
    sources_metadata_map = {}

    for sq, chunks in state.get("retrieved_chunks", {}).items():
        evidence_parts.append(f"\nSub-question: {sq}")
        if chunks:
            for chunk in chunks[:3]:
                title = chunk.get("title", "JRC Report")
                year = chunk.get("publication_year", 2023)
                source = chunk.get("source", "European Commission JRC")
                page = chunk.get("page", 1)
                url = chunk.get("url", "")
                category = chunk.get("category", "general_transport")

                evidence_parts.append(
                    f"  Source: {title} ({year}, Page {page})\n"
                    f"  Content: {chunk['content'][:400]}"
                )
                if title:
                    sources_used.add(title)
                    sources_metadata_map[title] = {
                        "title": title,
                        "publication_year": year,
                        "source": source,
                        "category": category,
                        "page": page,
                        "url": url,
                        "chunk_id": chunk.get("chunk_id", "")
                    }
        else:
            evidence_parts.append("  [No relevant evidence found]")

    evidence_text = "\n".join(evidence_parts)
    draft = ""

    llm = get_llm()
    if llm:
        try:
            prompt_str = SYNTHESISER_PROMPT.format(
                question=state["question"],
                evidence=evidence_text
            )
            draft = llm.invoke(prompt_str)
            if not isinstance(draft, str):
                draft = getattr(draft, "content", str(draft))
        except Exception as e:
            print(f"[SYNTHESISER] Ollama invocation failed ({e}). Using evidence synthesis engine.")

    if not draft:
        draft = fallback_synthesise(state["question"], state.get("retrieved_chunks", {}))

    print(f"[SYNTHESISER] Draft answer generated ({len(draft)} chars)")

    elapsed = round(time.time() - start_time, 2)
    step_num = len(trace) + 1
    est_tokens = len(draft) // 4

    trace.append({
        "step": step_num,
        "agent": "Synthesiser",
        "icon": "✍️",
        "status": "SUCCESS",
        "title": "Synthesiser Execution",
        "detail": f"Synthesised evidence-backed report citing {len(sources_used)} JRC document sources.",
        "metrics": f"~{est_tokens} tokens synthesized",
        "latency_sec": elapsed,
        "timestamp": datetime.now().isoformat()
    })

    return {
        **state,
        "draft_answer": draft,
        "sources_used": list(sources_used),
        "sources_metadata": list(sources_metadata_map.values()),
        "agent_trace": trace
    }
