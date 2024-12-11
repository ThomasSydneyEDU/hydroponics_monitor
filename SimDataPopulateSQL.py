import sqlite3
import random
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect("hydroponics_data.db")
cursor = conn.cursor()

# Function to generate simulated sensor data
def generate_simulated_data():
    ph = round(random.uniform(5.5, 7.5), 2)  # pH range
    temperature = round(random.uniform(20.0, 30.0), 2)  # Temperature in °C
    ec = round(random.uniform(0.5, 2.5), 2)  # Electrical conductivity in mS/cm
    tds = round(random.uniform(0, 500), 2)  # Total dissolved solids in ppm
    water_level = round(random.uniform(0.0, 1.0), 2)  # Water level in meters
    return ph, temperature, ec, tds, water_level

# Generate data for the past 48 hours at 15-minute intervals
start_time = datetime.now() - timedelta(hours=48)
time_interval = timedelta(minutes=15)

current_time = start_time
while current_time <= datetime.now():
    data = generate_simulated_data()
    cursor.execute("""
        INSERT INTO sensor_data (timestamp, ph, temperature, ec, tds, water_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (current_time, *data))
    current_time += time_interval

# Commit and close the connection
conn.commit()
conn.close()

print("Simulated data inserted successfully.")