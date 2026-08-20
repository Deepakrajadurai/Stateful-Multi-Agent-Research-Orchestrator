# Stateful Multi-Agent Research Orchestrator (v2.0 Production Grade)

> An autonomous stateful multi-agent system built with LangGraph that decomposes complex European Joint Research Centre (JRC) automotive queries, performs semantic retrieval over vectorized documents with provenance tracking, synthesises evidence-backed answers, and uses an iterative validator feedback loop with execution tracing to guarantee answer completeness.

---

## 📐 Architecture Diagram

```
                                  User Question
                                        │
                                        ▼
                               ┌─────────────────┐
                               │    PLANNER      │ ──► sub_questions[]
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │   RETRIEVER     │ ──► retrieved_chunks{}
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │  SYNTHESISER    │ ──► draft_answer
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │    VALIDATOR    │ ──► validation_passed?
                               └────────┬────────┘
                                        │
                       ┌────────────────┴────────────────┐
                       ▼                                 ▼
                    [ YES ]                           [ NO ]
                       │                                 │
                       ▼                                 ▼
                 Final Answer                    gaps_identified[]
                                                         │
                                                         ▼
                                              [ Loop to RETRIEVER ]
                                                 (Max 2 retries)
```

---

## 📊 Adversarial Benchmark Evaluation Metrics

The system was evaluated across a 30-case benchmark suite categorized into **Group A (Normal Single-Domain)**, **Group B (Hard Niche Retrieval)**, and **Group C (Multi-Domain Recovery Loop)** test cases:

| Benchmark Metric | Group A (Normal) | Group B (Hard Retrieval) | Group C (Recovery Loop) | Overall Fleet |
| :--- | :---: | :---: | :---: | :---: |
| **Test Cases** | 10 | 10 | 10 | **30** |
| **Retrieval Recall@5** | **97.5%** | **83.3%** | **69.0%** | **83.3%** |
| **Answer Completeness** | **100%** | **100%** | **100%** | **100%** |
| **Citation Correctness** | **100%** | **100%** | **100%** | **100%** |
| **Validator Pass Rate** | **100%** | **100%** | **100%** | **100%** |
| **Retries Triggered** | **0** | **0** | **1 (Recovery)** | **1** |
| **Retry Recovery Rate** | N/A | N/A | **100.0%** | **100.0%** |
| **Avg. Graph Iterations** | **1.0** | **1.0** | **1.1** | **1.03** |
| **Avg. Query Latency** | **22.5s** | **19.2s** | **20.7s** | **20.8s** |

---

## 🏷️ Document Provenance & Metadata Schema

Every document chunk indexed in Chroma DB retains explicit provenance tags:

```json
{
    "document_id": "jrc-bev-cold-temp-2024",
    "dataset_id": "jrc-bev-cold-temp-2024",
    "title": "JRC EV Cold Weather Real-World Energy Consumption & Sub-Zero Range Degradation",
    "source": "European Commission - Joint Research Centre (JRC)",
    "category": "electric_vehicle",
    "publication_year": 2024,
    "page": 1,
    "url": "https://data.jrc.ec.europa.eu/dataset/jrc-bev-cold-temp-2024",
    "chunk_id": "jrc-bev-cold-temp-2024_chk_1"
}
```

Rendered on the Frontend UI:

```
SOURCE
European Commission — JRC

DOCUMENT
JRC EV Cold Weather Real-World Energy Consumption & Sub-Zero Range Degradation

CATEGORY
Electric Vehicles (BEV)

YEAR
2024

PAGE
1
```

---

## 🧠 Live Agent Execution Tracing

The frontend UI displays a real-time execution trace timeline showing the recovery loop firing when gaps are identified:

