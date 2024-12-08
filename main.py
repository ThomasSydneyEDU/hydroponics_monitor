import serial

def read_sensor_data():
    with serial.Serial('/dev/ttyUSB0', 9600) as ser:
        while True:
            data = ser.readline().decode('utf-8').strip()
            print(f"Sensor data: {data}")

if __name__ == "__main__":
    read_sensor_data()