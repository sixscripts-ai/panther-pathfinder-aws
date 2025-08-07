import urllib.parse

# Dictionary of building codes with their coordinates
BUILDING_COORDINATES = {
    "A": {"lat": 36.67497601961465, "lng": -121.66600192296555, "name": "Hartnell College Library"},
    "B": {"lat": 36.674594109144145, "lng": -121.66528974254899, "name": "Student Services"},
    "C": {"lat": 36.67408990462679, "lng": -121.6658739129372, "name": "Hartnell College Bookstore"},
    "D": {"lat": 36.67360987241185, "lng": -121.66522682209852, "name": "College Administration North"},
    "E": {"lat": 36.673267525337444, "lng": -121.66518277607484, "name": "College Administration South"},
    "F": {"lat": 36.67311540426318, "lng": -121.66584630911161, "name": "Hartnell College Gymnasium"},
    "G": {"lat": 36.673067058576976, "lng": -121.66612717101663, "name": "Hartnell College Gymnasium"},
    "H": {"lat": 36.67294327101412, "lng": -121.66647445548287, "name": "Hartnell College Gymnasium"},
    "J": {"lat": 36.672849972701066, "lng": -121.66766890557878, "name": "Visual Arts"},
    "K": {"lat": 36.673321970596234, "lng": -121.66756228611722, "name": "The Western Stage"},
    "L": {"lat": 36.67361813538571, "lng": -121.66849285041586, "name": "Maintenance, Operations and Receiving"},
    "M": {"lat": 36.67381185515153, "lng": -121.66774543891108, "name": "Hartnell College Child Development Center"},
    "N": {"lat": 36.6739493219602, "lng": -121.66701075185577, "name": "Merrill Hall"},
    "O": {"lat": 36.67288467675031, "lng": -121.66504135458179, "name": "Nursing and Health Sciences Center"},
    "S": {"lat": 36.67341935072183, "lng": -121.6666138266549, "name": "STEM Building, Hartnell College"}
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

def get_building_code_by_name(building_name):
    """
    Find the building code for a given building name.
    
    Args:
        building_name (str): The building name (e.g., 'Hartnell College Library')
    
    Returns:
        str: Building code if name is found, None otherwise
    """
    building_name = building_name.strip()
    
    # Search through all buildings to find matching name (case-insensitive)
    for code, data in BUILDING_COORDINATES.items():
        if data["name"].lower() == building_name.lower():
            return code
    
    # If exact match not found, try partial matching
    for code, data in BUILDING_COORDINATES.items():
        if building_name.lower() in data["name"].lower():
            return code
    
    return None

def get_google_maps_directions_link(destination_lat, destination_lng, origin_address="", mode="walking"):
    base_url = "https://www.google.com/maps/dir/?"
    params = {
        "api": "1",
        "destination": f"{destination_lat},{destination_lng}",
        "travelmode": mode
    }
    if origin_address:
        # Check if origin_address is a building code or a regular address
        origin_coords = get_building_coordinates(origin_address)
        if origin_coords:
            # It's a building code, use coordinates
            origin_lat, origin_lng = origin_coords
            params["origin"] = f"{origin_lat},{origin_lng}"
        else:
            # It's a regular address string
            params["origin"] = origin_address

    query_string = urllib.parse.urlencode(params)
    return base_url + query_string

def get_building_directions_link(building_code, origin_address="", mode="walking"):
    """
    Get Google Maps directions link to a building by building code.
    This function combines coordinate lookup and directions link generation.
    
    Args:
        building_code (str): The building code (e.g., 'A', 'B', 'C')
        origin_address (str): Starting address or building code (optional)
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
            # Check if origin_address is a building code or a regular address
            origin_coords = get_building_coordinates(origin_address)
            if origin_coords:
                # It's a building code, use coordinates
                origin_lat, origin_lng = origin_coords
                params["origin"] = f"{origin_lat},{origin_lng}"
            else:
                # It's a regular address string
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

def get_google_maps_directions_link_to_query(destination_query, origin_query="", mode="walking"):
    """
    Get Google Maps directions link using text queries instead of coordinates.
    
    Args:
        destination_query (str): The destination search query
        origin_query (str): The origin search query (optional)
        mode (str): Travel mode ('walking', 'driving', 'transit', 'bicycling')
    
    Returns:
        str: Google Maps directions URL
    """
    base_url = "https://www.google.com/maps/dir/?"
    params = {
        "api": "1",
        "destination": destination_query,
        "travelmode": mode
    }
    if origin_query:
        params["origin"] = origin_query

    query_string = urllib.parse.urlencode(params)
    return base_url + query_string

def get_building_directions_link_by_name(destination_code, origin_code="", mode="walking"):
    """
    Get Google Maps directions link using building codes but querying by building names.
    
    Args:
        destination_code (str): The destination building code (e.g., 'A', 'B', 'C')
        origin_code (str): The origin building code (optional)
        mode (str): Travel mode ('walking', 'driving', 'transit', 'bicycling')
    
    Returns:
        str: Google Maps directions URL, or None if building code not found
    """
    destination_code = destination_code.upper().strip()
    
    # Get destination building name
    if destination_code not in BUILDING_COORDINATES:
        return None
    
    destination_query = BUILDING_COORDINATES[destination_code]["name"]
    
    # Get origin building name if provided
    origin_query = ""
    if origin_code:
        origin_code = origin_code.upper().strip()
        if origin_code in BUILDING_COORDINATES:
            origin_query = BUILDING_COORDINATES[origin_code]["name"]
        else:
            # If not a valid building code, treat as regular address
            origin_query = origin_code
    
    return get_google_maps_directions_link_to_query(destination_query, origin_query, mode)

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
