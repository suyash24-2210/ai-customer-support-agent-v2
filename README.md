
# AI Customer Support Agent

An intelligent customer-support workflow built with **LangGraph, Groq, Semantic RAG, FastAPI, Sentence Transformers, and Human-in-the-Loop review**.

The system automatically understands incoming customer tickets, retrieves relevant support knowledge, generates grounded responses, and routes risky or uncertain cases to a human reviewer.

---

## Overview

Traditional support bots often generate responses without proper grounding or escalation logic.

This project demonstrates a more reliable agentic workflow that combines:

- LLM-based ticket understanding
- Structured outputs with Pydantic
- Semantic knowledge retrieval
- Grounded response generation
- Risk-based routing
- Human approval, editing, and escalation
- Persistent LangGraph checkpoints
- REST API access through FastAPI
- Automated evaluation

The goal is to build a support agent that does not simply answer questions, but also knows **when not to answer automatically**.

---

## Architecture

```text
                    Customer Request
                           |
                           v
                   Ticket Assessment
                           |
                           v
                    Risk Evaluation
                           |
                           v
                    Semantic RAG
                           |
                           v
              Grounded Response Generation
                           |
                           v
                    Routing Decision
                     /             \
                    /               \
                   v                 v
            Auto Resolution     Human Review
                                   |
                         -----------------------
                         |          |          |
                      Approve      Edit     Escalate
                         |          |          |
                         -------- Final --------
```

---

## Core Features

### Intelligent Ticket Classification

The LLM analyzes each support request and returns structured information including:

- Category
- Intent
- Urgency
- Customer tone
- Confidence score
- Classification explanation

Pydantic models are used to enforce predictable structured outputs.

---

### Semantic RAG

The project includes a lightweight semantic retrieval system built using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Support articles are converted into embeddings and compared with the customer's message using cosine similarity.

The retriever also applies a small category-based ranking bonus to improve relevance.

Example:

```text
Customer:
"I was charged twice for the same purchase"

Top retrieved article:
Duplicate payment policy
```

---

### Grounded Response Generation

The LLM is instructed to answer only using retrieved support knowledge.

The system explicitly prevents unsupported claims such as:

- Invented refund timelines
- Fake verification procedures
- Unsupported payment requirements
- Made-up fees
- Fabricated company policies
- Unverified processing times

If the available information is insufficient, the model routes the ticket for human review instead of guessing.

---

### Human-in-the-Loop

LangGraph interrupts are used to pause risky workflows before sending a final response.

A human reviewer can:

```text
approve
edit
escalate
```

The workflow then resumes from the exact saved state.

Example:

```text
Customer:
"My account was hacked and I cannot log in."

Agent:
Security risk detected.

Action:
Human review required.
```

---

### Persistent Workflow State

LangGraph checkpoints are stored using SQLite.

This allows interrupted workflows to survive server restarts.

```text
Customer request
      ↓
Workflow pauses
      ↓
Checkpoint saved in SQLite
      ↓
Human reviews later
      ↓
Workflow resumes using thread_id
```

---

### FastAPI REST API

The agent can be used through a REST API.

Interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

Main endpoints:

```text
GET  /
POST /support
POST /review
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| LangGraph | Agent workflow orchestration |
| Groq | LLM inference |
| Pydantic | Structured LLM outputs |
| Sentence Transformers | Text embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| FastAPI | REST API |
| SQLite | Persistent workflow checkpoints |
| LangGraph Checkpoint SQLite | Workflow persistence |

---

## Project Structure

```text
ai-customer-support-agent-v2/
│
├── app/
│   ├── config.py
│   │
│   ├── agent/
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── workflow.py
│   │
│   ├── rag/
│   │   ├── knowledge.py
│   │   └── retriever.py
│   │
│   ├── schemas/
│   │   └── outputs.py
│   │
│   └── api/
│       ├── routes.py
│       └── server.py
│
├── evaluation/
│   ├── evaluate.py
│   └── test_cases.json
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## Workflow

The support workflow follows these stages:

```text
1. Customer submits ticket
        ↓
2. LLM analyzes ticket
        ↓
3. Risk level is evaluated
        ↓
4. Relevant knowledge is retrieved
        ↓
5. Grounded response is generated
        ↓
6. Routing decision is made
        ↓
7. Auto resolve OR Human review
        ↓
8. Final response / escalation
```