```
┌────────────────────────────────────────────────────────┐
│ AGENT EXECUTION TRACE (Group C Multi-Domain Recovery)  │
├────────────────────────────────────────────────────────┤
│                                                        │
│ 🧠 Planner                ✓  (0.01s)                  │
│    Decomposed query into 3 targeted sub-questions      │
│                                                        │
│ 🔎 Retriever (Pass #1)    ✓  (0.04s)                  │
│    Retrieved 15 chunks with full provenance metadata   │
│                                                        │
│ ✍️ Synthesiser            ✓  (0.02s)                  │
│    ~840 tokens synthesized                             │
│                                                        │
│ 🔍 Validator              ⚠️  (0.01s)                  │
│    Gaps: Hydrogen fuel cell stack durability           │
│                                                        │
│ 🔄 Recovery Loop          →  (0.01s)                  │
│    Routing state back to Retriever (Pass #2)           │
│                                                        │
│ 🔎 Retriever (Pass #2)    ✓  (0.03s)                  │
│    Retrieved targeted missing gap chunks               │
│                                                        │
│ 🔍 Validator              ✓  (0.01s)                  │
│    Answer passed quality validation                    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

- **Orchestration**: [LangGraph](https://github.com/langchain-ai/langgraph) (`StateGraph` with stateful recovery loop)
- **Agent Framework**: [LangChain](https://github.com/langchain-ai/langchain)
- **Vector Database**: [Chroma DB](https://www.trychroma.com/)
- **Local Inference & Embeddings**: [Ollama](https://ollama.ai/) (`nomic-embed-text` & `llama3.2`) / HuggingFace `all-MiniLM-L6-v2`
- **Data Source & Extraction**: European Commission Joint Research Centre (JRC) Data Catalogue & `pdfplumber`
- **Backend API**: FastAPI & Uvicorn
- **Frontend**: Glassmorphic HTML5 & Vanilla JavaScript
- **Containerization**: Docker & Docker Compose

---

## 💡 Benchmark Research Queries

1. *"How does cold weather affect real-world EV range degradation according to JRC VELA data?"*
2. *"What is the gap between WLTP laboratory ratings and real-world fuel consumption for plug-in hybrids?"*
3. *"What are the key findings from JRC research on real-world CO2 emissions under RDE conditions?"*
4. *"Compare battery-electric vehicle cold weather range degradation with heavy-duty hydrogen fuel cell stack durability and PHEV WLTP fuel gaps under Euro 7 regulations."*

---

## 🚀 Quickstart Guide

### 1. Local Setup

```bash
# Clone repository and create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Fetch JRC dataset metadata & build manifest
python 1_data/fetch_jrc.py
python 1_data/fetch_pdfs.py

# Build vector store index with full provenance
python 2_vectorstore/build_index.py

# Run 3-Group Adversarial Benchmark Suite
python evaluation/run_evaluation.py 30

# Launch FastAPI backend
uvicorn 5_api.app:app --reload --port 8000

# Serve Frontend UI
python -m http.server 3000 --directory 6_frontend
```

### 2. Docker Setup

```bash
docker-compose up --build
```

Access the frontend UI at `http://localhost:3000` and API docs at `http://localhost:8000/docs`.

---

## 📁 Repository Structure

```
stateful-multi-agent-research-orchestrator/
│
├── 1_data/
│   ├── fetch_jrc.py              # Stage 1: fetch JRC dataset metadata
│   ├── fetch_pdfs.py             # Stage 2: download & extract PDF report text
│   ├── corpus_manifest.json      # Structured manifest of all indexed documents
│   ├── jrc_datasets.json         # Raw fetched metadata catalog
│   ├── jrc_documents.json        # Processed text corpus
│   ├── raw/                      # Raw API output files
│   └── processed/                # Processed corpus JSON files
│
├── 2_vectorstore/
│   ├── build_index.py            # Stage 3: chunk, embed with provenance, store in Chroma
│   └── chroma_db/                # Persisted Chroma DB vector store
│
├── 3_agents/
│   ├── planner.py                # Stage 4: decomposes questions & traces execution
│   ├── retriever.py              # Stage 5: semantic search with metadata filtering
│   ├── synthesiser.py            # Stage 6: synthesises evidence report with citations
│   └── validator.py              # Stage 7: quality validation & recovery loop trigger
│
├── 4_graph/
│   └── research_graph.py         # Stage 8: wires agents into stateful LangGraph
│
├── 5_api/
│   ├── app.py                    # Stage 9: FastAPI backend API
│   └── schemas.py                # Request & response Pydantic models with trace schemas
│
├── 6_frontend/
│   ├── index.html                # Stage 10: Glassmorphic UI with trace & metadata filter
│   └── app.js                    # Frontend client & execution timeline renderer
│
├── evaluation/
│   ├── questions.json            # 30-case 3-group benchmark dataset (Group A, B, C)
│   ├── metrics.py                # Grouped recall, completeness & citation metrics
│   ├── run_evaluation.py         # Automated evaluation test suite runner
│   └── results/
│       └── eval_report.json      # Adversarial benchmark results
│
├── Dockerfile                    # Container build configuration
├── docker-compose.yml            # Production container orchestration
├── state.py                      # Shared state schema (TypedDict) with agent_trace
├── config.py                     # Central configuration & sys.path management
├── main.py                       # CLI entry point for testing
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```
