import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from datetime import datetime, timedelta
import sqlite3
import numpy as np
import os

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

# Button actions
def show_ph():
    plot_data("ph", "pH", (5, 8))

def show_temp():
    plot_data("temperature", "Temperature (°C)", (15, 35))

def show_ec():
    plot_data("ec", "EC (mS/cm)", (0, 3))

def show_tds():
    plot_data("tds", "TDS (ppm)", (0, 600))

def show_water_level():
    plot_data("water_level", "Water Level (m)", (0, 1))

def close_program():
    root.destroy()

# Sleep Timer
def set_sleep_timer():
    """Set display to blank after 2 minutes of inactivity."""
    os.system("xset dpms 120 120 120")
    os.system("xset s activate")

def reset_sleep_timer(event=None):
    """Reset sleep timer when there is user activity."""
    os.system("xset s reset")

# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.attributes("-fullscreen", True)  # Full-screen mode
root.configure(bg="black")

# Bind user interaction to reset the sleep timer
root.bind_all("<Any-KeyPress>", reset_sleep_timer)
root.bind_all("<Any-ButtonPress>", reset_sleep_timer)

# Left frame for buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Right frame for plot with white border
plot_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)
plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Add buttons
button_size = {"width": 20, "height": 1}  # Adjusted height for thinner buttons
buttons = [
    ("Show pH Data", show_ph),
    ("Show Temperature Data", show_temp),
    ("Show EC Data", show_ec),
    ("Show TDS Data", show_tds),
    ("Show Water Level Data", show_water_level),
]
for text, command in buttons:
    btn = tk.Button(button_frame, text=text, font=("Arial", 14), command=command, **button_size, bg="#444444", fg="black")
    btn.pack(pady=5)

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
show_ph()

# Set the sleep timer
set_sleep_timer()

# Run the main loop
root.mainloop()