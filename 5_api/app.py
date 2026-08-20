import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from state import ResearchState

try:
    from schemas import QueryRequest, QueryResponse
except ImportError:
    from api.schemas import QueryRequest, QueryResponse

try:
    from graph.research_graph import research_graph
except ImportError:
    from research_graph import research_graph

app = FastAPI(
    title="Stateful Multi-Agent Research Orchestrator",
    description="JRC automotive data research using LangGraph agents with validator feedback loops",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    initial_state: ResearchState = {
        "question": req.question,
        "metadata_filters": req.metadata_filters,
        "sub_questions": [],
        "retrieved_chunks": {},
        "draft_answer": "",
        "validation_passed": False,
        "gaps_identified": [],
        "retry_count": 0,
        "agent_trace": [],
        "final_answer": "",
        "sources_used": [],
        "sources_metadata": []
    }

    result = research_graph.invoke(initial_state)

    return QueryResponse(
        question=req.question,
        answer=result["final_answer"],
        sources=result["sources_used"],
        sources_metadata=result.get("sources_metadata", []),
        sub_questions=result["sub_questions"],
        retry_count=result["retry_count"],
        agent_trace=result.get("agent_trace", []),
    )
