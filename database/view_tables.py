# Prints the contents of each table to the terminal.

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "places.db")

def print_table_contents():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # List tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables in database:", [table[0] for table in tables])

        # Query and print each table's contents
        for table_name, in tables:
            print(f"\nContents of '{table_name}':")
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()

            # Get column names
            cursor.execute(f"PRAGMA table_info({table_name})")
            column_names = [col[1] for col in cursor.fetchall()]
            print(", ".join(column_names))

            for row in rows:
                print(row)

if not os.path.exists(DB_PATH):
    print(f"Database file not found at {DB_PATH}")
else:
    print(f"Database file found at {DB_PATH}")
    print_table_contents()