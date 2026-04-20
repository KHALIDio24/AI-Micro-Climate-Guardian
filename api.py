from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
import threading
import time
import random
import uvicorn

app = FastAPI(title="Unified Micro-Climate Guardian API", version="3.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "guardian.db"

# ============================================
# DATABASE FUNCTIONS
# ============================================

def init_db():
    """Initialize database with multi-source support"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Main sensor readings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        lux REAL,
        uv_index REAL,
        pm25 REAL,
        location_tag TEXT,
        x INTEGER DEFAULT 0,
        y INTEGER DEFAULT 0,
        battery_level REAL DEFAULT 100,
        data_source TEXT DEFAULT 'sensor'
    )
    """)
    
    # External real-time data table
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
    
    # Manual inputs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manual_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        humidity REAL,
        condition_notes TEXT,
        location_tag TEXT,
        user_name TEXT
    )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_external_timestamp ON external_data(timestamp)")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def insert_sensor_reading(reading):
    """Insert sensor reading"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensor_readings 
        (temperature, humidity, lux, uv_index, pm25, location_tag, x, y, battery_level, data_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reading.get('temperature'),
        reading.get('humidity'),
        reading.get('lux', 0),
        reading.get('uv_index', 0),
        reading.get('pm25', 0),
        reading.get('location_tag'),
        reading.get('x', 0),
        reading.get('y', 0),
        reading.get('battery_level', 100),
        'sensor'
    ))
    conn.commit()
    conn.close()

def insert_manual_reading(reading):
    """Insert manual reading"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO manual_readings (temperature, humidity, condition_notes, location_tag, user_name)
        VALUES (?, ?, ?, ?, ?)
    """, (
        reading.get('temperature'),
        reading.get('humidity'),
        reading.get('condition_notes'),
        reading.get('location_tag'),
        reading.get('user_name')
    ))
    conn.commit()
    conn.close()

def insert_external_data(data_type, data):
    """Insert external API data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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

# ============================================
# REAL-TIME DATA FUNCTIONS (No external imports needed)
# ============================================

def fetch_weather_data(city="London", lat=None, lon=None):
    """Fetch simulated weather data (no API key needed)"""
    weather_db = {
        "London": {"temp": 12, "humidity": 75, "wind": 5, "pressure": 1013},
        "Paris": {"temp": 14, "humidity": 70, "wind": 4, "pressure": 1015},
        "New York": {"temp": 8, "humidity": 65, "wind": 6, "pressure": 1012},
        "Tokyo": {"temp": 16, "humidity": 60, "wind": 3, "pressure": 1014},
        "Sydney": {"temp": 22, "humidity": 55, "wind": 4, "pressure": 1016},
        "Dubai": {"temp": 28, "humidity": 45, "wind": 3, "pressure": 1010},
        "Mumbai": {"temp": 30, "humidity": 70, "wind": 2, "pressure": 1008},
        "Singapore": {"temp": 27, "humidity": 80, "wind": 3, "pressure": 1009}
    }
    
    data = weather_db.get(city, weather_db["London"])
    
    # Add randomness for realism
    return {
        'temperature': round(data['temp'] + random.uniform(-3, 3), 1),
        'humidity': round(data['humidity'] + random.uniform(-10, 10), 1),
        'pressure': round(data['pressure'] + random.uniform(-5, 5), 1),
        'wind_speed': round(data['wind'] + random.uniform(-1, 1), 1),
        'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
        'rainfall': round(random.uniform(0, 2) if random.random() > 0.7 else 0, 1),
        'uv_index': round(random.uniform(0, 6), 1),
        'source_api': 'SimulatedWeatherAPI'
    }

def fetch_air_quality_data(lat=51.5074, lon=-0.1278):
    """Fetch simulated air quality data"""
    # Different air quality based on location
    distance_from_center = min(abs(lat - 51.5) + abs(lon + 0.1), 1) * 100
    base_aqi = int(30 + distance_from_center * 2)
    
    return {
        'air_quality_index': max(0, min(300, base_aqi + random.randint(-15, 15))),
        'pm25': round(max(0, min(150, base_aqi * 0.8 + random.uniform(-10, 20))), 1),
        'pm10': round(max(0, min(200, base_aqi * 1.2 + random.uniform(-15, 25))), 1),
        'no2': round(random.uniform(10, 50), 1),
        'o3': round(random.uniform(20, 60), 1),
        'co': round(random.uniform(100, 400), 1),
        'so2': round(random.uniform(1, 10), 1),
        'source_api': 'SimulatedAQI'
    }

