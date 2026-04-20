import requests
import sqlite3
from datetime import datetime
import json
import os
from typing import Optional, Dict

DB_PATH = "guardian.db"

class RealTimeDataFetcher:
    def __init__(self):
        self.db_path = DB_PATH
        # Using free APIs without API keys (with rate limits)
        # For production, get free API keys from these services
        
    def get_weather_simulated(self, city: str = "London") -> Optional[Dict]:
        """Simulated weather data (for demo without API keys)"""
        # This simulates real API data - replace with actual API calls
        import random
        
        weather_data = {
            "London": {"temp": 12, "humidity": 75, "wind": 5},
            "Paris": {"temp": 14, "humidity": 70, "wind": 4},
            "New York": {"temp": 8, "humidity": 65, "wind": 6},
            "Tokyo": {"temp": 16, "humidity": 60, "wind": 3}
        }
        
        data = weather_data.get(city, weather_data["London"])
        
        # Add some randomness for realism
        return {
            'temperature': data['temp'] + random.uniform(-2, 2),
            'humidity': data['humidity'] + random.uniform(-5, 5),
            'pressure': 1013 + random.uniform(-10, 10),
            'wind_speed': data['wind'] + random.uniform(-1, 1),
            'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
            'rainfall': random.uniform(0, 2) if random.random() > 0.7 else 0,
            'uv_index': random.uniform(0, 5),
            'source_api': 'SimulatedWeatherAPI',
            'timestamp': datetime.now()
        }
    
    def get_air_quality_simulated(self, lat: float = 51.5074, lon: float = -0.1278) -> Optional[Dict]:
        """Simulated air quality data (for demo without API keys)"""
        import random
        
        # Simulate different air quality levels based on location
        # Major cities have worse air quality typically
        city_aqi = {
            (51.5074, -0.1278): 45,  # London - Good
            (48.8566, 2.3522): 55,   # Paris - Moderate
            (40.7128, -74.0060): 65, # New York - Moderate
            (35.6762, 139.6503): 70  # Tokyo - Moderate
        }
        
        base_aqi = city_aqi.get((round(lat, 4), round(lon, 4)), 50)
        
        return {
            'air_quality_index': max(0, min(300, base_aqi + random.randint(-15, 15))),
            'pm25': max(0, min(150, base_aqi * 0.8 + random.uniform(-10, 20))),
            'pm10': max(0, min(200, base_aqi * 1.2 + random.uniform(-15, 25))),
            'no2': random.uniform(10, 50),
            'o3': random.uniform(20, 60),
            'co': random.uniform(100, 400),
            'so2': random.uniform(1, 10),
            'source_api': 'SimulatedAQI',
            'timestamp': datetime.now()
        }
    
    def save_external_data(self, data_type: str, data: Dict):
        """Save external data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO external_data 
            (data_type, temperature, humidity, pressure, wind_speed, wind_direction, 
             rainfall, uv_index, air_quality_index, pm25, pm10, no2, o3, co, so2, 
             location_lat, location_lon, source_api, raw_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data_type,
            data.get('temperature'),
            data.get('humidity'),
            data.get('pressure'),
            data.get('wind_speed'),
            data.get('wind_direction'),
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
            data.get('source_api'),
            json.dumps(data.get('raw_data', {}))
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Saved {data_type} data to database")

# Global fetcher instance
fetcher = RealTimeDataFetcher()

def fetch_and_store_real_time_data(city: str = "London", lat: float = 51.5074, lon: float = -0.1278):
    """Fetch and store all real-time data sources"""
    results = {}
    
    # Fetch simulated weather data
    weather = fetcher.get_weather_simulated(city)
    if weather:
        weather['location_lat'] = lat
        weather['location_lon'] = lon
        fetcher.save_external_data('weather', weather)
        results['weather'] = weather
    
    # Fetch simulated air quality
    aqi = fetcher.get_air_quality_simulated(lat, lon)
    if aqi:
        aqi['location_lat'] = lat
        aqi['location_lon'] = lon
        fetcher.save_external_data('air_quality', aqi)
        results['air_quality'] = aqi
    
    return results

if __name__ == "__main__":
    # Test the fetcher
    print("Testing real-time data fetcher...")
    data = fetch_and_store_real_time_data("New York", 40.7128, -74.0060)
    print("Fetched data:", data)