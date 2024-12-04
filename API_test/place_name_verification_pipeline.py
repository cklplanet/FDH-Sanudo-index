import json
import os
from three_api_check import nominatim_is_in_venice, geodata_is_in_venice, wikidata_is_in_venice

# Define the path to the JSON file
json_file_path = os.path.join(os.getcwd(), "example_place_extraction_results.json")
output_file_path = os.path.join(os.getcwd(), "data_analysis_results.json") # or data_analysis_results.json

# Load the JSON data
try:
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        print("JSON data loaded successfully.")
except FileNotFoundError:
    print(f"File not found at path: {json_file_path}")
    exit()

# Set to keep track of already processed place names
processed_names = set()
existed_names = set()

# Initialize the results list (if you want to update the file, keep track of previous results)
if os.path.exists(output_file_path):
    with open(output_file_path, "r", encoding="utf-8") as f:
        results_list = json.load(f)
        # Fill the existed_names set with the names already present in the results list
        existed_names = {result["place_name"] for result in results_list}
else:
    results_list = []

# To store results with unique IDs
next_id = len(results_list) + 1

# Calculate total unique places to process
all_place_names = set()
for place_group in data.keys():
    all_place_names.update(eval(place_group))  # Convert string list to an actual list and add to all_place_names

total_places = len(all_place_names)
processed_count = 0

try:
    
  # Iterate over each place name in the JSON data and get coordinates from each API
  for place_group, columns in data.items():
      place_names = eval(place_group)  # Convert string list to actual list
      
      # Combine all place names (including alternative names)
      all_names = set(place_names)  # Ensuring no duplicates within this set
      
      for place in all_names:
          #  Skip already processed place names or "veneziano"
          if place in processed_names or place in existed_names or place == 'veneziano':
              continue

          results = {
              "id": next_id,
              "place_name": place,
              "place_alternative_name": list(all_names - {place}),  # Excluding the main name for alternatives
              "place_index": columns,  # The column index from the JSON data
              "nominatim_coords": None,
              "geodata_coords": None,
              "wikidata_coords": None,
              "nominatim_match": False,
              "geodata_match": False,
              "wikidata_match": False,
              "latitude": None,
              "longitude": None
          }

          # Check Nominatim
          nominatim_coords = nominatim_is_in_venice(place)
          if nominatim_coords:
              results["nominatim_coords"] = nominatim_coords
              results["latitude"], results["longitude"] = nominatim_coords
              results["nominatim_match"] = True

          # Check Geodata
          geodata_coords = geodata_is_in_venice(place)
          if geodata_coords:
              results["geodata_coords"] = geodata_coords
              results["latitude"], results["longitude"] = geodata_coords
              results["geodata_match"] = True

          # Check Wikidata
          wikidata_coords = wikidata_is_in_venice(place)
          if wikidata_coords:
              results["wikidata_coords"] = wikidata_coords
              results["latitude"], results["longitude"] = wikidata_coords
              results["wikidata_match"] = True

          # Check if the APIs return the same coordinates
          coords = [nominatim_coords, geodata_coords, wikidata_coords]
          unique_coords = {coord for coord in coords if coord}
          results["agreement_count"] = len(unique_coords)

          processed_names.add(place)

          # Only add to the results list if we found coordinates for the place
          if results["latitude"] is not None and results["longitude"] is not None:
              results_list.append(results)
              next_id += 1  # Increment for the next unique id

          
          # Update and display progress in the same line, ensuring the line is fully cleared
          processed_count += 1
          progress_percent = (processed_count / total_places) * 100
          print(f"\rProcessing: '{place}', Completion: {progress_percent:.2f}%{' ' * 2}", end='')

except KeyboardInterrupt:
    print("\nProcessing interrupted by user.")

finally:
    # Save the updated results to the output file (this will update the file with new results)
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(results_list, f, ensure_ascii=False, indent=4)
    print("\nFinal Results have been saved to:", output_file_path)
