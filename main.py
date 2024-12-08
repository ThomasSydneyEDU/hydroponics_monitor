import tkinter as tk
import random

# Set typical ranges and standard deviations for each sensor
SENSOR_RANGES = {
    "water_level": (0.0, 1.0, 0.05),  # Water level in meters (0-1m)
    "water_temp": (20.0, 30.0, 0.4),  # Water temperature in °C
    "ec": (0.5, 2.5, 0.1),  # Electrical conductivity in mS/cm
    "tds": (0, 500, 20),  # Total dissolved solids in ppm
    "ph": (5.5, 7.5, 0.2),  # pH level (5.5-7.5)
}

def simulate_sensor_data():
    """Simulate sensor data based on typical ranges and standard deviations."""
    water_level = random.gauss((SENSOR_RANGES["water_level"][0] + SENSOR_RANGES["water_level"][1]) / 2, SENSOR_RANGES["water_level"][2])
    water_temp = random.gauss((SENSOR_RANGES["water_temp"][0] + SENSOR_RANGES["water_temp"][1]) / 2, SENSOR_RANGES["water_temp"][2])
    ec = random.gauss((SENSOR_RANGES["ec"][0] + SENSOR_RANGES["ec"][1]) / 2, SENSOR_RANGES["ec"][2])
    tds = random.gauss((SENSOR_RANGES["tds"][0] + SENSOR_RANGES["tds"][1]) / 2, SENSOR_RANGES["tds"][2])
    ph = random.gauss((SENSOR_RANGES["ph"][0] + SENSOR_RANGES["ph"][1]) / 2, SENSOR_RANGES["ph"][2])
    
    # Clip values to realistic ranges
    water_level = max(SENSOR_RANGES["water_level"][0], min(SENSOR_RANGES["water_level"][1], water_level))
    water_temp = max(SENSOR_RANGES["water_temp"][0], min(SENSOR_RANGES["water_temp"][1], water_temp))
    ec = max(SENSOR_RANGES["ec"][0], min(SENSOR_RANGES["ec"][1], ec))
    tds = max(SENSOR_RANGES["tds"][0], min(SENSOR_RANGES["tds"][1], tds))
    ph = max(SENSOR_RANGES["ph"][0], min(SENSOR_RANGES["ph"][1], ph))
    
    return water_level, water_temp, ec, tds, ph

def update_display():
    """Update the display with simulated sensor data."""
    water_level, water_temp, ec, tds, ph = simulate_sensor_data()
    water_level_label.config(text=f"Water Level: {water_level:.2f} m")
    water_temp_label.config(text=f"Water Temp: {water_temp:.1f}°C")
    ec_label.config(text=f"EC: {ec:.2f} mS/cm")
    tds_label.config(text=f"TDS: {tds:.1f} ppm")
    ph_label.config(text=f"pH: {ph:.1f}")
    root.after(1000, update_display)  # Update every second

# Create the main window
root = tk.Tk()
root.title("Hydroponics Dashboard")
root.geometry("480x320")  # Size for Raspberry Pi touchscreen

# Add labels to display sensor data
water_level_label = tk.Label(root, text="Water Level: -- m", font=("Arial", 16))
water_level_label.pack(pady=5)

water_temp_label = tk.Label(root, text="Water Temp: --°C", font=("Arial", 16))
water_temp_label.pack(pady=5)

ec_label = tk.Label(root, text="EC: -- mS/cm", font=("Arial", 16))
ec_label.pack(pady=5)

tds_label = tk.Label(root, text="TDS: -- ppm", font=("Arial", 16))
tds_label.pack(pady=5)

ph_label = tk.Label(root, text="pH: --", font=("Arial", 16))
ph_label.pack(pady=5)

# Start updating the display
root.after(1000, update_display)

# Run the main loop
root.mainloop()