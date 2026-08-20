from pydantic import BaseModel
from typing import Optional, Any

class QueryRequest(BaseModel):
    question: str
    metadata_filters: Optional[dict[str, Any]] = None

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    sources_metadata: list[dict[str, Any]]
    sub_questions: list[str]
    retry_count: int
    agent_trace: list[dict[str, Any]]
