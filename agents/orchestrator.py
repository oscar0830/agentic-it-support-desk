"""
IT Support Multi-Agent Orchestrator
Pure Python — no LangGraph, no LangChain.
Only dependency: OpenAI (pip install OpenAI)

Architecture:
  TicketState  – plain dataclass holding all shared state
  llm_router() – calls OpenAI to decide the next agent
  run_*()      – one wrapper per agent; mutates state in-place
  Orchestrator – the main loop that ties everything together
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from openai import OpenAI

# Real agent 
from agents.escalation_agent import escalation_agent
# ─────────────────────────────────────────────
# 1. STATE
#    A plain dataclass; every agent reads from
#    and writes back into this single object.
# ─────────────────────────────────────────────

@dataclass
class TicketState:
    # ── Initial inputs ────────────────────────
    ticket_text: str
    employee_id: str

    # ── Conversation log (role, content tuples) ──
    messages: list[dict] = field(default_factory=list)

    # ── Intake Agent outputs ──────────────────
    ticket_category: str = ""   # "password" | "network" | "software" | "hardware"
    priority: str = ""          # "P1" | "P2" | "P3" | "P4"
    intent: str = ""            # "password_reset" | "software_install" | "unknown" …

    # ── Knowledge Agent outputs ───────────────
    kb_results: list[str] = field(default_factory=list)
    kb_confidence: float = 0.0  # 0.0 – 1.0

    # ── Workflow Agent outputs ────────────────
    workflow_attempted: bool = False
    workflow_result: str = "not_attempted"  # "success"|"failed"|"not_attempted"|"awaiting_confirmation"

    # ── Escalation Agent outputs ──────────────
    escalation_summary: str = ""
    ticket_id: Optional[str] = None     # Supabase ticket ID

    # ── Router control ────────────────────────
    next_agent: str = ""
    user_confirmed: Optional[bool] = None   # None = not asked yet

    # ── Terminal flag ─────────────────────────
    resolved: bool = False

    def add_message(self, role: str, agent: str, content: str) -> None:
        self.messages.append({"role": role, "agent": agent, "content": content})

    def last_message(self) -> str:
        return self.messages[-1]["content"] if self.messages else "none"


# ─────────────────────────────────────────────
# 2. LLM ROUTER
#    Calls Claude with a compact state snapshot.
#    Returns the name of the next agent to run.
# ─────────────────────────────────────────────

ROUTER_SYSTEM_PROMPT = """You are the orchestrator of a multi-agent IT support system.
Your only job is to decide which agent to run next given the current ticket state.

Agents available:
- "intake"     → Run first. Classifies ticket type, priority, and intent.
- "knowledge"  → Run after intake for informational issues or troubleshooting steps.
- "workflow"   → Run after intake or knowledge when the issue is automatable.
                 Automatable intents include password_reset, account_unlock, vpn_issue,
                 network, wifi_issue, mfa_reset, and software_install.
- "escalation" → Run only when workflow failed, user declined workflow, intent is unknown,
                 kb_confidence is low with no useful answer, or issue is not automatable.
                 Do NOT escalate just because priority is P1 or P2 if the intent is automatable.
- "end"        → Run when the ticket is fully resolved.

Routing priority:
1. If no category/intent exists yet, choose "intake".
2. If intent is password_reset, account_unlock, vpn_issue, network, wifi_issue, mfa_reset, or software_install, choose "workflow".
3. If knowledge has resolved the issue, choose "end".
4. If workflow succeeded, choose "end".
5. If workflow failed or issue is not automatable, choose "escalation".
6. If already escalated, choose "end".

