#!/bin/bash

# Variables
REPO_PATH="/home/tcar5787/Documents/hydroponics_monitor"        # Full path to your project directory
VENV_PATH="/home/tcar5787/Documents/PyEnviroments/hydromonitor" # Full path to your virtual environment
ARDUINO_SCRIPT="arduino_to_db.py"  # Python script for Arduino data
GUI_SCRIPT="gui_display.py"        # Python script for GUI
LOG_DIR="$REPO_PATH/logs"          # Directory to store logs

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

# Check and install dependencies
echo "Checking and installing dependencies..."
pip install --upgrade pip  # Upgrade pip to the latest version
pip install -r requirements.txt || { echo "Error: Failed to install dependencies"; deactivate; exit 1; }

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

# Deactivate the virtual environment after launching scripts
deactivate
echo "Virtual environment deactivated."

# Display success message
echo "All processes started successfully!"
echo "Logs can be found in $LOG_DIR"

# Exit the script
exit 0