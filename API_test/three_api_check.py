import requests
from api_wikidata import wikidata_is_in_venice

# Check Nominatim
def nominatim_is_in_venice(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location_name,
        "format": "json",
        "addressdetails": 1
    }
    headers = { "User-Agent": "Mozilla/5.0 (compatible; MyApp/1.0; +http://example.com)" }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200 or not response.content:
            return None
        
        data = response.json()
        for place in data:
            address = place.get("address", {})
            if address.get("city") in ["Venice", "Venezia"] or address.get("county") in ["Venice", "Venezia"]:
                return (place.get("lat"), place.get("lon"))
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

# Check Geodata
def geodata_is_in_venice(location_name):
    url = "http://api.geonames.org/searchJSON"
    params = {"q": location_name, "maxRows": 10, "username": "cklplanet"}
    try:
        response = requests.get(url, params=params)
        for place in response.json().get('geonames', []):
            id = place['geonameId']
            hierarchy_url = "http://api.geonames.org/hierarchyJSON"
            hierarchy_params = {"geonameId": id, "username": "cklplanet"}
            response_city = requests.get(hierarchy_url, params=hierarchy_params)
            venice_id = 6542284  # Venice city geoname ID
            if any(level.get("geonameId") == venice_id for level in response_city.json().get("geonames", [])):
                return (place['lat'], place['lng'])
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

# Main script

# place = "Venice" # 3 pass
# place = "Murano" # 3 pass
# place = "San Francesco della Vigna" # 3 pass
# place = "Giudecca" # 3 pass
# place = "Rialto Bridge" # 1 fail: wikidata
# # place = "Noale" # 2 fail: wikidata, geodata
def pipeline_check(place):

    results = {
        "name": place,
        "coords": None,
        "sources": {
            "nominatim": False,
            "geodata": False,
            "wikidata": False
        }
    }

    # Check each source
    nominatim_coords = nominatim_is_in_venice(place)
    if nominatim_coords:
        results["coords"] = nominatim_coords
        results["sources"]["nominatim"] = True
        print(f'name: {place}, coords: ({nominatim_coords[0]}, {nominatim_coords[1]}), source: nominatim')

    geodata_coords = geodata_is_in_venice(place)
    if geodata_coords:
        results["coords"] = geodata_coords
        results["sources"]["geodata"] = True
        print(f'name: {place}, coords: ({geodata_coords[0]}, {geodata_coords[1]}), source: geodata')

    # wikidata_coords = wikidata_is_in_venice(place)
    # if wikidata_coords:
    #     results["coords"] = wikidata_coords[0]['coordinates']
    #     results["sources"]["wikidata"] = True
    #     print(f'name: {place}, coords: ({wikidata_coords[0]["coordinates"]}), source: wikidata')
    wikidata_coords = wikidata_is_in_venice(place)
    if wikidata_coords:
        results["coords"] = wikidata_coords
        results["sources"]["wikidata"] = True
        print(f'name: {place}, coords: ({wikidata_coords[0]}, {wikidata_coords[1]}), source: wikidata')

# pipeline_check("Africa")
# print(results)
