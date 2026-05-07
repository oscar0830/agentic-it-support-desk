def workflow_agent(context):
    print("\n[WORKFLOW AGENT] Processing workflow automation...")
 
    intent = context.get("intent", "unknown")
    priority = context.get("priority", "medium")
    user_input = context.get("user_input", "")
    ticket_id = context.get("ticket_id")
 
    if not ticket_id:
        raise ValueError(
            "[WORKFLOW AGENT] ticket_id is missing from context. "
            "Intake Agent must create the ticket before Workflow runs."
        )
 
    lower_input = user_input.lower()
 
    # -----------------------------------
    # PASSWORD RESET
    # -----------------------------------
    if intent == "password_reset" or "password" in lower_input:
        return {
            "agent": "workflow_agent",
            "resolved": True,
            "ticket_id": ticket_id,
            "intent": intent,
            "priority": priority,
            "workflow_action": "password_reset",
            "status": "completed",
            "message": (
                "Password reset workflow initiated.\n"
                "A reset link has been sent to the user's backup email."
            )
        }
 
    # -----------------------------------
    # VPN SUPPORT
    # -----------------------------------
    elif intent == "vpn_issue" or "vpn" in lower_input:
        return {
            "agent": "workflow_agent",
            "resolved": True,
            "ticket_id": ticket_id,
            "intent": intent,
            "priority": priority,
            "workflow_action": "vpn_refresh",
            "status": "completed",
            "message": (
                "VPN troubleshooting workflow completed.\n"
                "VPN credentials were refreshed and connection settings were reloaded."
            )
        }
 
    # -----------------------------------
    # NETWORK / WIFI SUPPORT
    # -----------------------------------
    elif intent == "network" or "wifi" in lower_input:
        return {
            "agent": "workflow_agent",
            "resolved": True,
            "ticket_id": ticket_id,
            "intent": intent,
            "priority": priority,
            "workflow_action": "network_restart",
            "status": "completed",
            "message": (
                "Network support workflow executed.\n"
                "Recommended actions:\n"
                "1. Restart router\n"
                "2. Reconnect device to WiFi\n"
                "3. Run network diagnostics"
            )
        }
 
    # -----------------------------------
    # ACCOUNT LOCKOUT
    # -----------------------------------
    elif "locked" in lower_input or "unlock" in lower_input:
        return {
            "agent": "workflow_agent",
            "resolved": True,
            "ticket_id": ticket_id,
            "intent": intent,
            "priority": priority,
            "workflow_action": "account_unlock",
            "status": "completed",
            "message": (
                "Account unlock workflow completed.\n"
                "The user account has been unlocked."
            )
        }
 
    # -----------------------------------
    # SOFTWARE INSTALL REQUEST
    # -----------------------------------
    elif "install" in lower_input or "software" in lower_input:
        return {
            "agent": "workflow_agent",
            "resolved": True,
            "ticket_id": ticket_id,
            "intent": intent,
            "priority": priority,
            "workflow_action": "software_request",
            "status": "submitted",
            "message": (
                "Software installation request submitted successfully.\n"
                "IT will review and approve the request."
            )
        }
 
    # -----------------------------------
    # UNKNOWN / NOT AUTOMATABLE
    # -----------------------------------
    else:
        return {
            "agent": "workflow_agent",
            "resolved": False,
            "ticket_id": ticket_id,
            "intent": intent,
            "priority": priority,
            "workflow_action": "unknown",
            "status": "needs_review",
            "message": (
                "This request could not be automatically resolved.\n"
                "Escalation to IT support may be required."
            )
        }
