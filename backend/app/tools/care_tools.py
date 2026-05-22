"""Care recommendation tools"""
from typing import Dict
import json


def recommend_interim_care(diagnostic_summary: str) -> str:
    """
    Generate interim care recommendation based on diagnostic summary.
    
    Args:
        diagnostic_summary: The preliminary diagnostic summary
        
    Returns:
        Interim care recommendation
    """
    # Simple rule-based recommendations
    summary_lower = diagnostic_summary.lower()
    
    if any(word in summary_lower for word in ['urgence', 'urgent', 'immédiat']):
        return "⚠️ Consultation médicale urgente recommandée. Ne pas attendre."
    
    elif any(word in summary_lower for word in ['fièvre', 'température', 'infection']):
        return "Repos au lit, hydratation abondante, surveillance de la température. Paracétamol si nécessaire. Consulter si aggravation."
    
    elif any(word in summary_lower for word in ['toux', 'gorge', 'rhume']):
        return "Repos, hydratation avec boissons chaudes, miel pour la gorge. Éviter les changements de température. Surveiller l'apparition de fièvre."
    
    elif any(word in summary_lower for word in ['fatigue', 'épuisement', 'stress']):
        return "Repos adapté, alimentation équilibrée, hydratation. Réduire le stress. Consulter si les symptômes persistent plus d'une semaine."
    
    else:
        return "Repos, hydratation, surveillance des symptômes. Consulter un médecin en cas d'aggravation ou de persistance des symptômes."


def check_red_flags(answers: list) -> Dict[str, bool]:
    """
    Check for red flags in patient answers.
    
    Args:
        answers: List of patient answers
        
    Returns:
        Dictionary of red flags detected
    """
    red_flags = {
        "chest_pain": False,
        "breathing_difficulty": False,
        "consciousness_loss": False,
        "severe_bleeding": False,
        "high_fever": False
    }
    
    all_text = " ".join([a.get("answer", "").lower() for a in answers])
    
    if any(word in all_text for word in ["douleur thoracique", "poitrine serrée"]):
        red_flags["chest_pain"] = True
    
    if any(word in all_text for word in ["difficulté respirer", "essoufflement", "respiration difficile"]):
        red_flags["breathing_difficulty"] = True
    
    if any(word in all_text for word in ["perte connaissance", "évanouissement", "inconscient"]):
        red_flags["consciousness_loss"] = True
    
    if "39.5" in all_text or "40" in all_text:
        red_flags["high_fever"] = True
    
    return red_flags