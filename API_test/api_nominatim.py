import requests

def is_in_venice(location_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": location_name,
        "format": "json",
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyApp/1.0; +http://example.com)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        # Check if the request was successful
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            return False
        
        # Check if the response has content
        if not response.content:
            print("Error: Received empty response")
            return False
        
        data = response.json()
        
        for place in data:
            address = place.get("address", {})
            # Check if the city or county field has Venice or Venezia
            if address.get("city") == "Venice" or address.get("city") == "Venezia" or \
               address.get("county") == "Venice" or address.get("county") == "Venezia":
                return True
        return False
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False
    except ValueError:
        print("Error: Could not decode JSON response")
        return False

# Parse list of places from external dictionary

# For each place, check if the place is in Venice.
print(is_in_venice("Noale"))  # Should return True if it's in Venice
# If true, return the co-ordinates

# city, (latitude, longitude), [index1, index2, ... ]
# Format
#   {"name": {"coords":(la,ln),"indices":[]}, "wikidata":"True", "nominatim":"False", "Last one":"False"}
# 1 for nominatim, 2 for wikidata, 3 for 