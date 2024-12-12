import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from datetime import datetime, timedelta
import numpy as np

# Simulate 24-hour data for testing
timestamps = [datetime.now() - timedelta(minutes=i) for i in range(1440)]  # 1 minute intervals for 24 hours
sensor_data = {
    "pH": [np.random.uniform(5.5, 7.5) for _ in range(1440)],
    "Temperature": [np.random.uniform(20, 30) for _ in range(1440)],
    "EC": [np.random.uniform(0.5, 2.5) for _ in range(1440)],
    "TDS": [np.random.uniform(0, 500) for _ in range(1440)],
    "Water Level": [np.random.uniform(0.0, 1.0) for _ in range(1440)],
}

# Resample data to align with tick intervals
def resample_data(times, data, interval_minutes):
    """Resample data to a specific interval for consistent plotting."""
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
        data
    )
    return resampled_times, resampled_data

# Plot the resampled and latest data
def plot_data(sensor_name, ylabel, y_range, interval_minutes=15):
    """Fetch, resample, and plot data for a specific sensor."""
    ax.clear()

    # Fetch data
    times, data = timestamps, sensor_data[sensor_name]
    if not times or not data:
        ax.text(0.5, 0.5, "No Data Available", fontsize=16, color="white", ha="center", transform=ax.transAxes)
        canvas.draw()
        return

    # Resample data
    resampled_times, resampled_data = resample_data(times, data, interval_minutes)

    # Plot resampled data
    ax.plot(resampled_times, resampled_data, 'o-', color="white", label="15-min Trend")

    # Plot the most recent data point
    if times and data:
        ax.scatter(times[-1], data[-1], color="green", s=50, label="Latest Value")  # Green marker for the latest point

    # Configure grid
    ax.grid(which="major", color="white", linestyle="-", linewidth=0.8)
    ax.grid(which="minor", color="lightgray", linestyle="--", linewidth=0.5)

    # Configure x-axis
    ax.set_xlim(times[0], times[-1])
    ax.xaxis.set_major_locator(HourLocator(interval=4))
    ax.xaxis.set_minor_locator(HourLocator(interval=2))
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax.tick_params(axis='x', which='major', labelsize=10, colors="white")
    ax.tick_params(axis='x', which='minor', length=5, colors="white")
    ax.tick_params(axis='y', colors="white")

    # Add labels, limits, and legend
    ax.set_xlabel("Time (24hr)", color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.set_ylim(y_range)
    ax.legend(loc="upper left", fontsize=10, facecolor="black", edgecolor="white")

    canvas.draw()

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
    """Close the GUI and release the terminal."""
    root.destroy()
    print("\nGUI closed. You can now use the terminal.")

# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.geometry("800x480")
root.configure(bg="black")

# Left frame for buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Right frame for plot with white border
plot_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)
plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Add buttons
button_size = {"width": 20, "height": 1}  # Reduced button height
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

# Run the main loop
root.mainloop()