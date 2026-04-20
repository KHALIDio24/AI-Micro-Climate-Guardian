import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os

DB_PATH = 'heritage_monitoring.db'

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sensor readings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            room_name TEXT,
            temperature REAL,
            pressure REAL,
            humidity REAL,
            light_intensity REAL,
            pm1_0 REAL,
            pm2_5 REAL,
            pm10 REAL,
            risk_score REAL,
            risk_level TEXT
        )
    ''')
    
    # Manual readings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS manual_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            room_name TEXT,
            location_detail TEXT,
            temperature REAL,
            humidity REAL,
            light_condition TEXT,
            light_intensity TEXT,
            wall_condition TEXT,
            ceiling_condition TEXT,
            floor_condition TEXT,
            window_condition TEXT,
            artifact_condition TEXT,
            artifact_material TEXT,
            artifact_location TEXT,
            proximity_to_window TEXT,
            pest_detected TEXT,
            pest_description TEXT,
            odor_detected TEXT,
            odor_description TEXT,
            hvac_status TEXT,
            air_circulation TEXT,
            recent_weather TEXT,
            ventilation_type TEXT,
            temperature_notes TEXT,
            general_notes TEXT,
            inspector_name TEXT,
            risk_score REAL,
            risk_level TEXT
        )
    ''')
    
    # Satellite data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS satellite_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            city TEXT,
            province TEXT,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            wind_speed REAL,
            wind_direction TEXT,
            uv_index REAL,
            weather_condition TEXT,
            aqi INTEGER,
            pm2_5 REAL,
            pm10 REAL,
            risk_score REAL,
            risk_level TEXT,
            alerts TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_sensor_reading(data):
    """Save a sensor reading to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sensor_readings (
            timestamp, room_name, temperature, pressure, humidity, 
            light_intensity, pm1_0, pm2_5, pm10, risk_score, risk_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        data.get('room_name'),
        data.get('temperature'),
        data.get('pressure'),
        data.get('humidity'),
        data.get('light_intensity'),
        data.get('pm1_0'),
        data.get('pm2_5'),
        data.get('pm10'),
        data.get('risk_score'),
        data.get('risk_level')
    ))
    
    conn.commit()
    conn.close()

def get_latest_sensor_reading(room_name):
    """Get the latest sensor reading for a room"""
    conn = get_db_connection()
    query = "SELECT * FROM sensor_readings WHERE room_name = ? ORDER BY timestamp DESC LIMIT 1"
    df = pd.read_sql_query(query, conn, params=[room_name])
    conn.close()
    
    if not df.empty:
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.iloc[0].to_dict()
    return None

def get_sensor_history(room_name=None, days=30):
    """Get sensor history for a specific room"""
    conn = get_db_connection()
    
    # Calculate the date threshold
    threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    if room_name:
        query = "SELECT * FROM sensor_readings WHERE room_name = ? AND timestamp >= ? ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn, params=[room_name, threshold_date])
    else:
        query = "SELECT * FROM sensor_readings WHERE timestamp >= ? ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn, params=[threshold_date])
    
    conn.close()
    
    # Convert timestamp to datetime
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

def save_manual_reading(data):
    """Save a manual inspection reading"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO manual_readings (
            timestamp, room_name, location_detail, temperature, humidity,
            light_condition, light_intensity, wall_condition, ceiling_condition,
            floor_condition, window_condition, artifact_condition, artifact_material,
            artifact_location, proximity_to_window, pest_detected, pest_description,
            odor_detected, odor_description, hvac_status, air_circulation,
            recent_weather, ventilation_type, temperature_notes, general_notes,
            inspector_name, risk_score, risk_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        data.get('room_name'),
        data.get('location_detail'),
        data.get('temperature'),
        data.get('humidity'),
        data.get('light_condition'),
        data.get('light_intensity'),
        data.get('wall_condition'),
        data.get('ceiling_condition'),
        data.get('floor_condition'),
        data.get('window_condition'),
        data.get('artifact_condition'),
        data.get('artifact_material'),
        data.get('artifact_location'),
        data.get('proximity_to_window'),
        data.get('pest_detected'),
        data.get('pest_description'),
        data.get('odor_detected'),
        data.get('odor_description'),
        data.get('hvac_status'),
        data.get('air_circulation'),
        data.get('recent_weather'),
        data.get('ventilation_type'),
        data.get('temperature_notes'),
        data.get('general_notes'),
        data.get('inspector_name'),
        data.get('risk_score'),
        data.get('risk_level')
    ))
    
    conn.commit()
    conn.close()

def get_manual_history(days=90):
    """Get manual inspection history"""
    conn = get_db_connection()
    threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    query = "SELECT * FROM manual_readings WHERE timestamp >= ? ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn, params=[threshold_date])
    conn.close()
    
    # Convert timestamp to datetime
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

def save_satellite_data(data):
    """Save satellite weather data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO satellite_data (
            timestamp, city, province, temperature, humidity, pressure,
            wind_speed, wind_direction, uv_index, weather_condition,
            aqi, pm2_5, pm10, risk_score, risk_level, alerts
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().isoformat(),
        data.get('city'),
        data.get('province'),
        data.get('temperature'),
        data.get('humidity'),
        data.get('pressure'),
        data.get('wind_speed'),
        data.get('wind_direction'),
        data.get('uv_index'),
        data.get('weather_condition'),
        data.get('aqi'),
        data.get('pm2_5'),
        data.get('pm10'),
        data.get('risk_score'),
        data.get('risk_level'),
        data.get('alerts')
    ))
    
    conn.commit()
    conn.close()

def get_satellite_history(city=None, days=30):
    """Get satellite data history"""
    conn = get_db_connection()
    threshold_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    if city:
        query = "SELECT * FROM satellite_data WHERE city = ? AND timestamp >= ? ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn, params=[city, threshold_date])
    else:
        query = "SELECT * FROM satellite_data WHERE timestamp >= ? ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn, params=[threshold_date])
    
    conn.close()
    
    # Convert timestamp to datetime
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df

def get_database_stats():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM sensor_readings")
    sensor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM manual_readings")
    manual_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM satellite_data")
    satellite_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'sensor_readings': sensor_count,
        'manual_readings': manual_count,
        'satellite_records': satellite_count
    }