"""
FastAPI routes for the AI Customer Support Agent.
"""

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langgraph.types import Command

from app.agent.workflow import build_workflow


router = APIRouter()

graph = build_workflow()


class SupportRequest(BaseModel):
    customer_id: str
    message: str


class ReviewRequest(BaseModel):
    thread_id: str
    decision: str
    edited_response: str = ""
    notes: str = ""


@router.get("/")
def health_check():
    return {
        "message": "AI Customer Support Agent API is running"
    }


@router.post("/support")
def create_support_ticket(request: SupportRequest):
    if not request.customer_id.strip():
        raise HTTPException(
            status_code=400,
            detail="customer_id cannot be empty",
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="message cannot be empty",
        )

    ticket_id = f"T-{uuid.uuid4().hex[:8]}"
    thread_id = f"{request.customer_id}-{uuid.uuid4().hex[:8]}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "ticket_id": ticket_id,
        "customer_id": request.customer_id,
        "message": request.message,
    }

    result = graph.invoke(
        initial_state,
        config=config,
    )

    interrupts = result.get("__interrupt__")

    if interrupts:
        review_data = interrupts[0].value

        return {
            "ticket_id": ticket_id,
            "thread_id": thread_id,
            "status": "human_review_required",
            "review": review_data,
        }

    return {
        "ticket_id": ticket_id,
        "thread_id": thread_id,
        "status": result.get("final_status"),
        "response": result.get("final_response"),
    }


@router.post("/review")
def review_support_ticket(request: ReviewRequest):
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    snapshot = graph.get_state(config)

    if not snapshot.values:
        raise HTTPException(
            status_code=404,
            detail="Thread not found",
        )

    if not snapshot.next:
        raise HTTPException(
            status_code=409,
            detail="Workflow has already completed",
        )

    if request.decision not in [
        "approve",
        "edit",
        "escalate",
    ]:
        raise HTTPException(
            status_code=400,
            detail="decision must be approve, edit, or escalate",
        )

    human_reply = {
        "decision": request.decision,
        "notes": request.notes,
    }

    if request.decision == "edit":
        if not request.edited_response.strip():
            raise HTTPException(
                status_code=400,
                detail="edited_response is required when decision is edit",
            )

        human_reply["edited_response"] = request.edited_response

    result = graph.invoke(
        Command(resume=human_reply),
        config=config,
    )

    interrupts = result.get("__interrupt__")

    if interrupts:
        return {
            "thread_id": request.thread_id,
            "status": "human_review_required",
            "review": interrupts[0].value,
        }

    return {
        "thread_id": request.thread_id,
        "status": result.get("final_status"),
        "response": result.get("final_response"),
    }