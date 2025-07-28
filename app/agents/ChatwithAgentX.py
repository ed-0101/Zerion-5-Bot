# File: app/agents/ChatwithAgentX.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.ollama_rag_engine_v2 import get_qa_chain

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

qa_chain = get_qa_chain()

@router.post("/agentx/chat")
def chat_with_agentx(req: ChatRequest):
    response = qa_chain.invoke({"query": req.message})
    return {"response": response}
