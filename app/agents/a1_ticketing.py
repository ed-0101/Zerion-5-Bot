# File: app/agents/a1_ticketing.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.file_loader import json_data
import random

router = APIRouter()

class TicketRequest(BaseModel):
    name: str
    origin: str
    destination: str
    travel_date: str
    return_date: str | None = None

@router.post("/book")
def book_ticket(request: TicketRequest):
    cities_info = json_data.get("cities_and_countries.json", [])

    # Correctly extract nested city names
    destinations = [city["name"] for country in cities_info for city in country.get("cities", [])]

    if request.destination not in destinations:
        return {"error": f"Destination '{request.destination}' not found in known Zerion-5 cities."}

    ticket_id = f"Z5-TICKET-{random.randint(100000, 999999)}"
    return {
        "ticket_id": ticket_id,
        "name": request.name,
        "from": request.origin,
        "to": request.destination,
        "departure": request.travel_date,
        "return": request.return_date or "Open",
        "status": "Confirmed"
    }