Respond ONLY with a JSON object like: {"next": "workflow"}
Do not explain. Do not add any other text.
"""

_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def llm_router(state: TicketState) -> str:
    """Ask Claude what the next agent should be. Returns agent name string."""

    state_snapshot = {
        "ticket_category": state.ticket_category,
        "intent":          state.intent,
        "priority":        state.priority,
        "kb_confidence":   state.kb_confidence,
        "workflow_result": state.workflow_result,
        "user_confirmed":  state.user_confirmed,
        "escalated":       bool(state.escalation_summary),
        "ticket_id":       state.ticket_id,
        "last_message":    state.last_message(),
    }
    response = _client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Current state:\n{json.dumps(state_snapshot, indent=2)}\n\nWhat is the next agent?",
        },
    ],
    temperature=0,
)

    raw = response.choices[0].message.content.strip()
    try:
        decision = json.loads(raw)
        next_agent = decision.get("next", "escalation")
    except (json.JSONDecodeError, KeyError):
        next_agent = "escalation"   # safe fallback

    valid = {"intake", "knowledge", "workflow", "escalation", "end"}
    return next_agent if next_agent in valid else "escalation"


# ─────────────────────────────────────────────
# 3. AGENT WRAPPERS
#    Each function receives the full TicketState,
#    mutates it in-place, and returns nothing.
#    Swap the stub bodies for your real agents.
# ─────────────────────────────────────────────

def run_intake_agent(state: TicketState) -> None:
    """
    Intake Agent: classifies the ticket, assigns priority, extracts intent.
    STUB — replace with your real IntakeAgent call.
    """
    # ── YOUR AGENT GOES HERE ──────────────────────────────────────────────
    # result = your_intake_agent.run(state.ticket_text)
    state.ticket_category = "password"
    state.priority        = "P2"
    state.intent          = "password_reset"
   
    if not state.ticket_id:
        state.ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    # ─────────────────────────────────────────────────────────────────────

    msg = (
        f"Classified as '{state.ticket_category}' | "
        f"Priority: {state.priority} | Intent: {state.intent}"
    )
    state.add_message("assistant", "intake_agent", msg)
    print(f"[INTAKE]     {msg}")


def run_knowledge_agent(state: TicketState) -> None:
    """
    Knowledge Agent: RAG retrieval over the IT knowledge base.
    STUB — replace with your real KnowledgeAgent call.
    """
    # ── YOUR AGENT GOES HERE ──────────────────────────────────────────────
    # result = your_knowledge_agent.run(state.ticket_text, state.ticket_category)
    state.kb_results = [
        "Step 1: Go to company SSO portal → 'Forgot Password'.",
        "Step 2: Verify via MFA to your registered mobile device.",
        "Step 3: Set a new password meeting complexity requirements.",
    ]
    state.kb_confidence = 0.91
    # ─────────────────────────────────────────────────────────────────────

    msg = (
        f"Retrieved {len(state.kb_results)} steps "
        f"(confidence: {state.kb_confidence:.0%}): {state.kb_results[0][:60]}…"
    )
    state.add_message("assistant", "knowledge_agent", msg)
    print(f"[KNOWLEDGE]  {msg}")


def run_workflow_agent(state: TicketState) -> None:

        # Expect confirmation to already exist in state from the UI/API layer
    if state.user_confirmed is None:
        state.workflow_result = "awaiting_confirmation"

        msg = (
            "I can attempt to automatically resolve this issue. "
            "Would you like me to proceed?"
        )

        state.add_message("assistant", "workflow_agent", msg)
        print(f"[WORKFLOW] {msg}")
        return
    
    if state.user_confirmed is False:
        state.workflow_result = "not_attempted"

        msg = "User declined automation. Routing to escalation."

        state.add_message("assistant", "workflow_agent", msg)
        print(f"[WORKFLOW] {msg}")
        return

    # ── YOUR AGENT GOES HERE (when built) ────────────────────────────────
    # result = your_workflow_agent.execute(state.ticket_category, state.employee_id)
    state.workflow_attempted = True
    state.workflow_result    = "failed"   # change to "success" when real agent is ready
    # ─────────────────────────────────────────────────────────────────────

    msg = f"Execution result: {state.workflow_result}"
    state.add_message("assistant", "workflow_agent", msg)
    print(f"[WORKFLOW]   {msg}")


def run_escalation_agent(state: TicketState) -> None:
    """
    Escalation Agent: updates or creates a Supabase ticket and writes a
    human-readable handoff summary.

    Bridges TicketState ↔ escalation_agent(context) interface.
    """
    # ── BRIDGE: TicketState → escalation_agent context ───────────────────
    #
    # priority: your agent expects "high"/"low"; state uses "P1"–"P4".
    raw_priority    = state.priority or "P3"
    mapped_priority = "high" if raw_priority in ("P1", "P2") else "low"
    intent          = state.intent or state.ticket_category or "unknown"

    context = {
        "intake": {
            "priority":   mapped_priority,
            "intent":     intent,
            "user_input": state.ticket_text,
            "ticket_id":  state.ticket_id,      # may be None on first run
        },
        "primary_result": {
            "confidence": state.kb_confidence,
            "ticket_id":  state.ticket_id,
        },
    }
    # ─────────────────────────────────────────────────────────────────────

    # ── REAL AGENT CALL ───────────────────────────────────────────────────
    result = escalation_agent(context)
    # result keys: agent, escalated, ticket_id, priority, reason, message
    # ─────────────────────────────────────────────────────────────────────

    # ── BRIDGE: result → TicketState ─────────────────────────────────────
    if result.get("ticket_id"):
        state.ticket_id = result["ticket_id"]

    state.escalation_summary = (
        f"Escalated: {result['escalated']}\n"
        f"Ticket ID: {result.get('ticket_id', 'N/A')}\n"
        f"Priority:  {result.get('priority', 'N/A')}\n"
        f"Reason:    {result.get('reason', '')}\n"
        f"Message:   {result.get('message', '')}"
    )

    msg = result.get("message", state.escalation_summary)
    state.add_message("assistant", "escalation_agent", msg)
    print(f"[ESCALATION] {msg}")
    # ─────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────
# 4. ORCHESTRATOR
#    The main loop: router → agent → router …
#    until the router returns "end" or the
#    safety step limit is hit.
# ─────────────────────────────────────────────

AGENT_MAP: dict[str, callable] = {
    "intake":     run_intake_agent,
    "knowledge":  run_knowledge_agent,
    "workflow":   run_workflow_agent,
    "escalation": run_escalation_agent,
}

class Orchestrator:

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps


    def run(self, state: TicketState) -> TicketState:

        print("=== IT Support Orchestrator started ===\n")

        state.add_message("user", "user", state.ticket_text)

        for step in range(self.max_steps):

            # 1. Ask router where to go
            next_agent = llm_router(state)
            state.next_agent = next_agent

            print(f"[ROUTER]      → {next_agent.upper()}")

            # 2. End condition
            if next_agent == "end":
                state.resolved = True
                print("\n=== Ticket resolved. ===")
                return state

            # 3. Get selected agent
            agent_fn = AGENT_MAP.get(next_agent)

            # 4. Unknown route safety
            if agent_fn is None:
                print(f"[ROUTER] Unknown agent '{next_agent}', escalating.")
                run_escalation_agent(state)
                return state

            # 5. Run agent
            agent_fn(state)

            # 6. Pause flow if waiting for user
            if state.workflow_result == "awaiting_confirmation":
                print("[ORCHESTRATOR] Waiting for user confirmation. Pausing flow.")
                return state

            print()

        # 7. Safety fallback
        print(f"[ORCHESTRATOR] Max steps ({self.max_steps}) reached. Force-escalating.")
        run_escalation_agent(state)

        return state


# ─────────────────────────────────────────────
# 5. ENTRY POINT
def orchestrator(user_input: str) -> dict:
    initial_state = TicketState(
        ticket_text=user_input,
        employee_id="unknown"
    )

    runner = Orchestrator(max_steps=10)
    final_state = runner.run(initial_state)

    return {
        "user_input": final_state.ticket_text,
        "employee_id": final_state.employee_id,
        "category": final_state.ticket_category,
        "intent": final_state.intent,
        "priority": final_state.priority,
        "kb_results": final_state.kb_results,
        "kb_confidence": final_state.kb_confidence,
        "workflow_attempted": final_state.workflow_attempted,
        "workflow_result": final_state.workflow_result,
        "ticket_id": final_state.ticket_id,
        "escalation_summary": final_state.escalation_summary,
        "resolved": final_state.resolved,
        "messages": final_state.messages,
    }
# ─────────────────────────────────────────────
"""
if __name__ == "__main__":
    initial_state = TicketState(
        ticket_text="I forgot my password and can't log in.",
        employee_id="emp_00123",
        user_confirmed=True,

    )

    orchestrator = Orchestrator(max_steps=10)
    final_state  = orchestrator.run(initial_state)

    print("\n=== Final State Summary ===")
    print(f"Resolved:  {final_state.resolved}")
    print(f"Ticket ID: {final_state.ticket_id}")
    print(f"Category:  {final_state.ticket_category}")
    print(f"Priority:  {final_state.priority}")

if final_state.escalation_summary:
    print(f"\nEscalation summary:\n{final_state.escalation_summary}")
    """