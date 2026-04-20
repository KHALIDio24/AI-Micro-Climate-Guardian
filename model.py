import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings('ignore')

DB_PATH = "guardian.db"

class RiskPredictor:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        
    def get_historical_data(self, location_tag, days=90):
        """Fetch historical data for analysis"""
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT * FROM sensor_readings 
            WHERE location_tag=? 
            ORDER BY timestamp DESC
        """
        df = pd.read_sql(query, conn, params=(location_tag,))
        conn.close()
        
        if df.empty:
            return None
            
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df['timestamp'] >= cutoff].sort_values('timestamp')
        return df
    
    def calculate_features(self, location_tag):
        """Extract advanced features from sensor data"""
        df = self.get_historical_data(location_tag, 30)
        if df is None or df.empty:
            return None
        
        features = {}
        
        # Environmental stability metrics
        features['temp_variance'] = df['temperature'].var()
        features['humidity_variance'] = df['humidity'].var()
        features['temp_range'] = df['temperature'].max() - df['temperature'].min()
        features['humidity_range'] = df['humidity'].max() - df['humidity'].min()
        
        # Rolling averages
        features['temp_rolling_std'] = df['temperature'].rolling(24).std().iloc[-1]
        features['humidity_rolling_std'] = df['humidity'].rolling(24).std().iloc[-1]
        
        # Humidity features
        recent = df[df['timestamp'] >= datetime.now() - timedelta(hours=24)]
        features['avg_humidity_24h'] = recent['humidity'].mean()
        features['avg_humidity_7d'] = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]['humidity'].mean()
        features['avg_humidity_30d'] = df['humidity'].mean()
        features['hours_above_75'] = df[df['humidity'] > 75].shape[0]
        features['max_humidity'] = df['humidity'].max()
        
        # Temperature swings
        df['temp_swing'] = df['temperature'].diff().abs()
        features['avg_temp_swing'] = df['temp_swing'].mean()
        features['max_temp_swing'] = df['temp_swing'].max()
        features['temp_trend'] = df['temperature'].iloc[-1] - df['temperature'].iloc[0]
        
        # Light/UV exposure
        features['avg_lux'] = df['lux'].mean()
        features['max_uv'] = df['uv_index'].max()
        features['weekly_uv'] = df[df['timestamp'] >= datetime.now() - timedelta(days=7)]['uv_index'].sum()
        features['uv_hours_above_5'] = df[df['uv_index'] > 5].shape[0]
        
        # PM2.5 analysis
        features['pm25_mean'] = df['pm25'].mean()
        features['pm25_max'] = df['pm25'].max()
        features['pm25_days_above_35'] = df[df['pm25'] > 35]['timestamp'].dt.date.nunique()
        features['pm25_days_above_50'] = df[df['pm25'] > 50]['timestamp'].dt.date.nunique()
        
        # Time-based features
        features['hour'] = datetime.now().hour
        features['month'] = datetime.now().month
        features['is_weekend'] = 1 if datetime.now().weekday() >= 5 else 0
        
        # Season
        if features['month'] in [12, 1, 2]:
            features['season'] = 'winter'
        elif features['month'] in [3, 4, 5]:
            features['season'] = 'spring'
        elif features['month'] in [6, 7, 8]:
            features['season'] = 'summer'
        else:
            features['season'] = 'autumn'
        
        # Combined risk indicators
        features['temp_humidity_interaction'] = features['avg_humidity_7d'] * features['avg_temp_swing']
        
        return features
    
    def predict_risks(self, location_tag):
        """Generate comprehensive risk assessment"""
        f = self.calculate_features(location_tag)
        if f is None:
            return None
        
        risks = {}
        
        # Mold Risk (enhanced)
        mold_score = 0
        if f['avg_humidity_7d'] > 80 or f['hours_above_75'] > 20:
            mold_score = 3
        elif f['avg_humidity_7d'] > 70 or f['hours_above_75'] > 10:
            mold_score = 2
        elif f['avg_humidity_7d'] > 60:
            mold_score = 1
        risks['Mold'] = {'score': mold_score, 'level': ['LOW', 'MEDIUM', 'HIGH'][mold_score-1] if mold_score > 0 else 'LOW'}
        
        # Wood Cracking Risk
        crack_score = 0
        if f['avg_temp_swing'] > 10 or f['max_temp_swing'] > 15:
            crack_score = 3
        elif f['avg_temp_swing'] > 5 or f['max_temp_swing'] > 8:
            crack_score = 2
        elif f['avg_temp_swing'] > 2:
            crack_score = 1
        risks['Wood Crack'] = {'score': crack_score, 'level': ['LOW', 'MEDIUM', 'HIGH'][crack_score-1] if crack_score > 0 else 'LOW'}
        
        # Paint Fading Risk
        fade_score = 0
        if f['weekly_uv'] > 5000 or f['max_uv'] > 8:
            fade_score = 3
        elif f['weekly_uv'] > 2500 or f['max_uv'] > 5:
            fade_score = 2
        elif f['weekly_uv'] > 1000:
            fade_score = 1
        risks['Paint Fading'] = {'score': fade_score, 'level': ['LOW', 'MEDIUM', 'HIGH'][fade_score-1] if fade_score > 0 else 'LOW'}
        
        # Corrosion Risk
        corrosion_score = 0
        if f['pm25_days_above_50'] >= 3 or f['avg_humidity_7d'] > 75:
            corrosion_score = 3
        elif f['pm25_days_above_35'] >= 5 or f['avg_humidity_7d'] > 65:
            corrosion_score = 2
        elif f['pm25_days_above_35'] >= 2:
            corrosion_score = 1
        risks['Corrosion'] = {'score': corrosion_score, 'level': ['LOW', 'MEDIUM', 'HIGH'][corrosion_score-1] if corrosion_score > 0 else 'LOW'}
        
        # Overall Risk Score
        total_score = sum(r['score'] for r in risks.values())
        max_score = len(risks) * 3
        overall_percentage = (total_score / max_score) * 100
        
        if overall_percentage >= 60:
            overall_level = 'HIGH'
        elif overall_percentage >= 30:
            overall_level = 'MEDIUM'
        else:
            overall_level = 'LOW'
            
        risks['Overall'] = {
            'score': overall_percentage,
            'level': overall_level,
            'total_score': total_score,
            'max_score': max_score
        }
        
        return risks
    
    def predict_trend(self, location_tag, hours=24):
        """Predict future values using simple time series"""
        df = self.get_historical_data(location_tag, 7)
        if df is None or df.empty:
            return None
        
        predictions = {}
        
        # Simple exponential smoothing for each metric
        for metric in ['temperature', 'humidity', 'pm25']:
            values = df[metric].values
            if len(values) < 10:
                predictions[metric] = [values[-1]] * hours
                continue
            
            # Simple moving average with trend
            alpha = 0.3
            smoothed = [values[0]]
            for v in values[1:]:
                smoothed.append(alpha * v + (1 - alpha) * smoothed[-1])
            
            # Extrapolate
            last_slope = (smoothed[-1] - smoothed[-10]) / 10 if len(smoothed) >= 10 else 0
            future = []
            for i in range(hours):
                pred = smoothed[-1] + (last_slope * (i + 1))
                future.append(max(0, pred))  # No negative values
            predictions[metric] = future
        
        return predictions

# Global instance
predictor = RiskPredictor()

def get_risk_assessment(location_tag):
    """Convenience function for risk assessment"""
    return predictor.predict_risks(location_tag)

def get_trend_prediction(location_tag, hours=24):
    """Convenience function for trend prediction"""
    return predictor.predict_trend(location_tag, hours)