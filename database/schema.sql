-- Create the main places table
CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY,
    place_name TEXT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

-- Create the alternative names table
CREATE TABLE IF NOT EXISTS alternative_names (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id INTEGER NOT NULL,
    alternative_name TEXT NOT NULL,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
);

-- Create the place indexes table
CREATE TABLE IF NOT EXISTS place_indexes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    place_id INTEGER NOT NULL,
    index_value TEXT NOT NULL,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
);
