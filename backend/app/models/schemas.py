"""Pydantic schemas for API responses"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ConsultationStartRequest(BaseModel):
    patient_initial_case: str = Field(..., description="Initial patient complaint or symptoms")
    patient_id: Optional[str] = None


class ConsultationResponse(BaseModel):
    thread_id: str
    status: str
    current_step: str
    question: Optional[str] = None
    questions_asked: List[str] = []
    patient_answers: List[Dict[str, str]] = []
    diagnostic_summary: Optional[str] = None
    interim_care: Optional[str] = None


class AnswerRequest(BaseModel):
    thread_id: str
    answer: str


class PhysicianReviewRequest(BaseModel):
    thread_id: str
    treatment: str
    notes: str


class FinalReport(BaseModel):
    thread_id: str
    report: str
    diagnostic_summary: str
    interim_care: str
    physician_treatment: str
    generated_at: datetime


class SessionInfo(BaseModel):
    thread_id: str
    status: str
    created_at: datetime