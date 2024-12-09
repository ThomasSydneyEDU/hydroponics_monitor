import tkinter as tk
from tkinter import messagebox
import serial
import time
import random
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from datetime import datetime, timedelta
import matplotlib.dates as mdates

# Try to connect to the Arduino
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Explicitly set to ttyACM0
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

# Define y-axis ranges for each sensor type
Y_AXIS_RANGES = {
    "WATER_LEVEL": (0, 1),  # meters
    "WATER_TEMP": (15, 35),  # °C
    "EC": (0, 3),  # mS/cm
    "TDS": (0, 600),  # ppm
    "PH": (5, 9),  # pH
}

# Simulate sensor data when Arduino is not connected (for testing)
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
            status_label.config(text="Arduino Connected", fg="green")
        else:
            data = simulate_sensor_data()
            status_label.config(text="Arduino Disconnected", fg="red")

        # Append data with timestamp
        now = datetime.now()
        timestamps.append(now)
        for key, value in data.items():
            sensor_data[key].append(float(value))

        # Limit data to 1 month
        cutoff_time = now - timedelta(days=30)
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
        status_label.config(text="Arduino Disconnected", fg="red")

    root.after(1000, update_data)

# Show interactive graph for a sensor
def show_graph(sensor_name):
    if len(sensor_data[sensor_name]) == 0:
        messagebox.showinfo("No Data", "Not enough data available to display a graph.")
        return

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.subplots_adjust(bottom=0.2)
    
    def plot_data(hours, time_label):
        ax.clear()
        now = datetime.now()
        start_time = now - timedelta(hours=hours)

        # Filter data for the selected time range
        filtered_times = []
        filtered_values = []
        for i in range(len(timestamps)):
            if timestamps[i] >= start_time:
                filtered_times.append(timestamps[i])
                filtered_values.append(sensor_data[sensor_name][i])

        if filtered_values:
            ax.plot(filtered_times, filtered_values, color='black', linewidth=2, label='Recorded Data')
        else:
            # If insufficient data, plot average
            average_value = sum(sensor_data[sensor_name]) / len(sensor_data[sensor_name])
            ax.axhline(average_value, color='red', linestyle='--', linewidth=2, label='Average Value')

        # Customize x-axis labels
        ax.xaxis.set_major_formatter(mdates.DateFormatter(time_label))
        if hours <= 6:  # Hourly data
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        elif hours <= 24:  # Daily data
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
        elif hours <= 168:  # Weekly data
            ax.xaxis.set_major_locator(mdates.DayLocator())
        else:  # Monthly data
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

        ax.set_title(f"{sensor_name} Data - Last {hours} Hours")
        ax.set_xlabel("Time")
        ax.set_ylabel(sensor_name)
        ax.set_ylim(Y_AXIS_RANGES[sensor_name])
        ax.legend()
        plt.xticks(rotation=45)
        fig.canvas.draw()

    # Initial plot for 1 hour
    plot_data(1, '%H:%M')

    # Add interactive buttons
    buttons = [
        ("1 Hour", 1, '%H:%M'), ("6 Hours", 6, '%H:%M'),
        ("1 Day", 24, '%H:%M'), ("1 Week", 168, '%d-%b'),
        ("1 Month", 720, '%d-%b')
    ]
    for idx, (label, hours, time_label) in enumerate(buttons):
        ax_button = plt.axes([0.1 + idx * 0.16, 0.05, 0.14, 0.075])
        btn = Button(ax_button, label)
        btn.on_clicked(lambda _, h=hours, t=time_label: plot_data(h, t))

    plt.show()

# Restart the program
def restart_program():
    import os
    import sys
    os.execl(sys.executable, sys.executable, *sys.argv)

# Close the program
def close_program():
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Hydroponics Dashboard")
root.attributes("-fullscreen", True)  # Make the application full-screen

# Create a frame for the connection status
status_frame = tk.Frame(root)
status_frame.pack(fill=tk.X)
status_label = tk.Label(status_frame, text="Arduino Status: Checking...", font=("Arial", 18))
status_label.pack(pady=10)

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

# Close button
close_btn = tk.Button(root, text="Close Program", font=("Arial", 14), width=20, height=2, bg="red", fg="white",
                      command=close_program)
close_btn.pack(pady=20)

# Start updating data
root.after(1000, update_data)

# Run the main loop
root.mainloop()