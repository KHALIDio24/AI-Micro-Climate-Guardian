import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import time
import random

st.set_page_config(
    page_title="Micro-Climate Guardian Pro",
    page_icon="🏛️",
    layout="wide"
)

# API Configuration
API_URL = "http://localhost:8000"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .risk-high { 
        background-color: #ff6b6b; 
        padding: 20px; 
        border-radius: 10px; 
        color: white; 
        text-align: center;
        animation: pulse 1s infinite;
    }
    .risk-medium { 
        background-color: #ffd93d; 
        padding: 20px; 
        border-radius: 10px; 
        color: #333; 
        text-align: center;
    }
    .risk-low { 
        background-color: #6bcf7f; 
        padding: 20px; 
        border-radius: 10px; 
        color: white; 
        text-align: center;
    }
    .data-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #4CAF50;
    }
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }
    .sensor-badge { background-color: #4CAF50; color: white; }
    .manual-badge { background-color: #FF9800; color: white; }
    .satellite-badge { background-color: #2196F3; color: white; }
    .stButton button {
        width: 100%;
        border-radius: 8px;
        height: 45px;
        font-weight: bold;
    }
    div[data-testid="stAlert"] {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🏛️ Micro-Climate Guardian Pro</h1>
    <p>AI-Powered Heritage Protection System</p>
    <small>3 Data Sources: IoT Sensors | Manual Input | Satellite/Weather API</small>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR - Data Source Selection
# ============================================

st.sidebar.markdown("## 📡 Data Source Selection")

# Data source selector
data_source = st.sidebar.radio(
    "Choose Data Input Method",
    ["📊 IoT Sensors", "✏️ Manual Input", "🛰️ Real-Time Data (Satellite/Weather)"],
    help="Select how you want to input environmental data"
)

st.sidebar.markdown("---")

# Location selector
st.sidebar.markdown("## 📍 Location")

# Predefined locations
locations_list = ["Main Gallery", "Archive Room", "Conservation Lab", "Storage Vault", "Courtyard", "Entrance Hall"]

location = st.sidebar.selectbox("Select Location", locations_list)

# Custom location option
use_custom = st.sidebar.checkbox("Use custom location name")
if use_custom:
    location = st.sidebar.text_input("Custom Location Name", value=location)

st.sidebar.markdown("---")

# Auto-refresh option (only for sensor data)
if data_source == "📊 IoT Sensors":
    auto_refresh = st.sidebar.checkbox("Auto-refresh (every 10 seconds)", value=False)
else:
    auto_refresh = False

# Refresh button
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** You can switch between data sources anytime. Each source provides different types of environmental data.")

# ============================================
# MAIN CONTENT BASED ON DATA SOURCE
# ============================================

# Function to get sensor data
@st.cache_data(ttl=10 if auto_refresh else 60)
def get_sensor_data(location):
    try:
        response = requests.get(f"{API_URL}/api/combined-data/{location}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# Function to get risk assessment
@st.cache_data(ttl=30)
def get_risk_assessment(location):
    try:
        response = requests.get(f"{API_URL}/api/risk-assessment/{location}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ============================================
# OPTION 1: IoT SENSORS
# ============================================

if data_source == "📊 IoT Sensors":
    st.header("📡 IoT Sensor Data")
    st.markdown("*Real-time data from physical sensors installed at the location*")
    
    # Check API connection
    try:
        health = requests.get(f"{API_URL}/api/health", timeout=2)
        api_connected = health.status_code == 200
    except:
        api_connected = False
    
    if not api_connected:
        st.warning("⚠️ API Server not connected. Please run: `python unified_api.py`")
        st.info("📌 **Quick Setup:**\n1. Open terminal\n2. Run: `python unified_api.py`\n3. Then refresh this page")
        
        # Option to run simulator
        if st.button("🚀 Start Sensor Simulator (Generate Test Data)"):
            st.info("Simulator would run in background. For now, use Manual Input option.")
    else:
        data = get_sensor_data(location)
        
        if data and data.get('sensor_data'):
            sensor = data['sensor_data']
            
            # Display sensor metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌡️ Temperature", f"{sensor.get('temperature', 'N/A')}°C", 
                         delta=None if not sensor.get('temperature') else None)
            with col2:
                st.metric("💧 Humidity", f"{sensor.get('humidity', 'N/A')}%")
            with col3:
                st.metric("💨 PM2.5", f"{sensor.get('pm25', 'N/A')} µg/m³")
            with col4:
                st.metric("🔋 Battery", f"{sensor.get('battery_level', 'N/A')}%")
            
            # Additional sensor data
            col5, col6 = st.columns(2)
            with col5:
                st.metric("☀️ UV Index", f"{sensor.get('uv_index', 'N/A')}")
            with col6:
                st.metric("💡 Lux", f"{sensor.get('lux', 'N/A')} lux")
            
            st.markdown(f'<span class="badge sensor-badge">📡 Data Source: IoT Sensor</span>', unsafe_allow_html=True)
            st.caption(f"Last updated: {sensor.get('timestamp', 'Unknown')}")
            
        else:
            st.warning("⚠️ No sensor data available for this location")
            st.info("📌 **Options:**\n"
                   "1. Run sensor simulator: `python simulate_sensors.py`\n"
                   "2. Or switch to 'Manual Input' tab to add data manually\n"
                   "3. Or use 'Real-Time Data' for satellite/weather data")
            
            # Quick action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Use Manual Input Instead"):
                    st.rerun()
            with col2:
                if st.button("🛰️ Use Real-Time Data"):
                    st.session_state['switch_to'] = 'real_time'
                    st.rerun()

# ============================================
# OPTION 2: MANUAL INPUT
# ============================================

elif data_source == "✏️ Manual Input":
    st.header("✏️ Manual Environmental Reading")
    st.markdown("*Enter environmental data manually when sensors are not available*")
    
    with st.form("manual_data_form", clear_on_submit=False):
        st.subheader("📊 Enter Current Conditions")
        
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.number_input(
                "🌡️ Temperature (°C)", 
                value=20.0, 
                step=0.5,
                min_value=-10.0,
                max_value=50.0,
                help="Current air temperature"
            )
            
            humidity = st.number_input(
                "💧 Humidity (%)", 
                value=50.0, 
                step=1.0,
                min_value=0.0,
                max_value=100.0,
                help="Relative humidity percentage"
            )
            
            uv_index = st.slider(
                "☀️ UV Index", 
                min_value=0, 
                max_value=11, 
                value=2,
                help="Ultraviolet radiation level (0-11+)"
            )
        
        with col2:
            pm25 = st.number_input(
                "🌫️ PM2.5 (µg/m³)", 
                value=25.0, 
                step=5.0,
                min_value=0.0,
                max_value=500.0,
                help="Fine particulate matter concentration"
            )
            
            lux = st.number_input(
                "💡 Light Level (lux)", 
                value=300.0, 
                step=50.0,
                min_value=0.0,
                max_value=2000.0,
                help="Illuminance level"
            )
            
            condition_notes = st.text_area(
                "📝 Condition Notes",
                placeholder="e.g., Visible moisture on walls, discoloration detected, etc.",
                help="Any observations about artifact condition"
            )
        
        user_name = st.text_input("👤 Your Name", value="Conservator")
        
        submitted = st.form_submit_button("💾 Save Manual Reading", use_container_width=True)
        
        if submitted:
            manual_data = {
                "temperature": temperature,
                "humidity": humidity,
                "condition_notes": condition_notes,
                "location_tag": location,
                "user_name": user_name
            }
            
            try:
                response = requests.post(f"{API_URL}/api/manual-reading", json=manual_data, timeout=5)
                if response.status_code == 200:
                    st.success("✅ Manual reading saved successfully!")
                    st.balloons()
                    
                    # Store in session state for immediate display
                    st.session_state['manual_data'] = manual_data
                    st.session_state['manual_saved'] = True
                else:
                    st.error("Failed to save manual reading")
            except Exception as e:
                st.error(f"⚠️ API Connection Error: {e}")
                st.info("Make sure the API server is running: `python unified_api.py`")
    
    # Display recently saved manual data
    if st.session_state.get('manual_saved') or st.session_state.get('manual_data'):
        st.subheader("📋 Last Manual Reading")
        manual = st.session_state.get('manual_data', {})
        
        if manual:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Temperature", f"{manual.get('temperature', 'N/A')}°C")
                st.metric("Humidity", f"{manual.get('humidity', 'N/A')}%")
            with col2:
                st.metric("UV Index", manual.get('uv_index', 'N/A'))
                st.metric("PM2.5", f"{manual.get('pm25', 'N/A')} µg/m³")
            with col3:
                st.metric("Light", f"{manual.get('lux', 'N/A')} lux")
            
            st.markdown(f'<span class="badge manual-badge">✏️ Data Source: Manual Input</span>', unsafe_allow_html=True)
            st.caption(f"Notes: {manual.get('condition_notes', 'No notes')}")
            
            # Calculate risk from manual data
            risk_score = 0
            if manual.get('humidity', 50) > 70:
                risk_score += 30
            if manual.get('temperature', 20) > 28:
                risk_score += 25
            if manual.get('pm25', 25) > 35:
                risk_score += 20
            if manual.get('uv_index', 2) > 5:
                risk_score += 15
            
            if risk_score >= 60:
                st.error(f"⚠️ HIGH RISK SCORE: {risk_score}%")
            elif risk_score >= 30:
                st.warning(f"⚠️ MEDIUM RISK SCORE: {risk_score}%")
            else:
                st.success(f"✅ LOW RISK SCORE: {risk_score}%")

# ============================================
# OPTION 3: REAL-TIME DATA (Satellite/Weather)
# ============================================

else:  # Real-Time Data
    st.header("🛰️ Real-Time Environmental Data")
    st.markdown("*Live data from weather satellites and global monitoring networks*")
    
    # City selector for real-time data
    col1, col2 = st.columns([2, 1])
    with col1:
        city = st.selectbox(
            "Select City for Real-Time Data",
            ["London", "Paris", "New York", "Tokyo", "Sydney", "Dubai", "Singapore", "Mumbai"],
            help="Weather and air quality data for this location"
        )
    with col2:
        if st.button("🌍 Fetch Live Data", use_container_width=True):
            st.cache_data.clear()
    
    # Fetch real-time data
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_real_time_weather(city_name):
        try:
            response = requests.post(
                f"{API_URL}/api/fetch-weather", 
                json={"city": city_name},
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Error fetching weather data: {e}")
        return None
    
    # Get weather data
    weather_data = fetch_real_time_weather(city)
    
    if weather_data and weather_data.get('data'):
        data = weather_data['data']
        
        # Display weather metrics
        st.subheader(f"📍 Current Conditions in {city}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if data.get('weather'):
                weather = data['weather']
                st.metric("🌡️ Temperature", f"{weather.get('temperature', 'N/A')}°C")
                st.metric("💧 Humidity", f"{weather.get('humidity', 'N/A')}%")
            else:
                st.info("Weather data loading...")
        
        with col2:
            if data.get('weather'):
                weather = data['weather']
                st.metric("💨 Wind Speed", f"{weather.get('wind_speed', 'N/A')} m/s")
                st.metric("☀️ UV Index", f"{weather.get('uv_index', 'N/A')}")
            else:
                st.info("Weather data loading...")
        
        with col3:
            if data.get('air_quality'):
                aqi = data['air_quality']
                aqi_val = aqi.get('air_quality_index', 'N/A')
                st.metric("🌫️ Air Quality Index", aqi_val)
                if isinstance(aqi_val, (int, float)):
                    if aqi_val <= 50:
                        st.success("Good")
                    elif aqi_val <= 100:
                        st.warning("Moderate")
                    else:
                        st.error("Poor")
            else:
                st.info("AQI data loading...")
        
        with col4:
            if data.get('air_quality'):
                aqi = data['air_quality']
                st.metric("PM2.5", f"{aqi.get('pm25', 'N/A')} µg/m³")
                st.metric("PM10", f"{aqi.get('pm10', 'N/A')} µg/m³")
            else:
                st.info("Particulate data loading...")
        
        st.markdown(f'<span class="badge satellite-badge">🛰️ Data Source: Satellite/Weather API</span>', unsafe_allow_html=True)
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Risk assessment from real-time data
        st.subheader("🤖 AI Risk Assessment (Based on Real-Time Data)")
        
        # Calculate risk from real-time data
        risk_score = 0
        alerts = []
        
        if data.get('weather'):
            weather = data['weather']
            temp = weather.get('temperature', 20)
            humidity = weather.get('humidity', 50)
            
            if temp > 28:
                risk_score += 25
                alerts.append("⚠️ High temperature alert from satellite data")
            if humidity > 75:
                risk_score += 30
                alerts.append("💧 High humidity detected - Mold risk")
        
        if data.get('air_quality'):
            aqi = data['air_quality']
            aqi_val = aqi.get('air_quality_index', 50)
            pm25 = aqi.get('pm25', 25)
            
            if aqi_val > 150 or pm25 > 50:
                risk_score += 25
                alerts.append("🌫️ Poor air quality - Protection needed for artifacts")
            elif aqi_val > 100:
                risk_score += 15
        
        if risk_score >= 60:
            st.markdown(f'<div class="risk-high"><h2>⚠️ HIGH RISK</h2><h3>Score: {risk_score}/100</h3></div>', unsafe_allow_html=True)
        elif risk_score >= 30:
            st.markdown(f'<div class="risk-medium"><h2>⚠️ MEDIUM RISK</h2><h3>Score: {risk_score}/100</h3></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="risk-low"><h2>✅ LOW RISK</h2><h3>Score: {risk_score}/100</h3></div>', unsafe_allow_html=True)
        
        if alerts:
            st.warning("### Active Alerts")
            for alert in alerts:
                st.error(alert)
        else:
            st.success("✅ No active alerts - Conditions are stable")
        
        # Recommendations based on real-time data
        st.subheader("💡 Recommendations")
        if risk_score > 60:
            st.warning("🚨 **Immediate Action Required:**\n- Close windows and doors\n- Activate climate control system\n- Move sensitive artifacts to protected areas")
        elif risk_score > 30:
            st.info("📊 **Preventive Measures:**\n- Monitor conditions closely\n- Consider additional protection\n- Schedule inspection")
        else:
            st.success("✅ **Status:** Conditions are favorable for heritage preservation")
            
    else:
        st.warning("⚠️ Unable to fetch real-time data")
        st.info("📌 **Note:** The API is using simulated data. For real satellite data, you would need:\n"
               "- OpenWeatherMap API key\n"
               "- WAQI (Air Quality) API token\n\n"
               "For demo purposes, simulated data is being displayed.")
        
        # Show simulated data preview
        st.subheader("📊 Simulated Data Preview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperature", f"{random.uniform(10, 28):.1f}°C")
            st.metric("Humidity", f"{random.uniform(40, 80):.0f}%")
        with col2:
            st.metric("UV Index", f"{random.uniform(0, 8):.1f}")
            st.metric("AQI", f"{random.randint(30, 150)}")

# ============================================
# COMMON SECTION - Risk Assessment (for all sources)
# ============================================

st.markdown("---")
st.subheader("🤖 AI Risk Analysis Dashboard")

# Try to get risk assessment from API if available
risk = get_risk_assessment(location)

if risk and risk.get('risk_score', 0) > 0:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        risk_score = risk['risk_score']
        risk_level = risk['risk_level']
        
        if risk_level == 'HIGH':
            st.error(f"### Risk Score: {risk_score}%\n### Level: {risk_level}")
        elif risk_level == 'MEDIUM':
            st.warning(f"### Risk Score: {risk_score}%\n### Level: {risk_level}")
        else:
            st.success(f"### Risk Score: {risk_score}%\n### Level: {risk_level}")
    
    with col2:
        if risk.get('alerts'):
            st.write("**Active Alerts:**")
            for alert in risk['alerts'][:3]:  # Show top 3 alerts
                st.write(f"• {alert}")
else:
    st.info("💡 **How to get risk assessment:**\n"
           "1. Select a data source from the sidebar\n"
           "2. Add data via IoT sensors, Manual input, or Real-time data\n"
           "3. Risk assessment will appear here automatically")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <small>
    🟢 IoT Sensors | ✏️ Manual Input | 🛰️ Satellite/Weather Data<br>
    <i>Powered by AI for Cultural Heritage Protection</i>
    </small>
</div>
""", unsafe_allow_html=True)

# Auto-refresh logic
if auto_refresh:
    time.sleep(10)
    st.rerun()