"""MCP (Model Context Protocol) Server"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

app = FastAPI(title="MCP Server for Medical Agents", version="1.0.0")

# Tool registry
TOOLS = {
    "get_medical_guidelines": {
        "description": "Get medical guidelines for common symptoms",
        "parameters": {"symptom": "string"}
    },
    "check_medication_interaction": {
        "description": "Check interactions between medications",
        "parameters": {"medications": "list"}
    },
    "validate_symptom_severity": {
        "description": "Validate severity of symptoms",
        "parameters": {"symptom": "string", "severity": "integer"}
    }
}


class ToolCall(BaseModel):
    parameters: Dict[str, Any]


@app.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    return {"tools": TOOLS}


@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, call: ToolCall):
    """Execute an MCP tool"""
    
    if tool_name == "get_medical_guidelines":
        symptom = call.parameters.get("symptom", "")
        guidelines = get_medical_guidelines_mcp(symptom)
        return {"result": guidelines}
    
    elif tool_name == "check_medication_interaction":
        medications = call.parameters.get("medications", [])
        interactions = check_medication_interactions(medications)
        return {"result": interactions}
    
    elif tool_name == "validate_symptom_severity":
        symptom = call.parameters.get("symptom", "")
        severity = call.parameters.get("severity", 0)
        validation = validate_symptom_severity(symptom, severity)
        return {"result": validation}
    
    else:
        raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")


def get_medical_guidelines_mcp(symptom: str) -> str:
    """Medical guidelines database"""
    guidelines = {
        "fièvre": "Température > 38°C. Recommandations: repos, hydratation, paracétamol. Consulter si > 39.5°C ou > 3 jours.",
        "toux": "Toux sèche ou grasse. Recommandations: hydratation, miel, éviter irritants. Consulter si persistante > 2 semaines.",
        "douleur thoracique": "URGENCE MÉDICALE. Appeler immédiatement les urgences.",
        "céphalée": "Mal de tête. Repos dans pièce obscure, hydratation. Consulter si inhabituelle ou sévère.",
        "dyspnée": "Difficulté respiratoire. Nécessite une évaluation médicale rapide.",
    }
    return guidelines.get(symptom.lower(), "Consulter un médecin pour évaluation.")


def check_medication_interactions(medications: list) -> str:
    """Check medication interactions"""
    common_interactions = {
        ("aspirine", "ibuprofène"): "Risque accru d'effets secondaires gastro-intestinaux",
        ("paracétamol", "alcool"): "Risque de toxicité hépatique",
    }
    
    for med_pair, interaction in common_interactions.items():
        if all(med.lower() in [m.lower() for m in medications] for med in med_pair):
            return f"Interaction détectée: {interaction}"
    
    return "Aucune interaction majeure détectée"


def validate_symptom_severity(symptom: str, severity: int) -> dict:
    """Validate severity level"""
    if severity < 1 or severity > 10:
        return {"valid": False, "message": "La sévérité doit être entre 1 et 10"}
    
    if severity >= 8:
        return {"valid": True, "alert": "Sévérité élevée - Consultation recommandée"}
    elif severity >= 5:
        return {"valid": True, "alert": "Sévérité modérée - Surveiller et consulter si persistance"}
    else:
        return {"valid": True, "alert": "Sévérité légère - Repos et surveillance"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)