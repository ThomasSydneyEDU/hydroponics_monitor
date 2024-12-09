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

# Check if the virtual environment is already active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating the virtual environment..."
    source "$VENV_PATH/bin/activate" || { echo "Error: Failed to activate virtual environment"; exit 1; }
else
    echo "Virtual environment already active: $VIRTUAL_ENV"
fi

# Run the Python script
echo "Running the program..."
python3 "$SCRIPT_NAME"

# Deactivate the virtual environment if it was activated in this script
if [ -z "$VIRTUAL_ENV" ]; then
    deactivate
    echo "Virtual environment deactivated."
fi