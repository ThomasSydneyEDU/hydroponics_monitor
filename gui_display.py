import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import SecondLocator, DateFormatter
from datetime import datetime, timedelta
import numpy as np
import os
import time

# Simulated 24-hour data for testing
timestamps = sorted([datetime.now() - timedelta(seconds=15 * i) for i in range(5760)])  # 15s intervals for 24 hours
sensor_data = {
    "pH": [np.random.uniform(5.5, 7.5) for _ in range(5760)],
    "Temperature": [np.random.uniform(20, 30) for _ in range(5760)],
    "EC": [np.random.uniform(0.5, 2.5) for _ in range(5760)],
    "TDS": [np.random.uniform(0, 500) for _ in range(5760)],
    "Water Level": [np.random.uniform(0.0, 1.0) for _ in range(5760)],
}

# Arduino connection simulation
arduino_connected = True
last_flash = None
last_interaction = time.time()


def toggle_dot():
    """Toggle the Arduino status dot."""
    global last_flash
    if arduino_connected:
        new_color = "green" if status_dot.cget("bg") == "black" else "black"
        status_dot.config(bg=new_color)
        last_flash = root.after(500, toggle_dot)
    else:
        status_dot.config(bg="red")


def resample_data(times, data, interval_seconds):
    """Resample data to a specific interval for consistent plotting."""
    if not times or not data:
        return [], []

    start_time = times[0]
    end_time = times[-1]
    resampled_times = [
        start_time + timedelta(seconds=i)
        for i in range(0, int((end_time - start_time).total_seconds()), interval_seconds)
    ]
    resampled_data = np.interp(
        [t.timestamp() for t in resampled_times],
        [t.timestamp() for t in times],
        data
    )
    return resampled_times, resampled_data


def plot_data(sensor_name, ylabel, y_range, interval_seconds=15):
    """Fetch, resample, and plot data for a specific sensor."""
    ax.clear()

    # Fetch data
    times, data = timestamps, sensor_data[sensor_name]
    if not times or not data:
        ax.text(0.5, 0.5, "No Data Available", fontsize=16, color="white", ha="center", transform=ax.transAxes)
        canvas.draw()
        return

    # Resample data
    resampled_times, resampled_data = resample_data(times, data, interval_seconds)

    # Plot resampled data
    ax.plot(resampled_times, resampled_data, 'o-', color="white")

    # Configure grid
    ax.grid(which="major", color="white", linestyle="-", linewidth=0.8)
    ax.grid(which="minor", color="lightgray", linestyle="--", linewidth=0.5)

    # Configure x-axis
    ax.set_xlim(times[0], times[-1])
    ax.xaxis.set_major_locator(SecondLocator(interval=900))  # Major ticks every 15 minutes
    ax.xaxis.set_minor_locator(SecondLocator(interval=300))  # Minor ticks every 5 minutes
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    ax.tick_params(axis='x', which='major', labelsize=10, colors="white")
    ax.tick_params(axis='x', which='minor', length=5, colors="white")
    ax.tick_params(axis='y', colors="white")

    # Add labels and limits
    ax.set_xlabel("Time (Last 24 hours)", color="white")
    ax.set_ylabel(ylabel, color="white")
    ax.set_ylim(y_range)

    canvas.draw()


def reset_sleep_timer():
    """Reset the sleep timer."""
    global last_interaction
    last_interaction = time.time()


def check_sleep():
    """Check if the display should go to sleep."""
    if time.time() - last_interaction > 120:  # 2 minutes of inactivity
        sleep_display()
    else:
        root.after(1000, check_sleep)  # Check every second


def sleep_display():
    """Put the display to sleep."""
    if os.system("xset dpms force off") == 0:  # Turn off display on Raspberry Pi
        print("Display is sleeping...")


def wake_display(event):
    """Wake up the display on user interaction."""
    os.system("xset dpms force on")  # Wake up display on Raspberry Pi
    reset_sleep_timer()


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
    """Close the GUI and stop background tasks."""
    global last_flash
    if last_flash:
        root.after_cancel(last_flash)
    root.destroy()


# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.geometry("800x480")
root.configure(bg="black")

# Bind activity to wake display
root.bind_all("<Any-KeyPress>", wake_display)
root.bind_all("<Any-ButtonPress>", wake_display)

# Arduino connection status
status_frame = tk.Frame(root, bg="black")
status_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
status_label = tk.Label(status_frame, text="Arduino Connected", font=("Arial", 12), fg="white", bg="black")
status_label.pack(side=tk.LEFT, padx=5)
status_dot = tk.Label(status_frame, text="  ", font=("Arial", 12), bg="green", width=2, height=1)
status_dot.pack(side=tk.LEFT)

# Left frame for buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Right frame for plot with white border
plot_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)  # White border added
plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Add buttons
button_size = {"width": 20, "height": 1}  # Reduced button height
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
current_sensor = ("pH", "pH", (5, 8))
show_ph()

# Start Arduino status flashing
toggle_dot()

# Start sleep timer
root.after(1000, check_sleep)

# Run the main loop
root.mainloop()