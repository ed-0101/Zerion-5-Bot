# File: app/agents/agent3_local_travel.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.utils.file_loader import json_data
from app.utils.rag_engine import query_documents, initialize_rag_engine

router = APIRouter()

class TravelRequest(BaseModel):
    name: str
    city: str
    places_to_visit: List[str]

@router.post("/book")
def book_local_transport(request: TravelRequest):
    travel_info = json_data.get("local_travel.json", [])

    # Filter routes that originate from the requested city
    city_routes = [item for item in travel_info if item["from"] == request.city]

    if not city_routes:
        return {"error": f"No local travel data available for city: {request.city}"}

    # Unique travel modes available
    available_modes = list(set(item["mode"] for item in city_routes))

    # Build route descriptions
    routes = []
    for place in request.places_to_visit:
        route = next((r for r in city_routes if r["to"] == place), None)
        if route:
            routes.append(
                f"{request.city} to {place} via {route['mode']} "
                f"(Duration: {route['duration_minutes']} mins, Price: ${route['price']})"
            )
        else:
            routes.append(f"No direct route from {request.city} to {place}.")

    # RAG query
    rag_result = query_documents(
        collection=initialize_rag_engine(),
        query=f"Describe local travel options in {request.city} on Zerion-5",
        top_k=2
    )
    travel_context = rag_result.get("documents", [])

    return {
        "message": f"Local travel booked for {request.name} in {request.city}.",
        "modes": available_modes,
        "routes": routes,
        "info": travel_context
    }
