# This pipeline takes as input place_verification_results.json
# and converts into tables with place entities.
# Eventually, each place entity will be displayed on a front end.

import sqlite3
import json
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "places.db")
JSON_PATH = os.path.join(BASE_DIR, "../place_verification_results.json")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

# Create or connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables using the schema
with open(SCHEMA_PATH, "r") as schema_file:
    schema = schema_file.read()
cursor.executescript(schema)

# Load JSON data
with open(JSON_PATH, "r") as json_file:
    data = json.load(json_file)

# Insert data into the tables
for place in data:
    # Insert into places
    cursor.execute("""
        INSERT INTO places (id, place_name, latitude, longitude)
        VALUES (?, ?, ?, ?)
    """, (place["id"], place["place_name"], float(place["latitude"]), float(place["longitude"])))

    # Insert alternative names
    for alt_name in place["place_alternative_name"]:
        cursor.execute("""
            INSERT INTO alternative_names (place_id, alternative_name)
            VALUES (?, ?)
        """, (place["id"], alt_name))

    # Insert place indexes
    for index_value in place["place_index"]:
        cursor.execute("""
            INSERT INTO place_indexes (place_id, index_value)
            VALUES (?, ?)
        """, (place["id"], index_value))

# Commit and close connection
conn.commit()
conn.close()
print("Database setup complete!")
