"""
LangGraph workflow for the AI customer support agent.
"""

import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, END, StateGraph

from app.agent.state import SupportState
from app.agent.nodes import (
    assess_ticket,
    evaluate_risk,
    retrieve_context,
    generate_response,
    human_review,
    finalize_response,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "support_checkpoints.db"


def route_after_response(state: SupportState) -> str:
    """
    Decide whether the generated response can be automatically
    resolved or must be reviewed by a human.
    """

    if state.get("review_required", False):
        return "human_review"

    if state.get("proposed_action") in [
        "human_review",
        "escalate",
    ]:
        return "human_review"

    if state.get("response_confidence", 0.0) < 0.80:
        return "human_review"

    return "finalize"


def build_workflow():
    """
    Build and compile the customer support workflow
    with persistent SQLite checkpoints.
    """

    graph = StateGraph(SupportState)

    graph.add_node("assess_ticket", assess_ticket)
    graph.add_node("evaluate_risk", evaluate_risk)
    graph.add_node("retrieve_context", retrieve_context)
    graph.add_node("generate_response", generate_response)
    graph.add_node("human_review", human_review)
    graph.add_node("finalize", finalize_response)

    graph.add_edge(
        START,
        "assess_ticket",
    )

    graph.add_edge(
        "assess_ticket",
        "evaluate_risk",
    )

    graph.add_edge(
        "evaluate_risk",
        "retrieve_context",
    )

    graph.add_edge(
        "retrieve_context",
        "generate_response",
    )

    graph.add_conditional_edges(
        "generate_response",
        route_after_response,
        {
            "human_review": "human_review",
            "finalize": "finalize",
        },
    )

    graph.add_edge(
        "human_review",
        END,
    )

    graph.add_edge(
        "finalize",
        END,
    )

    connection = sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False,
    )

    checkpointer = SqliteSaver(connection)
    checkpointer.setup()

    return graph.compile(
        checkpointer=checkpointer
    )