"""
FastAPI application entry point.
"""

from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="AI Customer Support Agent",
    description=(
        "LangGraph-powered customer support system "
        "with semantic RAG and human-in-the-loop review."
    ),
    version="2.0.0",
)


app.include_router(router)