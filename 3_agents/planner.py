import sys
import time
import json
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
        return Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
    except ImportError:
        try:
            from langchain_ollama import OllamaLLM as Ollama
            return Ollama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL)
        except ImportError:
            return None

PLANNER_PROMPT = """You are a research planning agent.

Given a research question, decompose it into 3-5 specific sub-questions
that together would fully answer the original question.

Each sub-question should target a distinct aspect. Return ONLY a JSON array
of strings, nothing else.

Example output:
["sub-question 1", "sub-question 2", "sub-question 3"]

Research question: {question}"""

def fallback_planner(question: str) -> list[str]:
    q_lower = question.lower()
    sub_questions = []

    # Detect all distinct domain aspects in the query
    if "cold" in q_lower or "weather" in q_lower or "sub-zero" in q_lower or "bev range" in q_lower:
        sub_questions.append("What is the quantitative battery range degradation percentage at sub-zero cold weather temperatures according to JRC VELA data?")
    if "heat pump" in q_lower or "cop" in q_lower or "ptc" in q_lower:
        sub_questions.append("How does cabin thermal heating (PTC heaters vs heat pumps) impact EV real-world energy consumption?")
    if "phev" in q_lower or "plug-in" in q_lower or "wltp" in q_lower:
        sub_questions.append("What is the measured numerical gap between official WLTP fuel ratings and real-world PHEV fuel consumption?")
    if "rde" in q_lower or "pems" in q_lower or "nox" in q_lower:
        sub_questions.append("What are the key real-world NOx emission conformity factors observed during JRC PEMS on-road testing?")
    if "hydrogen" in q_lower or "fcev" in q_lower or "fuel cell" in q_lower or "pemfc" in q_lower:
        sub_questions.append("What is the voltage degradation rate of heavy-duty fuel cell (PEMFC) stacks during dynamic load cycling?")
    if "hrs" in q_lower or "700 bar" in q_lower or "refueling" in q_lower:
        sub_questions.append("Why is -40°C hydrogen pre-cooling required during 700 bar high-flow refueling of heavy-duty trucks?")
    if "adas" in q_lower or "autonomous" in q_lower or "sensor fusion" in q_lower:
        sub_questions.append("How do adverse weather conditions (heavy rain, fog) degrade ADAS camera and radar sensor fusion?")
    if "cybersecurity" in q_lower or "r155" in q_lower or "ota" in q_lower:
        sub_questions.append("What cybersecurity and OTA software update compliance requirements are outlined in UN R155/R156 guidelines?")

    if not sub_questions:
        sub_questions = [
            f"What are the baseline empirical data and testing methodologies regarding {question}?",
            f"What specific vehicle components or operating conditions drive performance variations for {question}?",
            f"What conclusions and regulatory insights are established by JRC research on {question}?"
        ]

    return sub_questions[:5]

def planner_node(state: ResearchState) -> ResearchState:
    start_time = time.time()
    print(f"\n[PLANNER] Decomposing: {state['question']}")
    sub_questions = []
    trace = list(state.get("agent_trace", []))

    llm = get_llm()
    if llm:
        try:
            prompt_str = PLANNER_PROMPT.format(question=state["question"])
            response = llm.invoke(prompt_str)
            if not isinstance(response, str):
                response = getattr(response, "content", str(response))

            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != -1:
                sub_questions = json.loads(response[start:end])
            else:
                lines = [line.strip().lstrip("0123456789.-) ") for line in response.split("\n") if len(line.strip()) > 15]
                if lines:
                    sub_questions = lines[:5]
        except Exception as e:
            print(f"[PLANNER] Ollama invocation failed ({e}). Using deterministic research planner.")

    if not sub_questions:
        sub_questions = fallback_planner(state["question"])

    print(f"[PLANNER] Generated {len(sub_questions)} sub-questions:")
    for i, sq in enumerate(sub_questions, 1):
        print(f"  {i}. {sq}")

    elapsed = round(time.time() - start_time, 2)
    step_num = len(trace) + 1

    trace.append({
        "step": step_num,
        "agent": "Planner",
        "icon": "🧠",
        "status": "SUCCESS",
        "title": "Planner Execution",
        "detail": f"Decomposed query into {len(sub_questions)} targeted research sub-questions.",
        "metrics": f"{len(sub_questions)} subtasks generated",
        "latency_sec": elapsed,
        "timestamp": datetime.now().isoformat()
    })

    return {
        **state,
        "sub_questions": sub_questions,
        "retrieved_chunks": {},
        "agent_trace": trace
    }
