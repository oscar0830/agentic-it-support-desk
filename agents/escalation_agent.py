from rag.supabase_client import supabase
 
 
def escalation_agent(context):
    print("\n[ESCALATION AGENT] Checking escalation rules...")
 
    intake = context.get("intake", context)
    primary_result = context.get("primary_result", {})
 
    confidence = primary_result.get(
        "confidence",
        intake.get("confidence", context.get("confidence", 0))
    )
    priority = intake.get("priority", context.get("priority", "low"))
    intent = intake.get("intent", context.get("intent", "unknown"))
    user_issue = intake.get("user_input", context.get("user_input", ""))
 
    ticket_id = (
        context.get("ticket_id")
        or intake.get("ticket_id")
        or primary_result.get("ticket_id")
    )
 
    if not ticket_id:
        raise ValueError(
            "[ESCALATION AGENT] ticket_id is missing from context. "
            "Intake Agent must create the ticket before Escalation runs."
        )
 
    should_escalate = (
        confidence < 0.7
        or priority == "high"
        or intent == "unknown"
    )
 
    # No escalation needed
    if not should_escalate:
        return {
            "agent": "escalation_agent",
            "escalated": False,
            "ticket_id": ticket_id,
            "priority": priority,
            "reason": (
                "No escalation needed because confidence is acceptable "
                "and priority is not high."
            ),
            "message": (
                "This issue can be handled automatically using the "
                "knowledge base response."
            )
        }
 
    # Escalate — update the existing Intake-created ticket
    escalation_reason = (
        "Escalated because confidence is low, "
        "priority is high, or issue type is unknown."
    )
 
    response = supabase.table("tickets").update({
        "status": "escalated",
        "priority": priority,
    }).eq("ticket_id", ticket_id).execute()
 
    updated_ticket = response.data[0] if response.data else {}
    final_ticket_id = updated_ticket.get("ticket_id", ticket_id)
 
    return {
        "agent": "escalation_agent",
        "escalated": True,
        "ticket_id": final_ticket_id,
        "priority": priority,
        "reason": escalation_reason,
        "message": (
            f"Your issue has been escalated to IT support.\n\n"
            f"Ticket ID: {final_ticket_id}\n"
            f"Priority: {priority}\n\n"
            f"A support specialist should review this request soon."
        )
    }
