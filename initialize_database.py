import sqlite3
from datetime import datetime, timedelta
import random

DB_FILE = "hydroponics_data.db"

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def initialize_database():
    """Initialize the database and populate it with simulated data."""
    conn = connect_db()
    cursor = conn.cursor()

    # Create the sensor_data table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            ph REAL NOT NULL,
            temperature REAL NOT NULL,
            ec REAL NOT NULL,
            tds REAL NOT NULL,
            water_level REAL NOT NULL
        )
    """)

    # Clear any existing data
    cursor.execute("DELETE FROM sensor_data")

    # Populate the database with simulated data
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)  # Populate data for the last 7 days
    interval = timedelta(seconds=15)  # 15-second resolution
    current_time = start_time

    simulated_data = []
    while current_time <= end_time:
        simulated_data.append((
            current_time.isoformat(),
            round(random.uniform(5.5, 7.5), 2),  # pH
            round(random.uniform(20.0, 30.0), 2),  # Temperature (°C)
            round(random.uniform(0.5, 2.5), 2),  # EC (mS/cm)
            round(random.uniform(0, 500), 2),  # TDS (ppm)
            round(random.uniform(0.0, 1.0), 2),  # Water Level (m)
        ))
        current_time += interval

    # Insert data into the database
    cursor.executemany("""
        INSERT INTO sensor_data (timestamp, ph, temperature, ec, tds, water_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, simulated_data)

    conn.commit()
    conn.close()
    print(f"Database initialized with {len(simulated_data)} records.")

if __name__ == "__main__":
    initialize_database()