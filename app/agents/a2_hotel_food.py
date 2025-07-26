# File: app/agents/agent2_hotel_food.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.utils.file_loader import csv_data
from app.utils.rag_engine import query_documents, initialize_rag_engine

router = APIRouter()

class HotelFoodRequest(BaseModel):
    name: str
    city: str
    stay_dates: List[str]  # ["start_date", "end_date"]

@router.post("/book")
def book_hotel_and_food(request: HotelFoodRequest):
    df = csv_data.get("hotel_directory.csv")
    if df is None:
        return {"error": "Hotel directory data not available."}

    city_hotels = df[df["city"].str.lower() == request.city.lower()]
    if city_hotels.empty:
        return {"error": f"No hotels found in city: {request.city}"}

    top_hotels = city_hotels.sort_values(by="star_rating", ascending=False).head(3)
    hotel_list = top_hotels[["hotel_name", "star_rating", "city"]].to_dict(orient="records")

    food_query = f"What are the best traditional dishes to try in {request.city} on Zerion-5?"
    rag_result = query_documents(
        collection=initialize_rag_engine(),
        query=food_query,
        top_k=2
    )
    food_info = rag_result["documents"] if rag_result and "documents" in rag_result else []

    return {
        "message": f"Hotel and food booking confirmed for {request.name} in {request.city} from {request.stay_dates[0]} to {request.stay_dates[1]}",
        "hotels": hotel_list,
        "food_suggestions": [f"Try local delicacies and ask for chef specials in {request.city} restaurants."],
        "info": food_info
    }
