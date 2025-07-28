# File: app/agents/agentX.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from transformers import pipeline

from app.utils.rag_engine import initialize_rag_engine, query_documents
from app.agents.a1_ticketing import book_ticket, TicketRequest
from app.agents.a2_hotel_food import book_hotel_and_food, HotelRequest
from app.agents.a3_local_travel import book_local_transport, TravelRequest
from app.agents.a4_security import security_briefing, SecurityRequest

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[str]] = []

class ChatResponse(BaseModel):
    reply: str
    next_action: Optional[str] = None
    required_fields: Optional[List[str]] = None
    payload: Optional[dict] = None

qa_pipeline = pipeline("question-answering")

def extract_field(question: str, context: str) -> str:
    try:
        return qa_pipeline({"question": question, "context": context})["answer"]
    except:
        return ""

@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(request: ChatRequest):
    user_message = request.message
    collection = initialize_rag_engine()
    rag_result = query_documents(collection, query=user_message, top_k=2)
    context_docs = rag_result.get("documents", [""])
    context = " ".join(doc if isinstance(doc, str) else " ".join(doc) for doc in context_docs)

    # Extract common fields
    name = extract_field("What is traveler name?", user_message)
    origin = extract_field("What is the from city or origin city?", user_message)
    destination = extract_field("What is the to city or destination city?", user_message)
    travel_date = extract_field("What is the travel start date?", user_message)
    return_date = extract_field("What is the travel return date?", user_message)
    city = extract_field("Which city is the hotel in?", user_message)
    stay_dates_raw = extract_field("What are the stay dates?", user_message)
    stay_dates = [d.strip() for d in stay_dates_raw.split("to")] if "to" in stay_dates_raw else [stay_dates_raw]
    place = extract_field("What place do you want to visit?", user_message)

    payloads = {}
    reply_parts = []

    # Book ticket
    if origin and destination and travel_date:
        ticket_req = TicketRequest(
            name=name,
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            return_date=return_date or None
        )
        payloads["ticket"] = book_ticket(ticket_req)
        reply_parts.append("Ticket booked successfully.")

    # Book hotel
    if city and stay_dates:
        hotel_req = HotelRequest(
            name=name,
            city=city,
            starting_date=travel_date,
            ending_date=return_date or travel_date  # Use travel_date if return_date is not
        )
        payloads["hotel"] = book_hotel_and_food(hotel_req)
        reply_parts.append("Hotel booked successfully.")

    # Local transport
    if city and place:
        travel_req = TravelRequest(
            name=name,
            city=city,
            places_to_visit=[place]
        )
        payloads["local_travel"] = book_local_transport(travel_req)
        reply_parts.append("Local transport arranged.")

    # Security briefing
    if origin and destination and travel_date and return_date and place:
        sec_req = SecurityRequest(
            name=name,
            origin=origin,
            destination=destination,
            travel_date=travel_date,
            return_date=return_date,
            stay_dates=[travel_date, return_date],
            places_to_visit=[place]
        )
        payloads["security"] = security_briefing(sec_req)
        reply_parts.append("Security clearance initiated.")

    if not reply_parts:
        return ChatResponse(
            reply="I couldn't determine what to do. Please provide more travel details.",
            payload={"context": context_docs}
        )

    return ChatResponse(
        reply="\n".join(reply_parts),
        payload=payloads
    )
