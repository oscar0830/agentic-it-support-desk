import json
import time
from datetime import datetime, timezone
 
from openai import OpenAI
from rag.supabase_client import supabase
from rag.vector_store import search_similar_tickets
 
client = OpenAI()
 
SYSTEM_PROMPT = """You are the Intake Agent of an autonomous IT support platform.
Your job is to classify an employee IT support request.
 
You have already been given the results of a knowledge base search for similar past tickets.
Use those results to inform your classification.
 
## Intent categories
- network   : Wi-Fi, VPN, connectivity, DNS, firewall
- password  : password reset, account unlock, MFA, SSO
- hardware  : laptop, monitor, peripheral, printer, physical device
- software  : application install/crash, OS, license, SaaS access
- unknown   : too vague or does not fit the above
 
## Category (human-readable label for dashboards)
- Connectivity   : maps to network intent
- Account Access : maps to password intent
- Device Issue   : maps to hardware intent
- Application    : maps to software intent
- Other          : maps to unknown intent
 
## Priority
- high   : fully blocked, production issue, security incident
- medium : partially degraded, workaround exists
- low    : cosmetic, question, nice-to-have
 
## Output — respond ONLY with raw JSON, no markdown:
{
  "intent": "<category>",
  "category": "<human-readable label from the Category list above>",
  "priority": "<high|medium|low>",
  "confidence": <0.0-1.0>,
  "clarification_needed": <true|false>,
  "clarification_question": "<one specific question, or empty string>",
  "summary": "<one sentence plain-English description>",
  "rag_match": <true|false>,
  "rag_summary": "<brief description of the matching past ticket, or empty string>",
  "reason": "<brief explanation of why this intent and priority were chosen>"
}
 
If confidence < 0.7, set clarification_needed=true and write one clarification_question."""
 
INTENT_TO_CATEGORY = {
    "network": "Connectivity",
    "password": "Account Access",
    "hardware": "Device Issue",
    "software": "Application",
    "unknown": "Other",
}
 
 
def _keyword_fallback(user_input: str) -> dict:
    """Fallback classification if the LLM API fails — keeps the system alive."""
    print("[INTAKE AGENT] LLM failed — using keyword fallback.")
    lower = user_input.lower()
 
    if any(w in lower for w in ("wifi", "wi-fi", "vpn", "internet", "network", "connect")):
        intent, priority = "network", "high"
    elif any(w in lower for w in ("password", "reset", "locked", "unlock", "mfa", "sso")):
        intent, priority = "password", "medium"
    elif any(w in lower for w in ("laptop", "monitor", "keyboard", "mouse", "printer")):
        intent, priority = "hardware", "medium"
    elif any(w in lower for w in ("app", "software", "install", "crash", "license", "access")):
        intent, priority = "software", "medium"
    else:
        intent, priority = "unknown", "low"
 
    return {
        "intent": intent,
        "category": INTENT_TO_CATEGORY.get(intent, "Other"),
        "priority": priority,
        "confidence": 0.5,
        "clarification_needed": intent == "unknown",
        "clarification_question": "Could you describe what's not working in more detail?" if intent == "unknown" else "",
        "summary": f"Possible {intent} issue (keyword fallback).",
        "rag_match": False,
        "rag_summary": "",
        "reason": "LLM API unavailable — classified by keyword fallback.",
    }
 
 
def _classify(user_input: str, employee_id: str, device_info: str, conversation_history: list) -> dict:
    """Run RAG search then call the LLM to classify. Returns raw result dict."""
 
    # RAG — search for similar past tickets before classifying
    rag_results = []
    try:
        rag_results = search_similar_tickets(query=user_input, top_k=3)
    except Exception as e:
        print(f"[INTAKE AGENT] RAG search failed: {e}")
 
    rag_context = (
        f"Similar past tickets:\n{json.dumps(rag_results, indent=2)}"
        if rag_results
        else "No similar past tickets found."
    )
 
    user_message = (
        f"Employee ID: {employee_id}\n"
        f"Device: {device_info}\n\n"
        f"Request: {user_input}\n\n"
        f"{rag_context}"
    )
 
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + conversation_history
        + [{"role": "user", "content": user_message}]
    )
 
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        print(f"[INTAKE AGENT] LLM error: {e}")
        return _keyword_fallback(user_input)
 
 
