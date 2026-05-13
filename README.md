# Agentic IT Support Desk

An AI-powered multi-agent IT support system built for SJSU BUS4-118S.

This project demonstrates a custom agent orchestration architecture inspired by LangGraph concepts, combining multiple specialized agents, FastAPI backend services, Retrieval-Augmented Generation (RAG), Supabase persistence, and a React frontend dashboard.

---

# Project Overview

The Agentic IT Support Desk simulates an enterprise IT support workflow where tickets are:

1. Submitted through a frontend UI
2. Classified by AI agents
3. Routed dynamically by an orchestrator
4. Resolved through knowledge retrieval or workflow automation
5. Escalated to human IT support when necessary
6. Persisted into Supabase for tracking and auditing

The system emphasizes:

* Multi-agent orchestration
* Intelligent routing
* Retrieval-Augmented Generation (RAG)
* Safe fallback escalation
* Ticket persistence
* Frontend + backend integration

---

# Architecture

## Agent Flow

User Request
→ Intake Agent
→ Orchestrator Router
→ Knowledge Agent OR Workflow Agent OR Escalation Agent
→ Resolution / Escalation
→ Supabase Persistence

---

# Core Components

## Intake Agent

Responsible for:

* Reading incoming requests
* Classifying ticket intent
* Assigning category
* Assigning priority level (P1–P4)

Examples:

* Password reset
* VPN issue
* WiFi issue
* Account lockout

---

## Orchestrator

Acts as the central routing system.

Responsibilities:

* Maintains shared ticket state
* Decides which agent should execute next
* Handles fallback logic
* Prevents workflow crashes
* Escalates unresolved tickets safely

Architecture inspiration:

* LangGraph-style state routing
* Multi-agent orchestration patterns

---

## Knowledge Agent

Uses Retrieval-Augmented Generation (RAG).

Responsibilities:

* Searches knowledge base chunks stored in Supabase
* Retrieves semantically relevant support documents
* Returns contextual troubleshooting steps

Example use cases:

* VPN troubleshooting
* WiFi troubleshooting
* Password reset instructions

---

## Workflow Agent

Responsible for operational actions.

Responsibilities:

* Validates ticket schema
* Simulates workflow execution
* Creates audit-ready ticket data
* Stores ticket information into Supabase

---

## Escalation Agent

Fallback safety layer.

Responsibilities:

* Detect unresolved issues
* Escalate tickets to human IT support
* Generate escalation summaries
* Prevent hard workflow failures

---

# Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS
* Vercel Deployment

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

## AI / Agent System

* Custom multi-agent orchestration
* LangGraph-inspired architecture
* RAG pipeline
* Semantic retrieval

## Database

* Supabase
* PostgreSQL
* Vector-enabled knowledge storage

---

# Features

* Multi-agent ticket routing
* Intent classification
* Dynamic orchestration
* Retrieval-Augmented Generation (RAG)
* Supabase ticket persistence
* Escalation handling
* Frontend dashboard UI
* Live ticket resolution display
* Modular agent architecture
* Safe fallback routing

---

# Frontend Demo

Features include:

* Dashboard view
* Ticket submission form
* Ticket history
* Resolution display
* Escalation display
* Agent processing pipeline visualization

---

# Supabase Integration

Supabase is used for:

* Ticket persistence
* Knowledge chunk storage
* Audit trail simulation
* Workflow validation support

Tables include:

* tickets
* knowledge_chunks
* agent_metrics

---

# Local Setup

## Clone Repository

```bash
git clone https://github.com/oscar0830/agentic-it-support-desk.git
cd agentic-it-support-desk
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

Frontend dependencies:

```bash
cd frontend
npm install
```

---

# Environment Variables

Create a `.env` file:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_api_key
```

---

# Running the Backend

From the project root:

```bash
python3 app.py
```

Backend runs at:

```text
http://localhost:8000
```

Health endpoint:

```text
http://localhost:8000/health
```

---

# Running the Frontend

Inside `/frontend`:

```bash
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

# Example Ticket Flow

Example input:

```text
I forgot my password and cannot log in.
```

Flow:

1. Intake Agent classifies request
2. Orchestrator routes ticket
3. Knowledge Agent retrieves troubleshooting guidance
4. Workflow Agent validates and stores ticket
5. Escalation Agent activates if unresolved
6. Ticket persists into Supabase

---

# Project Goals

This project was designed to explore:

* Enterprise AI workflows
* Agent orchestration
* RAG implementation
* Intelligent ticket routing
* AI-assisted IT support systems
* Safe fallback architectures
* Full-stack AI application integration

---

# Future Improvements

Potential next steps:

* Real-time streaming agent responses
* LangGraph implementation
* Authentication layer
* Admin analytics dashboard
* Human-in-the-loop escalation workflows
* Advanced vector search optimization
* Slack / Teams integration
* Ticket assignment automation
* Memory-enabled agent state

---

# Team

SJSU BUS4-118S – Agentic AI for Business

Agentic IT Support Desk Project Team

Contributors:

* Oscar Aparicio
* Team 3

---

# Repository

GitHub Repository:

[https://github.com/oscar0830/agentic-it-support-desk](https://github.com/oscar0830/agentic-it-support-desk)

---

# Live Demo

Frontend Deployment:

[https://agentic-it-support-desk.vercel.app](https://agentic-it-support-desk.vercel.app)

---

# License

Educational / Academic Project

Built for academic demonstration purposes at San José State University.
