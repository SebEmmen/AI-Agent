from services.google_places import search_sport_locations

locations = search_sport_locations(
    location="Den Haag",
    sport_preference="fitness",
    max_results=5
)

for place in locations:
    print(place["name"], "-", place["rating"])