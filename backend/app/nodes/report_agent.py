"""Report Agent - generates final structured report"""
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from ..state import MedicalState
import os
from datetime import datetime

llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"), temperature=0.2)


def report_agent(state: MedicalState) -> dict:
    """
    Generate final structured medical report
    """
    
    # Build complete report
    report_prompt = SystemMessage(content="""
    Vous êtes un assistant médical. Générez un rapport final structuré basé sur toutes les informations disponibles.
    
    Le rapport doit inclure:
    1. Informations patient (anonymisées)
    2. Motif de consultation initial
    3. Réponses aux questions clés
    4. Synthèse clinique préliminaire
    5. Recommandations intermédiaires
    6. Décisions du médecin traitant (traitement/ conduite)
    7. Recommandations finales
    
    IMPORTANT: Ajoutez la mention obligatoire: 
    "Ce système ne remplace pas une consultation médicale. Ce rapport est à titre informatif uniquement."
    
    Format structuré et professionnel.
    """)
    
    report_content = f"""
    === RAPPORT MÉDICAL ===
    
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    MOTIF DE CONSULTATION:
    {state.get('patient_initial_case', 'Non spécifié')}
    
    QUESTIONS ET RÉPONSES:
    """
    
    questions_asked = state.get('questions_asked', [])
    patient_answers = state.get('patient_answers', [])
    
    for i, (q, a) in enumerate(zip(questions_asked, patient_answers)):
        report_content += f"\nQ{i+1}: {q}\nR: {a.get('answer', '')}\n"
    
    report_content += f"""
    
    SYSTHÈSE CLINIQUE PRÉLIMINAIRE:
    {state.get('diagnostic_summary', 'Non disponible')}
    
    RECOMMANDATION INTERMÉDIAIRE:
    {state.get('interim_care', 'Non disponible')}
    
    DÉCISIONS DU MÉDECIN TRAITANT:
    Traitement/Conduite: {state.get('physician_treatment', 'Non spécifié')}
    Notes complémentaires: {state.get('physician_notes', 'Aucune')}
    
    SIGNES D'ALERTE DÉTECTÉS: {'Oui' if state.get('red_flags_detected', False) else 'Non'}
    
    =======================================
    ⚠️ AVERTISSEMENT: 
    Ce système ne remplace pas une consultation médicale. 
    Ce rapport est à titre informatif uniquement.
    =======================================
    """
    
    # Enhance with LLM for better formatting
    human_report = HumanMessage(content=report_content)
    response = llm.invoke([report_prompt, human_report])
    final_report = response.content
    
    return {
        "final_report": final_report,
        "session_status": "completed",
        "next": "FINISH",
        "messages": state.get("messages", []) + [AIMessage(content="Rapport final généré")]
    }