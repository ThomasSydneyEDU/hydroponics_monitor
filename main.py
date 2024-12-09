import tkinter as tk
import serial
import time

# Try to connect to the Arduino
try:
    arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Replace with your actual port
    time.sleep(2)  # Wait for the connection to initialize
    arduino_connected = True
except serial.SerialException:
    arduino_connected = False

# Create the main window
root = tk.Tk()
root.title("Hydroponics Dashboard")
root.geometry("480x320")  # Size for Raspberry Pi touchscreen

# Add labels to display sensor data or status
status_label = tk.Label(root, text="", font=("Arial", 20), fg="red")
status_label.pack(pady=20)

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

def update_display():
    """Update the display with data from Arduino or show disconnected status."""
    global arduino_connected

    if arduino_connected:
        try:
            if arduino.in_waiting > 0:
                line = arduino.readline().decode('utf-8').strip()
                data = dict(item.split(':') for item in line.split(','))

                # Update labels with data from Arduino
                water_level_label.config(text=f"Water Level: {data['WATER_LEVEL']} m")
                water_temp_label.config(text=f"Water Temp: {data['WATER_TEMP']}°C")
                ec_label.config(text=f"EC: {data['EC']} mS/cm")
                tds_label.config(text=f"TDS: {data['TDS']} ppm")
                ph_label.config(text=f"pH: {data['PH']}")
                status_label.config(text="Arduino Connected", fg="green")
        except Exception as e:
            # Handle disconnection or data errors
            print(f"Error: {e}")
            arduino_connected = False
            status_label.config(text="Arduino Not Connected", fg="red")
            reset_labels()
    else:
        status_label.config(text="Arduino Not Connected", fg="red")
        reset_labels()

    root.after(1000, update_display)  # Update every second

def reset_labels():
    """Reset the sensor labels to default values."""
    water_level_label.config(text="Water Level: -- m")
    water_temp_label.config(text="Water Temp: --°C")
    ec_label.config(text="EC: -- mS/cm")
    tds_label.config(text="TDS: -- ppm")
    ph_label.config(text="pH: --")

# Start updating the display
root.after(1000, update_display)

# Run the main loop
root.mainloop()