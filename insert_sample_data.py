import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect("guardian.db")
cursor = conn.cursor()

locations = ["room1", "room2", "room3"]

for i in range(30):  # last 30 days
    for loc in locations:
        cursor.execute("""
        INSERT INTO sensor_readings (timestamp, temperature, humidity, lux, uv_index, pm25, location_tag)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            (datetime.now() - timedelta(days=i)).isoformat(),
            round(random.uniform(20, 35), 2),
            round(random.uniform(30, 90), 2),
            round(random.uniform(100, 1000), 2),
            round(random.uniform(0, 10), 2),
            round(random.uniform(5, 50), 2),
            loc
        ))

conn.commit()
conn.close()
print("Sample data inserted into sensor_readings!")