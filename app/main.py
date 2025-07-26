# === STEP 1: FastAPI Boilerplate ===
# File: app/main.py
from app.utils.rag_engine import initialize_rag_engine
from fastapi import FastAPI
from app.agents import (
    a1_ticketing,
    a2_hotel_food,
    a3_local_travel,
    a4_security,
    agentX
)

app = FastAPI(title="Zerion-5 Travel AI")

# Initialize RAG Engine
rag_engine = initialize_rag_engine()

# Include agent routes
app.include_router(a1_ticketing.router, prefix="/agent1", tags=["Ticket Booking"])
app.include_router(a2_hotel_food.router, prefix="/agent2", tags=["Hotel & Food"])
app.include_router(a3_local_travel.router, prefix="/agent3", tags=["Local Travel"])
app.include_router(a4_security.router, prefix="/agent4", tags=["Security"])
app.include_router(agentX.router, prefix="/agentX", tags=["Full Planner"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Zerion-5 Interstellar Travel AI System!"}
