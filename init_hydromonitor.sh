#!/bin/bash

# Variables
REPO_PATH="/home/tcar5787/Documents/hydroponics_monitor"        # Replace with the full path to your project directory
VENV_PATH="/home/tcar5787/Documents/PyEnviroments/hydromonitor"  # Replace with the full path to your virtual environment
INIT_DB_SCRIPT="initialize_database.py"  # Script to initialize the database
ARDUINO_SCRIPT="arduino_to_db.py"        # Script to fetch data from Arduino
GUI_SCRIPT="gui_display.py"              # GUI display script

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

# Activate the virtual environment
echo "Activating the virtual environment..."
source "$VENV_PATH/bin/activate" || { echo "Error: Failed to activate virtual environment"; exit 1; }

# Initialize the database
read -p "WARNING: This will delete existing data. Proceed? (y/n): " confirm
if [[ $confirm == "y" || $confirm == "Y" ]]; then
    echo "Initializing the database..."
    python3 "$INIT_DB_SCRIPT" || { echo "Error: Failed to initialize the database"; deactivate; exit 1; }
else
    echo "Skipping database initialization."
fi

# Start the Arduino data logging script
echo "Starting Arduino to Database script..."
python3 "$ARDUINO_SCRIPT" &

# Start the GUI
echo "Starting the GUI..."
python3 "$GUI_SCRIPT"

# Deactivate the virtual environment
deactivate
echo "Virtual environment deactivated."