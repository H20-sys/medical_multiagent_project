"""Streamlit frontend for Medical Multi-Agent System"""
import streamlit as st
import requests
import json
from typing import Dict, Any

# API configuration
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Système Médical Multi-Agents",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background-color: #2c3e50;
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .report-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "step" not in st.session_state:
    st.session_state.step = "initial"
if "questions_asked" not in st.session_state:
    st.session_state.questions_asked = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "consultation_data" not in st.session_state:
    st.session_state.consultation_data = None


def start_consultation(initial_case: str):
    """Start a new consultation"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/sessions/start",
            json={"patient_initial_case": initial_case}
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.thread_id = data["thread_id"]
            st.session_state.step = "questions"
            st.session_state.consultation_data = data
            st.session_state.questions_asked = data.get("questions_asked", [])
            st.session_state.answers = data.get("patient_answers", [])
            st.rerun()
        else:
            st.error(f"Erreur: {response.status_code}")
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")


def submit_answer(answer: str):
    """Submit answer to current question"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/consultation/answer",
            json={
                "thread_id": st.session_state.thread_id,
                "answer": answer
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.consultation_data = data
            st.session_state.questions_asked = data.get("questions_asked", [])
            st.session_state.answers = data.get("patient_answers", [])
            
            # Check if questions are complete
            if data.get("diagnostic_summary"):
                st.session_state.step = "physician_review"
            
            st.rerun()
        else:
            st.error(f"Erreur: {response.status_code}")
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")


def submit_physician_review(treatment: str, notes: str):
    """Submit physician review"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/consultation/physician_review",
            json={
                "thread_id": st.session_state.thread_id,
                "treatment": treatment,
                "notes": notes
            }
        )
        
        if response.status_code == 200:
            st.session_state.step = "report"
            st.rerun()
        else:
            st.error(f"Erreur: {response.status_code}")
    except Exception as e:
        st.error(f"Erreur de connexion: {str(e)}")


def load_report():
    """Load the final report"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/consultation/{st.session_state.thread_id}/report"
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Erreur: {str(e)}")
        return None


# Main UI
st.markdown('<div class="main-header"><h1>🏥 Système Médical Multi-Agents</h1><p>Orientation Clinique Préliminaire</p></div>', 
            unsafe_allow_html=True)

# Warning message
st.markdown("""
<div class="warning-box">
⚠️ <strong>Avertissement médical important :</strong><br>
Ce système est un exercice académique. Il ne remplace pas une consultation médicale.
En cas d'urgence, contactez immédiatement les services d'urgence (15, 112).
</div>
""", unsafe_allow_html=True)

# Step 1: Initial case
if st.session_state.step == "initial":
    st.subheader("📋 Nouvelle Consultation")
    
    with st.form("initial_case_form"):
        initial_case = st.text_area(
            "Décrivez vos symptômes ou motifs de consultation",
            placeholder="Exemple: Je tousse depuis 3 jours, j'ai de la fièvre et je me sens fatigué...",
            height=150
        )
        
        submitted = st.form_submit_button("Commencer la Consultation")
        
        if submitted and initial_case:
            start_consultation(initial_case)

# Step 2: Questions
elif st.session_state.step == "questions":
    st.subheader("💬 Questions d'évaluation")
    
    # Show progress
    progress = len(st.session_state.answers) / 5
    st.progress(progress)
    st.write(f"Question {len(st.session_state.answers) + 1}/5")
    
    # Display consultation info
    if st.session_state.consultation_data:
        with st.expander("Voir vos réponses précédentes"):
            for i, (q, a) in enumerate(zip(st.session_state.questions_asked, st.session_state.answers)):
                st.write(f"**Q{i+1}:** {q}")
                st.write(f"**R:** {a.get('answer', '')}")
                st.divider()
    
    # Current question
    current_question = st.session_state.consultation_data.get("question")
    
    if current_question:
        st.info(f"**Question :** {current_question}")
        
        with st.form("answer_form"):
            answer = st.text_input("Votre réponse:", key="answer_input")
            submitted = st.form_submit_button("Répondre")
            
            if submitted and answer:
                submit_answer(answer)
    else:
        st.success("✅ Toutes les questions ont été répondues!")
        st.rerun()

# Step 3: Physician Review
elif st.session_state.step == "physician_review":
    st.subheader("👨‍⚕️ Revue Médicale")
    
    data = st.session_state.consultation_data
    
    # Display summary for physician
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### 📊 Synthèse Clinique")
        st.write(data.get("diagnostic_summary", "En cours..."))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("### 💊 Recommandation Intermédiaire")
        st.write(data.get("interim_care", "En cours..."))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Questions and answers summary
    with st.expander("Voir les questions et réponses du patient"):
        for i, (q, a) in enumerate(zip(st.session_state.questions_asked, st.session_state.answers)):
            st.write(f"**Q{i+1}:** {q}")
            st.write(f"**R:** {a.get('answer', '')}")
            st.divider()
    
    st.markdown("---")
    
    # Physician input form
    st.markdown("### ✍️ Avis du Médecin Traitant")
    
    with st.form("physician_form"):
        treatment = st.text_area(
            "Traitement ou conduite à tenir",
            placeholder="Exemple: Repos, paracétamol 500mg 3x/jour, consultation de contrôle dans 48h...",
            height=100
        )
        
        notes = st.text_area(
            "Notes complémentaires",
            placeholder="Observations supplémentaires, précautions, etc.",
            height=100
        )
        
        submitted = st.form_submit_button("Valider et Générer le Rapport")
        
        if submitted:
            if treatment:
                submit_physician_review(treatment, notes)
            else:
                st.warning("Veuillez indiquer un traitement ou une conduite à tenir")

# Step 4: Final Report
elif st.session_state.step == "report":
    st.subheader("📄 Rapport Final")
    
    report_data = load_report()
    
    if report_data:
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        
        # Display report content
        st.markdown(report_data.get("report", ""))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download button
        st.download_button(
            label="📥 Télécharger le rapport (PDF)",
            data=report_data.get("report", ""),
            file_name=f"rapport_medical_{st.session_state.thread_id}.txt",
            mime="text/plain"
        )
        
        # New consultation button
        if st.button("🔄 Nouvelle Consultation"):
            for key in ["thread_id", "step", "questions_asked", "answers", "consultation_data"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    else:
        st.error("Impossible de charger le rapport")

# Sidebar
with st.sidebar:
    st.markdown("### ℹ️ Information")
    st.markdown("""
    **Système Multi-Agents Médical**
    
    Agents:
    - 🎯 **Superviseur** : Orchestre le workflow
    - 💬 **Agent Diagnostic** : Pose 5 questions
    - 👨‍⚕️ **Revue Médecin** : Intervention humaine
    - 📋 **Agent Rapport** : Génère rapport final
    
    **Technologies:**
    - LangGraph pour le workflow
    - FastAPI pour l'API
    - MCP pour les outils
    - Streamlit pour l'interface
    """)
    
    if st.session_state.thread_id:
        st.markdown("---")
        st.markdown(f"**Session ID:** `{st.session_state.thread_id[:8]}...`")
        st.markdown(f"**Statut:** {st.session_state.step}")