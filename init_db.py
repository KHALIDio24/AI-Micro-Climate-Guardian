import sqlite3

conn = sqlite3.connect("guardian.db")
cursor = conn.cursor()

# Create table for sensor readings
cursor.execute("""
CREATE TABLE IF NOT EXISTS sensor_readings (
    timestamp TEXT,
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

print("Database and table 'sensor_readings' created!")