def fetch_and_store_real_time_data(city="London", lat=51.5074, lon=-0.1278):
    """Fetch and store all real-time data"""
    results = {}
    
    # Fetch weather data
    weather = fetch_weather_data(city, lat, lon)
    if weather:
        weather['location_lat'] = lat
        weather['location_lon'] = lon
        insert_external_data('weather', weather)
        results['weather'] = weather
        print(f"✅ Weather data saved for {city}")
    
    # Fetch air quality
    aqi = fetch_air_quality_data(lat, lon)
    if aqi:
        aqi['location_lat'] = lat
        aqi['location_lon'] = lon
        insert_external_data('air_quality', aqi)
        results['air_quality'] = aqi
        print(f"✅ Air quality data saved for {city}")
    
    return results

# ============================================
# BACKGROUND TASK (No external file needed)
# ============================================

background_running = False
background_thread = None

def background_data_updater():
    """Background thread to update external data periodically"""
    global background_running
    print("🔄 Background data updater thread started")
    
    while background_running:
        try:
            print(f"\n📡 Fetching external data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Cities to update
            cities = [
                ("London", 51.5074, -0.1278),
                ("Paris", 48.8566, 2.3522),
                ("New York", 40.7128, -74.0060),
                ("Tokyo", 35.6762, 139.6503),
            ]
            
            for city, lat, lon in cities:
                fetch_and_store_real_time_data(city, lat, lon)
                time.sleep(2)  # Small delay between cities
            
            print(f"✅ Background update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Background update error: {e}")
        
        # Wait for 1 hour before next update
        for _ in range(3600):  # 3600 seconds = 1 hour
            if not background_running:
                break
            time.sleep(1)
    
    print("🛑 Background data updater stopped")

def start_background_updater():
    """Start the background updater thread"""
    global background_running, background_thread
    
    if background_running:
        print("Background updater already running")
        return
    
    background_running = True
    background_thread = threading.Thread(target=background_data_updater, daemon=True)
    background_thread.start()
    print("✅ Background data updater started (updates every hour)")

def stop_background_updater():
    """Stop the background updater thread"""
    global background_running
    background_running = False
    print("🛑 Stopping background updater...")

# ============================================
# PYDANTIC MODELS
# ============================================

class SensorReading(BaseModel):
    temperature: float
    humidity: float
    lux: float
    uv_index: float
    pm25: float
    location_tag: str
    x: Optional[int] = 0
    y: Optional[int] = 0
    battery_level: Optional[float] = 100

class ManualReading(BaseModel):
    temperature: float
    humidity: float
    condition_notes: str
    location_tag: str
    user_name: str

class WeatherRequest(BaseModel):
    city: str = "London"
    lat: Optional[float] = None
    lon: Optional[float] = None

# ============================================
# API ENDPOINTS
# ============================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    init_db()
    start_background_updater()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    stop_background_updater()

@app.post("/api/sensor-data")
def receive_sensor_data(reading: SensorReading):
    """Receive data from IoT sensors"""
    try:
        data = reading.dict()
        insert_sensor_reading(data)
        return {"status": "success", "source": "sensor", "message": "Data saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/manual-reading")
def add_manual_reading(reading: ManualReading):
    """Add manual readings from user input"""
    try:
        data = reading.dict()
        insert_manual_reading(data)
        return {"status": "success", "source": "manual", "message": "Manual reading saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fetch-weather")
def fetch_weather(request: WeatherRequest):
    """Fetch current weather data on demand"""
    try:
        if request.lat and request.lon:
            data = fetch_and_store_real_time_data(request.city, request.lat, request.lon)
        else:
            data = fetch_and_store_real_time_data(request.city)
        return {"status": "success", "data": data, "message": "Weather data fetched and saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/combined-data/{location_tag}")
def get_combined_data(location_tag: str):
    """Get combined data from all sources"""
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Get latest sensor data
        sensor_query = """
            SELECT * FROM sensor_readings 
            WHERE location_tag = ? 
            ORDER BY timestamp DESC LIMIT 1
        """
        sensor_df = pd.read_sql(sensor_query, conn, params=(location_tag,))
        
        # Get latest external weather
        external_query = """
            SELECT * FROM external_data 
            WHERE data_type = 'weather'
            ORDER BY timestamp DESC LIMIT 1
        """
        weather_df = pd.read_sql(external_query, conn)
        
        # Get latest air quality
        aqi_query = """
            SELECT * FROM external_data 
            WHERE data_type = 'air_quality'
            ORDER BY timestamp DESC LIMIT 1
        """
        aqi_df = pd.read_sql(aqi_query, conn)
        
        # Get recent manual readings
        manual_query = """
            SELECT * FROM manual_readings 
            WHERE location_tag = ? 
            ORDER BY timestamp DESC LIMIT 5
        """
        manual_df = pd.read_sql(manual_query, conn, params=(location_tag,))
        
        return {
            'sensor_data': sensor_df.to_dict(orient='records')[0] if not sensor_df.empty else None,
            'weather_data': weather_df.to_dict(orient='records')[0] if not weather_df.empty else None,
            'air_quality': aqi_df.to_dict(orient='records')[0] if not aqi_df.empty else None,
            'manual_readings': manual_df.to_dict(orient='records') if not manual_df.empty else [],
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/api/risk-assessment/{location_tag}")
def get_risk_assessment(location_tag: str):
    """Enhanced risk assessment using all data sources"""
    combined = get_combined_data(location_tag)
    
    if not combined['sensor_data'] and not combined['manual_readings']:
        return {
            'risk_score': 0,
            'risk_level': 'NO DATA',
            'risk_color': 'gray',
            'alerts': ['No data available for this location'],
            'data_source': 'none',
            'data_sources_used': {
                'sensor': False,
                'weather_api': False,
                'air_quality_api': False,
                'manual_inputs': False
            }
        }
    
    # Use sensor data if available, otherwise use latest manual reading
    if combined['sensor_data']:
        current_data = combined['sensor_data']
        data_source = 'sensor'
    elif combined['manual_readings']:
        current_data = combined['manual_readings'][0]
        data_source = 'manual'
    else:
        current_data = {}
        data_source = 'none'
    
    weather = combined.get('weather_data', {})
    aqi = combined.get('air_quality', {})
    
    # Risk calculation
    risk_score = 0
    alerts = []
    
    # Temperature risk
    temp = current_data.get('temperature', 20)
    weather_temp = weather.get('temperature', 20) if weather else 20
    
    if temp > 30 or weather_temp > 28:
        risk_score += 30
        alerts.append("⚠️ HIGH: Temperature risk - Immediate attention needed")
    elif temp > 25 or weather_temp > 24:
        risk_score += 15
        alerts.append("🌡️ MEDIUM: Elevated temperature - Monitor closely")
    
    # Humidity risk
    humidity = current_data.get('humidity', 50)
    weather_humidity = weather.get('humidity', 50) if weather else 50
    
    if humidity > 75 or weather_humidity > 80:
        risk_score += 30
        alerts.append("💧 HIGH: Humidity - Mold growth risk")
    elif humidity > 60 or weather_humidity > 65:
        risk_score += 15
        alerts.append("💧 MEDIUM: Moderate humidity levels")
    
    # Air quality risk
    aqi_value = aqi.get('air_quality_index', 50) if aqi else 50
    pm25 = current_data.get('pm25', 15)
    
    if aqi_value > 150 or pm25 > 50:
        risk_score += 25
        alerts.append("🌫️ HIGH: Poor air quality - Risk to artifacts")
    elif aqi_value > 100 or pm25 > 35:
        risk_score += 15
        alerts.append("🌫️ MEDIUM: Moderate air quality concerns")
    
    # UV risk
    uv = current_data.get('uv_index', 0)
    if uv > 5:
        risk_score += 15
        alerts.append("☀️ HIGH: UV exposure - Artifact fading risk")
    elif uv > 3:
        risk_score += 8
        alerts.append("☀️ MEDIUM: UV levels - Consider protection")
    
    # Determine risk level
    if risk_score >= 60:
        level = "HIGH"
        color = "red"
    elif risk_score >= 30:
        level = "MEDIUM"
        color = "orange"
    else:
        level = "LOW"
        color = "green"
    
    return {
        'risk_score': risk_score,
        'risk_level': level,
        'risk_color': color,
        'alerts': alerts,
        'data_source': data_source,
        'data_sources_used': {
            'sensor': bool(combined['sensor_data']),
            'weather_api': bool(combined['weather_data']),
            'air_quality_api': bool(combined['air_quality']),
            'manual_inputs': bool(combined['manual_readings'])
        }
    }

@app.get("/api/locations")
def get_locations():
    """Get all available locations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT DISTINCT location_tag FROM sensor_readings UNION SELECT DISTINCT location_tag FROM manual_readings")
    locations = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    if not locations:
        locations = ["Main Gallery", "Archive Room", "Conservation Lab", "Storage Vault"]
    
    return {"locations": locations}

@app.get("/api/health")
def health_check():
    """API health check"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM sensor_readings")
    sensor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM external_data")
    external_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "sensor_readings": sensor_count,
        "external_data_points": external_count,
        "background_updater": "running" if background_running else "stopped"
    }

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "name": "Unified Micro-Climate Guardian API",
        "version": "3.0",
        "endpoints": {
            "sensor_data": "POST /api/sensor-data",
            "manual_reading": "POST /api/manual-reading",
            "fetch_weather": "POST /api/fetch-weather",
            "combined_data": "GET /api/combined-data/{location}",
            "risk_assessment": "GET /api/risk-assessment/{location}",
            "locations": "GET /api/locations",
            "health": "GET /api/health"
        }
    }

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Unified Micro-Climate Guardian API")
    print("=" * 60)
    print(f"📊 Database: {DB_PATH}")
    print(f"🌐 API URL: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)