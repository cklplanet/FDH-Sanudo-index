import json
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic
from datetime import datetime

# Load results into a DataFrame
output_file_path = "data_analysis/data_analysis_results.json"
results_df = pd.read_json(output_file_path)

print(results_df.head())  # Inspect the first few rows

# Calculate total and successful matches
total_places = len(results_df)
api_success = {
    "Nominatim": results_df["nominatim_match"].sum(),
    "Geodata": results_df["geodata_match"].sum(),
    "Wikidata": results_df["wikidata_match"].sum(),
}

# Convert to percentages
api_success_rate = {k: f"{v / total_places * 100:.2f}%" for k, v in api_success.items()}
print("API Success Rates:", api_success_rate)

# Plot success rates for each API
plt.figure(figsize=(8, 5))
plt.bar(api_success.keys(), api_success.values(), color=["blue", "green", "orange"])
plt.title("API Success Comparison", fontsize=14)
plt.xlabel("API", fontsize=12)
plt.ylabel("Number of Matches", fontsize=12)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.show()

# Agreement stats
agreement_counts = results_df["agreement_count"].value_counts()
print("Agreement Counts:")
print(agreement_counts)

# Plot agreement count distribution
agreement_counts.plot(kind='bar', title="API Agreement Levels", xlabel="Number of Unique Coordinate Sets", ylabel="Frequency")
plt.show()


# Filter rows with disagreements
disagreements = results_df[results_df["agreement_count"] > 1]
print(f"Number of Disagreements: {len(disagreements)}")
print(disagreements[["place_name", "nominatim_coords", "geodata_coords", "wikidata_coords"]])

# Agreement visualization
results_df["agreement_count"].hist(bins=[1, 2, 3, 4], grid=False)
plt.title("Agreement Distribution")
plt.xlabel("Number of Unique Coordinate Sets")
plt.ylabel("Frequency")
plt.show()

################## CHECK COORDINATE DIFFERENCE #############################

# Function to calculate the Haversine distance between two coordinates
def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).meters  # returns distance in meters

# Check for small or large coordinate differences
threshold_small_distance = 100  # Small distance threshold in meters (100 meters)
threshold_large_distance = 1000  # Large distance threshold in meters (1000 meters)

potential_conflicts = []

for index, row in results_df.iterrows():
    # Initialize a list to store available coordinates
    coordinates = []

    # Check which coordinates are available
    if row['nominatim_coords']:
        coordinates.append(('nominatim', (row['nominatim_coords'][0], row['nominatim_coords'][1])))
    if row['geodata_coords']:
        coordinates.append(('geodata', (row['geodata_coords'][0], row['geodata_coords'][1])))
    if row['wikidata_coords']:
        coordinates.append(('wikidata', (row['wikidata_coords'][0], row['wikidata_coords'][1])))

    # If at least two coordinates are available, calculate distances between them
    if len(coordinates) >= 2:
        for i in range(len(coordinates)):
            for j in range(i + 1, len(coordinates)):
                coord1_label, coord1 = coordinates[i]
                coord2_label, coord2 = coordinates[j]

                distance = calculate_distance(coord1, coord2)

                # Check if the distance is large
                if distance > threshold_large_distance:
                    potential_conflicts.append({
                        "place_name": row['place_name'],
                        f"{coord1_label}_coords": coord1,
                        f"{coord2_label}_coords": coord2,
                        "distance": distance
                    })

# Print or display places with large coordinate differences
if potential_conflicts:
    print("\nPotential Conflicts (Large Distance Differences):")
    for conflict in potential_conflicts:
        print(f"\nPlace: {conflict['place_name']}")
        print(f"  Coordinates for {list(conflict.keys())[1]}: {conflict[list(conflict.keys())[1]]}")
        print(f"  Coordinates for {list(conflict.keys())[2]}: {conflict[list(conflict.keys())[2]]}")
        print(f"  Distance: {conflict['distance']} meters")

summary = {
    "Total Places Processed": total_places,
    "API Success Rates": api_success_rate,
    "Disagreements": len(disagreements),
    "Agreement Distribution": agreement_counts.to_dict(),
    "Potential Conflicts (Large Distance Differences)": len(potential_conflicts)
}

# Log the summary to a file with date and time
log_file_path = "data_analysis/log.txt"
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(log_file_path, "a") as log_file:
    log_file.write(f"{current_time} - Summary:\n")
    log_file.write(json.dumps(summary, indent=4))
    log_file.write("\n\n")

    if potential_conflicts:
        log_file.write(f"{current_time} - Potential Conflicts (Large Distance Differences):\n")
        for conflict in potential_conflicts:
            conflict_details = {
                "place_name": conflict["place_name"],
                "coordinates": {
                    list(conflict.keys())[1]: conflict[list(conflict.keys())[1]],
                    list(conflict.keys())[2]: conflict[list(conflict.keys())[2]],
                },
                "distance": conflict["distance"],
            }
            log_file.write(json.dumps(conflict_details, indent=4))
            log_file.write("\n")
    else:
        log_file.write(f"{current_time} - No Potential Conflicts Detected.\n")