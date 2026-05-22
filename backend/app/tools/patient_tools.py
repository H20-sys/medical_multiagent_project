"""Patient interaction tools"""
from typing import Dict, List
import json


def ask_question_tool(question: str) -> str:
    """
    Tool to ask a question to the patient.
    
    Args:
        question: The question to ask the patient
        
    Returns:
        A formatted question string
    """
    return f"QUESTION: {question}"


def record_patient_answer(question: str, answer: str) -> Dict[str, str]:
    """
    Record patient's answer to a question.
    
    Args:
        question: The question asked
        answer: Patient's response
        
    Returns:
        Dictionary containing question and answer
    """
    return {
        "question": question,
        "answer": answer
    }


def get_medical_guidelines(symptom: str) -> str:
    """
    Get basic medical guidelines for common symptoms (MCP tool)
    
    Args:
        symptom: The symptom to look up
        
    Returns:
        Guidelines for the symptom
    """
    guidelines_db = {
        "fièvre": "Repos, hydratation, surveillance de la température. Consulter si > 39.5°C ou persistance > 3 jours.",
        "toux": "Repos, hydratation, miel pour apaiser. Consulter si difficultés respiratoires ou sang.",
        "douleur thoracique": "URGENCE - Consulter immédiatement les urgences.",
        "mal de tête": "Repos, hydratation, éviter lumière vive. Consulter si persistant ou intense.",
        "fatigue": "Repos, alimentation équilibrée, hydratation. Consulter si prolongée > 2 semaines.",
    }
    
    return guidelines_db.get(symptom.lower(), 
                             "Repos et hydratation recommandés. Surveiller l'évolution. Consulter en cas d'aggravation.")