import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from datetime import datetime, timedelta
import sqlite3
import numpy as np

# Connect to the SQLite database
DB_FILE = "hydroponics_data.db"

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DB_FILE)

# Fetch data from the database
def fetch_data(sensor_name, hours=24):
    """Fetch data for the specified sensor and time range from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    start_time = datetime.now() - timedelta(hours=hours)
    query = f"""
        SELECT timestamp, {sensor_name}
        FROM sensor_data
        WHERE timestamp >= ?
        ORDER BY timestamp ASC
    """
    cursor.execute(query, (start_time,))
    rows = cursor.fetchall()
    conn.close()
    times, values = [], []
    for row in rows:
        try:
            timestamp = datetime.fromisoformat(row[0])
            times.append(timestamp)
            values.append(row[1])
        except ValueError:
            print(f"Skipping invalid timestamp: {row[0]}")
    print(f"Fetched {len(times)} data points for {sensor_name}.")  # Debugging output
    return times, values

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

# Plot the resampled data
def plot_data(sensor_name, ylabel, y_range, interval_minutes=15):
    """Fetch, resample, and plot data for a specific sensor."""
    ax.clear()
    times, data = fetch_data(sensor_name.lower(), hours=24)
    if not times or not data:
        ax.text(0.5, 0.5, "No Data Available", fontsize=16, color="white", ha="center", transform=ax.transAxes)
        canvas.draw()
        return
    resampled_times, resampled_data = resample_data(times, data, interval_minutes)
    ax.plot(resampled_times, resampled_data, 'o-', color="white")
    ax.grid(which="major", color="white", linestyle="-", linewidth=0.8)
    ax.grid(which="minor", color="lightgray", linestyle="--", linewidth=0.5)
    ax.set_xlim(times[0], times[-1])
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
    """Refresh the plot with the most recent data."""
    global current_sensor
    if current_sensor:
        print(f"Refreshing plot for {current_sensor[0]}...")  # Debugging output
        plot_data(*current_sensor)
    root.after(15000, refresh_plot)  # Schedule the next refresh in 15 seconds

# Button actions
def show_ph():
    global current_sensor
    current_sensor = ("ph", "pH", (5, 8))
    plot_data(*current_sensor)

def show_temp():
    global current_sensor
    current_sensor = ("temperature", "Temperature (°C)", (15, 35))
    plot_data(*current_sensor)

def show_ec():
    global current_sensor
    current_sensor = ("ec", "EC (mS/cm)", (0, 3))
    plot_data(*current_sensor)

def show_tds():
    global current_sensor
    current_sensor = ("tds", "TDS (ppm)", (0, 600))
    plot_data(*current_sensor)

def show_water_level():
    global current_sensor
    current_sensor = ("water_level", "Water Level (m)", (0, 1))
    plot_data(*current_sensor)

def close_program():
    root.destroy()

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
current_sensor = ("ph", "pH", (5, 8))
show_ph()

# Start periodic plot refresh
root.after(15000, refresh_plot)

# Run the main loop
root.mainloop()