"""
Shared state for the AI customer support workflow.
"""

from typing import TypedDict


class SupportState(TypedDict, total=False):
    """
    Data that moves through the LangGraph workflow.

    Each node reads the fields it needs and returns
    only the fields it wants to update.
    """

    # Input
    ticket_id: str
    customer_id: str
    message: str

    # LLM assessment
    category: str
    intent: str
    urgency: str
    tone: str
    assessment_confidence: float
    assessment_explanation: str

    # Risk / routing
    review_required: bool
    review_reason: str
    reviewer_decision: str
    reviewer_notes: str

    # RAG
    retrieved_context: list[dict]

    # Response generation
    proposed_response: str
    proposed_action: str
    response_reason: str
    response_confidence: float

    # Final outcome
    final_response: str
    final_status: str