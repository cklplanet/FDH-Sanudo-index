import json
import pandas as pd

# Load results into a DataFrame
output_file_path = "../place_verification_results.json"
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

# Agreement stats
agreement_counts = results_df["agreement_count"].value_counts()
print("Agreement Counts:")
print(agreement_counts)

import matplotlib.pyplot as plt

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

summary = {
    "Total Places Processed": total_places,
    "API Success Rates": api_success_rate,
    "Disagreements": len(disagreements),
    "Agreement Distribution": agreement_counts.to_dict()
}

print(json.dumps(summary, indent=4))
