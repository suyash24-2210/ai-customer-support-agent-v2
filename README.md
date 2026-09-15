\# AI Customer Support Agent



An agentic customer-support system built with LangGraph, Groq, semantic RAG, FastAPI, and human-in-the-loop review.



The system classifies support tickets, retrieves relevant support knowledge using semantic search, generates grounded responses, and routes risky or uncertain cases to a human reviewer.



\---



\## Features



\- LLM-based ticket classification

\- Structured outputs with Pydantic

\- Semantic RAG using Sentence Transformers

\- Human-in-the-loop approval, editing, and escalation

\- LangGraph workflow orchestration

\- Persistent workflow checkpoints using SQLite

\- FastAPI REST API

\- Hallucination-control prompting

\- Lightweight evaluation pipeline



\---



\## Architecture



```text

Customer Request

&#x20;      |

&#x20;      v

Ticket Assessment

&#x20;      |

&#x20;      v

Risk Evaluation

&#x20;      |

&#x20;      v

Semantic Retrieval

&#x20;      |

&#x20;      v

Grounded Response Generation

&#x20;      |

&#x20;      v

Routing Decision

&#x20;    /       \\

&#x20;   /         \\

Auto Resolve   Human Review

&#x20;                 |

&#x20;         Approve / Edit / Escalate

