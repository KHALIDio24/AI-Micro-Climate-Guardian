import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import requests
import json

from database import *
from risk_analyzer import risk_analyzer
from sensor_integration import sensor_manager, get_sensor_data

st.set_page_config(
    page_title="Micro-Climate Guardian Pro",
    page_icon="🏛️",
    layout="wide"
)

# Initialize database and sensors
init_database()
sensor_manager.init_sensors()

# Session state
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_city' not in st.session_state:
    st.session_state.selected_city = "Beijing"
if 'selected_room' not in st.session_state:
    st.session_state.selected_room = "Main Gallery"

# ============================================
# CUSTOM CSS - Classic Large Design
# ============================================

st.markdown("""
<style>
    /* Main header */
    .main-header {
        text-align: center;
        padding: 50px;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 25px;
        color: white;
        margin-bottom: 50px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 3.5em;
        margin-bottom: 15px;
        letter-spacing: 2px;
    }
    
    .main-header p {
        font-size: 1.3em;
        opacity: 0.95;
    }
    
    /* Large Card Styles */
    .sensor-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #a5d6a7 100%);
        padding: 50px 30px;
        border-radius: 25px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 2px solid #4caf50;
    }
    
    .sensor-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    }
    
    .manual-card {
        background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
        padding: 50px 30px;
        border-radius: 25px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 2px solid #ff9800;
    }
    
    .manual-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    }
    
    .satellite-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #90caf9 100%);
        padding: 50px 30px;
        border-radius: 25px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        border: 2px solid #2196f3;
    }
    
    .satellite-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    }
    
    .card-icon {
        font-size: 5em;
        margin-bottom: 25px;
    }
    
    .card-title {
        font-size: 2.2em;
        font-weight: bold;
        margin-bottom: 20px;
        color: #1a237e;
    }
    
    .card-description {
        font-size: 1.1em;
        margin-bottom: 25px;
        color: #333;
    }
    
    .card-features {
        font-size: 1em;
        margin-top: 25px;
        padding-top: 20px;
        border-top: 2px solid rgba(0,0,0,0.1);
        color: #444;
    }
    
    /* Risk level styles */
    .risk-high {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 20px 0;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #ffd93d 0%, #f9ca24 100%);
        padding: 30px;
        border-radius: 20px;
        color: #333;
        text-align: center;
        margin: 20px 0;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #6bcf7f 0%, #4cd964 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 20px 0;
    }
    
    /* Weather alert cards */
    .alert-critical {
        background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
        border-left: 5px solid #ffeb3b;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    
    .alert-info {
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 10px 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 10px 0;
        border: 1px solid #e0e0e0;
    }
    
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #1e3c72;
    }
    
    .metric-label {
        font-size: 1em;
        color: #666;
        margin-top: 10px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 30px;
        font-weight: bold;
        font-size: 1.1em;
        border-radius: 15px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    
    /* Back button */
    .back-button {
        margin-bottom: 20px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 30px;
        margin-top: 50px;
        color: #666;
        border-top: 2px solid #e0e0e0;
        background: #f5f5f5;
        border-radius: 15px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 2em;
        font-weight: bold;
        color: #1e3c72;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================

st.markdown("""
<div class="main-header">
    <h1>🏛️ Micro-Climate Guardian Pro</h1>
    <p>AI-Powered Heritage Protection System</p>
    <p style="font-size: 1em; margin-top: 15px;">BMP280 • BH1750 • PMS5003 | Real-time Monitoring | Long-term Analysis</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR
# ============================================

st.sidebar.markdown("## 🎯 Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["🏠 Home", "📡 Sensor Data", "✏️ Manual Input", "🛰️ Satellite Data", "📈 Long-Term Analysis"],
    format_func=lambda x: x.split(" ")[1] if " " in x else x
)

# System status
st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
status = sensor_manager.get_status()

if status['use_real_sensors']:
    st.sidebar.success("✅ Real Sensors Connected")
else:
    st.sidebar.info("📡 Simulation Mode Active")

# Database stats
stats = get_database_stats()
st.sidebar.markdown("---")
st.sidebar.markdown("### Database Statistics")
st.sidebar.metric("Sensor Readings", stats['sensor_readings'])
st.sidebar.metric("Manual Entries", stats['manual_readings'])
st.sidebar.metric("Satellite Records", stats['satellite_records'])

# ============================================
# HOME PAGE - Large Classic Cards
# ============================================

if page == "🏠 Home":
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 50px;">
        <h2 style="color: #1e3c72; font-size: 2.2em;">Welcome to Heritage Protection System</h2>
        <p style="font-size: 1.2em; color: #555;">Select your data source below to begin monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="sensor-card">
            <div class="card-icon">📡</div>
            <div class="card-title">IoT Sensors</div>
            <div class="card-description">BMP280 • BH1750 • PMS5003</div>
            <div class="card-features">
                🌡️ Temperature & Pressure<br>
                💡 Light Intensity (Lux)<br>
                🌫️ PM1.0, PM2.5, PM10<br>
                📊 Real-time Monitoring
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📡 Start Sensor Monitoring", key="home_sensor", use_container_width=True):
            st.session_state.page = "📡 Sensor Data"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="manual-card">
            <div class="card-icon">✏️</div>
            <div class="card-title">Manual Input</div>
            <div class="card-description">Comprehensive Inspection</div>
            <div class="card-features">
                📝 Environmental Readings<br>
                🏛️ Building Condition<br>
                🖼️ Artifact Condition<br>
                🐜 Pest & Odor Detection
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("✏️ Enter Manual Data", key="home_manual", use_container_width=True):
            st.session_state.page = "✏️ Manual Input"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="satellite-card">
            <div class="card-icon">🛰️</div>
            <div class="card-title">Satellite Data</div>
            <div class="card-description">Real-time Weather for China</div>
            <div class="card-features">
                🌤️ Temperature & Humidity<br>
                💨 Wind Speed & Direction<br>
                ⚡ UV Index & AQI<br>
                🌪️ Storm & Weather Warnings
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🛰️ Get Satellite Data", key="home_satellite", use_container_width=True):
            st.session_state.page = "🛰️ Satellite Data"
            st.rerun()
    
    # System overview
    st.markdown("---")
    st.markdown("<h3 style='text-align: center;'>System Overview</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 3em;">📡</div>
            <div class="metric-value">Real-time</div>
            <div class="metric-label">Sensor Monitoring</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 3em;">🤖</div>
            <div class="metric-value">AI Risk</div>
            <div class="metric-label">Assessment</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 3em;">📈</div>
            <div class="metric-value">90-Day</div>
            <div class="metric-label">History & Trends</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 3em;">⚡</div>
            <div class="metric-value">Instant</div>
            <div class="metric-label">Weather Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #e8eaf6; padding: 25px; border-radius: 20px; margin: 30px 0; border-left: 5px solid #3f51b5;">
        <h4>💡 How It Works</h4>
        <p>Select one of the three data sources above to begin monitoring your heritage site:</p>
        <ul>
            <li><strong>IoT Sensors</strong> - Connect BMP280, BH1750, PMS5003 sensors for automatic monitoring</li>
            <li><strong>Manual Input</strong> - Enter inspection data manually when sensors are unavailable</li>
            <li><strong>Satellite Data</strong> - Get real-time weather, air quality, and storm warnings for Chinese cities</li>
        </ul>
        <p>All data is stored locally and analyzed with AI for risk assessment and protection recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# SENSOR DATA PAGE
# ============================================

elif page == "📡 Sensor Data":
    st.markdown('<div class="section-header">📡 IoT Sensor Monitoring</div>', unsafe_allow_html=True)
    st.markdown("*BMP280 (Temperature, Pressure, Humidity) | BH1750 (Light Intensity) | PMS5003 (PM1.0, PM2.5, PM10)*")
    
    if not status['use_real_sensors']:
        st.info("📡 Simulation Mode: Using generated sensor data (No hardware detected)")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        room_name = st.selectbox(
            "Select Room",
            ["Main Gallery", "Archive Room", "Conservation Lab", "Storage Room", "Courtyard"],
            key="sensor_room"
        )
        st.session_state.selected_room = room_name
    
    with col2:
        if st.button("📡 Read Sensors Now", use_container_width=True):
            with st.spinner("Reading sensors..."):
                sensor_data = get_sensor_data(room_name)
                risk_score, risk_level, alerts = risk_analyzer.calculate_risk_score(sensor_data)
                sensor_data['risk_score'] = risk_score
                sensor_data['risk_level'] = risk_level
                save_sensor_reading(sensor_data)
                st.success("✅ Sensor reading saved successfully!")
                st.balloons()
                time.sleep(1)
                st.rerun()
    
    latest = get_latest_sensor_reading(room_name)
    
    if latest is not None:
        # Display all sensor readings
        st.markdown("---")
        st.markdown("### 📊 Current Sensor Readings")
        
        # BMP280 Readings
        st.markdown("#### 🌡️ BMP280 - Temperature, Pressure & Humidity")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Temperature", f"{latest['temperature']:.1f}°C")
        with col2:
            st.metric("Pressure", f"{latest['pressure']:.1f} hPa")
        with col3:
            st.metric("Humidity", f"{latest['humidity']:.1f}%")
        
        # BH1750 Reading
        st.markdown("#### 💡 BH1750 - Light Intensity")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Light Intensity", f"{latest['light_intensity']:.0f} lux")
        with col2:
            if latest['light_intensity'] > 300:
                st.warning("⚠️ Light level may cause fading")
            else:
                st.success("✅ Light level within safe range")
        
        # PMS5003 Readings
        st.markdown("#### 🌫️ PMS5003 - Air Quality (Particulate Matter)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("PM1.0", f"{latest['pm1_0']:.1f} µg/m³")
        with col2:
            st.metric("PM2.5", f"{latest['pm2_5']:.1f} µg/m³")
        with col3:
            st.metric("PM10", f"{latest['pm10']:.1f} µg/m³")
        
        # PM2.5 Gauge
        pm25_value = latest['pm2_5']
        if pm25_value <= 35:
            st.progress(0.3, text=f"PM2.5: {pm25_value} µg/m³ - Good")
        elif pm25_value <= 75:
            st.progress(0.6, text=f"PM2.5: {pm25_value} µg/m³ - Moderate")
        else:
            st.progress(0.9, text=f"PM2.5: {pm25_value} µg/m³ - Unhealthy")
        
        # Risk Assessment
        risk_score = latest['risk_score']
        risk_level = latest['risk_level']
        
        if risk_level == "HIGH":
            st.markdown(f'<div class="risk-high"><h2>⚠️ HIGH RISK - Immediate Action Required</h2><h3>Risk Score: {risk_score}/100</h3><p>Environmental conditions are critical for artifact preservation</p></div>', unsafe_allow_html=True)
        elif risk_level == "MEDIUM":
            st.markdown(f'<div class="risk-medium"><h2>⚠️ MEDIUM RISK - Monitor Closely</h2><h3>Risk Score: {risk_score}/100</h3><p>Some parameters are outside recommended ranges</p></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="risk-low"><h2>✅ LOW RISK - Stable Conditions</h2><h3>Risk Score: {risk_score}/100</h3><p>All parameters within safe ranges</p></div>', unsafe_allow_html=True)
        
        # Instant Recommendations
        st.markdown("### 💡 Instant Recommendations")
        latest_dict = dict(latest)
        _, _, alerts = risk_analyzer.calculate_risk_score(latest_dict)
        recommendations = risk_analyzer.get_instant_recommendations(latest_dict, risk_level, alerts)
        for rec in recommendations:
            st.info(rec)
        
        # Historical Trends
        st.markdown("---")
        st.markdown("### 📈 Historical Trends & Analysis")
        
        history_days = st.selectbox("Select Time Period", [7, 30, 60, 90], index=1)
        df_history = get_sensor_history(room_name, history_days)
        
        if not df_history.empty:
            fig = make_subplots(rows=3, cols=2, 
                               subplot_titles=('Temperature Trend', 'Humidity Trend', 'Pressure Trend', 
                                              'Light Intensity Trend', 'PM2.5 Trend', 'Risk Score Trend'))
            
            fig.add_trace(go.Scatter(x=df_history['timestamp'], y=df_history['temperature'], 
                                    mode='lines', name='Temperature', line=dict(color='#ff6b6b', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_history['timestamp'], y=df_history['humidity'], 
                                    mode='lines', name='Humidity', line=dict(color='#4facfe', width=2)), row=1, col=2)
            fig.add_trace(go.Scatter(x=df_history['timestamp'], y=df_history['pressure'], 
                                    mode='lines', name='Pressure', line=dict(color='#764ba2', width=2)), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_history['timestamp'], y=df_history['light_intensity'], 
                                    mode='lines', name='Light', line=dict(color='#f9ca24', width=2)), row=2, col=2)
            fig.add_trace(go.Scatter(x=df_history['timestamp'], y=df_history['pm2_5'], 
                                    mode='lines', name='PM2.5', line=dict(color='#e74c3c', width=2)), row=3, col=1)
            fig.add_trace(go.Scatter(x=df_history['timestamp'], y=df_history['risk_score'], 
                                    mode='lines', name='Risk Score', line=dict(color='#ff6b6b', width=2, dash='dash')), row=3, col=2)
            
            fig.update_layout(height=800, showlegend=True, title_text=f"Environmental History for {room_name}")
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Value")
            st.plotly_chart(fig, use_container_width=True)
            
            # Long-term risk assessment
            trends = risk_analyzer.analyze_long_term_trend(df_history)
            if trends:
                st.markdown("### 📊 Long-Term Risk Assessment")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Temperature Trend:** {trends.get('temperature_trend', 'stable').upper()}")
                    st.write(f"**Humidity Trend:** {trends.get('humidity_trend', 'stable').upper()}")
                with col2:
                    st.write(f"**Risk Trend:** {trends.get('risk_trend', 'stable').upper()}")
                    st.write(f"**Days Analyzed:** {trends.get('summary', {}).get('days_covered', 0)}")
                
                if trends.get('risk_trend') == 'worsening':
                    st.error("🚨 CRITICAL: Risk levels are increasing over time! Schedule immediate review.")
                elif trends.get('risk_trend') == 'improving':
                    st.success("✅ Positive: Risk levels are decreasing. Continue current practices.")
                else:
                    st.info("📊 Stable: Risk levels are stable. Maintain regular monitoring.")
        else:
            st.info(f"No historical data for {room_name}. Take more sensor readings.")
    else:
        st.info(f"No data for {room_name}. Click 'Read Sensors Now' to start monitoring.")

# ============================================
# MANUAL INPUT PAGE
# ============================================

elif page == "✏️ Manual Input":
    st.markdown('<div class="section-header">✏️ Manual Environmental Inspection</div>', unsafe_allow_html=True)
    st.markdown("*Enter comprehensive inspection data for instant analysis and long-term tracking*")
    
    with st.form("manual_form"):
        st.markdown("### 📍 Location Information")
        col1, col2 = st.columns(2)
        with col1:
            room_name = st.text_input("Room/Building Name", "Main Gallery")
            location_detail = st.text_input("Detailed Location", "Museum, Beijing")
        with col2:
            inspector_name = st.text_input("Inspector Name", "Conservator")
        
        st.markdown("### 🌡️ Environmental Measurements")
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.number_input("Temperature (°C)", value=22.0, step=0.5, min_value=-10.0, max_value=50.0)
            humidity = st.number_input("Humidity (%)", value=50.0, step=1.0, min_value=0.0, max_value=100.0)
        with col2:
            light_condition = st.selectbox("Light Condition", ["Good", "Too Bright", "Too Dark", "UV Present", "Flickering"])
            light_intensity = st.selectbox("Light Intensity (Lux)", ["Low (<100)", "Medium (100-300)", "High (300-500)", "Very High (>500)"])
        
        st.markdown("### 🏛️ Building Condition")
        col1, col2 = st.columns(2)
        with col1:
            wall_condition = st.selectbox("Wall Condition", ["Good", "Damp", "Cracked", "Moldy", "Discolored", "Peeling Paint"])
            ceiling_condition = st.selectbox("Ceiling Condition", ["Good", "Water Stain", "Cracked", "Moldy", "Leaking"])
        with col2:
            floor_condition = st.selectbox("Floor Condition", ["Good", "Damp", "Cracked", "Warped", "Uneven"])
            window_condition = st.selectbox("Window Condition", ["Good", "Drafty", "Condensation", "Broken Seal", "Cracked Glass"])
        
        st.markdown("### 🖼️ Artifact Condition")
        col1, col2 = st.columns(2)
        with col1:
            artifact_condition = st.selectbox("Artifact Condition", ["Good", "Discolored", "Cracked", "Warped", "Corroded", "Fading", "Brittle"])
            artifact_material = st.selectbox("Artifact Material", ["Paper", "Canvas", "Wood", "Metal", "Ceramic", "Textile", "Stone", "Mixed Media"])
        with col2:
            artifact_location = st.selectbox("Artifact Location", ["Wall Mounted", "Display Case", "Floor Standing", "Storage Shelf", "Drawer", "Pedestal"])
            proximity_to_window = st.selectbox("Proximity to Window", ["Direct Sunlight", "Indirect Light", "No Window", "Near Window (<1m)", "Far from Window (>3m)"])
        
        st.markdown("### 🐜 Pest & Odor Detection")
        col1, col2 = st.columns(2)
        with col1:
            pest_detected = st.selectbox("Pest Detected", ["None", "Live Insects", "Insect Traces", "Rodents", "Bird Nests", "Termites", "Moths"])
            pest_description = st.text_area("Pest Description", placeholder="Describe any pest activity, location, and severity...")
        with col2:
            odor_detected = st.selectbox("Odor Detected", ["None", "Musty/Moldy", "Chemical", "Rotten", "Metallic", "Smoky", "Sharp/Acidic"])
            odor_description = st.text_area("Odor Description", placeholder="Describe any unusual odors...")
        
        st.markdown("### 🌡️ Climate & HVAC")
        col1, col2 = st.columns(2)
        with col1:
            hvac_status = st.selectbox("HVAC System Status", ["Working Normally", "Needs Maintenance", "Not Working", "Recently Serviced", "Intermittent Issues"])
            air_circulation = st.selectbox("Air Circulation", ["Good", "Poor", "Stagnant", "Drafty", "Uneven"])
        with col2:
            recent_weather = st.selectbox("Recent Weather", ["Sunny", "Rainy", "Stormy", "Humid", "Dry", "Cold", "Hot"])
            ventilation_type = st.selectbox("Ventilation Type", ["Natural", "Mechanical", "HVAC", "None", "Mixed"])
        
        st.markdown("### 📝 Notes & Observations")
        temperature_notes = st.text_area("Temperature/Humidity Notes", placeholder="e.g., Localized hot spots, cold drafts, condensation on windows...")
        general_notes = st.text_area("General Observations", placeholder="Any other observations about the environment or artifacts...")
        
        submitted = st.form_submit_button("💾 Save Manual Inspection Data", use_container_width=True)
        
        if submitted:
            data = {'temperature': temperature, 'humidity': humidity, 'pm2_5': 0, 'light_intensity': 0, 'pressure': 1013}
            risk_score, risk_level, alerts = risk_analyzer.calculate_risk_score(data)
            
            manual_reading = {
                'room_name': room_name,
                'location_detail': location_detail,
                'temperature': temperature,
                'humidity': humidity,
                'light_condition': light_condition,
                'light_intensity': light_intensity,
                'wall_condition': wall_condition,
                'ceiling_condition': ceiling_condition,
                'floor_condition': floor_condition,
                'window_condition': window_condition,
                'artifact_condition': artifact_condition,
                'artifact_material': artifact_material,
                'artifact_location': artifact_location,
                'proximity_to_window': proximity_to_window,
                'pest_detected': pest_detected,
                'pest_description': pest_description,
                'odor_detected': odor_detected,
                'odor_description': odor_description,
                'hvac_status': hvac_status,
                'air_circulation': air_circulation,
                'recent_weather': recent_weather,
                'ventilation_type': ventilation_type,
                'temperature_notes': temperature_notes,
                'general_notes': general_notes,
                'inspector_name': inspector_name,
                'risk_score': risk_score,
                'risk_level': risk_level
            }
            
            save_manual_reading(manual_reading)
            st.success("✅ Manual inspection data saved successfully!")
            st.balloons()
            
            st.markdown("---")
            st.markdown("### 📊 Instant Analysis")
            
            if risk_level == "HIGH":
                st.markdown(f'<div class="risk-high"><h3>⚠️ HIGH RISK - Immediate Attention Needed</h3><p>Risk Score: {risk_score}/100</p><p>Based on your inspection data, immediate action is required</p></div>', unsafe_allow_html=True)
            elif risk_level == "MEDIUM":
                st.markdown(f'<div class="risk-medium"><h3>⚠️ MEDIUM RISK - Monitor Closely</h3><p>Risk Score: {risk_score}/100</p><p>Some conditions require attention</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="risk-low"><h3>✅ LOW RISK - Conditions Good</h3><p>Risk Score: {risk_score}/100</p><p>Environment is stable for heritage preservation</p></div>', unsafe_allow_html=True)
            
            recommendations = risk_analyzer.get_instant_recommendations(data, risk_level, alerts)
            for rec in recommendations:
                st.info(rec)
    
    st.markdown("---")
    st.markdown("### 📋 Manual Inspection History")
    
    manual_history = get_manual_history(90)
    if not manual_history.empty:
        display_cols = ['timestamp', 'room_name', 'temperature', 'humidity', 'risk_level', 'artifact_condition', 'pest_detected']
        available_cols = [col for col in display_cols if col in manual_history.columns]
        st.dataframe(manual_history[available_cols], use_container_width=True)
        
        if len(manual_history) > 1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=manual_history['timestamp'], y=manual_history['risk_score'], 
                                    mode='lines+markers', name='Risk Score', line=dict(color='#ff6b6b', width=2)))
            fig.update_layout(title="Manual Inspection Risk Trend", xaxis_title="Date", yaxis_title="Risk Score")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No manual readings yet. Add your first manual inspection above.")

# ============================================
# SATELLITE DATA PAGE - REAL DATA with Weather Warnings
# ============================================

elif page == "🛰️ Satellite Data":
    st.markdown('<div class="section-header">🛰️ Real-Time Satellite Weather Data</div>', unsafe_allow_html=True)
    st.markdown("*Live environmental data from global satellites for Chinese cities with weather warnings*")
    
    # China cities with coordinates
    china_cities = {
        "Beijing": {"province": "Beijing", "lat": 39.9042, "lon": 116.4074},
        "Shanghai": {"province": "Shanghai", "lat": 31.2304, "lon": 121.4737},
        "Guangzhou": {"province": "Guangdong", "lat": 23.1291, "lon": 113.2644},
        "Shenzhen": {"province": "Guangdong", "lat": 22.5431, "lon": 114.0579},
        "Tianjin": {"province": "Tianjin", "lat": 39.0841, "lon": 117.2009},
        "Chongqing": {"province": "Chongqing", "lat": 29.4316, "lon": 106.9123},
        "Chengdu": {"province": "Sichuan", "lat": 30.5728, "lon": 104.0668},
        "Wuhan": {"province": "Hubei", "lat": 30.5928, "lon": 114.3055},
        "Xi'an": {"province": "Shaanxi", "lat": 34.3416, "lon": 108.9402},
        "Nanjing": {"province": "Jiangsu", "lat": 32.0603, "lon": 118.7969},
        "Hangzhou": {"province": "Zhejiang", "lat": 30.2741, "lon": 120.1551},
        "Suzhou": {"province": "Jiangsu", "lat": 31.2989, "lon": 120.5853},
        "Kunming": {"province": "Yunnan", "lat": 24.8801, "lon": 102.8329},
        "Qingdao": {"province": "Shandong", "lat": 36.0671, "lon": 120.3826},
        "Dalian": {"province": "Liaoning", "lat": 38.9140, "lon": 121.6147},
        "Xiamen": {"province": "Fujian", "lat": 24.4798, "lon": 118.0894},
        "Harbin": {"province": "Heilongjiang", "lat": 45.8038, "lon": 126.5340},
        "Zhengzhou": {"province": "Henan", "lat": 34.7473, "lon": 113.6253},
        "Changsha": {"province": "Hunan", "lat": 28.2282, "lon": 112.9388},
        "Nanchang": {"province": "Jiangxi", "lat": 28.6820, "lon": 115.8579}
    }
    
    col1, col2 = st.columns(2)
    with col1:
        city = st.selectbox("Select Chinese City", list(china_cities.keys()))
        province = china_cities[city]["province"]
        st.session_state.selected_city = city
    with col2:
        st.metric("Province", province)
        st.caption("📍 Data Source: Open-Meteo Satellite Network")
    
    if st.button("🛰️ Fetch Real-Time Satellite Data", use_container_width=True):
        with st.spinner(f"Fetching real-time data for {city} from satellites..."):
            coords = china_cities[city]
            url = f"http://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,pressure_msl,windspeed_10m,uv_index"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    current = data.get('current_weather', {})
                    hourly = data.get('hourly', {})
                    hour_index = datetime.now().hour
                    
                    temperature = current.get('temperature', 0)
                    wind_speed = current.get('windspeed', 0)
                    wind_direction = current.get('winddirection', 0)
                    humidity = hourly.get('relativehumidity_2m', [50])[hour_index] if hourly.get('relativehumidity_2m') else 50
                    pressure = hourly.get('pressure_msl', [1013])[hour_index] if hourly.get('pressure_msl') else 1013
                    uv_index = hourly.get('uv_index', [2])[hour_index] if hourly.get('uv_index') else 2
                    
                    # Weather condition
                    weather_code = current.get('weathercode', 0)
                    weather_conditions = {
                        0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
                        45: "Fog", 48: "Depositing Fog", 51: "Light Drizzle", 53: "Moderate Drizzle",
                        55: "Dense Drizzle", 61: "Light Rain", 63: "Moderate Rain", 65: "Heavy Rain",
                        71: "Light Snow", 73: "Moderate Snow", 75: "Heavy Snow", 95: "Thunderstorm"
                    }
                    weather_condition = weather_conditions.get(weather_code, "Unknown")
                    
                    # Get AQI data
                    aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={coords['lat']}&longitude={coords['lon']}&hourly=pm10,pm2_5"
                    aqi_response = requests.get(aqi_url, timeout=10)
                    
                    pm25 = 25
                    pm10 = 40
                    aqi_value = 50
                    
                    if aqi_response.status_code == 200:
                        aqi_data = aqi_response.json()
                        hourly_aqi = aqi_data.get('hourly', {})
                        pm25 = hourly_aqi.get('pm2_5', [25])[hour_index] if hourly_aqi.get('pm2_5') else 25
                        pm10 = hourly_aqi.get('pm10', [40])[hour_index] if hourly_aqi.get('pm10') else 40
                        
                        if pm25 <= 12:
                            aqi_value = 50
                        elif pm25 <= 35:
                            aqi_value = 100
                        elif pm25 <= 55:
                            aqi_value = 150
                        elif pm25 <= 150:
                            aqi_value = 200
                        else:
                            aqi_value = 300
                    
                    # Weather Warnings Generation
                    weather_warnings = []
                    prevention_actions = []
                    
                    # Storm Warning
                    if pressure < 1005 and wind_speed > 10:
                        weather_warnings.append({"type": "critical", "title": "🌪️ STORM WARNING", "message": "Low pressure and high wind speed detected. Severe weather approaching!"})
                        prevention_actions.extend([
                            "Close all windows and doors immediately",
                            "Move valuable artifacts away from windows and exterior walls",
                            "Check roof and windows for potential water leaks",
                            "Backup climate control systems",
                            "Monitor weather updates closely every 30 minutes"
                        ])
                    elif pressure < 1010 and wind_speed > 8:
                        weather_warnings.append({"type": "warning", "title": "⚠️ Storm Approaching", "message": "Weather conditions are deteriorating. Prepare for potential storm."})
                        prevention_actions.extend([
                            "Prepare emergency supplies",
                            "Secure loose items near windows",
                            "Check drainage systems"
                        ])
                    
                    # Heavy Rain Warning
                    if weather_condition in ["Heavy Rain", "Thunderstorm"]:
                        weather_warnings.append({"type": "warning", "title": "🌧️ HEAVY RAIN WARNING", "message": "Heavy rainfall expected. Risk of flooding and water damage."})
                        prevention_actions.extend([
                            "Check for potential water leaks in the building",
                            "Ensure dehumidifiers are ready for operation",
                            "Monitor humidity levels closely",
                            "Move artifacts from flood-prone areas",
                            "Place water-absorbing materials near windows and doors"
                        ])
                    elif weather_condition in ["Light Rain", "Moderate Rain"]:
                        weather_warnings.append({"type": "info", "title": "🌧️ Rain Alert", "message": "Rain expected. Monitor humidity levels."})
                        prevention_actions.extend([
                            "Close windows",
                            "Prepare dehumidifiers if needed"
                        ])
                    
                    # Extreme Heat Warning
                    if temperature > 35:
                        weather_warnings.append({"type": "critical", "title": "🔥 EXTREME HEAT WARNING", "message": f"Temperature {temperature}°C - Critical conditions for artifacts!"})
                        prevention_actions.extend([
                            "Activate emergency cooling systems immediately",
                            "Close all blinds, curtains, and UV-protective coverings",
                            "Monitor temperature every 2 hours",
                            "Check for heat damage on sensitive materials (wax, paintings, paper)",
                            "Increase air circulation with fans",
                            "Consider relocating most sensitive artifacts to cooler areas"
                        ])
                    elif temperature > 30:
                        weather_warnings.append({"type": "warning", "title": "⚠️ High Temperature Alert", "message": f"Temperature {temperature}°C above recommended range."})
                        prevention_actions.extend([
                            "Increase air conditioning settings",
                            "Ensure proper ventilation",
                            "Monitor temperature-sensitive artifacts closely",
                            "Close blinds during peak sun hours"
                        ])
                    
                    # Extreme Cold Warning
                    if temperature < 0:
                        weather_warnings.append({"type": "critical", "title": "❄️ EXTREME COLD WARNING", "message": f"Temperature {temperature}°C - Risk of freezing damage!"})
                        prevention_actions.extend([
                            "Activate heating systems immediately",
                            "Check for freezing risks in water pipes and sprinkler systems",
                            "Monitor for condensation issues on walls and artifacts",
                            "Protect artifacts from cold drafts",
                            "Avoid moving artifacts between drastically different temperatures",
                            "Check for ice formation near windows and doors"
                        ])
                    elif temperature < 5:
                        weather_warnings.append({"type": "warning", "title": "❄️ Low Temperature Alert", "message": f"Temperature {temperature}°C below recommended range."})
                        prevention_actions.extend([
                            "Increase heating gradually",
                            "Check for cold spots near windows and exterior walls",
                            "Monitor for condensation"
                        ])
                    
                    # Snow Warning
                    if weather_condition in ["Light Snow", "Moderate Snow", "Heavy Snow"]:
                        weather_warnings.append({"type": "warning", "title": "🌨️ SNOW WARNING", "message": "Snow expected. Risk of moisture and temperature fluctuations."})
                        prevention_actions.extend([
                            "Close all windows and doors",
                            "Check roof for snow accumulation",
                            "Monitor indoor humidity levels",
                            "Prepare dehumidifiers for melting snow",
                            "Ensure heating systems are working properly",
                            "Clear snow from entrances and exits"
                        ])
                    
                    # High Wind Warning
                    if wind_speed > 15:
                        weather_warnings.append({"type": "warning", "title": "💨 HIGH WIND WARNING", "message": f"Wind speed {wind_speed} m/s - Risk of damage from debris."})
                        prevention_actions.extend([
                            "Secure all windows and doors",
                            "Move artifacts away from windows",
                            "Check for drafts and air leaks",
                            "Inspect building exterior for loose elements"
                        ])
                    elif wind_speed > 10:
                        weather_warnings.append({"type": "info", "title": "💨 Strong Wind Alert", "message": f"Wind speed {wind_speed} m/s. Monitor for drafts."})
                        prevention_actions.extend([
                            "Check window seals",
                            "Ensure doors are properly closed"
                        ])
                    
                    # Extreme UV Warning
                    if uv_index > 8:
                        weather_warnings.append({"type": "critical", "title": "☀️ EXTREME UV RADIATION", "message": f"UV Index {uv_index} - Severe fading risk for artifacts!"})
                        prevention_actions.extend([
                            "Close all blinds, curtains, and UV-protective coverings immediately",
                            "Apply UV-filtering film to windows if not already installed",
                            "Move light-sensitive artifacts (textiles, paintings, paper) to darker areas",
                            "Use UV-protective display cases for exposed artifacts",
                            "Limit natural light exposure during peak UV hours (10 AM - 4 PM)",
                            "Consider rotating sensitive artifacts to reduce cumulative exposure"
                        ])
                    elif uv_index > 5:
                        weather_warnings.append({"type": "warning", "title": "☀️ High UV Alert", "message": f"UV Index {uv_index} - Fading risk for light-sensitive materials."})
                        prevention_actions.extend([
                            "Use UV-protective covers on sensitive artifacts",
                            "Close blinds during peak sun hours",
                            "Monitor light-sensitive materials"
                        ])
                    
                    # High Humidity Warning (Mold Risk)
                    if humidity > 75:
                        weather_warnings.append({"type": "critical", "title": "💧 HIGH HUMIDITY - CRITICAL MOLD RISK", "message": f"Humidity {humidity}% - Immediate action required!"})
                        prevention_actions.extend([
                            "Activate dehumidifiers immediately",
                            "Increase air circulation with fans",
                            "Check for mold growth on walls, ceilings, and artifacts",
                            "Inspect HVAC system for proper operation",
                            "Remove any visible moisture from surfaces",
                            "Consider using moisture-absorbing materials in storage areas",
                            "Monitor humidity levels every 2 hours"
                        ])
                    elif humidity > 65:
                        weather_warnings.append({"type": "warning", "title": "💧 High Humidity Alert", "message": f"Humidity {humidity}% - Mold growth risk increasing."})
                        prevention_actions.extend([
                            "Activate dehumidifiers",
                            "Improve air circulation",
                            "Monitor for condensation on walls and windows",
                            "Check vulnerable artifacts for signs of mold"
                        ])
                    
                    # Low Humidity Warning (Cracking Risk)
                    if humidity < 30:
                        weather_warnings.append({"type": "warning", "title": "🏜️ EXTREME DRY CONDITIONS", "message": f"Humidity {humidity}% - Risk of cracking and embrittlement!"})
                        prevention_actions.extend([
                            "Activate humidifiers immediately",
                            "Check for cracking in wooden artifacts, paintings, and paper",
                            "Monitor organic materials closely",
                            "Avoid moving artifacts between environments",
                            "Consider using microclimate enclosures for sensitive items"
                        ])
                    elif humidity < 40:
                        weather_warnings.append({"type": "info", "title": "🏜️ Low Humidity Alert", "message": f"Humidity {humidity}% - Monitor for drying."})
                        prevention_actions.extend([
                            "Consider using humidifiers",
                            "Check wooden artifacts for signs of cracking"
                        ])
                    
                    # Poor Air Quality Warning
                    if aqi_value > 150:
                        weather_warnings.append({"type": "critical", "title": "🌫️ HAZARDOUS AIR QUALITY", "message": f"AQI {aqi_value} - Severe risk to artifacts and health!"})
                        prevention_actions.extend([
                            "Close all external ventilation immediately",
                            "Activate air purifiers with HEPA filters",
                            "Limit exposure of sensitive artifacts",
                            "Seal any gaps around windows and doors",
                            "Consider relocating artifacts to sealed display cases",
                            "Monitor PM2.5 levels continuously"
                        ])
                    elif aqi_value > 100:
                        weather_warnings.append({"type": "warning", "title": "🌫️ Unhealthy Air Quality", "message": f"AQI {aqi_value} - Poor air quality affecting artifacts."})
                        prevention_actions.extend([
                            "Close external windows and vents",
                            "Activate air purifiers",
                            "Monitor for dust accumulation on artifacts"
                        ])
                    
                    # Calculate overall risk score
                    risk_data = {
                        'temperature': temperature,
                        'humidity': humidity,
                        'pm2_5': pm25,
                        'uv_index': uv_index,
                        'pressure': pressure,
                        'wind_speed': wind_speed
                    }
                    risk_score, risk_level, alerts = risk_analyzer.calculate_risk_score(risk_data)
                    
                    # Save to database
                    satellite_record = {
                        'city': city,
                        'province': province,
                        'temperature': temperature,
                        'humidity': humidity,
                        'pressure': pressure,
                        'wind_speed': wind_speed,
                        'wind_direction': str(wind_direction),
                        'uv_index': uv_index,
                        'weather_condition': weather_condition,
                        'aqi': aqi_value,
                        'pm2_5': pm25,
                        'pm10': pm10,
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'alerts': ', '.join([w['title'] for w in weather_warnings])
                    }
                    save_satellite_data(satellite_record)
                    
                    st.success(f"✅ Real-time satellite data retrieved for {city}!")
                    
                    # Display weather warnings prominently
                    if weather_warnings:
                        st.markdown("---")
                        st.markdown("## 🚨 WEATHER WARNINGS & ALERTS")
                        for warning in weather_warnings:
                            if warning['type'] == 'critical':
                                st.markdown(f'<div class="alert-critical"><h3>{warning["title"]}</h3><p>{warning["message"]}</p></div>', unsafe_allow_html=True)
                            elif warning['type'] == 'warning':
                                st.markdown(f'<div class="alert-warning"><h3>{warning["title"]}</h3><p>{warning["message"]}</p></div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="alert-info"><h3>{warning["title"]}</h3><p>{warning["message"]}</p></div>', unsafe_allow_html=True)
                    
                    # Display prevention actions
                    if prevention_actions:
                        st.markdown("## 🛡️ RECOMMENDED PREVENTION ACTIONS")
                        for action in prevention_actions:
                            st.info(f"✓ {action}")
                    
                    # Display current conditions
                    st.markdown("---")
                    st.markdown(f"## 📍 Current Conditions in {city}, {province}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🌡️ Temperature", f"{temperature:.1f}°C")
                        st.metric("💧 Humidity", f"{humidity:.1f}%")
                    with col2:
                        st.metric("📊 Pressure", f"{pressure:.1f} hPa")
                        st.metric("💨 Wind Speed", f"{wind_speed:.1f} m/s")
                    with col3:
                        st.metric("☀️ UV Index", f"{uv_index:.1f}")
                        st.metric("🎭 Weather", weather_condition)
                    with col4:
                        st.metric("🌫️ AQI", aqi_value)
                        if aqi_value <= 50:
                            st.success("Good Air Quality")
                        elif aqi_value <= 100:
                            st.warning("Moderate Air Quality")
                        else:
                            st.error("Poor Air Quality")
                        st.metric("PM2.5", f"{pm25:.1f} µg/m³")
                    
                    # Risk assessment
                    if risk_level == "HIGH":
                        st.markdown(f'<div class="risk-high"><h2>⚠️ HIGH RISK - Take Immediate Precautions</h2><h3>Risk Score: {risk_score}/100</h3><p>Environmental conditions pose a serious threat to heritage artifacts</p></div>', unsafe_allow_html=True)
                    elif risk_level == "MEDIUM":
                        st.markdown(f'<div class="risk-medium"><h2>⚠️ MEDIUM RISK - Monitor Weather Conditions</h2><h3>Risk Score: {risk_score}/100</h3><p>Some parameters require attention</p></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="risk-low"><h2>✅ LOW RISK - Conditions Favorable</h2><h3>Risk Score: {risk_score}/100</h3><p>Current conditions are suitable for heritage preservation</p></div>', unsafe_allow_html=True)
                    
                    st.caption(f"🕐 Data Source: Open-Meteo Satellite Network | Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                else:
                    st.error(f"Failed to fetch data. API returned: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Error fetching satellite data: {e}")
                st.info("Please check your internet connection and try again.")
    
    st.markdown("---")
    st.markdown("### 📊 Satellite Data History")
    
    if 'city' in locals() and city:
        sat_history = get_satellite_history(city, 30)
    else:
        sat_history = get_satellite_history(days=30)
    
    if not sat_history.empty:
        display_cols = ['timestamp', 'city', 'temperature', 'weather_condition', 'aqi', 'risk_level']
        available_cols = [col for col in display_cols if col in sat_history.columns]
        st.dataframe(sat_history[available_cols], use_container_width=True)
        
        # Historical trends
        if len(sat_history) > 1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sat_history['timestamp'], y=sat_history['temperature'], 
                                    mode='lines+markers', name='Temperature', line=dict(color='#ff6b6b', width=2)))
            fig.add_trace(go.Scatter(x=sat_history['timestamp'], y=sat_history['risk_score'], 
                                    mode='lines', name='Risk Score', line=dict(color='#ffd93d', width=2, dash='dash')))
            fig.update_layout(title=f"Weather Trend Analysis for {city if 'city' in locals() else 'City'}", 
                             xaxis_title="Date", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)
            
            # Long-term assessment
            if len(sat_history) >= 7:
                st.markdown("### 📈 Long-Term Weather Assessment")
                
                avg_temp = sat_history['temperature'].mean()
                avg_humidity = sat_history['humidity'].mean()
                avg_pressure = sat_history['pressure'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Temperature", f"{avg_temp:.1f}°C")
                    if avg_temp > 25:
                        st.warning("Above ideal range for artifacts")
                    elif avg_temp < 18:
                        st.warning("Below ideal range for artifacts")
                    else:
                        st.success("Within ideal range")
                
                with col2:
                    st.metric("Average Humidity", f"{avg_humidity:.1f}%")
                    if avg_humidity > 55:
                        st.warning("Above ideal range - Mold risk")
                    elif avg_humidity < 45:
                        st.warning("Below ideal range - Cracking risk")
                    else:
                        st.success("Within ideal range")
                
                with col3:
                    st.metric("Average Pressure", f"{avg_pressure:.1f} hPa")
                    if avg_pressure < 1010:
                        st.warning("Low pressure - Unstable weather patterns")
                    else:
                        st.success("Normal pressure")
                
                # Long-term recommendations
                st.markdown("### 📋 Long-Term Recommendations")
                if avg_temp > 24:
                    st.info("• Consider upgrading cooling systems for summer months")
                if avg_humidity > 55:
                    st.info("• Install additional dehumidifiers for monsoon season")
                if avg_pressure < 1010:
                    st.info("• Prepare for storm season - Check building integrity regularly")
                
                # Risk trend
                risk_trend = sat_history['risk_score'].diff().mean()
                if risk_trend > 0:
                    st.warning("⚠️ Risk levels are increasing over time. Schedule comprehensive review.")
                elif risk_trend < 0:
                    st.success("✅ Risk levels are decreasing. Continue current practices.")
                else:
                    st.info("📊 Risk levels are stable. Maintain regular monitoring.")
    else:
        st.info("No satellite data available. Click 'Fetch Real-Time Satellite Data' to get current conditions.")

# ============================================
# LONG-TERM ANALYSIS PAGE
# ============================================

elif page == "📈 Long-Term Analysis":
    st.markdown('<div class="section-header">📈 Comprehensive Long-Term Analysis</div>', unsafe_allow_html=True)
    st.markdown("*2-3 months historical data analysis with trend detection and prevention recommendations*")
    
    analysis_type = st.radio("Select Data Type", ["Sensor Data", "Manual Data", "Satellite Data"], horizontal=True)
    
    if analysis_type == "Sensor Data":
        rooms = ["Main Gallery", "Archive Room", "Conservation Lab", "Storage Room", "Courtyard"]
        selected_room = st.selectbox("Select Room", rooms)
        days = st.slider("Time Period (days)", 30, 90, 60)
        
        df = get_sensor_history(selected_room, days)
        
        if not df.empty:
            trends = risk_analyzer.analyze_long_term_trend(df)
            
            st.markdown("### 📊 Executive Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### 🌡️ Temperature")
                st.metric("Average", f"{df['temperature'].mean():.1f}°C")
                st.metric("Max", f"{df['temperature'].max():.1f}°C")
                st.metric("Min", f"{df['temperature'].min():.1f}°C")
            with col2:
                st.markdown("#### 💧 Humidity")
                st.metric("Average", f"{df['humidity'].mean():.1f}%")
                st.metric("Max", f"{df['humidity'].max():.1f}%")
                st.metric("Min", f"{df['humidity'].min():.1f}%")
            with col3:
                st.markdown("#### 📈 Risk Assessment")
                st.metric("Average Risk", f"{df['risk_score'].mean():.1f}")
                st.metric("High Risk Days", len(df[df['risk_score'] > 60]))
                st.metric("Critical Events", len(df[df['risk_level'] == 'HIGH']))
            
            if trends:
                st.markdown("### 📈 Trend Analysis")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Temperature Trend:** {trends.get('temperature_trend', 'stable').upper()}")
                    st.write(f"**Humidity Trend:** {trends.get('humidity_trend', 'stable').upper()}")
                with col2:
                    st.write(f"**Risk Trend:** {trends.get('risk_trend', 'stable').upper()}")
                    st.write(f"**Days Analyzed:** {trends.get('summary', {}).get('days_covered', 0)}")
            
            # Graphs
            fig = make_subplots(rows=4, cols=1, 
                               subplot_titles=('Temperature Trend', 'Humidity Trend', 'PM2.5 Trend', 'Risk Score Trend'))
            
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'], mode='lines', name='Temperature', line=dict(color='#ff6b6b', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['humidity'], mode='lines', name='Humidity', line=dict(color='#4facfe', width=2)), row=2, col=1)
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['pm2_5'], mode='lines', name='PM2.5', line=dict(color='#764ba2', width=2)), row=3, col=1)
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['risk_score'], mode='lines+markers', name='Risk Score', line=dict(color='#ff6b6b', width=2)), row=4, col=1)
            
            fig.update_layout(height=900, showlegend=True, title_text=f"Long-Term Analysis for {selected_room}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk distribution
            risk_counts = df['risk_level'].value_counts()
            fig_pie = go.Figure(data=[go.Pie(labels=risk_counts.index, values=risk_counts.values, hole=0.3)])
            fig_pie.update_layout(title="Risk Level Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Prevention recommendations
            st.markdown("### 🛡️ Prevention Recommendations")
            
            if trends and trends.get('risk_trend') == 'worsening':
                st.error("🚨 **CRITICAL:** Risk trend is worsening over time!")
                st.markdown("""
                **Immediate Actions Required:**
                - Schedule comprehensive HVAC system inspection and maintenance
                - Install additional climate control equipment if needed
                - Review and update preservation protocols
                - Consider relocating most sensitive artifacts to more stable environments
                - Increase monitoring frequency to daily
                """)
            elif trends and trends.get('risk_trend') == 'improving':
                st.success("✅ **Positive:** Risk trend is improving.")
                st.markdown("""
                **Continue Current Practices:**
                - Maintain regular monitoring schedule
                - Document successful interventions for future reference
                - Continue preventive conservation measures
                """)
            else:
                st.info("📊 **Stable:** Risk levels are stable.")
                st.markdown("""
                **Maintain Standard Protocols:**
                - Continue regular monitoring
                - Perform scheduled maintenance of climate control systems
                - Document all environmental readings
                """)
            
            # Specific recommendations based on averages
            if df['temperature'].mean() > 24:
                st.warning("🌡️ **Temperature Alert:** Average temperature above ideal range. Consider cooling system upgrades.")
            if df['humidity'].mean() > 55:
                st.warning("💧 **Humidity Alert:** Average humidity above ideal range. Increase dehumidification.")
            if df['pm2_5'].mean() > 35:
                st.warning("🌫️ **Air Quality Alert:** Average PM2.5 above safe levels. Improve air filtration.")
        else:
            st.info(f"No sensor data for {selected_room} in the selected period.")
    
    elif analysis_type == "Manual Data":
        manual_history = get_manual_history(90)
        if not manual_history.empty:
            st.dataframe(manual_history, use_container_width=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=manual_history['timestamp'], y=manual_history['risk_score'], 
                                    mode='lines+markers', name='Risk Score', line=dict(color='#ff6b6b', width=2)))
            fig.update_layout(title="Manual Inspection Risk Trend", xaxis_title="Date", yaxis_title="Risk Score")
            st.plotly_chart(fig, use_container_width=True)
            
            # Prevention recommendations based on manual data
            st.markdown("### 🛡️ Prevention Recommendations")
            high_risk_entries = manual_history[manual_history['risk_level'] == 'HIGH']
            if len(high_risk_entries) > 0:
                st.error(f"⚠️ Found {len(high_risk_entries)} high-risk inspections. Review these entries for patterns.")
            else:
                st.success("✅ No high-risk inspections recorded. Continue regular monitoring.")
        else:
            st.info("No manual data available")
    
    else:
        sat_history = get_satellite_history(days=90)
        if not sat_history.empty:
            st.dataframe(sat_history, use_container_width=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=sat_history['timestamp'], y=sat_history['temperature'], 
                                    mode='lines+markers', name='Temperature', line=dict(color='#4facfe', width=2)))
            fig.add_trace(go.Scatter(x=sat_history['timestamp'], y=sat_history['risk_score'], 
                                    mode='lines', name='Risk Score', line=dict(color='#ff6b6b', width=2)))
            fig.update_layout(title="Satellite Data Long-Term Trends", xaxis_title="Date", yaxis_title="Value")
            st.plotly_chart(fig, use_container_width=True)
            
            # Seasonal recommendations
            st.markdown("### 🛡️ Seasonal Prevention Recommendations")
            avg_temp = sat_history['temperature'].mean()
            avg_humidity = sat_history['humidity'].mean()
            
            if avg_temp > 25:
                st.info("☀️ **Summer Preparation:** Prepare cooling systems, UV protection, and monitor for heat stress on artifacts.")
            elif avg_temp < 10:
                st.info("❄️ **Winter Preparation:** Prepare heating systems, monitor for condensation, protect against cold drafts.")
            
            if avg_humidity > 60:
                st.info("💧 **Monsoon Preparation:** Prepare dehumidifiers, check for leaks, monitor mold growth.")
        else:
            st.info("No satellite data available")

# ============================================
# FOOTER
# ============================================

st.markdown("""
<div class="footer">
    <small>
    <strong>Micro-Climate Guardian Pro</strong> | AI-Powered Heritage Protection System<br>
    Sensors: BMP280 (Temperature, Pressure, Humidity) • BH1750 (Light Intensity) • PMS5003 (PM1.0, PM2.5, PM10)<br>
    Data stored locally | Real-time monitoring | Long-term analysis | AI risk assessment
    </small>
</div>
""", unsafe_allow_html=True)