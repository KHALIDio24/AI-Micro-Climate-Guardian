# simulate_live_data.py
import requests
import random
import time

URL = "http://127.0.0.1:8000/sensor-data"  # FastAPI endpoint
LOCATIONS = ["room1", "room2", "room3"]

while True:
    for loc in LOCATIONS:
        data = {
            "temperature": round(random.uniform(20, 35), 2),
            "humidity": round(random.uniform(30, 90), 2),
            "lux": round(random.uniform(100, 1000), 2),
            "uv_index": round(random.uniform(0, 12), 2),
            "pm25": round(random.uniform(5, 100), 2),
            "location_tag": loc
        }
        try:
            resp = requests.post(URL, json=data)
            print(f"Sent: {data} → Response: {resp.json()}")
        except Exception as e:
            print("Error:", e)
    time.sleep(15)  # every 15 seconds