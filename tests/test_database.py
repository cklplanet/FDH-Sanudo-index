import sqlite3
import pytest
import os

DB_PATH = "database/places.db"

def test_places_path():
  print("Absolute path to DB:", os.path.abspath(DB_PATH))

def test_places_table():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM places")
        count = cursor.fetchone()[0]
        assert count > 0, "Places table is empty!"

def test_alternative_names_table():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM alternative_names")
        count = cursor.fetchone()[0]
        assert count >= 0, "Alternative names table test failed!"

def test_place_indexes_table():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM place_indexes")
        count = cursor.fetchone()[0]
        assert count >= 0, "Place indexes table test failed!"
