import serial
import time
from datetime import datetime
from threading import Thread, Event

# Arduino connection settings
ARDUINO_PORT = "/dev/ttyACM0"  # Adjust to your port
BAUD_RATE = 9600
TIMEOUT = 1  # Seconds

# Data buffer for real-time data
sensor_data = {"WATER_LEVEL": 0, "WATER_TEMP": 0, "EC": 0, "TDS": 0, "PH": 0}

# Event to signal the GUI about new data
new_data_event = Event()

def read_from_arduino():
    """
    Read and parse data from the Arduino.
    This function runs in a background thread and updates the sensor_data dictionary.
    """
    global sensor_data

    try:
        arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=TIMEOUT)
        print("Connected to Arduino.")
        time.sleep(2)  # Allow time for the connection to stabilize
    except serial.SerialException as e:
        print(f"Error connecting to Arduino: {e}")
        return

    try:
        while True:
            try:
                # Attempt to read a line of data from the Arduino
                line = arduino.readline().decode("utf-8").strip()
                if line:
                    try:
                        # Parse the line into sensor values
                        data = dict(item.split(":") for item in line.split(","))
                        sensor_data["WATER_LEVEL"] = float(data.get("WATER_LEVEL", 0))
                        sensor_data["WATER_TEMP"] = float(data.get("WATER_TEMP", 0))
                        sensor_data["EC"] = float(data.get("EC", 0))
                        sensor_data["TDS"] = float(data.get("TDS", 0))
                        sensor_data["PH"] = float(data.get("PH", 0))

                        # Signal that new data is available
                        new_data_event.set()
                    except ValueError as ve:
                        print(f"Malformed data line skipped: {line}, Error: {ve}")
                else:
                    print("No data received. Retrying...")
            except Exception as e:
                print(f"Error reading data: {e}")
    except KeyboardInterrupt:
        print("Terminating the script...")
    finally:
        arduino.close()
        print("Arduino connection closed.")

# Thread management
def start_arduino_thread():
    """
    Start the thread to read data from the Arduino.
    """
    thread = Thread(target=read_from_arduino, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # Start the Arduino thread for testing purposes
    start_arduino_thread()

    try:
        while True:
            # Wait for new data
            new_data_event.wait()
            print(f"Received Data: {sensor_data}")
            new_data_event.clear()  # Reset the event
    except KeyboardInterrupt:
        print("Exiting the program...")