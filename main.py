"""
Command-line interface for the AI Customer Support Agent.
"""

import uuid

from langgraph.types import Command

from app.agent.workflow import build_workflow


def main():
    graph = build_workflow()

    print("\nAI Customer Support Agent")
    print("-" * 30)

    customer_id = input("Customer ID: ").strip()

    while not customer_id:
        print("Customer ID cannot be empty.")
        customer_id = input("Customer ID: ").strip()

    message = input("Customer message: ").strip()

    while not message:
        print("Customer message cannot be empty.")
        message = input("Customer message: ").strip()

    ticket_id = f"T-{uuid.uuid4().hex[:8]}"
    thread_id = f"{customer_id}-{uuid.uuid4().hex[:8]}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "message": message,
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    interrupts = result.get("__interrupt__")

    if interrupts:
        review_data = interrupts[0].value

        print("\n--- HUMAN REVIEW REQUIRED ---")
        print(
            "Reason:",
            review_data.get("review_reason")
        )

        print("\nProposed response:")
        print(
            review_data.get("proposed_response")
        )

        print("\nChoices:")
        print("1. approve")
        print("2. edit")
        print("3. escalate")

        decision = input(
            "\nDecision: "
        ).strip().lower()

        human_reply = {
            "decision": decision,
        }

        if decision == "edit":
            edited_response = input(
                "Enter edited response: "
            ).strip()

            human_reply["edited_response"] = edited_response

        notes = input(
            "Reviewer notes (optional): "
        ).strip()

        human_reply["notes"] = notes

        result = graph.invoke(
            Command(resume=human_reply),
            config=config,
        )

    print("\n--- FINAL RESULT ---")
    print(
        "Status:",
        result.get("final_status"),
    )

    if result.get("final_response"):
        print("\nResponse:")
        print(
            result.get("final_response")
        )


if __name__ == "__main__":
    main()