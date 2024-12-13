from google.cloud import firestore
import pandas as pd
import matplotlib.pyplot as plt

# Firestore setup
def initialize_firestore():
    """
    Initialize Firestore using the service account key.
    """
    return firestore.Client.from_service_account_json("/Users/tcar5787/APIKeys/hydro_web_interface/serviceAccountKey.json")

# Fetch data from Firestore
def fetch_data_from_firestore(db):
    """
    Fetch sensor data from Firestore and return as a Pandas DataFrame.
    """
    try:
        # Reference Firestore collection
        collection_ref = db.collection("sensor_readings")
        docs = collection_ref.stream()

        # Extract data into a list of dictionaries
        data = []
        for doc in docs:
            doc_data = doc.to_dict()
            # Convert Firestore timestamp to Python datetime
            if 'timestamp' in doc_data and doc_data['timestamp']:
                doc_data['timestamp'] = doc_data['timestamp'].timestamp()  # Convert to a POSIX timestamp
            data.append(doc_data)

        # Create a Pandas DataFrame
        df = pd.DataFrame(data)
        # Convert the POSIX timestamp back to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Sort the DataFrame by timestamp
        df.sort_values(by='timestamp', inplace=True)

        return df
    except Exception as e:
        print(f"Error fetching data from Firestore: {e}")
        return None

# Plot the data
def plot_data(df):
    """
    Plot sensor data using Matplotlib.
    """
    if df is None or df.empty:
        print("No data available to plot.")
        return

    # Set timestamp as the DataFrame index
    df.set_index('timestamp', inplace=True)

    # Create plots for each sensor type
    plt.figure(figsize=(12, 8))

    # Water Level
    plt.subplot(3, 2, 1)
    plt.plot(df.index, df['water_level'], label='Water Level')
    plt.title('Water Level')
    plt.xlabel('Time')
    plt.ylabel('Level')
    plt.grid(True)

    # Water Temperature
    plt.subplot(3, 2, 2)
    plt.plot(df.index, df['water_temp'], label='Water Temp', color='orange')
    plt.title('Water Temperature')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)

    # EC
    plt.subplot(3, 2, 3)
    plt.plot(df.index, df['ec'], label='EC', color='green')
    plt.title('Electrical Conductivity (EC)')
    plt.xlabel('Time')
    plt.ylabel('EC')
    plt.grid(True)

    # TDS
    plt.subplot(3, 2, 4)
    plt.plot(df.index, df['tds'], label='TDS', color='purple')
    plt.title('Total Dissolved Solids (TDS)')
    plt.xlabel('Time')
    plt.ylabel('TDS')
    plt.grid(True)

    # pH
    plt.subplot(3, 2, 5)
    plt.plot(df.index, df['ph'], label='pH', color='red')
    plt.title('pH Levels')
    plt.xlabel('Time')
    plt.ylabel('pH')
    plt.grid(True)

    # Adjust layout
    plt.tight_layout()
    plt.show()

def main():
    # Initialize Firestore
    db = initialize_firestore()

    # Fetch data
    df = fetch_data_from_firestore(db)
    if df is not None:
        print("Fetched data:")
        print(df.head())

        # Plot the data
        plot_data(df)
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()