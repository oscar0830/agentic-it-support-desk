from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timezone
import os

from rag.supabase_client import supabase
from agents.orchestrator import orchestrator

app = FastAPI(title="IT Support Desk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TicketRequest(BaseModel):
    issue: str


def create_ticket(issue: str) -> str:
    ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    now = datetime.now(timezone.utc).isoformat()

    supabase.table("tickets").insert({
        "ticket_id": ticket_id,
        "user_issue": issue,
        "employee_id": "unknown",
        "status": "open",
        "resolved": False,
        "created_at": now,
        "updated_at": now,
    }).execute()

    return ticket_id


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ticket")
def submit_ticket(request: TicketRequest):
    if not request.issue.strip():
        raise HTTPException(status_code=400, detail="Issue description is required")

    ticket_id = create_ticket(request.issue)

    result = orchestrator(request.issue)

    if isinstance(result, dict):
        result["ticket_id"] = ticket_id
        return result

    return {
        "ticket_id": ticket_id,
        "message": str(result),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)