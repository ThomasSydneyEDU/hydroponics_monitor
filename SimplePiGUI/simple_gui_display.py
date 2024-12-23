import tkinter as tk
import serial
import time
from datetime import datetime

# Arduino Serial Connection Settings
ARDUINO_PORT = "/dev/ttyACM0"  # Adjust to your port
BAUD_RATE = 9600
TIMEOUT = 1  # Seconds

arduino_connected = False
last_flash = None
last_interaction = time.time()

# Attempt to connect to Arduino
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=TIMEOUT)
    arduino_connected = True
except serial.SerialException:
    arduino_connected = False


# Read Arduino Data
def read_arduino_data():
    """Read and parse data from Arduino."""
    global arduino_connected

    if not arduino_connected:
        try:
            arduino.open()
            arduino_connected = True
        except Exception as e:
            print(f"Error reconnecting to Arduino: {e}")
            return  # Skip if unable to reconnect

    try:
        line = arduino.readline().decode("utf-8").strip()
        print(f"Raw Arduino data: {line}")  # Debugging output

        # Parse the line into a dictionary
        try:
            data = dict(item.split(":") for item in line.split(","))
        except ValueError as ve:
            print(f"Error parsing line: {line}, Error: {ve}")
            return {}

        return data

    except Exception as e:
        print(f"Error reading from Arduino: {e}")
        arduino_connected = False
        return {}


# Update Displayed Values
def update_display():
    """Fetch new data and update the display."""
    data = read_arduino_data()
    if data:
        # Update labels with Arduino keys
        if "PH" in data:
            labels["PH"].config(text=f"pH: {data['PH']}")
        if "WATER_TEMP" in data:
            labels["WATER_TEMP"].config(text=f"Temperature: {data['WATER_TEMP']} °C")
        if "WATER_LEVEL" in data:
            labels["WATER_LEVEL"].config(text=f"Water Level: {data['WATER_LEVEL']} m")

    root.after(1000, update_display)  # Refresh every second


# Update Arduino Connection Status
def update_arduino_status():
    """Update the Arduino connection status indicator."""
    global last_flash

    try:
        if arduino_connected:
            current_time = time.time()
            if last_flash is None or current_time - last_flash > 0.5:
                light_color = "green" if status_light.cget("bg") == "black" else "black"
                status_light.config(bg=light_color)
                last_flash = current_time
            status_label.config(text="Arduino Connected", fg="white")
        else:
            status_light.config(bg="red")
            status_label.config(text="Arduino Disconnected", fg="white")
    except Exception as e:
        print(f"Error updating Arduino status: {e}")

    root.after(500, update_arduino_status)  # Update every 500ms


# Close Program
def close_program():
    root.destroy()


# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.geometry("400x300")
root.configure(bg="black")

# Arduino status label and light
status_frame = tk.Frame(root, bg="black")
status_frame.pack(pady=5)
status_label = tk.Label(status_frame, text="Arduino Status", font=("Arial", 12), fg="white", bg="black")
status_label.pack(side=tk.LEFT)
status_light = tk.Label(status_frame, text="  ", bg="red", width=2, height=1)
status_light.pack(side=tk.LEFT, padx=5)

# Sensor data display
data_frame = tk.Frame(root, bg="black")
data_frame.pack(expand=True, fill=tk.BOTH, pady=20)

# Add labels for each sensor
labels = {
    "PH": tk.Label(data_frame, text="pH: --", font=("Arial", 14), fg="white", bg="black"),
    "WATER_TEMP": tk.Label(data_frame, text="Temperature: -- °C", font=("Arial", 14), fg="white", bg="black"),
    "WATER_LEVEL": tk.Label(data_frame, text="Water Level: -- m", font=("Arial", 14), fg="white", bg="black"),
}
for label in labels.values():
    label.pack(anchor="w", padx=10, pady=5)

# Close button
close_button = tk.Button(root, text="Close", font=("Arial", 12), command=close_program, bg="#FF3333", fg="black")
close_button.pack(pady=10)

# Start Arduino status updates and data fetching
root.after(500, update_arduino_status)
root.after(1000, update_display)

# Run the main loop
root.mainloop()
