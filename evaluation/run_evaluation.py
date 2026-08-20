import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from state import ResearchState

try:
    from graph.research_graph import research_graph
except ImportError:
    from research_graph import research_graph

from metrics import (
    calculate_topic_recall,
    calculate_answer_completeness,
    calculate_citation_correctness,
    summarize_evaluation_results
)

RESULTS_DIR = ROOT_DIR / "evaluation" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def run_evaluation_suite(limit: int = 30):
    questions_file = ROOT_DIR / "evaluation" / "questions.json"
    with open(questions_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    if limit and limit < len(test_cases):
        test_cases = test_cases[:limit]

    print(f"\n" + "="*70)
    print(f"RUNNING ADVERSARIAL BENCHMARK SUITE ({len(test_cases)} TEST CASES ACROSS GROUPS A, B, C)")
    print("="*70 + "\n")

    eval_results = []

    for idx, tc in enumerate(test_cases, 1):
        q_id = tc["id"]
        group = tc.get("group", "General")
        question = tc["question"]
        expected_topics = tc.get("expected_topics", [])

        print(f"[{idx}/{len(test_cases)}] Evaluating [{q_id} | {group}]")
        print(f"  Question: \"{question[:75]}...\"")

        start_t = time.time()

        initial_state: ResearchState = {
            "question": question,
            "metadata_filters": None,
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

        try:
            res = research_graph.invoke(initial_state)
            latency = round(time.time() - start_t, 2)

            recall = calculate_topic_recall(res["retrieved_chunks"], expected_topics)
            completeness = calculate_answer_completeness(res["final_answer"], res["sub_questions"])
            citation_correctness = calculate_citation_correctness(res["sources_used"], res["sources_metadata"])

            eval_entry = {
                "id": q_id,
                "group": group,
                "category": tc["category"],
                "question": question,
                "recall_at_k": recall,
                "completeness_score": completeness,
                "citation_correctness": citation_correctness,
                "validation_passed": res["validation_passed"],
                "retry_count": res["retry_count"],
                "iterations": 1 + res["retry_count"],
                "sources_cited": len(res["sources_used"]),
                "sub_questions_count": len(res["sub_questions"]),
                "total_latency_sec": latency,
                "agent_trace_steps": len(res["agent_trace"])
            }
            eval_results.append(eval_entry)

            print(f"  Result: Recall={recall:.2f} | Completeness={completeness:.2f} | RetryPasses={res['retry_count']} | Latency={latency}s")
            print("-" * 60)

        except Exception as e:
            print(f"  ERROR executing evaluation for {q_id}: {e}")

    summary = summarize_evaluation_results(eval_results)

    report_payload = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "detailed_results": eval_results
    }

    report_file = RESULTS_DIR / "eval_report.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2, ensure_ascii=False)

    print("\n" + "="*70)
    print("ADVERSARIAL BENCHMARK COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("Grouped Summary:")
    print(json.dumps(summary, indent=2))
    print(f"\nDetailed Evaluation Report saved to: {report_file}\n")

if __name__ == "__main__":
    limit_val = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    run_evaluation_suite(limit=limit_val)
