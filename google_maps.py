import urllib.parse

# Dictionary of building codes with their coordinates
BUILDING_COORDINATES = {
    "A": {"lat": 36.67497601961465, "lng": -121.66600192296555, "name": "Building A - Library/Learning Resource Center"},
    "B": {"lat": 36.674594109144145, "lng": -121.66528974254899, "name": "Building B - Student Services"},
    "C": {"lat": 36.67408990462679, "lng": -121.6658739129372, "name": "Building C - Student Center"},
    "D": {"lat": 36.67360987241185, "lng": -121.66522682209852, "name": "Building D - College Administration North"},
    "E": {"lat": 36.673267525337444, "lng": -121.66518277607484, "name": "Building E - College Administration South"},
    "F": {"lat": 36.67311540426318, "lng": -121.66584630911161, "name": "Building F - Weightroom"},
    "G": {"lat": 36.673067058576976, "lng": -121.66612717101663, "name": "Building G - Auxiliary Gym"},
    "H": {"lat": 36.67294327101412, "lng": -121.66647445548287, "name": "Building H - Main Gym"},
    "J": {"lat": 36.672849972701066, "lng": -121.66766890557878, "name": "Building J - Visual Arts"},
    "K": {"lat": 36.673321970596234, "lng": -121.66756228611722, "name": "Building K - Nursing"},
    "L": {"lat": 36.67361813538571, "lng": -121.66849285041586, "name": "Building L - Maintenance Building"},
    "M": {"lat": 36.67381185515153, "lng": -121.66774543891108, "name": "Building M - Child Development"},
    "N": {"lat": 36.6739493219602, "lng": -121.66701075185577, "name": "Building N - STEM Center"},
    "O": {"lat": 36.67288467675031, "lng": -121.66504135458179, "name": "Building O - Welcome Kiosk"},
    "P": {"lat": 36.67329479507463, "lng": -121.67093696927407, "name": "Building P - Planetarium"},
    "S": {"lat": 36.67341935072183, "lng": -121.6666138266549, "name": "Building S - STEM Center"}
}

def get_building_coordinates(building_code):
    """
    Get latitude and longitude coordinates for a given building code.
    
    Args:
        building_code (str): The building code (e.g., 'A', 'B', 'C')
    
    Returns:
        tuple: (latitude, longitude) if building code exists, None otherwise
    """
    building_code = building_code.upper().strip()
    
    if building_code in BUILDING_COORDINATES:
        coords = BUILDING_COORDINATES[building_code]
        return coords["lat"], coords["lng"]
    else:
        return None

def get_google_maps_directions_link(destination_lat, destination_lng, origin_address="", mode="walking"):
    base_url = "https://www.google.com/maps/dir/?"
    params = {
        "api": "1",
        "destination": f"{destination_lat},{destination_lng}",
        "travelmode": mode
    }
    if origin_address:
        params["origin"] = origin_address

    query_string = urllib.parse.urlencode(params)
    return base_url + query_string

def get_building_directions_link(building_code, origin_address="", mode="walking"):
    """
    Get Google Maps directions link to a building by building code.
    This function combines coordinate lookup and directions link generation.
    
    Args:
        building_code (str): The building code (e.g., 'A', 'B', 'C')
        origin_address (str): Starting address (optional)
        mode (str): Travel mode ('walking', 'driving', 'transit', 'bicycling')
    
    Returns:
        str: Google Maps directions URL, or None if building code not found
    """
    building_code = building_code.upper().strip()
    
    if building_code in BUILDING_COORDINATES:
        coords = BUILDING_COORDINATES[building_code]
        destination_lat = coords["lat"]
        destination_lng = coords["lng"]
        
        base_url = "https://www.google.com/maps/dir/?"
        params = {
            "api": "1",
            "destination": f"{destination_lat},{destination_lng}",
            "travelmode": mode
        }
        if origin_address:
            params["origin"] = origin_address

        query_string = urllib.parse.urlencode(params)
        return base_url + query_string
    else:
        return None

def get_directions_to_building(building_code, origin_address="", mode="walking"):
    """
    Get Google Maps directions link to a specific building by building code.
    (This is an alias for get_building_directions_link for backward compatibility)
    
    Args:
        building_code (str): The building code (e.g., 'A', 'B', 'C')
        origin_address (str): Starting address (optional)
        mode (str): Travel mode ('walking', 'driving', 'transit', 'bicycling')
    
    Returns:
        str: Google Maps directions URL, or None if building code not found
    """
    return get_building_directions_link(building_code, origin_address, mode)

# Example usage:
# # Get coordinates for Building A
# coords = get_building_coordinates('A')
# print(f"Building A coordinates: {coords}")
# 
# # Get directions to Building C (using combined function)
# link = get_building_directions_link('C', origin_address="Salinas, CA", mode="driving")
# print(f"Directions to Building C: {link}")
# 
# # Direct usage with coordinates
# destination_lat = 37.4220936
# destination_lng = -122.0840897
# link = get_google_maps_directions_link(destination_lat, destination_lng, "Monterey, CA", mode="walking")
# print(link)
