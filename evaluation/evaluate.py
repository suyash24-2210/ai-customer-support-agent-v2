"""
Lightweight evaluation for the AI Customer Support Agent.

Measures:
- category accuracy
- intent accuracy
- top-1 retrieval accuracy
- final human-review routing accuracy
"""

import json
from pathlib import Path

from app.agent.nodes import (
    assess_ticket,
    evaluate_risk,
    retrieve_context,
    generate_response,
)
from app.agent.workflow import route_after_response
from app.rag.retriever import retrieve_articles


TEST_FILE = Path(__file__).parent / "test_cases.json"


def load_test_cases():
    with open(TEST_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def run_evaluation():
    test_cases = load_test_cases()

    category_correct = 0
    intent_correct = 0
    retrieval_correct = 0
    review_correct = 0

    retrieval_total = 0

    print("\nAI Customer Support Agent Evaluation")
    print("=" * 45)

    for index, case in enumerate(test_cases, start=1):
        state = {
            "message": case["message"]
        }

        # Step 1: Classification
        assessment = assess_ticket(state)
        state.update(assessment)

        # Step 2: Initial risk check
        risk = evaluate_risk(state)
        state.update(risk)

        # Step 3: RAG retrieval
        retrieval_state = retrieve_context(state)
        state.update(retrieval_state)

        # Step 4: Generate response decision
        response_state = generate_response(state)
        state.update(response_state)

        # Evaluate top-1 retrieval separately
        retrieved = retrieve_articles(
            query=case["message"],
            category=state.get("category"),
            top_k=1,
        )

        predicted_article = (
            retrieved[0]["id"]
            if retrieved
            else None
        )

        expected_article = case.get("expected_article")

        category_match = (
            state.get("category")
            == case["expected_category"]
        )

        intent_match = (
            state.get("intent")
            == case["expected_intent"]
        )

        # Evaluate the ACTUAL final workflow route
        final_route = route_after_response(state)

        predicted_human_review = (
            final_route == "human_review"
        )

        review_match = (
            predicted_human_review
            == case["expected_human_review"]
        )

        if category_match:
            category_correct += 1

        if intent_match:
            intent_correct += 1

        if review_match:
            review_correct += 1

        retrieval_match = False

        if expected_article:
            retrieval_total += 1

            retrieval_match = (
                predicted_article
                == expected_article
            )

            if retrieval_match:
                retrieval_correct += 1

        print(f"\nTest {index}")
        print(f"Message: {case['message']}")

        print(
            "Category:",
            state.get("category"),
            "✓" if category_match else "✗",
        )

        print(
            "Intent:",
            state.get("intent"),
            "✓" if intent_match else "✗",
        )

        print(
            "Top article:",
            predicted_article,
            "✓" if retrieval_match else "✗",
        )

        print(
            "Human review:",
            predicted_human_review,
            "✓" if review_match else "✗",
        )

    total = len(test_cases)

    category_accuracy = (
        category_correct / total * 100
    )

    intent_accuracy = (
        intent_correct / total * 100
    )

    retrieval_accuracy = (
        retrieval_correct / retrieval_total * 100
        if retrieval_total
        else 0
    )

    review_accuracy = (
        review_correct / total * 100
    )

    print("\n" + "=" * 45)
    print("FINAL RESULTS")
    print("=" * 45)

    print(
        f"Category Accuracy     : "
        f"{category_correct}/{total} "
        f"({category_accuracy:.1f}%)"
    )

    print(
        f"Intent Accuracy       : "
        f"{intent_correct}/{total} "
        f"({intent_accuracy:.1f}%)"
    )

    print(
        f"Retrieval Accuracy    : "
        f"{retrieval_correct}/{retrieval_total} "
        f"({retrieval_accuracy:.1f}%)"
    )

    print(
        f"Human Review Accuracy : "
        f"{review_correct}/{total} "
        f"({review_accuracy:.1f}%)"
    )


if __name__ == "__main__":
    run_evaluation()