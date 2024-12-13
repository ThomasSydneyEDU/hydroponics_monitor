import time
from datetime import datetime
import serial
from google.cloud import firestore

# Firestore setup
def initialize_firestore():
    """
    Initialize Firestore using the service account key.
    """
    return firestore.Client.from_service_account_json("serviceAccountKey.json")

# Firestore function to write sensor data
def write_to_firestore(db, sensor_data):
    """
    Write sensor data to Firestore.
    """
    try:
        # Reference Firestore collection
        collection_ref = db.collection("sensor_readings")

        # Add sensor data with a server timestamp
        sensor_data["timestamp"] = firestore.SERVER_TIMESTAMP
        collection_ref.add(sensor_data)

        print(f"Data written to Firestore: {sensor_data}")
    except Exception as e:
        print(f"Error writing to Firestore: {e}")

# Function to read data from Arduino
def read_from_arduino(port="/dev/ttyACM0", baud_rate=9600, timeout=1):
    """
    Read sensor data from Arduino.
    """
    try:
        # Establish connection with Arduino
        arduino = serial.Serial(port, baud_rate, timeout=timeout)
        print("Connected to Arduino.")
        time.sleep(2)  # Allow time for the connection to stabilize

        # Read a line of data
        line = arduino.readline().decode("utf-8").strip()
        arduino.close()  # Close the connection after reading
        print(f"Raw data from Arduino: {line}")

        # Parse the line into sensor values
        # Example format: "WATER_LEVEL:50,WATER_TEMP:24.5,EC:1.2,TDS:500,PH:6.8"
        data = dict(item.split(":") for item in line.split(","))
        return {
            "water_level": float(data.get("WATER_LEVEL", 0)),
            "water_temp": float(data.get("WATER_TEMP", 0)),
            "ec": float(data.get("EC", 0)),
            "tds": float(data.get("TDS", 0)),
            "ph": float(data.get("PH", 0)),
        }
    except Exception as e:
        print(f"Error reading data from Arduino: {e}")
        return None

# Main loop to sample and send data to Firestore
def main(sampling_interval=900):
    """
    Main function to sample Arduino data and send to Firestore.
    
    Args:
        sampling_interval (int): Sampling interval in seconds (default 900s or 15 minutes).
    """
    # Initialize Firestore
    db = initialize_firestore()

    # Arduino port
    ARDUINO_PORT = "/dev/ttyACM0"  # Adjust as needed

    try:
        while True:
            # Read sensor data from Arduino
            sensor_data = read_from_arduino(port=ARDUINO_PORT)
            if sensor_data:
                # Write data to Firestore
                write_to_firestore(db, sensor_data)

            # Wait for the next sample
            print(f"Waiting for the next sample in {sampling_interval} seconds...")
            time.sleep(sampling_interval)

    except KeyboardInterrupt:
        print("Script terminated by user.")

if __name__ == "__main__":
    # Set the sampling interval as desired (default is 15 minutes)
    # Example: Pass 60 for a 1-minute sampling interval
    SAMPLING_INTERVAL = int(input("Enter sampling interval in seconds (default 900): ") or 900)
    main(sampling_interval=SAMPLING_INTERVAL)