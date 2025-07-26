# File: app/agents/agent4_security.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.utils.rag_engine import query_documents, initialize_rag_engine

router = APIRouter()

class SecurityRequest(BaseModel):
    name: str
    origin: str
    destination: str
    travel_dates: Optional[list] = None

@router.post("/brief")
def security_briefing(request: SecurityRequest):
    query = f"What are the security protocols for travelers from Earth to {request.destination} on Zerion-5?"

    rag_result = query_documents(
        collection=initialize_rag_engine(),
        query=query,
        top_k=3
    )

    context = rag_result["documents"] if rag_result and "documents" in rag_result else []

    return {
        "message": f"Security protocols briefing generated for {request.name} traveling to {request.destination}.",
        "origin": request.origin,
        "destination": request.destination,
        "info": context
    }