# File: app/agents/agentX_full_planner.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Request
from app.agents import a1_ticketing, a2_hotel_food, a3_local_travel, a4_security

router = APIRouter()

class FullTripRequest(BaseModel):
    name: str
    origin: str
    destination: str
    travel_date: str
    return_date: Optional[str] = None
    stay_dates: List[str]
    places_to_visit: List[str]

@router.post("/plan/full_trip")
def plan_full_trip(request: FullTripRequest):
    
    # Agent1: Book Ticket
    ticket_payload = a1_ticketing.TicketRequest(
        name=request.name,
        origin=request.origin,
        destination=request.destination,
        travel_date=request.travel_date,
        return_date=request.return_date
    )
    ticket_info = a1_ticketing.book_ticket(ticket_payload)

    # Agent2: Hotel and Food
    hotel_payload = a2_hotel_food.HotelFoodRequest(
        name=request.name,
        city=request.destination,
        stay_dates=request.stay_dates
    )
    hotel_food = a2_hotel_food.book_hotel_and_food(hotel_payload)

    # Agent3: Local Travel
    travel_payload = a3_local_travel.TravelRequest(
        name=request.name,
        city=request.destination,
        places_to_visit=request.places_to_visit
    )
    local_travel = a3_local_travel.book_local_transport(travel_payload)

    # Agent4: Security
    security_payload = a4_security.SecurityRequest(
        name=request.name,
        origin=request.origin,
        destination=request.destination,
        travel_dates=request.stay_dates
    )
    security = a4_security.security_briefing(security_payload)

    return {
        "ticket_info": ticket_info,
        "hotel_food": hotel_food,
        "local_travel": local_travel,
        "security": security
    }
