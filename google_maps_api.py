import googlemaps
from typing import Optional

GOOGLE_API_KEY = "AIzaSyC0qTGv7tBQbkIhuwBAtG2bUiswc5rbZXQ"
HARTNELL_MAIN_CAMPUS = {
    "lat": 36.677737,   # Approx. lat of Hartnell College
    "lng": -121.658638  # Approx. long of Hartnell College
}

def search_hartnell_building(building_query: str) -> Optional[dict]:
    """
    Searches for a building on Hartnell College's main campus using Google Places API.

    Args:
        building_query (str): Name or description of the building to find.

    Returns:
        dict: Dictionary with name, address, and coordinates, or None if not found.
    """
    gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

    response = gmaps.places(
        query=f"{building_query}, Hartnell College",
        location=(HARTNELL_MAIN_CAMPUS['lat'], HARTNELL_MAIN_CAMPUS['lng']),
        radius=500
    )

    if response.get("status") != "OK" or not response.get("results"):
        return None

    top_result = response["results"][0]
    return {
        "name": top_result.get("name"),
        "address": top_result.get("formatted_address"),
        "location": top_result["geometry"]["location"]
    }

print(search_hartnell_building("Building A"))
