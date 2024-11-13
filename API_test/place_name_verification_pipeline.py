import json
import os
from three_api_check import nominatim_is_in_venice, geodata_is_in_venice, wikidata_is_in_venice

# Define the path to the JSON file
json_file_path = os.path.join(os.getcwd(), "example_place_extraction_results.json")

# Load the JSON data
try:
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        print("JSON data loaded successfully.")
except FileNotFoundError:
    print(f"File not found at path: {json_file_path}")
    exit()

# Iterate over each place name in the JSON data and get coordinates from each API
results_list = []

for place_group in data.keys():
    place_names = eval(place_group)  # Converting string list to actual list
    
    for place in place_names:
        results = {
            "name": place,
            "coords": None,
            "sources": {
                "nominatim": False,
                "geodata": False,
                "wikidata": False
            }
        }

        # Check Nominatim
        nominatim_coords = nominatim_is_in_venice(place)
        if nominatim_coords:
            results["coords"] = nominatim_coords  # Expecting (lat, lon)
            results["sources"]["nominatim"] = True

        # Check Geodata
        geodata_coords = geodata_is_in_venice(place)
        if geodata_coords:
            results["coords"] = geodata_coords  # Expecting (lat, lon)
            results["sources"]["geodata"] = True

        # # Check Wikidata
        # wikidata_coords = wikidata_is_in_venice(place)  # Each call should process independently
        # if wikidata_coords and "coordinates" in wikidata_coords[0]:
        #     results["coords"] = (
        #         wikidata_coords[0]["coordinates"][0], 
        #         wikidata_coords[0]["coordinates"][1]
        #     )
        #     results["sources"]["wikidata"] = True
        # elif wikidata_coords:
        #     print(f'name: {place}, Wikidata API returned unexpected structure: {wikidata_coords}')
        #     continue  # Move to next place if unexpected structure appears

        # Only print and save the result if at least one API has returned coordinates
        if any(results["sources"].values()):
            print(f'name: {place}, coords: ({results["coords"][0]}, {results["coords"][1]}), sources: {", ".join([key for key, val in results["sources"].items() if val])}')
            results_list.append(results)

# Print or save final results
print("Final Results:", results_list)
