import re
from typing import List, Dict, Any

def calculate_topic_recall(retrieved_chunks: dict, expected_topics: list[str]) -> float:
    """Calculates the proportion of expected topics covered in the retrieved text chunks."""
    if not expected_topics:
        return 1.0

    all_retrieved_text = ""
    for chunks in retrieved_chunks.values():
        for chunk in chunks:
            all_retrieved_text += " " + chunk.get("content", "").lower() + " " + chunk.get("title", "").lower()

    found_count = 0
    for topic in expected_topics:
        topic_lower = topic.lower()
        if topic_lower in all_retrieved_text:
            found_count += 1
        else:
            words = [w for w in topic_lower.split() if len(w) > 3]
            if words and any(w in all_retrieved_text for w in words):
                found_count += 1

    return round(found_count / len(expected_topics), 3)

def calculate_answer_completeness(final_answer: str, sub_questions: list[str]) -> float:
    """Estimates how well the final answer addresses the generated sub-questions."""
    if not sub_questions or not final_answer:
        return 0.0

    answer_lower = final_answer.lower()
    covered_count = 0

    for sq in sub_questions:
        keywords = [w.lower() for w in re.findall(r'\b\w{4,}\b', sq) if w.lower() not in {"what", "how", "does", "which", "according", "jrc", "data", "show"}]
        if not keywords:
            covered_count += 1
            continue

        match_score = sum(1 for kw in keywords if kw in answer_lower)
        if match_score / len(keywords) >= 0.25:
            covered_count += 1

    return round(covered_count / len(sub_questions), 3)

def calculate_citation_correctness(sources_used: list[str], sources_metadata: list[dict]) -> float:
    """Verifies that all cited sources have valid metadata mappings."""
    if not sources_used:
        return 1.0
    valid_count = sum(1 for s in sources_used if any(meta.get("title") == s for meta in sources_metadata))
    return round(valid_count / len(sources_used), 3)

def summarize_evaluation_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Computes overall and group-specific benchmark metrics for Group A, Group B, and Group C."""
    total_evals = len(results)
    if total_evals == 0:
        return {}

    groups = {}
    for r in results:
        grp = r.get("group", "General")
        if grp not in groups:
            groups[grp] = []
        groups[grp].append(r)

    group_summaries = {}
    for grp_name, grp_results in groups.items():
        count = len(grp_results)
        avg_rec = round(sum(r["recall_at_k"] for r in grp_results) / count, 3)
        avg_comp = round(sum(r["completeness_score"] for r in grp_results) / count, 3)
        avg_lat = round(sum(r["total_latency_sec"] for r in grp_results) / count, 2)
        avg_iters = round(sum(r["iterations"] for r in grp_results) / count, 2)
        retry_triggered = sum(1 for r in grp_results if r["retry_count"] > 0)
        retry_passed = sum(1 for r in grp_results if r["retry_count"] > 0 and r["validation_passed"])
        pass_rate = round(sum(1 for r in grp_results if r["validation_passed"]) / count, 3)

        group_summaries[grp_name] = {
            "test_cases": count,
            "retrieval_recall_at_5": avg_rec,
            "answer_completeness": avg_comp,
            "validation_pass_rate": pass_rate,
            "retry_triggered_count": retry_triggered,
            "retry_recovery_success_rate": round(retry_passed / retry_triggered, 3) if retry_triggered > 0 else 1.0,
            "avg_iterations": avg_iters,
            "avg_latency_sec": avg_lat
        }

    overall_recall = round(sum(r["recall_at_k"] for r in results) / total_evals, 3)
    overall_completeness = round(sum(r["completeness_score"] for r in results) / total_evals, 3)
    overall_citation = round(sum(r["citation_correctness"] for r in results) / total_evals, 3)
    overall_lat = round(sum(r["total_latency_sec"] for r in results) / total_evals, 2)
    overall_iters = round(sum(r["iterations"] for r in results) / total_evals, 2)
    total_retries = sum(1 for r in results if r["retry_count"] > 0)
    total_retry_passed = sum(1 for r in results if r["retry_count"] > 0 and r["validation_passed"])

    return {
        "overall_evaluation_count": total_evals,
        "overall_metrics": {
            "retrieval_recall_at_5": overall_recall,
            "answer_completeness": overall_completeness,
            "citation_correctness": overall_citation,
            "validator_pass_rate": round(sum(1 for r in results if r["validation_passed"]) / total_evals, 3),
            "total_retries_triggered": total_retries,
            "validator_retry_success_rate": round(total_retry_passed / total_retries, 3) if total_retries > 0 else 1.0,
            "avg_iterations": overall_iters,
            "avg_latency_sec": overall_lat
        },
        "group_metrics": group_summaries
    }
