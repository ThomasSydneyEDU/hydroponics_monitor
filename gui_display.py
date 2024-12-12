import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from datetime import datetime, timedelta
import serial
import time
import numpy as np
import random

# Arduino connection settings
ARDUINO_PORT = "/dev/ttyACM0"  # Adjust to your port
BAUD_RATE = 9600
TIMEOUT = 1  # Seconds

# Initialize connection to Arduino
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=TIMEOUT)
    time.sleep(2)  # Wait for the connection to stabilize
    arduino_connected = True
except serial.SerialException as e:
    print(f"Error connecting to Arduino: {e}")
    arduino_connected = False

# Simulate 24 hours of initial data
def simulate_initial_data():
    """Simulate 24 hours of data for all sensors."""
    now = datetime.now()
    simulated_times = [now - timedelta(minutes=i) for i in range(1440)]  # 1440 minutes = 24 hours
    simulated_data = {
        "pH": [round(random.uniform(5.5, 7.5), 2) for _ in range(1440)],
        "Temperature": [round(random.uniform(20.0, 30.0), 2) for _ in range(1440)],
        "EC": [round(random.uniform(0.5, 2.5), 2) for _ in range(1440)],
        "TDS": [round(random.uniform(0, 500), 1) for _ in range(1440)],
        "Water Level": [round(random.uniform(0.0, 1.0), 2) for _ in range(1440)],
    }
    return simulated_times[::-1], {k: v[::-1] for k, v in simulated_data.items()}

# Initialize data storage with simulated data
timestamps, sensor_data = simulate_initial_data()

# Define y-axis ranges for each sensor type
Y_AXIS_RANGES = {
    "pH": (5, 8),  # pH
    "Temperature": (15, 35),  # °C
    "EC": (0, 3),  # mS/cm
    "TDS": (0, 600),  # ppm
    "Water Level": (0, 1),  # meters
}

# Fetch and update sensor data
def fetch_sensor_data():
    global arduino_connected
    try:
        if arduino_connected and arduino.in_waiting > 0:
            line = arduino.readline().decode("utf-8").strip()
            data = dict(item.split(":") for item in line.split(","))
            now = datetime.now()
            timestamps.append(now)
            for key, value in data.items():
                sensor_data[key].append(float(value))
            
            # Keep only the last 24 hours of data
            cutoff_time = now - timedelta(hours=24)
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.pop(0)
                for key in sensor_data:
                    sensor_data[key].pop(0)
        elif not arduino_connected:
            print("Arduino disconnected. No new data.")
    except Exception as e:
        print(f"Error fetching data: {e}")

# Resample data for consistent plotting
def resample_data(times, data, interval_minutes):
    """Resample data to align with tick intervals."""
    if not times or not data:
        return [], []
    start_time = times[0]
    end_time = times[-1]
    resampled_times = [
        start_time + timedelta(minutes=i)
        for i in range(0, int((end_time - start_time).total_seconds() / 60), interval_minutes)
    ]
    resampled_data = np.interp(
        [t.timestamp() for t in resampled_times],
        [t.timestamp() for t in times],
        data,
    )
    return resampled_times, resampled_data

# Plot the resampled data
def plot_data(sensor_name, ylabel, y_range, interval_minutes=15):
    ax.clear()
    if not timestamps or not sensor_data[sensor_name]:
        ax.text(0.5, 0.5, "No Data Available", fontsize=16, color="white", ha="center", transform=ax.transAxes)
        canvas.draw()
        return

    resampled_times, resampled_data = resample_data(timestamps, sensor_data[sensor_name], interval_minutes)
    ax.plot(resampled_times, resampled_data, 'o-', color="white")
    ax.grid(which="major", color="white", linestyle="-", linewidth=0.8)
    ax.grid(which="minor", color="lightgray", linestyle="--", linewidth=0.5)
    ax.set_xlim(timestamps[0], timestamps[-1])
    ax.xaxis.set_major_locator(HourLocator(interval=4))
    ax.xaxis.set_minor_locator(HourLocator(interval=2))
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax.tick_params(axis='x', which='major', labelsize=10, colors="white")
    ax.tick_params(axis='x', which='minor', length=5, colors="white")
    ax.tick_params(axis='y', colors="white")
    ax.set_xlabel("Time (24hr)", color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.set_ylim(y_range)
    canvas.draw()

# Refresh the plot periodically
def refresh_plot():
    """Fetch new data and refresh the plot."""
    fetch_sensor_data()
    if current_sensor:
        plot_data(*current_sensor)
    root.after(1000, refresh_plot)  # Update every second

# Button actions
def show_ph():
    global current_sensor
    current_sensor = ("pH", "pH", (5, 8))
    plot_data(*current_sensor)

def show_temp():
    global current_sensor
    current_sensor = ("Temperature", "Temperature (°C)", (15, 35))
    plot_data(*current_sensor)

def show_ec():
    global current_sensor
    current_sensor = ("EC", "EC (mS/cm)", (0, 3))
    plot_data(*current_sensor)

def show_tds():
    global current_sensor
    current_sensor = ("TDS", "TDS (ppm)", (0, 600))
    plot_data(*current_sensor)

def show_water_level():
    global current_sensor
    current_sensor = ("Water Level", "Water Level (m)", (0, 1))
    plot_data(*current_sensor)

def close_program():
    if arduino_connected:
        arduino.close()
    root.destroy()

# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.geometry("800x480")
root.configure(bg="black")

# Left frame for buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Right frame for plot
plot_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)
plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Add buttons
button_size = {"width": 20, "height": 2}
buttons = [
    ("Show pH Data", show_ph),
    ("Show Temperature Data", show_temp),
    ("Show EC Data", show_ec),
    ("Show TDS Data", show_tds),
    ("Show Water Level Data", show_water_level),
]
for text, command in buttons:
    btn = tk.Button(button_frame, text=text, font=("Arial", 14), command=command, **button_size, bg="#444444", fg="black")
    btn.pack(pady=10)

# Add Close button
close_button = tk.Button(button_frame, text="Close Program", font=("Arial", 14), command=close_program,
                         **button_size, bg="#FF3333", fg="black")
close_button.pack(pady=10)

# Initialize matplotlib figure
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Default plot
current_sensor = ("pH", "pH", (5, 8))
show_ph()

# Start periodic plot refresh
root.after(1000, refresh_plot)

# Run the main loop
root.mainloop()