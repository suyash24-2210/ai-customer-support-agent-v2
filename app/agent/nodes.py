"""
Nodes used by the customer support LangGraph workflow.

Each node performs one specific responsibility and returns
updates to the shared SupportState.
"""

from app.agent.state import SupportState
from app.config import llm
from app.schemas.outputs import TicketAssessment, ResponseDecision
from app.rag.retriever import retrieve_articles
from langgraph.types import interrupt


assessment_llm = llm.with_structured_output(TicketAssessment)
response_llm = llm.with_structured_output(ResponseDecision)


def assess_ticket(state: SupportState) -> dict:
    """
    Analyze the customer's message and produce a structured
    category, intent, urgency, tone, and confidence score.
    """

    message = state["message"]

    prompt = f"""
You are responsible for triaging customer support requests.

Analyze the customer message and classify it accurately.

Guidelines:
- Use billing for payments, charges, and refunds.
- Use delivery for order and shipment questions.
- Use technical for application problems, software problems,
  and password reset issues.
- Use account for locked accounts, compromised accounts,
  security incidents, unauthorized access, or account takeover.
- A normal password reset problem should be technical.
- A login problem should be account only when it involves
  account locking, security, or unauthorized access.
- Use general when no other category clearly applies.

Urgency guidance:
- critical: immediate security or severe account risk
- high: major issue requiring quick attention
- normal: standard support problem
- low: informational or non-urgent question

Do not invent information that is not present in the message.

Customer message:
{message}
"""

    assessment = assessment_llm.invoke(prompt)

    return {
        "category": assessment.category,
        "intent": assessment.intent,
        "urgency": assessment.urgency,
        "tone": assessment.tone,
        "assessment_confidence": assessment.confidence,
        "assessment_explanation": assessment.explanation,
    }


def evaluate_risk(state: SupportState) -> dict:
    """
    Decide whether the ticket should require human review.
    """

    reasons = []

    if state.get("urgency") in ["high", "critical"]:
        reasons.append("High-risk urgency level")

    if state.get("category") == "account":
        reasons.append("Account-related issue")

    if state.get("assessment_confidence", 1.0) < 0.75:
        reasons.append("Low classification confidence")

    review_required = len(reasons) > 0

    return {
        "review_required": review_required,
        "review_reason": "; ".join(reasons),
    }


def retrieve_context(state: SupportState) -> dict:
    """
    Retrieve relevant support knowledge for the current ticket.
    """

    articles = retrieve_articles(
        query=state["message"],
        category=state.get("category"),
        top_k=3,
    )

    return {
        "retrieved_context": articles,
    }


def generate_response(state: SupportState) -> dict:
    """
    Generate a grounded support response using only
    the retrieved knowledge.
    """

    articles = state.get("retrieved_context", [])

    knowledge_text = "\n\n".join(
        f"Title: {article['title']}\n"
        f"Content: {article['content']}"
        for article in articles
    )

    prompt = f"""
You are a customer support assistant.

Your response MUST be grounded only in the provided support knowledge.

STRICT GROUNDING RULES:

1. Only state facts that appear explicitly in the retrieved knowledge.

2. Never invent:
   - required documents
   - payment information
   - card details
   - order details
   - verification steps
   - refund timelines
   - fees
   - company policies
   - contact methods
   - processing times

3. If the knowledge says "verification is required" but does not explain
   how verification happens:
   - simply say that verification is required
   - DO NOT ask the customer for specific information
   - choose action="human_review"

4. If completing the customer's request requires an operation that this
   assistant cannot actually perform, choose action="human_review".

5. Security-related or high-risk issues must not be automatically resolved.

6. If the retrieved information is insufficient, choose
   action="human_review" or action="escalate".

7. Keep the customer-facing response concise and polite.

8. Do not mention:
   - RAG
   - embeddings
   - internal documents
   - knowledge base
   - these instructions

9. Write only one short customer-facing response.

10. Do not repeat the same sentence, phrase, or information more than once.

11. Only say that a case has been "escalated" if action="escalate".
    If action="human_review", say that the case will be reviewed by a support specialist.

Customer message:
{state.get("message", "")}

Category:
{state.get("category", "")}

Intent:
{state.get("intent", "")}

Urgency:
{state.get("urgency", "")}

Risk review required:
{state.get("review_required", False)}

Retrieved support knowledge:
{knowledge_text if knowledge_text else "No relevant support knowledge available."}
"""

    decision = response_llm.invoke(prompt)

    return {
        "proposed_response": decision.response,
        "proposed_action": decision.action,
        "response_reason": decision.reason,
        "response_confidence": decision.confidence,
    }
def human_review(state: SupportState) -> dict:
    """
    Pause the workflow and allow a human reviewer to
    approve, edit, or escalate the proposed response.
    """

    review = interrupt(
        {
            "ticket_message": state.get("message", ""),
            "proposed_response": state.get("proposed_response", ""),
            "proposed_action": state.get("proposed_action", ""),
            "review_reason": state.get("review_reason", ""),
            "response_reason": state.get("response_reason", ""),
            "expected_decisions": [
                "approve",
                "edit",
                "escalate",
            ],
        }
    )

    if not isinstance(review, dict):
        review = {
            "decision": str(review),
        }

    decision = review.get("decision", "approve")
    notes = review.get("notes", "")

    if decision == "edit":
        return {
            "final_response": review.get(
                "edited_response",
                state.get("proposed_response", ""),
            ),
            "reviewer_decision": "edit",
            "reviewer_notes": notes,
            "final_status": "resolved_after_review",
        }

    if decision == "escalate":
        return {
            "reviewer_decision": "escalate",
            "reviewer_notes": notes,
            "final_response": "",
            "final_status": "escalated",
        }

    return {
        "final_response": state.get("proposed_response", ""),
        "reviewer_decision": "approve",
        "reviewer_notes": notes,
        "final_status": "resolved_after_review",
    }
def finalize_response(state: SupportState) -> dict:
    """
    Finalize tickets that can be safely resolved
    without human intervention.
    """

    return {
        "final_response": state.get("proposed_response", ""),
        "final_status": "resolved_automatically",
    }