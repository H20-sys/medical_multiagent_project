"""FastAPI endpoints for the medical multi-agent system"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
import uuid
from datetime import datetime

from .graph import get_medical_graph
from .state import create_initial_state
from .models.schemas import *
from .nodes.physician_review import update_physician_review

app = FastAPI(title="Medical Multi-Agent System API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for session data
sessions: Dict[str, Dict] = {}
pending_answers: Dict[str, Dict] = {}


@app.get("/")
async def root():
    return {"message": "Medical Multi-Agent System API", "status": "running"}


@app.post("/sessions/start")
async def start_session(request: ConsultationStartRequest):
    """Start a new consultation session"""
    thread_id = str(uuid.uuid4())
    
    # Create initial state
    initial_state = create_initial_state(request.patient_initial_case)
    initial_state["patient_id"] = request.patient_id or thread_id
    
    # Store session
    sessions[thread_id] = {
        "state": initial_state,
        "created_at": datetime.now(),
        "status": "started"
    }
    
    # Get graph and invoke
    graph = get_medical_graph()
    
    # Start the consultation
    config = {"configurable": {"thread_id": thread_id}}
    
    # Invoke graph asynchronously
    try:
        # First invocation will go to diagnostic agent
        result = await graph.ainvoke(initial_state, config)
        sessions[thread_id]["state"] = result
        sessions[thread_id]["status"] = result.get("session_status", "in_progress")
        
        # Get current question if any
        current_question = None
        if result.get("question_count", 0) < 5 and result.get("questions_asked"):
            questions = result.get("questions_asked", [])
            if questions:
                current_question = questions[-1]
        
        return ConsultationResponse(
            thread_id=thread_id,
            status=result.get("session_status", "in_progress"),
            current_step="diagnostic_agent" if result.get("question_count", 0) < 5 else "awaiting_physician",
            question=current_question,
            questions_asked=result.get("questions_asked", []),
            patient_answers=result.get("patient_answers", []),
            diagnostic_summary=result.get("diagnostic_summary"),
            interim_care=result.get("interim_care")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting consultation: {str(e)}")


@app.post("/consultation/start")
async def start_consultation(request: ConsultationStartRequest):
    """Alternative endpoint for starting consultation"""
    return await start_session(request)


@app.post("/consultation/answer")
async def submit_answer(request: AnswerRequest):
    """Submit patient answer to a question"""
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.thread_id]
    state = session["state"]
    
    # Record answer
    questions_asked = state.get("questions_asked", [])
    patient_answers = state.get("patient_answers", [])
    
    if patient_answers and not patient_answers[-1].get("answer"):
        # Update last answer
        patient_answers[-1]["answer"] = request.answer
    else:
        # Add new answer
        if questions_asked:
            patient_answers.append({
                "question": questions_asked[-1],
                "answer": request.answer
            })
    
    state["patient_answers"] = patient_answers
    
    # Continue graph execution
    graph = get_medical_graph()
    config = {"configurable": {"thread_id": request.thread_id}}
    
    try:
        result = await graph.ainvoke(state, config)
        session["state"] = result
        session["status"] = result.get("session_status", "in_progress")
        
        # Get next question if any
        next_question = None
        if result.get("question_count", 0) < 5 and result.get("questions_asked"):
            questions = result.get("questions_asked", [])
            if len(questions) > len(patient_answers):
                next_question = questions[-1]
        
        return ConsultationResponse(
            thread_id=request.thread_id,
            status=result.get("session_status", "in_progress"),
            current_step="diagnostic_agent" if result.get("question_count", 0) < 5 else "awaiting_physician",
            question=next_question,
            questions_asked=result.get("questions_asked", []),
            patient_answers=result.get("patient_answers", []),
            diagnostic_summary=result.get("diagnostic_summary"),
            interim_care=result.get("interim_care")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")


@app.post("/consultation/resume")
async def resume_consultation(thread_id: str):
    """Resume a consultation after interruption"""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[thread_id]
    state = session["state"]
    
    graph = get_medical_graph()
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        result = await graph.ainvoke(state, config)
        session["state"] = result
        session["status"] = result.get("session_status", "in_progress")
        
        return ConsultationResponse(
            thread_id=thread_id,
            status=result.get("session_status", "in_progress"),
            current_step="awaiting_physician" if result.get("diagnostic_summary") and not result.get("physician_treatment") else "completed",
            questions_asked=result.get("questions_asked", []),
            patient_answers=result.get("patient_answers", []),
            diagnostic_summary=result.get("diagnostic_summary"),
            interim_care=result.get("interim_care")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resuming consultation: {str(e)}")


@app.post("/consultation/physician_review")
async def physician_review(request: PhysicianReviewRequest):
    """Submit physician review and treatment"""
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[request.thread_id]
    state = session["state"]
    
    # Update state with physician input
    updated_state = update_physician_review(state, request.treatment, request.notes)
    state.update(updated_state)
    
    # Continue graph execution
    graph = get_medical_graph()
    config = {"configurable": {"thread_id": request.thread_id}}
    
    try:
        result = await graph.ainvoke(state, config)
        session["state"] = result
        session["status"] = result.get("session_status", "completed")
        
        return {
            "thread_id": request.thread_id,
            "status": "completed",
            "message": "Physician review submitted, report generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing physician review: {str(e)}")


@app.get("/consultation/{thread_id}")
async def get_consultation_status(thread_id: str):
    """Get current status of a consultation"""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[thread_id]
    state = session["state"]
    
    return ConsultationResponse(
        thread_id=thread_id,
        status=session["status"],
        current_step="completed" if state.get("final_report") else "in_progress",
        questions_asked=state.get("questions_asked", []),
        patient_answers=state.get("patient_answers", []),
        diagnostic_summary=state.get("diagnostic_summary"),
        interim_care=state.get("interim_care")
    )


@app.get("/consultation/{thread_id}/report")
async def get_final_report(thread_id: str):
    """Get the final report for a consultation"""
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[thread_id]
    state = session["state"]
    
    if not state.get("final_report"):
        raise HTTPException(status_code=404, detail="Report not yet generated")
    
    return FinalReport(
        thread_id=thread_id,
        report=state["final_report"],
        diagnostic_summary=state.get("diagnostic_summary", ""),
        interim_care=state.get("interim_care", ""),
        physician_treatment=state.get("physician_treatment", ""),
        generated_at=datetime.now()
    )


@app.get("/sessions")
async def list_sessions():
    """List all sessions"""
    return [
        {
            "thread_id": thread_id,
            "status": session["status"],
            "created_at": session["created_at"]
        }
        for thread_id, session in sessions.items()
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)