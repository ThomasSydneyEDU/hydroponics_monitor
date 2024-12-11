import sqlite3
from datetime import datetime, timedelta

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect("hydroponics_data.db")
cursor = conn.cursor()

# Create a table to store sensor data
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    ph REAL,
    temperature REAL,
    ec REAL,
    tds REAL,
    water_level REAL
)
""")

# Commit and close the connection
conn.commit()
conn.close()

print("Database and table created successfully.")