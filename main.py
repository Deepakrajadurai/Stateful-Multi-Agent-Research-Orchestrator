import sys
import config
from state import ResearchState

try:
    from graph.research_graph import research_graph
except ImportError:
    from research_graph import research_graph

DEMO_QUESTIONS = [
    "How does cold weather affect real-world energy consumption and range in battery electric vehicles according to JRC data?",
    "What does the JRC evidence show about the gap between WLTP laboratory ratings and real-world fuel consumption for plug-in hybrids?",
    "What are the key findings from JRC research on real-world CO2 emissions from passenger vehicles under real driving conditions?",
]

def run_query(question: str) -> dict:
    initial_state: ResearchState = {
        "question": question,
        "sub_questions": [],
        "retrieved_chunks": {},
        "draft_answer": "",
        "validation_passed": False,
        "gaps_identified": [],
        "retry_count": 0,
        "final_answer": "",
        "sources_used": [],
    }

    print("\n" + "="*60)
    print(f"QUESTION: {question}")
    print("="*60)

    result = research_graph.invoke(initial_state)

    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(result["final_answer"])
    print("\nSOURCES USED:")
    for s in result["sources_used"]:
        print(f"  - {s}")

    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = DEMO_QUESTIONS[0]
    run_query(question)
