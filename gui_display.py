import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import MinuteLocator, DateFormatter
from datetime import datetime, timedelta
import numpy as np
import serial
import time

# Arduino Serial Connection Settings
ARDUINO_PORT = "/dev/ttyACM0"  # Adjust to your port
BAUD_RATE = 9600
TIMEOUT = 1  # Seconds

# Initialize data buffers
BUFFER_DURATION = 3600  # Store 1 hour of data (in seconds)
buffer = {
    "pH": [],
    "Temperature": [],
    "EC": [],
    "TDS": [],
    "Water Level": [],
}
timestamps = []
arduino_connected = False
last_flash = None
last_interaction = time.time()

# Attempt to connect to Arduino
try:
    arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=TIMEOUT)
    arduino_connected = True
except serial.SerialException:
    arduino_connected = False


def read_arduino_data():
    """Read and parse data from Arduino."""
    global arduino_connected

    if not arduino_connected:
        try:
            # Try to reconnect
            arduino.open()
            arduino_connected = True
        except Exception:
            return  # Skip if unable to reconnect

    try:
        line = arduino.readline().decode("utf-8").strip()
        if line:
            data = dict(item.split(":") for item in line.split(","))
            timestamp = datetime.now()

            # Update the buffer
            timestamps.append(timestamp)
            for key, value in buffer.items():
                if key in data:
                    value.append(float(data[key]))

            # Maintain buffer size
            cutoff = timestamp - timedelta(seconds=BUFFER_DURATION)
            while timestamps and timestamps[0] < cutoff:
                timestamps.pop(0)
                for key in buffer:
                    buffer[key].pop(0)
    except Exception as e:
        print(f"Error reading from Arduino: {e}")
        arduino_connected = False


def moving_average(data, window_size=4):
    """Calculate the moving average with a given window size."""
    return np.convolve(data, np.ones(window_size) / window_size, mode="valid")


def resample_data(times, data, interval_seconds):
    """Resample data to a specific interval for consistent plotting."""
    if not times or not data:
        return [], []

    start_time = times[0]
    end_time = times[-1]

    # Resample timestamps
    resampled_times = [
        start_time + timedelta(seconds=i)
        for i in range(0, int((end_time - start_time).total_seconds()), interval_seconds)
    ]

    # Apply moving average and downsample data
    smoothed_data = moving_average(data, window_size=4)  # Smoothing
    resampled_data = np.interp(
        [t.timestamp() for t in resampled_times],
        [t.timestamp() for t in times[:len(smoothed_data)]],
        smoothed_data,
    )

    return resampled_times, resampled_data


def plot_data(sensor_name, ylabel, y_range, interval_seconds=300):
    """Fetch, resample, and plot data for a specific sensor."""
    try:
        ax.clear()

        # Use buffered data
        times = timestamps
        data = buffer[sensor_name]

        # Resample data
        resampled_times, resampled_data = resample_data(times, data, interval_seconds)

        # Plot data
        ax.plot(resampled_times, resampled_data, 'o-', color="white")

        # Configure grid and ticks
        ax.grid(which="major", color="white", linestyle="-", linewidth=0.8)
        ax.grid(which="minor", color="lightgray", linestyle="--", linewidth=0.5)

        ax.set_xlim(times[0], times[-1])
        ax.xaxis.set_major_locator(MinuteLocator(interval=15))  # Major ticks every 15 minutes
        ax.xaxis.set_minor_locator(MinuteLocator(interval=5))  # Minor ticks every 5 minutes
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
        ax.tick_params(axis='x', which='major', labelsize=10, colors="white")
        ax.tick_params(axis='x', which='minor', length=5, colors="white")
        ax.tick_params(axis='y', colors="white")

        # Add labels and limits
        ax.set_xlabel("Time (1hr)", color="white")
        ax.set_ylabel(ylabel, color="white")
        ax.set_ylim(y_range)
        canvas.draw()
    except Exception as e:
        print(f"Error updating plot: {e}")


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


# Create the main window
root = tk.Tk()
root.title("Hydroponics Data Viewer")
root.geometry("800x480")
root.configure(bg="black")

# Arduino status label and light
status_frame = tk.Frame(root, bg="black")
status_frame.pack(pady=5)
status_label = tk.Label(status_frame, text="Arduino Status", font=("Arial", 12), fg="white", bg="black")
status_label.pack(side=tk.LEFT)
status_light = tk.Label(status_frame, text="  ", bg="red", width=2, height=1)
status_light.pack(side=tk.LEFT, padx=5)

# Left frame for buttons
button_frame = tk.Frame(root, bg="black")
button_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

# Right frame for plot with white border
plot_frame = tk.Frame(root, bg="black", highlightbackground="white", highlightthickness=2)
plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

# Add buttons
button_size = {"width": 15, "height": 1}
buttons = [
    ("pH", show_ph),
    ("Temperature", show_temp),
    ("EC", show_ec),
    ("TDS", show_tds),
    ("Water Level", show_water_level),
]
for text, command in buttons:
    btn = tk.Button(button_frame, text=text, font=("Arial", 12), command=command, **button_size, bg="#444444", fg="black")
    btn.pack(pady=5)

# Add Close button
close_button = tk.Button(button_frame, text="Close", font=("Arial", 12), command=close_program,
                         **button_size, bg="#FF3333", fg="black")
close_button.pack(pady=5)

# Initialize matplotlib figure
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Default plot
show_ph()

# Start Arduino status updates
root.after(500, update_arduino_status)

# Periodically fetch Arduino data
root.after(1000, read_arduino_data)

# Run the main loop
root.mainloop()