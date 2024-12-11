import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("hydroponics_data.db")
cursor = conn.cursor()

# Query the data
cursor.execute("SELECT * FROM sensor_data LIMIT 10")
rows = cursor.fetchall()

# Print the data
for row in rows:
    print(row)

# Close the connection
conn.close()