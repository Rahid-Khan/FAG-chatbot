"""Simple evaluation harness for measuring chatbot behavior on a labeled set."""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.chatbot import Chatbot


def main() -> None:
    eval_path = PROJECT_ROOT / "data" / "eval_set.json"
    cases = json.loads(eval_path.read_text(encoding="utf-8"))

    chatbot = Chatbot()
    exact_expectation_hits = 0
    match_expectation_hits = 0

    for case in cases:
        result = chatbot.get_response(case["query"])
        response_text = result["response"]
        contains_expected = case["expected_answer_contains"].lower() in response_text.lower()
        correct_match_state = result["matched"] == case["expected_match"]

        exact_expectation_hits += int(contains_expected)
        match_expectation_hits += int(correct_match_state)

        print(
            f"Query: {case['query']}\n"
            f"  matched={result['matched']} confidence={result['confidence']} score={result['score']:.4f}\n"
            f"  response={response_text}\n"
            f"  expected_contains_ok={contains_expected} expected_match_ok={correct_match_state}\n"
        )

    total_cases = len(cases)
    top1_accuracy = exact_expectation_hits / total_cases if total_cases else 0.0
    match_accuracy = match_expectation_hits / total_cases if total_cases else 0.0
    fallback_rate = sum(1 for case in cases if not chatbot.get_response(case["query"])["matched"]) / total_cases

    print("Summary")
    print(f"  Cases: {total_cases}")
    print(f"  Response expectation accuracy: {top1_accuracy:.2%}")
    print(f"  Match-state accuracy: {match_accuracy:.2%}")
    print(f"  Fallback rate: {fallback_rate:.2%}")


if __name__ == "__main__":
    main()
