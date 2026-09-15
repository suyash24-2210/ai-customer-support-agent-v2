"""
Application configuration.

Loads environment variables and creates the shared Groq LLM client
used across the support agent.
"""

import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is missing. "
        "Add it to your .env file before running the application."
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=GROQ_API_KEY,
)