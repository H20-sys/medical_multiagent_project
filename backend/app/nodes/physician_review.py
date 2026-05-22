"""Physician Review node - Human-in-the-Loop"""
from langchain_core.messages import HumanMessage, AIMessage
from ..state import MedicalState


def physician_review_node(state: MedicalState) -> dict:
    """
    Human-in-the-Loop node for physician review.
    This node will interrupt execution waiting for human input.
    """
    diagnostic_summary = state.get("diagnostic_summary", "")
    interim_care = state.get("interim_care", "")
    
    # Prepare information for the physician
    review_message = f"""
    === REVUE MÉDICALE REQUISE ===
    
    SYSTHÈSE CLINIQUE PRÉLIMINAIRE:
    {diagnostic_summary}
    
    RECOMMANDATION INTERMÉDIAIRE:
    {interim_care}
    
    Veuillez fournir:
    1. Traitement ou conduite à tenir
    2. Notes complémentaires
    """
    
    # This node will be interrupted by the graph
    # The API will handle the interruption and resume
    
    return {
        "messages": state.get("messages", []) + [AIMessage(content=review_message)],
        "session_status": "awaiting_physician"
    }


def update_physician_review(state: MedicalState, treatment: str, notes: str) -> dict:
    """Update state after physician review"""
    return {
        "physician_treatment": treatment,
        "physician_notes": notes,
        "session_status": "physician_reviewed",
        "next": "supervisor",
        "messages": state.get("messages", []) + [
            HumanMessage(content=f"Médecine traitant: {treatment}\nNotes: {notes}")
        ]
    }