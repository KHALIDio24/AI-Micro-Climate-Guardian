import sqlite3

# Connect or create database
conn = sqlite3.connect("guardian.db")
cursor = conn.cursor()

# Create table to store sensor readings
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    lux REAL,
    uv_index REAL,
    pm25 REAL,
    location_tag TEXT
)
""")

conn.commit()
conn.close()
print("Database created successfully!")