A case may require human review when:

- The issue has high or critical urgency
- The account may be compromised
- Classification confidence is low
- Retrieved knowledge is insufficient
- The response requires manual verification
- The LLM recommends escalation

---

## Installation

Clone the repository:

```bash
git clone https://github.com/suyash24-2210/ai-customer-support-agent-v2.git
cd ai-customer-support-agent-v2
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your-groq-api-key
```

An example file is included:

```text
.env.example
```

Never commit your real API key.

---

## Run the CLI

Start the command-line application:

```bash
python main.py
```

Example:

```text
AI Customer Support Agent
------------------------------

Customer ID: C001
Customer message: My account was hacked and I cannot log in

--- HUMAN REVIEW REQUIRED ---

Reason:
High-risk urgency level; Account-related issue

Proposed response:
I'm sorry to hear about this. Because this involves a possible
security issue, your case will be reviewed by a support specialist.

Decision:
approve
```

---

## Run the FastAPI Server

Start the API:

```bash
python -m uvicorn app.api.server:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## API Usage

### Create a Support Ticket

Endpoint:

```text
POST /support
```

Request:

```json
{
  "customer_id": "C001",
  "message": "My account was hacked and I cannot log in"
}
```

Example response:

```json
{
  "ticket_id": "T-12904e65",
  "thread_id": "C001-0759ef89",
  "status": "human_review_required",
  "review": {
    "ticket_message": "My account was hacked and I cannot log in",
    "proposed_action": "human_review",
    "review_reason": "High-risk urgency level; Account-related issue"
  }
}
```

---

### Resume a Human Review

Endpoint:

```text
POST /review
```

Approve:

```json
{
  "thread_id": "C001-0759ef89",
  "decision": "approve",
  "edited_response": "",
  "notes": ""
}
```

Edit:

```json
{
  "thread_id": "C001-0759ef89",
  "decision": "edit",
  "edited_response": "Your case has been reviewed and will be handled by our support team.",
  "notes": "Edited for clarity"
}
```

Escalate:

```json
{
  "thread_id": "C001-0759ef89",
  "decision": "escalate",
  "edited_response": "",
  "notes": "Possible account takeover."
}
```

---

## Evaluation

The project includes a lightweight evaluation pipeline covering:

```text
Ticket category classification
Intent classification
Top-1 semantic retrieval
Human-review routing
```

Run:

```bash
python -m evaluation.evaluate
```

Current results on the included 8-case development benchmark:

```text
Category Accuracy     : 100.0%
Intent Accuracy       : 100.0%
Retrieval Accuracy    : 87.5%
Human Review Accuracy : 75.0%
```

These results come from a small development test set and are intended to validate the workflow rather than represent production-level benchmark performance.

---

## Example Use Cases

The current knowledge base supports scenarios such as:

```text
Duplicate payments
Failed payments
Application crashes
Password reset problems
Order tracking
Locked accounts
Suspicious account activity
General support questions
```

---

## Security

Sensitive local files are excluded using `.gitignore`.

```text
.env
.venv/
*.db
*.db-shm
*.db-wal
__pycache__/
```

API keys and workflow checkpoint databases should never be committed to public repositories.

---

## Current Limitations

This project is designed as an AI engineering portfolio project rather than a production customer-support platform.

Current limitations include:

- Small local knowledge base
- Small evaluation dataset
- No authentication system
- No production database
- No external CRM integration
- No production deployment
- No conversation history across multiple customer turns

---

## Future Improvements

Potential extensions include:

```text
Vector database integration
Larger support knowledge base
Conversation memory
Automated regression testing
CRM integrations
Authentication and authorization
Observability and tracing
Production deployment
Expanded evaluation datasets
```

---

## What This Project Demonstrates

This project demonstrates practical experience with:

```text
Agentic AI workflows
LangGraph state machines
Human-in-the-loop systems
Retrieval-Augmented Generation
Semantic search
Embedding models
Structured LLM outputs
Prompt grounding
LLM hallucination control
FastAPI development
Persistent agent state
AI system evaluation
```

---

## License

This project is licensed under the MIT License.

Copyright © 2026 Suyash Billaiya