import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RiskAnalyzer:
    def __init__(self):
        self.temp_range = (18, 24)  # Ideal temperature range for heritage
        self.humidity_range = (40, 55)  # Ideal humidity range
        self.light_threshold = 200  # Max safe light intensity (lux)
        self.pm25_threshold = 35  # Max safe PM2.5 level
        
    def calculate_risk_score(self, data):
        """Calculate risk score based on environmental parameters"""
        risk_score = 0
        alerts = []
        
        # Temperature check
        temp = data.get('temperature', 22)
        if temp < self.temp_range[0]:
            diff = self.temp_range[0] - temp
            risk_score += min(diff * 3, 30)
            alerts.append(f"Temperature too low: {temp}°C (Ideal: {self.temp_range[0]}-{self.temp_range[1]}°C)")
        elif temp > self.temp_range[1]:
            diff = temp - self.temp_range[1]
            risk_score += min(diff * 3, 30)
            alerts.append(f"Temperature too high: {temp}°C (Ideal: {self.temp_range[0]}-{self.temp_range[1]}°C)")
        
        # Humidity check
        humidity = data.get('humidity', 50)
        if humidity < self.humidity_range[0]:
            diff = self.humidity_range[0] - humidity
            risk_score += min(diff * 2, 25)
            alerts.append(f"Humidity too low: {humidity}% (Ideal: {self.humidity_range[0]}-{self.humidity_range[1]}%)")
        elif humidity > self.humidity_range[1]:
            diff = humidity - self.humidity_range[1]
            risk_score += min(diff * 2, 25)
            alerts.append(f"Humidity too high: {humidity}% (Ideal: {self.humidity_range[0]}-{self.humidity_range[1]}%)")
        
        # Light intensity check
        light = data.get('light_intensity', 0)
        if light > self.light_threshold:
            risk_score += min((light - self.light_threshold) / 10, 20)
            alerts.append(f"Light intensity too high: {light:.0f} lux (Safe limit: {self.light_threshold} lux)")
        
        # PM2.5 check
        pm25 = data.get('pm2_5', 0)
        if pm25 > self.pm25_threshold:
            risk_score += min((pm25 - self.pm25_threshold) / 2, 25)
            alerts.append(f"PM2.5 level too high: {pm25:.1f} µg/m³ (Safe limit: {self.pm25_threshold} µg/m³)")
        
        # UV index check
        uv_index = data.get('uv_index', 0)
        if uv_index > 3:
            risk_score += min(uv_index * 2, 20)
            alerts.append(f"UV Index too high: {uv_index} (Safe limit: <3)")
        
        # Determine risk level
        risk_score = min(risk_score, 100)
        
        if risk_score >= 60:
            risk_level = "HIGH"
        elif risk_score >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return risk_score, risk_level, alerts
    
    def get_instant_recommendations(self, data, risk_level, alerts):
        """Get instant recommendations based on current conditions"""
        recommendations = []
        
        if risk_level == "HIGH":
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED: Environmental conditions are critical for heritage preservation")
        
        temp = data.get('temperature', 22)
        if temp < self.temp_range[0]:
            recommendations.append(f"🌡️ Increase temperature from {temp}°C to {self.temp_range[0]}°C - Activate heating system")
        elif temp > self.temp_range[1]:
            recommendations.append(f"🌡️ Decrease temperature from {temp}°C to {self.temp_range[1]}°C - Increase cooling/ventilation")
        
        humidity = data.get('humidity', 50)
        if humidity < self.humidity_range[0]:
            recommendations.append(f"💧 Increase humidity from {humidity}% to {self.humidity_range[0]}% - Activate humidifiers")
        elif humidity > self.humidity_range[1]:
            recommendations.append(f"💧 Decrease humidity from {humidity}% to {self.humidity_range[1]}% - Activate dehumidifiers")
        
        light = data.get('light_intensity', 0)
        if light > self.light_threshold:
            recommendations.append(f"💡 Reduce light intensity from {light:.0f} lux to below {self.light_threshold} lux - Close blinds or use UV filters")
        
        pm25 = data.get('pm2_5', 0)
        if pm25 > self.pm25_threshold:
            recommendations.append(f"🌫️ Improve air quality (PM2.5: {pm25:.1f} µg/m³) - Activate air purifiers")
        
        uv_index = data.get('uv_index', 0)
        if uv_index > 3:
            recommendations.append(f"☀️ Protect from UV radiation (UV Index: {uv_index}) - Close UV-blocking blinds")
        
        if not recommendations:
            recommendations.append("✅ All environmental parameters within safe ranges. Continue regular monitoring.")
        
        return recommendations
    
    def analyze_long_term_trend(self, df):
        """Analyze long-term trends in the data"""
        if df.empty or len(df) < 2:
            return {}
        
        try:
            # Ensure timestamp is datetime
            if 'timestamp' in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                
                # Remove any rows with invalid timestamps
                df = df.dropna(subset=['timestamp'])
            
            # Sort by timestamp
            df = df.sort_values('timestamp')
            
            # Calculate trends using linear regression or simple comparison
            trends = {}
            
            # Split data into two halves
            mid_point = len(df) // 2
            first_half = df.iloc[:mid_point]
            second_half = df.iloc[mid_point:]
            
            # Temperature trend
            if 'temperature' in df.columns:
                temp_first = first_half['temperature'].mean()
                temp_second = second_half['temperature'].mean()
                if temp_second > temp_first * 1.05:
                    trends['temperature_trend'] = 'increasing'
                elif temp_second < temp_first * 0.95:
                    trends['temperature_trend'] = 'decreasing'
                else:
                    trends['temperature_trend'] = 'stable'
            
            # Humidity trend
            if 'humidity' in df.columns:
                hum_first = first_half['humidity'].mean()
                hum_second = second_half['humidity'].mean()
                if hum_second > hum_first * 1.05:
                    trends['humidity_trend'] = 'increasing'
                elif hum_second < hum_first * 0.95:
                    trends['humidity_trend'] = 'decreasing'
                else:
                    trends['humidity_trend'] = 'stable'
            
            # Risk score trend
            if 'risk_score' in df.columns:
                risk_first = first_half['risk_score'].mean()
                risk_second = second_half['risk_score'].mean()
                if risk_second > risk_first * 1.1:
                    trends['risk_trend'] = 'worsening'
                elif risk_second < risk_first * 0.9:
                    trends['risk_trend'] = 'improving'
                else:
                    trends['risk_trend'] = 'stable'
            
            # Summary statistics
            if not df.empty and 'timestamp' in df.columns:
                time_diff = df['timestamp'].max() - df['timestamp'].min()
                trends['summary'] = {
                    'days_covered': time_diff.days if hasattr(time_diff, 'days') else 0,
                    'data_points': len(df),
                    'start_date': df['timestamp'].min().strftime('%Y-%m-%d') if pd.notna(df['timestamp'].min()) else None,
                    'end_date': df['timestamp'].max().strftime('%Y-%m-%d') if pd.notna(df['timestamp'].max()) else None
                }
            else:
                trends['summary'] = {
                    'days_covered': 0,
                    'data_points': len(df),
                    'start_date': None,
                    'end_date': None
                }
            
            return trends
            
        except Exception as e:
            print(f"Error in trend analysis: {e}")
            return {'error': str(e)}

# Create global instance
risk_analyzer = RiskAnalyzer()