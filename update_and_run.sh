#!/bin/bash

# Variables
REPO_PATH="/home/tcar5787/Documents/hydroponics_monitor"        # Replace with the full path to your project directory
VENV_PATH="/home/tcar5787/Documents/PyEnviroments/hydromonitor"  # Replace with the full path to your virtual environment
SCRIPT_NAME="main.py"       # Replace with your Python script name

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

# Run the Python script
echo "Running the program..."
python3 "$SCRIPT_NAME"

# Deactivate the virtual environment after the script finishes
deactivate
echo "Virtual environment deactivated."