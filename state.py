from typing import TypedDict, Optional, Any

class ResearchState(TypedDict):
    # Input
    question: str
    metadata_filters: Optional[dict[str, Any]]

    # Planner output
    sub_questions: list[str]

    # Retriever output
    retrieved_chunks: dict[str, list[dict]]
    # Format: {"sub_question_text": [{"content": "...", "source": "...", "title": "...", "publication_year": 2024, "category": "...", "page": 1, "chunk_id": "..."}]}

    # Synthesiser output
    draft_answer: str

    # Validator output
    validation_passed: bool
    gaps_identified: list[str]
    retry_count: int

    # Observability & Traceability
    agent_trace: list[dict[str, Any]]

    # Final output
    final_answer: str
    sources_used: list[str]
    sources_metadata: list[dict[str, Any]]
