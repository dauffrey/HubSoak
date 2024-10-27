import streamlit as st
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
import pandas as pd

from utils.database import Database
from utils.sensors import SensorSimulator
from utils.alerts import AlertSystem
from utils.recommendations import WaterQualityRecommender
from utils.maintenance import MaintenanceScheduler
from utils.remote_access import remote_access

# Page configuration
st.set_page_config(
    page_title="Hot Tub Monitor",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    return (
        Database(), 
        SensorSimulator(), 
        AlertSystem(), 
        WaterQualityRecommender(),
        MaintenanceScheduler()
    )

db, sensor_simulator, alert_system, recommender, maintenance = init_components()

def render_maintenance_section():
    st.header("🔧 Maintenance Schedule")
    
    # Tabs for different maintenance views
    tab1, tab2, tab3 = st.tabs(["Upcoming Tasks", "Add New Task", "Task History"])
    
    with tab1:
        upcoming_tasks = maintenance.get_upcoming_tasks(days_ahead=14)
        if not upcoming_tasks:
            st.info("No upcoming maintenance tasks in the next 14 days.")
        else:
            for task in upcoming_tasks:
                with st.expander(f"📅 {task['task_name']} - Due: {task['next_due'].strftime('%Y-%m-%d')}"):
                    st.write(f"**Description:** {task['description']}")
                    st.write(f"**Frequency:** Every {task['frequency_days']} days")
                    if task['last_completed']:
                        st.write(f"**Last completed:** {task['last_completed'].strftime('%Y-%m-%d')}")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        notes = st.text_input("Add completion notes (optional):", key=f"notes_{task['id']}")
                    with col2:
                        if st.button("Mark Complete", key=f"complete_{task['id']}"):
                            maintenance.complete_task(task['id'], notes)
                            st.success("Task marked as completed!")
                            st.rerun()
    
    with tab2:
        st.subheader("Add New Maintenance Task")
        
        # Option to add default tasks
        if st.button("Add Default Tasks"):
            default_tasks = maintenance.get_default_tasks()
            for task in default_tasks:
                maintenance.add_task(task['name'], task['description'], task['frequency_days'])
            st.success("Default maintenance tasks added!")
            st.rerun()
        
        # Custom task form
        with st.form("new_task_form"):
            task_name = st.text_input("Task Name")
            description = st.text_area("Description")
            frequency = st.number_input("Frequency (days)", min_value=1, value=30)
            
            if st.form_submit_button("Add Task"):
                if task_name and description:
                    maintenance.add_task(task_name, description, frequency)
                    st.success("New task added successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in both task name and description.")
    
    with tab3:
        st.subheader("Maintenance History")
        tasks = maintenance.get_upcoming_tasks(days_ahead=365)  # Get all tasks
        if tasks:
            task_id = st.selectbox(
                "Select Task",
                options=[task['id'] for task in tasks],
                format_func=lambda x: next(task['task_name'] for task in tasks if task['id'] == x)
            )
            
            history = maintenance.get_task_history(task_id)
            if history:
                for entry in history:
                    st.write(f"**Completed:** {entry['completed_at'].strftime('%Y-%m-%d %H:%M')}")
                    if entry['notes']:
                        st.write(f"**Notes:** {entry['notes']}")
                    st.divider()
            else:
                st.info("No history found for this task.")
        else:
            st.info("No tasks found. Add some tasks to view their history.")

def render_remote_access_section():
    st.header("🔒 Remote Access")
    
    # Get connection information
    connection_info = remote_access.get_connection_info()
    
    # Display connection status and information
    st.success("✅ Remote Access is Active")
    
    # Connection Information
    with st.expander("📡 Connection Information", expanded=True):
        st.write("**Access URL:**")
        st.code(connection_info['url'])
        st.write("""
        **How to Access:**
        1. Share this URL with authorized users
        2. The monitoring system can be accessed from any web browser
        3. All data is viewed in real-time through secure HTTPS
        """)
        
        st.info("""
        **Security Notes:**
        - All connections are encrypted using HTTPS
        - Access is read-only by default
        - Monitor access logs below for security
        """)
    
    # Access Logs
    st.subheader("📊 Recent Access Logs")
    logs = remote_access.get_access_logs()
    if logs:
        for log in logs:
            st.text(f"{log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {log['client']}")
    else:
        st.info("No access logs yet")

    # Monitoring Options
    st.subheader("⚙️ Monitoring Settings")
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Enable Email Notifications", 
                   help="Send email notifications when someone accesses the system")
    with col2:
        st.number_input("Auto-refresh Interval (seconds)", 
                       min_value=5, 
                       max_value=60, 
                       value=10)

def main():
    st.title("🌊 Hot Tub Monitoring System")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        update_interval = st.slider("Update Interval (seconds)", 1, 60, 5)
        show_historical = st.checkbox("Show Historical Data", True)
        
        st.header("Sensor Calibration")
        sensor_type = st.selectbox(
            "Select Sensor", 
            ["ph", "temperature", "turbidity", "orp", "conductivity", "free_chlorine", "total_chlorine"]
        )
        offset = st.number_input(f"{sensor_type.title()} Offset", -10.0, 10.0, 0.0, 0.1)
        scale = st.number_input(f"{sensor_type.title()} Scale Factor", 0.1, 2.0, 1.0, 0.1)
        
        if st.button("Apply Calibration"):
            sensor_simulator.update_calibration(sensor_type, offset, scale)
            db.update_calibration(sensor_type, offset, scale)
            st.success("Calibration updated successfully!")

    # Main content area
    tab1, tab2, tab3 = st.tabs(["Monitoring", "Maintenance", "Remote Access"])
    
    with tab1:
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        try:
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
                
            with col5:
                st.metric(
                    label="Conductivity/TDS",
                    value=f"{readings['conductivity']:.0f} ppm",
                    delta=f"{readings['conductivity'] - 600.0:.0f} from ideal"
                )

            with col6:
                st.metric(
                    label="Free Chlorine",
                    value=f"{readings['free_chlorine']:.1f} ppm",
                    delta=f"{readings['free_chlorine'] - 2.0:.1f} from ideal"
                )

            with col7:
                st.metric(
                    label="Total Chlorine",
                    value=f"{readings['total_chlorine']:.1f} ppm",
                    delta=f"{readings['total_chlorine'] - 3.0:.1f} from ideal"
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
            db.log_reading(
                readings['ph'], readings['temperature'], readings['turbidity'],
                readings['orp'], readings['conductivity'], readings['free_chlorine'],
                readings['total_chlorine']
            )

            # Historical data visualization
            if show_historical:
                st.header("Historical Data")
                historical_data = db.get_historical_data(hours=24)
                
                if historical_data:
                    # Convert to DataFrame
                    df = pd.DataFrame(historical_data)
                    df.columns = ['timestamp', 'ph_level', 'temperature', 'turbidity', 
                                'orp_level', 'conductivity', 'free_chlorine', 'total_chlorine']
                    
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
                    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['conductivity'],
                                         name='Conductivity', line=dict(color='orange')))
                    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['free_chlorine'],
                                         name='Free Chlorine', line=dict(color='cyan')))
                    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['total_chlorine'],
                                         name='Total Chlorine', line=dict(color='magenta')))
                    
                    fig.update_layout(
                        title='Sensor Readings Over Time',
                        xaxis_title='Time',
                        yaxis_title='Value',
                        height=500,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error loading sensor data: {str(e)}")
    
    with tab2:
        render_maintenance_section()
        
    with tab3:
        render_remote_access_section()

if __name__ == "__main__":
    main()