import config
from langgraph.graph import StateGraph, END
from state import ResearchState

try:
    from agents.planner import planner_node
    from agents.retriever import retriever_node
    from agents.synthesiser import synthesiser_node
    from agents.validator import validator_node
except ImportError:
    from planner import planner_node
    from retriever import retriever_node
    from synthesiser import synthesiser_node
    from validator import validator_node

def should_retry(state: ResearchState) -> str:
    """Conditional edge: retry retrieval or finish."""
    if state.get("validation_passed"):
        return "end"
    return "retriever"

def build_graph():
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("synthesiser", synthesiser_node)
    graph.add_node("validator", validator_node)

    # Define edges
    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_edge("retriever", "synthesiser")
    graph.add_edge("synthesiser", "validator")

    # Conditional edge from validator
    graph.add_conditional_edges(
        "validator",
        should_retry,
        {
            "retriever": "retriever",  # loop back
            "end": END                 # finish
        }
    )

    return graph.compile()

# Singleton — build once, reuse
research_graph = build_graph()
