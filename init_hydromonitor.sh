#!/bin/bash

# Variables
REPO_PATH="/home/tcar5787/Documents/hydroponics_monitor"        # Replace with the full path to your project directory
VENV_PATH="/home/tcar5787/Documents/PyEnviroments/hydromonitor" # Replace with the full path to your virtual environment
DB_FILE="$REPO_PATH/hydroponics_data.db"  # Path to the SQLite database
ARDUINO_SCRIPT="arduino_to_db.py"         # Python script for Arduino data
GUI_SCRIPT="gui_display.py"              # Python script for GUI
LOG_DIR="$REPO_PATH/logs"                 # Directory to store logs

# Change to the repository directory
cd "$REPO_PATH" || { echo "Error: Cannot access $REPO_PATH"; exit 1; }

# Pull the latest code from the repository
echo "Checking for updates in the repository..."
git fetch origin
if [ "$(git rev-parse HEAD)" != "$(git rev-parse @{u})" ]; then
    echo "Updates found! Pulling the latest changes..."
    git pull origin main || { echo "Error: Failed to pull latest code"; exit 1; }
else
    echo "Repository is up to date."
fi

# Delete the old database with a warning
if [ -f "$DB_FILE" ]; then
    echo "Warning: Database file already exists."
    read -p "Do you want to delete and recreate the database? (y/n): " CONFIRM
    if [ "$CONFIRM" = "y" ]; then
        rm "$DB_FILE"
        echo "Old database deleted."
    else
        echo "Keeping the existing database."
    fi
fi

# Create a new database
if [ ! -f "$DB_FILE" ]; then
    echo "Creating a new database..."
    python3 - <<EOF
import sqlite3

conn = sqlite3.connect("$DB_FILE")
cursor = conn.cursor()

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
conn.commit()
conn.close()
print("Database created successfully.")
EOF
fi

# Populate the database with simulated data
echo "Populating the database with simulated data..."
python3 - <<EOF
import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("$DB_FILE")
cursor = conn.cursor()

start_time = datetime.now() - timedelta(hours=48)
time_interval = timedelta(minutes=15)
current_time = start_time

while current_time <= datetime.now():
    ph = round(random.uniform(5.5, 7.5), 2)
    temperature = round(random.uniform(20.0, 30.0), 2)
    ec = round(random.uniform(0.5, 2.5), 2)
    tds = round(random.uniform(0, 500), 2)
    water_level = round(random.uniform(0.0, 1.0), 2)

    cursor.execute("""
        INSERT INTO sensor_data (timestamp, ph, temperature, ec, tds, water_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (current_time.strftime("%Y-%m-%d %H:%M:%S"), ph, temperature, ec, tds, water_level))
    current_time += time_interval

conn.commit()
conn.close()
print("Simulated data inserted successfully.")
EOF

# Activate the virtual environment
echo "Activating the virtual environment..."
source "$VENV_PATH/bin/activate" || { echo "Error: Failed to activate virtual environment"; exit 1; }

# Create the log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Start the Arduino-to-database script
echo "Starting Arduino-to-database script..."
nohup python "$ARDUINO_SCRIPT" > "$LOG_DIR/arduino_to_db.log" 2>&1 &
ARDUINO_PID=$!
echo "Arduino-to-database script started with PID: $ARDUINO_PID"

# Start the GUI script
echo "Starting GUI script..."
nohup python "$GUI_SCRIPT" > "$LOG_DIR/gui_display.log" 2>&1 &
GUI_PID=$!
echo "GUI script started with PID: $GUI_PID"

# Deactivate the virtual environment
deactivate
echo "Virtual environment deactivated."

# Display success message
echo "Initialization complete. Logs can be found in $LOG_DIR"