import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import HourLocator, DateFormatter
from datetime import datetime, timedelta
import numpy as np
import time

# Simulated data for testing
timestamps = sorted([datetime.now() - timedelta(seconds=15 * i) for i in range(5760)])  # 15s intervals for 24 hours
sensor_data = {
    "pH": [np.random.uniform(5.5, 7.5) for _ in range(5760)],
    "Temperature": [np.random.uniform(20, 30) for _ in range(5760)],
    "EC": [np.random.uniform(0.5, 2.5) for _ in range(5760)],
    "TDS": [np.random.uniform(0, 500) for _ in range(5760)],
    "Water Level": [np.random.uniform(0.0, 1.0) for _ in range(5760)],
}

arduino_connected = True  # Simulate Arduino connection
last_flash = None
last_interaction = time.time()


def moving_average(data, window_size=20):
    """Calculate the moving average with a given window size."""
    return np.convolve(data, np.ones(window_size) / window_size, mode="valid")


def resample_data(times, data, interval_minutes):
    """Resample data to a specific interval for consistent plotting."""
    start_time = times[0]
    end_time = times[-1]

    # Resample timestamps
    resampled_times = [
        start_time + timedelta(minutes=i)
        for i in range(0, int((end_time - start_time).total_seconds() / 60), interval_minutes)
    ]

    # Apply moving average and downsample data
    smoothed_data = moving_average(data, window_size=20)  # Smoothing
    resampled_data = np.interp(
        [t.timestamp() for t in resampled_times],
        [t.timestamp() for t in times[:len(smoothed_data)]],
        smoothed_data,
    )

    return resampled_times, resampled_data


def plot_data(sensor_name, ylabel, y_range, interval_minutes=5):
    """Fetch, resample, and plot data for a specific sensor."""
    ax.clear()

    # Simulate fetching data
    times = timestamps
    data = sensor_data[sensor_name]

    # Resample data
    resampled_times, resampled_data = resample_data(times, data, interval_minutes)

    # Plot data
    ax.plot(resampled_times, resampled_data, 'o-', color="white")

    # Configure grid and ticks
    ax.grid(which="major", color="white", linestyle="-", linewidth=0.8)
    ax.grid(which="minor", color="lightgray", linestyle="--", linewidth=0.5)

    ax.set_xlim(times[0], times[-1])
    ax.xaxis.set_major_locator(HourLocator(interval=6))  # Major ticks every 6 hours
    ax.xaxis.set_minor_locator(HourLocator(interval=1))  # Minor ticks every 1 hour
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    ax.tick_params(axis='x', which='major', labelsize=10, colors="white")
    ax.tick_params(axis='x', which='minor', length=5, colors="white")
    ax.tick_params(axis='y', colors="white")

    # Add labels and limits
    ax.set_xlabel("Time (24hr)", color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.set_ylim(y_range)
    canvas.draw()


def show_ph():
    plot_data("pH", "pH", (5, 8))


def show_temp():
    plot_data("Temperature", "Temperature (°C)", (15, 35))


def show_ec():
    plot_data("EC", "EC (mS/cm)", (0, 3))


def show_tds():
    plot_data("TDS", "TDS (ppm)", (0, 600))


def show_water_level():
    plot_data("Water Level", "Water Level (m)", (0, 1))


def close_program():
    root.destroy()


def sleep_display():
    """Simulate putting the display to sleep."""
    global last_interaction
    if time.time() - last_interaction > 120:  # 2 minutes
        root.withdraw()  # Hide the window
    root.after(1000, sleep_display)  # Check every second


def wake_display(event):
    """Wake the display on interaction."""
    global last_interaction
    last_interaction = time.time()
    root.deiconify()  # Show the window again


# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.geometry("800x480")
root.configure(bg="black")

# Bind interactions to wake the display
root.bind("<Any-KeyPress>", wake_display)
root.bind("<Any-ButtonPress>", wake_display)

# Left frame for buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Right frame for plot with white border
plot_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)
plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Add buttons
button_size = {"width": 15, "height": 2}
buttons = [
    ("pH", show_ph),
    ("Temperature", show_temp),
    ("EC", show_ec),
    ("TDS", show_tds),
    ("Water Level", show_water_level),
]
for text, command in buttons:
    btn = tk.Button(button_frame, text=text, font=("Arial", 14), command=command, **button_size, bg="#444444", fg="black")
    btn.pack(pady=10)

# Add Close button
close_button = tk.Button(button_frame, text="Close", font=("Arial", 14), command=close_program,
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

# Start sleep display check
root.after(1000, sleep_display)

# Run the main loop
root.mainloop()