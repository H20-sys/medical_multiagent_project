"""Supervisor node - orchestrates the workflow"""
from langchain_core.messages import HumanMessage
from ..state import MedicalState


def supervisor_node(state: MedicalState) -> dict:
    """
    Supervisor decides which agent to call next based on current state
    """
    
    # Determine next step based on state
    current_status = state.get("session_status", "started")
    question_count = state.get("question_count", 0)
    diagnostic_summary = state.get("diagnostic_summary", "")
    physician_treatment = state.get("physician_treatment", "")
    
    if current_status == "started":
        next_step = "diagnostic_agent"
    elif question_count < 5 and not diagnostic_summary:
        next_step = "diagnostic_agent"
    elif diagnostic_summary and not physician_treatment:
        next_step = "physician_review"
    elif physician_treatment and not state.get("final_report"):
        next_step = "report_agent"
    else:
        next_step = "FINISH"
    
    return {
        "next": next_step,
        "messages": state.get("messages", []) + [HumanMessage(content=f"Supervisor routing to: {next_step}")]
    }