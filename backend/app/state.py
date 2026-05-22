"""State management for the medical graph"""
from typing import Annotated, Literal, Optional, List, Dict, Any
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class MedicalState(TypedDict):
    """Shared state for the medical multi-agent system"""
    messages: Annotated[list, add_messages]
    next: Literal[
        "diagnostic_agent",
        "physician_review",
        "report_agent",
        "FINISH"
    ]
    question_count: int
    patient_initial_case: str
    patient_answers: List[Dict[str, str]]
    questions_asked: List[str]
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    physician_notes: str
    final_report: str
    patient_id: Optional[str]
    session_status: str
    red_flags_detected: bool


def create_initial_state(initial_case: str) -> MedicalState:
    """Create initial state for a new consultation"""
    return MedicalState(
        messages=[],
        next="diagnostic_agent",
        question_count=0,
        patient_initial_case=initial_case,
        patient_answers=[],
        questions_asked=[],
        interim_care="",
        diagnostic_summary="",
        physician_treatment="",
        physician_notes="",
        final_report="",
        patient_id=None,
        session_status="started",
        red_flags_detected=False
    )