def intake_agent(context: dict) -> dict:
    """
    Intake Agent — classifies an employee support request.
 
    Expects context keys:
        user_input            : str   — employee's latest Slack message
        employee_id           : str   — authenticated employee ID
        device_info           : str   — device/OS string (from MDM or profile)
        conversation_history  : list  — prior {"role", "content"} turns (default [])
 
    Returns a dict with:
        agent                 : "intake_agent"
        clarification_needed  : bool
        clarification_question: str
        conversation_history  : list  — updated history for next call
        intake                : dict  — classification payload for downstream agents
        ticket_id             : str | None
        metrics               : dict  — latency + RAG stats
        message               : str   — reply to send the employee via Slack
    """
    print("\n[INTAKE AGENT] Classifying request...")
    start_time = time.time()
 
    user_input = context.get("user_input", "")
    employee_id = context.get("employee_id", "unknown")
    device_info = context.get("device_info", "unknown")
    conversation_history = context.get("conversation_history", [])
 
    result = _classify(user_input, employee_id, device_info, conversation_history)
 
    intent = result.get("intent", "unknown")
    category = result.get("category", INTENT_TO_CATEGORY.get(intent, "Other"))
    priority = result.get("priority", "low")
    confidence = result.get("confidence", 0.0)
    clarification_needed = result.get("clarification_needed", False)
    clarification_question = result.get("clarification_question", "")
    summary = result.get("summary", user_input)
    rag_match = result.get("rag_match", False)
    rag_summary = result.get("rag_summary", "")
    reason = result.get("reason", "")
 
    latency_ms = round((time.time() - start_time) * 1000)
 
    metrics = {
        "agent": "intake_agent",
        "latency_ms": latency_ms,
        "rag_match": rag_match,
        "confidence": confidence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
 
    print(f"[INTAKE AGENT] Done in {latency_ms}ms | intent={intent} | category={category} | priority={priority} | confidence={confidence:.2f} | reason={reason}")
 
    updated_history = conversation_history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": json.dumps(result)},
    ]
 
    intake_payload = {
        "user_input": user_input,
        "employee_id": employee_id,
        "device_info": device_info,
        "intent": intent,
        "category": category,
        "priority": priority,
        "confidence": confidence,
        "summary": summary,
        "rag_match": rag_match,
        "rag_summary": rag_summary,
        "reason": reason,
    }
 
    # Clarification needed — hold ticket creation
    if clarification_needed:
        print(f"[INTAKE AGENT] Asking: {clarification_question}")
        return {
            "agent": "intake_agent",
            "clarification_needed": True,
            "clarification_question": clarification_question,
            "conversation_history": updated_history,
            "intake": intake_payload,
            "ticket_id": None,
            "metrics": metrics,
            "message": clarification_question,
        }
 
    # Confident — insert ticket into Supabase
    now = datetime.now(timezone.utc).isoformat()
 
    response = supabase.table("tickets").insert({
        "user_issue": user_input,
        "employee_id": employee_id,
        "device_info": device_info,
        "intent": intent,
        "category": category,
        "priority": priority,
        "summary": summary,
        "status": "open",
        "confidence": confidence,
        "rag_match": rag_match,
        "rag_summary": rag_summary,
        "reason": reason,
        "created_at": now,
        "agent_version": "intake_agent_v3",
        "latency_ms": latency_ms,
    }).execute()
 
    ticket = response.data[0] if response.data else {}
    ticket_id = ticket.get("ticket_id", ticket.get("id"))
 
    if not ticket_id:
        raise RuntimeError(
            "[INTAKE AGENT] Supabase insert returned no ticket_id. "
            "Cannot proceed — downstream agents require a valid ticket_id."
        )
 
    supabase.table("agent_metrics").insert({
        **metrics,
        "ticket_id": ticket_id,
        "intent": intent,
        "category": category,
        "priority": priority,
    }).execute()
 
    return {
        "agent": "intake_agent",
        "clarification_needed": False,
        "clarification_question": "",
        "conversation_history": updated_history,
        "intake": intake_payload,
        "ticket_id": ticket_id,
        "metrics": metrics,
        "message": (
            f"Got it — I've logged your request (Ticket #{ticket_id}).\n\n"
            f"**Issue**: {summary}\n"
            f"**Priority**: {priority.capitalize()}\n"
            + (f"**Similar past issue found**: {rag_summary}\n" if rag_match else "")
            + "\nI'll start working on a fix now."
        ),
    }
