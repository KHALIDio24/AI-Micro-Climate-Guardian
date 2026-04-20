import requests
import random
import time
from datetime import datetime

API_URL = "http://localhost:8000"
LOCATIONS = ["Main Gallery", "Archive Room", "Conservation Lab", "Storage Vault"]

print("=" * 60)
print("📡 Micro-Climate Sensor Simulator")
print("=" * 60)
print(f"📍 Simulating sensors at: {', '.join(LOCATIONS)}")
print(f"🔄 Sending data every 10 seconds")
print("Press Ctrl+C to stop\n")

def generate_realistic_data(location):
    """Generate realistic sensor data for different locations"""
    location_profiles = {
        "Main Gallery": {"temp": 22, "humidity": 50, "lux": 300, "uv": 1, "pm25": 20},
        "Archive Room": {"temp": 18, "humidity": 45, "lux": 100, "uv": 0.5, "pm25": 15},
        "Conservation Lab": {"temp": 21, "humidity": 55, "lux": 500, "uv": 2, "pm25": 10},
        "Storage Vault": {"temp": 15, "humidity": 40, "lux": 50, "uv": 0, "pm25": 25}
    }
    
    profile = location_profiles.get(location, location_profiles["Main Gallery"])
    hour = datetime.now().hour
    
    # Add daily variation
    day_factor = 2 * (hour - 14) / 12 if 8 <= hour <= 20 else 0
    
    return {
        "temperature": round(profile["temp"] + day_factor + random.uniform(-1, 1), 1),
        "humidity": round(profile["humidity"] + random.uniform(-3, 3), 1),
        "lux": round(profile["lux"] + random.uniform(-50, 100) + (200 if 10 <= hour <= 16 else 0), 0),
        "uv_index": round(profile["uv"] + random.uniform(-0.3, 0.5) + (1 if 12 <= hour <= 14 else 0), 1),
        "pm25": round(profile["pm25"] + random.uniform(-5, 10), 1),
        "location_tag": location,
        "battery_level": round(random.uniform(85, 100), 1),
        "x": random.randint(0, 100),
        "y": random.randint(0, 100)
    }

while True:
    for location in LOCATIONS:
        data = generate_realistic_data(location)
        
        try:
            response = requests.post(f"{API_URL}/api/sensor-data", json=data, timeout=5)
            if response.status_code == 200:
                print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] {location:20} | "
                      f"🌡️{data['temperature']:4.1f}°C | "
                      f"💧{data['humidity']:4.1f}% | "
                      f"🌫️{data['pm25']:4.1f}µg")
            else:
                print(f"❌ Error {response.status_code}: {location}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Cannot connect to API at {API_URL}")
            print("   Make sure API is running: python unified_api.py")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("-" * 60)
    time.sleep(10)