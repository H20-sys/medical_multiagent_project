"""Diagnostic Agent - asks questions and produces preliminary analysis"""
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from ..state import MedicalState
from ..tools.patient_tools import ask_question_tool, get_medical_guidelines
from ..tools.care_tools import recommend_interim_care
import os

llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"), temperature=0.3)

# Predefined medical questions based on common symptoms
MEDICAL_QUESTIONS = [
    "Depuis combien de temps ressentez-vous ces symptômes ? (en jours/heures)",
    "Sur une échelle de 1 à 10, comment évaluez-vous l'intensité de vos symptômes ?",
    "Avez-vous de la fièvre ? Si oui, quelle température ?",
    "Avez-vous d'autres symptômes associés (toux, maux de tête, douleurs musculaires, fatigue) ?",
    "Avez-vous des antécédents médicaux particuliers ou prenez-vous des traitements réguliers ?"
]


def diagnostic_agent(state: MedicalState) -> dict:
    """
    Diagnostic agent that asks 5 questions and produces a clinical summary
    """
    question_count = state.get("question_count", 0)
    questions_asked = state.get("questions_asked", [])
    patient_answers = state.get("patient_answers", [])
    
    # If we haven't asked all 5 questions yet
    if question_count < 5:
        next_question = MEDICAL_QUESTIONS[question_count]
        
        # Update state with the question
        updated_questions = questions_asked + [next_question]
        
        return {
            "question_count": question_count + 1,
            "questions_asked": updated_questions,
            "next": "diagnostic_agent",  # Stay in diagnostic to get answer
            "messages": state.get("messages", []) + [AIMessage(content=next_question)]
        }
    
    # All questions answered - produce diagnostic summary
    else:
        # Build context for LLM
        patient_context = f"""
        Cas initial: {state.get('patient_initial_case', '')}
        
        Réponses du patient:
        {chr(10).join([f"Q{i+1}: {q}\nR: {a.get('answer', '')}" for i, (q, a) in enumerate(zip(questions_asked, patient_answers))])}
        """
        
        # Generate diagnostic summary
        summary_prompt = SystemMessage(content="""
        Vous êtes un assistant médical. Produisez une synthèse clinique préliminaire basée sur les informations du patient.
        
        IMPORTANT: Ceci n'est pas un diagnostic définitif. Utilisez un langage prudent comme "suggère", "pourrait indiquer", "il serait prudent de considérer".
        
        Incluez dans votre synthèse:
        1. Résumé des symptômes rapportés
        2. Signes d'alerte potentiels à surveiller
        3. Recommandations générales prudentes
        4. Mention que l'avis d'un médecin est nécessaire
        
        Soyez professionnel mais accessible.
        """)
        
        human_context = HumanMessage(content=patient_context)
        
        response = llm.invoke([summary_prompt, human_context])
        diagnostic_summary = response.content
        
        # Generate interim care recommendation
        interim_care = recommend_interim_care(diagnostic_summary)
        
        # Check for red flags
        red_flags = any(flag in diagnostic_summary.lower() for flag in 
                       ['urgence', 'hospitalisation', 'douleur thoracique', 'difficulté respiratoire', 
                        'perte de conscience', 'convulsion', 'hémorragie'])
        
        return {
            "diagnostic_summary": diagnostic_summary,
            "interim_care": interim_care,
            "red_flags_detected": red_flags,
            "next": "supervisor",  # Go back to supervisor for routing
            "session_status": "diagnosis_complete",
            "messages": state.get("messages", []) + [
                AIMessage(content=f"Synthèse clinique établie. {diagnostic_summary}"),
                AIMessage(content=f"Recommandation intermédiaire: {interim_care}")
            ]
        }