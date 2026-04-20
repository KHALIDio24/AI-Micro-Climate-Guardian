import requests
import sqlite3
from datetime import datetime
import json
import random
from typing import Optional, Dict

DB_PATH = "guardian.db"

class RealTimeDataFetcher:
    def __init__(self):
        self.db_path = DB_PATH
        
    def get_weather_data(self, city: str = "London") -> Optional[Dict]:
        """Fetch simulated weather data (no API key needed for demo)"""
        # Simulated weather database
        weather_db = {
            "London": {"temp": 12, "humidity": 75, "wind": 5, "pressure": 1013},
            "Paris": {"temp": 14, "humidity": 70, "wind": 4, "pressure": 1015},
            "New York": {"temp": 8, "humidity": 65, "wind": 6, "pressure": 1012},
            "Tokyo": {"temp": 16, "humidity": 60, "wind": 3, "pressure": 1014},
        }
        
        data = weather_db.get(city, weather_db["London"])
        
        return {
            'temperature': round(data['temp'] + random.uniform(-2, 2), 1),
            'humidity': round(data['humidity'] + random.uniform(-5, 5), 1),
            'pressure': round(data['pressure'] + random.uniform(-5, 5), 1),
            'wind_speed': round(data['wind'] + random.uniform(-1, 1), 1),
            'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
            'rainfall': round(random.uniform(0, 2) if random.random() > 0.7 else 0, 1),
            'uv_index': round(random.uniform(0, 5), 1),
            'source_api': 'SimulatedWeatherAPI'
        }
    
    def get_air_quality_data(self, lat: float = 51.5074, lon: float = -0.1278) -> Optional[Dict]:
        """Fetch simulated air quality data"""
        base_aqi = 50 + random.randint(-20, 20)
        
        return {
            'air_quality_index': max(0, min(300, base_aqi)),
            'pm25': round(max(0, min(150, base_aqi * 0.8 + random.uniform(-10, 20))), 1),
            'pm10': round(max(0, min(200, base_aqi * 1.2 + random.uniform(-15, 25))), 1),
            'no2': round(random.uniform(10, 50), 1),
            'o3': round(random.uniform(20, 60), 1),
            'co': round(random.uniform(100, 400), 1),
            'so2': round(random.uniform(1, 10), 1),
            'source_api': 'SimulatedAQI'
        }
    
    def save_external_data(self, data_type: str, data: Dict):
        """Save external data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS external_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_type TEXT,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_speed REAL,
                wind_direction TEXT,
                rainfall REAL,
                uv_index REAL,
                air_quality_index INTEGER,
                pm25 REAL,
                pm10 REAL,
                no2 REAL,
                o3 REAL,
                co REAL,
                so2 REAL,
                location_lat REAL,
                location_lon REAL,
                source_api TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO external_data 
            (data_type, temperature, humidity, pressure, wind_speed, wind_direction, 
             rainfall, uv_index, air_quality_index, pm25, pm10, no2, o3, co, so2, 
             location_lat, location_lon, source_api)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data_type,
            data.get('temperature'),
            data.get('humidity'),
            data.get('pressure'),
            data.get('wind_speed'),
            str(data.get('wind_direction')),
            data.get('rainfall'),
            data.get('uv_index'),
            data.get('air_quality_index'),
            data.get('pm25'),
            data.get('pm10'),
            data.get('no2'),
            data.get('o3'),
            data.get('co'),
            data.get('so2'),
            data.get('location_lat'),
            data.get('location_lon'),
            data.get('source_api')
        ))
        
        conn.commit()
        conn.close()

# Global fetcher instance
fetcher = RealTimeDataFetcher()

def fetch_and_store_real_time_data(city: str = "London", lat: float = 51.5074, lon: float = -0.1278):
    """Fetch and store all real-time data sources"""
    results = {}
    
    # Fetch weather data
    weather = fetcher.get_weather_data(city)
    if weather:
        weather['location_lat'] = lat
        weather['location_lon'] = lon
        fetcher.save_external_data('weather', weather)
        results['weather'] = weather
        print(f"   ✓ Weather data saved for {city}")
    
    # Fetch air quality
    aqi = fetcher.get_air_quality_data(lat, lon)
    if aqi:
        aqi['location_lat'] = lat
        aqi['location_lon'] = lon
        fetcher.save_external_data('air_quality', aqi)
        results['air_quality'] = aqi
        print(f"   ✓ Air quality data saved for {city}")
    
    return results

if __name__ == "__main__":
    # Test the fetcher
    print("Testing real-time data fetcher...")
    data = fetch_and_store_real_time_data("London", 51.5074, -0.1278)
    print("Fetched data:", data)