import os
import requests
from dotenv import load_dotenv

from services.api_usage import (
    can_make_google_places_call,
    register_google_places_call,
)

load_dotenv()

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"


def search_sport_locations(
    location: str,
    sport_preference: str = "gym",
    max_results: int = 5
) -> list[dict]:
    """
    Zoekt sportlocaties via Google Places API (New).
    Bijvoorbeeld: fitness near Den Haag.
    """

    if not GOOGLE_PLACES_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY ontbreekt in je .env bestand.")

    if not can_make_google_places_call():
        raise RuntimeError("Dagelijkse Google Places API-limiet bereikt.")

    query = f"{sport_preference} near {location}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
        "X-Goog-FieldMask": (
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.userRatingCount,"
            "places.location,"
            "places.currentOpeningHours"
        ),
    }

    body = {
        "textQuery": query,
        "maxResultCount": max_results
    }

    response = requests.post(
        PLACES_TEXT_SEARCH_URL,
        headers=headers,
        json=body,
        timeout=10
    )

    response.raise_for_status()

    register_google_places_call()

    data = response.json()
    places = data.get("places", [])

    results = []

    for place in places:
        results.append({
            "name": place.get("displayName", {}).get("text"),
            "address": place.get("formattedAddress"),
            "rating": place.get("rating"),
            "user_rating_count": place.get("userRatingCount"),
            "latitude": place.get("location", {}).get("latitude"),
            "longitude": place.get("location", {}).get("longitude"),
            "opening_hours": place.get("currentOpeningHours", {}).get("weekdayDescriptions", [])
        })

    return results


def choose_best_locations(
    locations: list[dict],
    min_rating: float = 4.0
) -> list[dict]:
    """
    Filtert sportlocaties op minimale rating en sorteert van hoog naar laag.
    """

    filtered_locations = [
        location for location in locations
        if location.get("rating") is not None and location["rating"] >= min_rating
    ]

    return sorted(
        filtered_locations,
        key=lambda location: location["rating"],
        reverse=True
    )


def google_places_tool(
    user_location: str,
    preference: str = "gym"
) -> list[dict]:
    """
    Deze functie kan later als tool gebruikt worden in LangGraph.
    """

    locations = search_sport_locations(
        location=user_location,
        sport_preference=preference,
        max_results=5
    )

    return choose_best_locations(locations)