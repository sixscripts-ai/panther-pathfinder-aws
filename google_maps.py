import urllib.parse

def get_google_maps_directions_link(destination_address, origin_address="", mode="walking"):
    base_url = "https://www.google.com/maps/dir/?"
    params = {
        "api": "1",
        "destination": destination_address,
        "travelmode": mode
    }
    if origin_address:
        params["origin"] = origin_address

    query_string = urllib.parse.urlencode(params)
    return base_url + query_string

# Example usage:
# origin = ""
# destination = "1600 Amphitheatre Parkway, Mountain View, CA"
# link = get_google_maps_directions_link(destination, origin, mode="walking")
# print(link)
