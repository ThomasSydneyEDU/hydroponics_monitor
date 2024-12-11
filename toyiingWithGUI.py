import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from datetime import datetime, timedelta
import numpy as np
import random
import serial
import time

# Try to connect to the Arduino
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Explicitly set to ttyACM0
    time.sleep(2)  # Wait for the connection to initialize
    arduino_connected = True
except serial.SerialException:
    arduino_connected = False

# Initialize data storage
sensor_data = {
    "pH": [],
    "Temperature": [],
    "EC": [],
    "TDS": [],
    "Water Level": [],
}
timestamps = []

# Define y-axis ranges for each sensor type
Y_AXIS_RANGES = {
    "pH": (5, 8),  # pH
    "Temperature": (15, 35),  # °C
    "EC": (0, 3),  # mS/cm
    "TDS": (0, 600),  # ppm
    "Water Level": (0, 1),  # meters
}

# Simulate sensor data when Arduino is not connected
def simulate_sensor_data():
    return {
        "pH": round(random.uniform(5.5, 7.5), 2),
        "Temperature": round(random.uniform(20.0, 30.0), 2),
        "EC": round(random.uniform(0.5, 2.5), 2),
        "TDS": round(random.uniform(0, 500), 2),
        "Water Level": round(random.uniform(0.0, 1.0), 2),
    }

# Fetch and update sensor data
def update_data():
    global arduino_connected
    try:
        if arduino_connected and arduino.in_waiting > 0:
            line = arduino.readline().decode("utf-8").strip()
            data = dict(item.split(":") for item in line.split(","))
            for key, value in data.items():
                sensor_data[key].append(float(value))
            status_label.config(text="Arduino Connected", fg="green")
        else:
            data = simulate_sensor_data()
            for key, value in data.items():
                sensor_data[key].append(value)
            status_label.config(text="Arduino Disconnected (Simulating Data)", fg="red")

        # Add timestamps
        now = datetime.now()
        timestamps.append(now)

        # Limit data storage to 1 month
        cutoff_time = now - timedelta(days=30)
        while timestamps and timestamps[0] < cutoff_time:
            timestamps.pop(0)
            for key in sensor_data:
                sensor_data[key].pop(0)

    except Exception as e:
        print(f"Error fetching data: {e}")
        arduino_connected = False
        status_label.config(text="Arduino Disconnected (Simulating Data)", fg="red")

    root.after(1000, update_data)  # Update every second

# Resample data to align with tick intervals
def resample_data(times, data, interval_minutes):
    if not times or not data:
        return [], []
    start_time = times[0]  # The oldest time
    end_time = times[-1]  # The most recent time
    resampled_times = [
        start_time + timedelta(minutes=i)
        for i in range(0, int((end_time - start_time).total_seconds() / 60), interval_minutes)
    ]
    resampled_data = np.interp(
        [t.timestamp() for t in resampled_times],  # Convert resampled times to timestamps
        [t.timestamp() for t in times],  # Original timestamps
        data
    )
    return resampled_times, resampled_data

# Plot the resampled data
def plot_data(sensor_name):
    ax.clear()
    if len(timestamps) < 1:
        ax.set_title(f"No Data Available for {sensor_name}", fontsize=16, color="white")
        canvas.draw()
        return

    interval_minutes = 15
    resampled_times, resampled_data = resample_data(timestamps, sensor_data[sensor_name], interval_minutes)

    line_color = "red" if not arduino_connected else "white"
    ax.plot(resampled_times, resampled_data, 'o-', color=line_color)  # Plot resampled data with dots

    # Configure grid
    ax.grid(which="major", color="white", linestyle="-", linewidth=0.8)
    ax.grid(which="minor", color="lightgray", linestyle="--", linewidth=0.5)

    # Configure x-axis
    ax.set_xlim(timestamps[0] if timestamps else datetime.now(), datetime.now())
    ax.xaxis.set_major_locator(HourLocator(interval=4))  # Major ticks every 4 hours
    ax.xaxis.set_minor_locator(HourLocator(interval=2))  # Minor ticks every 2 hours
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))  # Format labels for major ticks
    ax.tick_params(axis='x', which='major', labelsize=10, colors="white")  # Larger labels for major ticks
    ax.tick_params(axis='x', which='minor', length=5, colors="white")  # Minor ticks without labels
    ax.tick_params(axis='y', colors="white")

    # Add labels and limits
    ax.set_title(sensor_name, fontsize=16, color="white")
    ax.set_xlabel("Time (24hr)", color="white")
    ax.set_ylabel(sensor_name, color="white")
    ax.set_ylim(Y_AXIS_RANGES[sensor_name])
    canvas.draw()

# Close the program
def close_program():
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.geometry("800x480")
root.configure(bg="black")

# Status label centered at the top
status_label = tk.Label(root, text="Checking Arduino Connection...", font=("Arial", 12), fg="white", bg="black")
status_label.pack(pady=10)

# Left frame for buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Right frame for plot with white border
plot_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)
plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Add buttons for sensors
button_size = {"width": 20, "height": 2}
sensors = ["pH", "Temperature", "EC", "TDS", "Water Level"]
for sensor in sensors:
    btn = tk.Button(button_frame, text=f"Show {sensor} Data", font=("Arial", 14), command=lambda s=sensor: plot_data(s),
                    **button_size, bg="#444444", fg="black")
    btn.pack(pady=10)

# Add Close button
close_button = tk.Button(button_frame, text="Close Program", font=("Arial", 14), command=close_program,
                         **button_size, bg="#FF3333", fg="black")
close_button.pack(pady=10)

# Initialize matplotlib figure
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor("black")  # Set figure background to black
ax.set_facecolor("black")  # Set axes background to black
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Start updating Arduino data
root.after(1000, update_data)

# Run the main loop
root.mainloop()