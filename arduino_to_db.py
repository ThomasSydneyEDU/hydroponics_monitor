import sqlite3
import serial
import time
from datetime import datetime

# Database file
DB_FILE = "hydroponics_data.db"

# Arduino connection settings
ARDUINO_PORT = "/dev/ttyACM0"  # Adjust to your port
BAUD_RATE = 9600
TIMEOUT = 1  # Seconds

# Data aggregation variables
data_buffer = {"WATER_LEVEL": [], "WATER_TEMP": [], "EC": [], "TDS": [], "PH": []}
last_insert_time = time.time()

# Connect to the SQLite database
def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DB_FILE)

# Insert data into the database
def insert_data(timestamp, ph, temperature, ec, tds, water_level):
    """Insert a row of sensor data into the database."""
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        INSERT INTO sensor_data (timestamp, ph, temperature, ec, tds, water_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (timestamp, ph, temperature, ec, tds, water_level))
    conn.commit()
    conn.close()

# Aggregate and reset data buffer
def aggregate_and_store():
    """Aggregate sensor data and store the average in the database."""
    global data_buffer

    # Compute averages
    avg_values = {
        key: sum(values) / len(values) if values else 0
        for key, values in data_buffer.items()
    }

    # Get the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Insert into the database
    insert_data(
        timestamp,
        avg_values["PH"],
        avg_values["WATER_TEMP"],
        avg_values["EC"],
        avg_values["TDS"],
        avg_values["WATER_LEVEL"],
    )
    print(f"Inserted: {timestamp}, {avg_values}")

    # Reset the buffer
    data_buffer = {key: [] for key in data_buffer}

# Read data from Arduino
def read_from_arduino():
    """Read and parse data from the Arduino."""
    global last_insert_time

    try:
        arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=TIMEOUT)
        print("Connected to Arduino.")
        time.sleep(2)  # Allow time for the connection to stabilize
    except serial.SerialException as e:
        print(f"Error connecting to Arduino: {e}")
        return

    while True:
        try:
            # Read a line of data from the Arduino
            line = arduino.readline().decode("utf-8").strip()
            if line:
                # Parse the line into sensor values
                data = dict(item.split(":") for item in line.split(","))
                data_buffer["WATER_LEVEL"].append(float(data.get("WATER_LEVEL", 0)))
                data_buffer["WATER_TEMP"].append(float(data.get("WATER_TEMP", 0)))
                data_buffer["EC"].append(float(data.get("EC", 0)))
                data_buffer["TDS"].append(float(data.get("TDS", 0)))
                data_buffer["PH"].append(float(data.get("PH", 0)))

                # Check if it's time to insert into the database
                current_time = time.time()
                if current_time - last_insert_time >= 15:  # Every 15 seconds
                    aggregate_and_store()
                    last_insert_time = current_time
        except Exception as e:
            print(f"Error reading data: {e}")

# Main entry point
if __name__ == "__main__":
    read_from_arduino()