"""
Sensor Integration for BMP280, BH1750, PMS5003
Pure Python simulation mode - No hardware dependencies required
Works on any computer without additional libraries
"""

import time
from datetime import datetime
import random
import math

# ============================================
# CONFIGURATION
# ============================================

# Set to True only if you have real sensors on Raspberry Pi with libraries installed
USE_REAL_SENSORS = False  

# ============================================
# BMP280 SIMULATOR - Temperature, Pressure & Humidity
# ============================================

class BMP280Sensor:
    """BMP280 - Temperature, Pressure & Humidity Sensor (Simulated)"""
    
    @staticmethod
    def read():
        """Read temperature (C), pressure (hPa), and humidity (%)"""
        # Always use simulation mode to avoid hardware imports
        return BMP280Sensor._simulate()
    
    @staticmethod
    def _simulate():
        """Generate realistic simulated BMP280 data"""
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        time_of_day = hour + minute / 60
        
        # Daily temperature cycle - warmer in afternoon, cooler at night
        if 6 <= time_of_day <= 18:
            # Daytime: peak at 2 PM (14:00)
            peak_temp = 24
            variation = -3 * ((time_of_day - 14) / 8) ** 2 + 3
        else:
            # Nighttime: cooler
            if time_of_day > 18:
                hours_since_evening = time_of_day - 18
            else:
                hours_since_evening = time_of_day + 6
            variation = -2 * (hours_since_evening / 12) ** 2
        
        base_temp = 22
        temperature = base_temp + variation + random.uniform(-0.5, 0.5)
        
        # Pressure simulation (normal range: 990-1030 hPa)
        pressure = 1013 + math.sin(hour * math.pi / 12) * 5 + random.uniform(-3, 3)
        
        # Humidity simulation (inverse relationship with temperature)
        humidity = 55 - (temperature - 20) * 0.8 + random.uniform(-5, 5)
        
        return {
            'temperature': round(max(15, min(35, temperature)), 1),
            'pressure': round(max(980, min(1040, pressure)), 1),
            'humidity': round(max(30, min(80, humidity)), 1)
        }

# ============================================
# BH1750 SIMULATOR - Light Intensity
# ============================================

class BH1750Sensor:
    """BH1750 - Light Intensity Sensor (Lux) - Simulated"""
    
    @staticmethod
    def read():
        """Read light intensity in Lux"""
        return BH1750Sensor._simulate()
    
    @staticmethod
    def _simulate():
        """Generate realistic simulated light data based on time of day"""
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        time_of_day = hour + minute / 60
        
        if 8 <= time_of_day <= 17:  # Daytime
            # Peak at noon (12:00)
            peak_light = 500
            variation = -peak_light * ((time_of_day - 12.5) / 5) ** 2
            light = peak_light + variation + random.uniform(-50, 100)
        elif 6 <= time_of_day < 8:  # Morning sunrise
            light = 50 + (time_of_day - 6) * 100 + random.uniform(-20, 50)
        elif 17 < time_of_day <= 19:  # Evening sunset
            light = 500 - (time_of_day - 17) * 150 + random.uniform(-50, 20)
        else:  # Nighttime
            light = 15 + random.uniform(0, 25)
        
        return {'light_intensity': round(max(5, min(1000, light)), 1)}

# ============================================
# PMS5003 SIMULATOR - Air Quality
# ============================================

class PMS5003Sensor:
    """PMS5003 - Air Quality Sensor (PM1.0, PM2.5, PM10) - Simulated"""
    
    @staticmethod
    def read():
        """Read particulate matter concentrations"""
        return PMS5003Sensor._simulate()
    
    @staticmethod
    def _simulate():
        """Generate realistic simulated air quality data"""
        now = datetime.now()
        hour = now.hour
        
        # Higher pollution during daytime and rush hours
        if 8 <= hour <= 10 or 17 <= hour <= 19:  # Rush hours
            multiplier = 1.5
        elif 10 < hour < 17:  # Daytime
            multiplier = 1.2
        else:  # Nighttime
            multiplier = 0.6
        
        # Base values
        base_pm1 = 10
        base_pm25 = 20
        base_pm10 = 30
        
        return {
            'pm1_0': round(base_pm1 * multiplier + random.uniform(-3, 8), 1),
            'pm2_5': round(base_pm25 * multiplier + random.uniform(-5, 12), 1),
            'pm10': round(base_pm10 * multiplier + random.uniform(-8, 15), 1)
        }

# ============================================
# SENSOR MANAGER
# ============================================

class SensorManager:
    """Main sensor manager - combines all sensors"""
    
    def __init__(self):
        self.bmp280 = BMP280Sensor()
        self.bh1750 = BH1750Sensor()
        self.pms5003 = PMS5003Sensor()
        self.initialized = True
    
    def init_sensors(self):
        """Initialize sensors - always returns True for simulation mode"""
        print("✅ Sensor system ready (Simulation Mode)")
        return True
    
    def read_all(self, room_name=""):
        """Read all sensors and return combined data"""
        data = {
            'room_name': room_name,
            'timestamp': datetime.now().isoformat(),
            **self.bmp280.read(),
            **self.bh1750.read(),
            **self.pms5003.read()
        }
        return data
    
    def get_status(self):
        """Get sensor system status"""
        return {
            'use_real_sensors': False,
            'simulation_mode': True,
            'sensors': ['BMP280', 'BH1750', 'PMS5003']
        }

# ============================================
# GLOBAL INSTANCE
# ============================================

# Create global sensor manager instance
sensor_manager = SensorManager()

def get_sensor_data(room_name):
    """Get sensor data for a specific room"""
    return sensor_manager.read_all(room_name)

# ============================================
# TEST FUNCTION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Sensor Integration (Simulation Mode)")
    print("=" * 50)
    
    # Initialize sensors
    sensor_manager.init_sensors()
    
    print("\n📡 Reading sensor data...\n")
    
    # Read sensors multiple times
    for i in range(3):
        print(f"Reading {i+1}:")
        data = get_sensor_data("Test Room")
        print(f"   🌡️ BMP280:")
        print(f"      Temperature: {data['temperature']}°C")
        print(f"      Pressure: {data['pressure']} hPa")
        print(f"      Humidity: {data['humidity']}%")
        print(f"   💡 BH1750:")
        print(f"      Light Intensity: {data['light_intensity']} lux")
        print(f"   🌫️ PMS5003:")
        print(f"      PM1.0: {data['pm1_0']} µg/m³")
        print(f"      PM2.5: {data['pm2_5']} µg/m³")
        print(f"      PM10: {data['pm10']} µg/m³")
        print()
        time.sleep(1)
    
    print("=" * 50)
    print("✅ Sensor integration test complete!")
    print("📡 Mode: Simulation (no hardware required)")
    print("=" * 50)