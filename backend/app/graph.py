"""LangGraph graph definition for medical multi-agent system"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from typing import Literal
import asyncio

from .state import MedicalState
from .nodes.supervisor import supervisor_node
from .nodes.diagnostic_agent import diagnostic_agent
from .nodes.physician_review import physician_review_node
from .nodes.report_agent import report_agent


def route_after_diagnostic(state: MedicalState) -> Literal["supervisor", "diagnostic_agent"]:
    """Route after diagnostic agent based on question count"""
    if state.get("question_count", 0) < 5:
        return "diagnostic_agent"  # Ask another question
    else:
        return "supervisor"  # Go to supervisor for next step


def route_after_supervisor(state: MedicalState) -> Literal[
    "diagnostic_agent", "physician_review", "report_agent", END
]:
    """Route after supervisor based on next field"""
    next_step = state.get("next", "FINISH")
    
    if next_step == "diagnostic_agent":
        return "diagnostic_agent"
    elif next_step == "physician_review":
        return "physician_review"
    elif next_step == "report_agent":
        return "report_agent"
    else:
        return END


def create_medical_graph(checkpointer: BaseCheckpointSaver = None):
    """
    Create and compile the medical multi-agent graph
    
    Args:
        checkpointer: Checkpoint saver for persistence
        
    Returns:
        Compiled graph
    """
    
    # Create graph builder
    builder = StateGraph(MedicalState)
    
    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("diagnostic_agent", diagnostic_agent)
    builder.add_node("physician_review", physician_review_node)
    builder.add_node("report_agent", report_agent)
    
    # Add edges
    builder.set_entry_point("supervisor")
    
    # Add conditional edges
    builder.add_conditional_edges(
        "diagnostic_agent",
        route_after_diagnostic,
        {
            "diagnostic_agent": "diagnostic_agent",
            "supervisor": "supervisor"
        }
    )
    
    builder.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            END: END
        }
    )
    
    # Add edges from physician review and report agent back to supervisor
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", END)
    
    # Create checkpointer if not provided
    if checkpointer is None:
        checkpointer = MemorySaver()
    
    # Compile graph
    graph = builder.compile(checkpointer=checkpointer)
    
    return graph


# Create a singleton graph instance
_medical_graph = None


def get_medical_graph():
    """Get or create the medical graph singleton"""
    global _medical_graph
    if _medical_graph is None:
        _medical_graph = create_medical_graph()
    return _medical_graph