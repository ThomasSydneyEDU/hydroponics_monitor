#!/bin/bash

# Variables
REPO_PATH="/home/tcar5787/Documents/hydroponics_monitor"        # Replace with the full path to your project directory
VENV_PATH="/home/tcar5787/Documents/PyEnviroments/hydromonitor"  # Replace with the full path to your virtual environment
ARDUINO_SCRIPT="arduino_to_sensor.py"        # Script to fetch data from Arduino
GUI_SCRIPT="gui_display.py"                  # GUI display script

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

# Start the Arduino data logging script
echo "Starting Arduino to Sensor script..."
python3 "$ARDUINO_SCRIPT" &  # Run in the background

# Start the GUI
echo "Starting the GUI..."
python3 "$GUI_SCRIPT"

# Deactivate the virtual environment
deactivate
echo "Virtual environment deactivated."