# === STEP 1: FastAPI Boilerplate ===
# File: app/main.py
from app.utils.rag_engine import initialize_rag_engine
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.utils.ollama_rag_engine_v2 import get_qa_chain
from app.agents import (
    a1_ticketing,
    a2_hotel_food,
    a3_local_travel,
    a4_security,
    agentX,
    ChatwithAgentX
)

app = FastAPI(title="Zerion-5 Travel AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

qa_chain = get_qa_chain()
class ChatQuery(BaseModel):
    question: str


# Initialize RAG Engine
rag_engine = initialize_rag_engine()

# Include agent routes
app.include_router(a1_ticketing.router, prefix="/agent1", tags=["Ticket Booking"])
app.include_router(a2_hotel_food.router, prefix="/agent2", tags=["Hotel & Food"])
app.include_router(a3_local_travel.router, prefix="/agent3", tags=["Local Travel"])
app.include_router(a4_security.router, prefix="/agent4", tags=["Security"])
# app.include_router(agentX.router, prefix="/agentX", tags=["Full Planner"])
app.include_router(ChatwithAgentX.router, prefix="/agentx", tags=["Lets Chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Zerion-5 Interstellar Travel AI System!"}

# === STEP 2: AgentX Chat Endpoint ===
@app.post("/agentx/chat")
async def chat_with_agentx(request: ChatQuery):
    try:
        response = qa_chain({"query": request.question})
        return {
            "response": response["result"],
            "sources": [doc.metadata.get("source") for doc in response["source_documents"]]
        }
    except Exception as e:
        return {"error": str(e)}


