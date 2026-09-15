"""
Structured outputs returned by the language model.

These schemas make the LLM return predictable data instead
of unstructured text.
"""

from typing import Literal

from pydantic import BaseModel, Field


class TicketAssessment(BaseModel):
    """Structured analysis of an incoming support request."""

    category: Literal[
        "billing",
        "technical",
        "delivery",
        "account",
        "general",
    ] = Field(
        description="Primary support category"
    )

    intent: Literal[
        "refund",
        "payment_problem",
        "software_issue",
        "password_help",
        "delivery_status",
        "account_access",
        "complaint",
        "information_request",
        "unknown",
    ] = Field(
        description="Main goal of the customer"
    )

    urgency: Literal[
        "low",
        "normal",
        "high",
        "critical",
    ] = Field(
        description="How urgently the issue should be handled"
    )

    tone: Literal[
        "positive",
        "neutral",
        "negative",
        "frustrated",
    ] = Field(
        description="Customer's emotional tone"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the assessment"
    )

    explanation: str = Field(
        description="Short reason for the classification"
    )


class ResponseDecision(BaseModel):
    """Structured decision produced when generating a response."""

    response: str = Field(
        description="Suggested response to the customer"
    )

    action: Literal[
        "resolve",
        "human_review",
        "escalate",
    ] = Field(
        description="Recommended next action"
    )

    reason: str = Field(
        description="Reason for the selected action"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the proposed response"
    )