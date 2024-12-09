import tkinter as tk
import serial
import time
import random
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Try to connect to the Arduino
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Replace with your actual port
    time.sleep(2)  # Wait for the connection to initialize
    arduino_connected = True
except serial.SerialException:
    arduino_connected = False

# Initialize data storage
sensor_data = {
    "WATER_LEVEL": [],
    "WATER_TEMP": [],
    "EC": [],
    "TDS": [],
    "PH": [],
}
timestamps = []

# Function to simulate sensor data when Arduino is not connected (for testing)
def simulate_sensor_data():
    return {
        "WATER_LEVEL": round(random.uniform(0.0, 1.0), 2),
        "WATER_TEMP": round(random.uniform(20.0, 30.0), 1),
        "EC": round(random.uniform(0.5, 2.5), 2),
        "TDS": round(random.uniform(0, 500), 1),
        "PH": round(random.uniform(5.5, 7.5), 1),
    }

# Update sensor data
def update_data():
    global arduino_connected
    try:
        if arduino_connected and arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            data = dict(item.split(':') for item in line.split(','))
        else:
            data = simulate_sensor_data()

        # Append data with timestamp
        now = datetime.now()
        timestamps.append(now)
        for key, value in data.items():
            sensor_data[key].append(float(value))

        # Limit data to 24 hours
        cutoff_time = now - timedelta(hours=24)
        while timestamps and timestamps[0] < cutoff_time:
            timestamps.pop(0)
            for key in sensor_data:
                sensor_data[key].pop(0)

        # Update button labels
        buttons["WATER_LEVEL"].config(text=f"Water Level: {data['WATER_LEVEL']} m")
        buttons["WATER_TEMP"].config(text=f"Water Temp: {data['WATER_TEMP']}°C")
        buttons["EC"].config(text=f"EC: {data['EC']} mS/cm")
        buttons["TDS"].config(text=f"TDS: {data['TDS']} ppm")
        buttons["PH"].config(text=f"pH: {data['PH']}")

    except Exception as e:
        print(f"Error: {e}")
        arduino_connected = False

    root.after(1000, update_data)

# Show graph for a sensor
def show_graph(sensor_name):
    if len(sensor_data[sensor_name]) == 0:
        tk.messagebox.showinfo("No Data", "Not enough data available to display a graph.")
        return

    plt.figure(figsize=(8, 4))
    plt.plot(timestamps, sensor_data[sensor_name], label=sensor_name)
    plt.xlabel("Time")
    plt.ylabel(sensor_name)
    plt.title(f"{sensor_name} over the last 24 hours")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.show()

# Restart the program
def restart_program():
    os.execl(sys.executable, sys.executable, *sys.argv)

# Create the main window
root = tk.Tk()
root.title("Hydroponics Dashboard")
root.geometry("480x320")  # Size for Raspberry Pi touchscreen

# Create buttons for the 2x3 grid
buttons = {}
button_frame = tk.Frame(root)
button_frame.pack(expand=True)

# Sensor buttons
sensors = ["WATER_LEVEL", "WATER_TEMP", "EC", "TDS", "PH"]
for i, sensor in enumerate(sensors):
    btn = tk.Button(button_frame, text=f"{sensor}: --", font=("Arial", 14), width=15, height=2,
                    command=lambda s=sensor: show_graph(s))
    btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)
    buttons[sensor] = btn

# Restart button
restart_btn = tk.Button(button_frame, text="Restart Program", font=("Arial", 14), width=15, height=2,
                        command=restart_program)
restart_btn.grid(row=1, column=2, padx=5, pady=5)

# Start updating data
root.after(1000, update_data)

# Run the main loop
root.mainloop()