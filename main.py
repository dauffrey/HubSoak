import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
import pandas as pd

from utils.database import Database
from utils.sensors import SensorSimulator
from utils.alerts import AlertSystem
from utils.recommendations import WaterQualityRecommender

# Page configuration
st.set_page_config(
    page_title="Hot Tub Monitor",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open('assets/styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def init_components():
    return Database(), SensorSimulator(), AlertSystem(), WaterQualityRecommender()

db, sensor_simulator, alert_system, recommender = init_components()

def main():
    st.title("🌊 Hot Tub Monitoring System")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        update_interval = st.slider("Update Interval (seconds)", 1, 60, 5)
        show_historical = st.checkbox("Show Historical Data", True)
        
        st.header("Sensor Calibration")
        sensor_type = st.selectbox("Select Sensor", ["ph", "temperature", "turbidity", "orp"])
        offset = st.number_input(f"{sensor_type.title()} Offset", -10.0, 10.0, 0.0, 0.1)
        scale = st.number_input(f"{sensor_type.title()} Scale Factor", 0.1, 2.0, 1.0, 0.1)
        
        if st.button("Apply Calibration"):
            sensor_simulator.update_calibration(sensor_type, offset, scale)
            db.update_calibration(sensor_type, offset, scale)
            st.success("Calibration updated successfully!")

    # Main content area
    col1, col2, col3, col4 = st.columns(4)
    
    # Get current readings
    readings = sensor_simulator.get_readings()
    alerts = sensor_simulator.check_alerts(readings)
    
    # Display current readings with metrics
    with col1:
        st.metric(
            label="pH Level",
            value=f"{readings['ph']:.2f}",
            delta=f"{readings['ph'] - 7.0:.2f} from neutral"
        )
    
    with col2:
        st.metric(
            label="Temperature",
            value=f"{readings['temperature']:.1f}°C",
            delta=f"{readings['temperature'] - 37.5:.1f}°C from ideal"
        )
    
    with col3:
        st.metric(
            label="Turbidity",
            value=f"{readings['turbidity']:.1f} NTU",
            delta=f"{readings['turbidity'] - 2.0:.1f} from ideal"
        )
        
    with col4:
        st.metric(
            label="ORP Level",
            value=f"{readings['orp']:.1f} mV",
            delta=f"{readings['orp'] - 700.0:.1f} mV from ideal"
        )

    # Process and display alerts
    current_alerts = alert_system.process_alerts(alerts)
    alert_system.display_alerts()

    # Display water quality recommendations
    st.header("📋 Water Quality Recommendations")
    recommendations = recommender.get_recommendations(readings)
    
    for rec in recommendations:
        if rec['status'] == 'optimal':
            st.success(f"✅ {rec['parameter']}: {rec['action']}")
        else:
            with st.expander(f"⚠️ {rec['parameter']} ({rec['status'].title()})"):
                st.write(f"**Recommended Action:** {rec['action']}")
                st.info(f"**Details:** {rec['details']}")

    # Log readings to database
    db.log_reading(readings['ph'], readings['temperature'], readings['turbidity'], readings['orp'])

    # Historical data visualization
    if show_historical:
        st.header("Historical Data")
        historical_data = db.get_historical_data(hours=24)
        
        if historical_data:
            df = pd.DataFrame(historical_data, 
                            columns=['timestamp', 'ph_level', 'temperature', 'turbidity', 'orp_level'])
            
            fig = go.Figure()
            
            # Add traces for each sensor
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ph_level'],
                                    name='pH Level', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['temperature'],
                                    name='Temperature', line=dict(color='red')))
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['turbidity'],
                                    name='Turbidity', line=dict(color='green')))
            fig.add_trace(go.Scatter(x=df['timestamp'], y=df['orp_level'],
                                    name='ORP Level', line=dict(color='purple')))
            
            fig.update_layout(
                title='Sensor Readings Over Time',
                xaxis_title='Time',
                yaxis_title='Value',
                height=500,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)

    # Auto-refresh
    time.sleep(update_interval)
    st.rerun()

if __name__ == "__main__":
    main()
