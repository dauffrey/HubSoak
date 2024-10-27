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
    initial_sidebar_state="collapsed"  # Start with collapsed sidebar for more space
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
    st.header("🔧 Maintenance")
    
    # Tabs for different maintenance views
    tab1, tab2, tab3 = st.tabs(["📅 Tasks", "➕ New", "📖 History"])
    
    with tab1:
        upcoming_tasks = maintenance.get_upcoming_tasks(days_ahead=14)
        if not upcoming_tasks:
            st.info("No upcoming tasks in next 14 days")
        else:
            for task in upcoming_tasks:
                with st.expander(f"📅 {task['task_name']}"):
                    st.write(f"**Due:** {task['next_due'].strftime('%Y-%m-%d')}")
                    st.write(f"**Description:** {task['description']}")
                    notes = st.text_input("Notes (optional):", key=f"notes_{task['id']}")
                    if st.button("✓ Complete", key=f"complete_{task['id']}", use_container_width=True):
                        maintenance.complete_task(task['id'], notes)
                        st.success("Task completed!")
                        st.rerun()
    
    with tab2:
        st.button("📋 Add Default Tasks", use_container_width=True, 
                 on_click=lambda: [maintenance.add_task(task['name'], task['description'], 
                                                      task['frequency_days']) 
                                 for task in maintenance.get_default_tasks()])
        
        # Custom task form
        with st.form("new_task_form"):
            task_name = st.text_input("Task Name")
            description = st.text_area("Description")
            frequency = st.number_input("Frequency (days)", min_value=1, value=30)
            
            if st.form_submit_button("Add Task", use_container_width=True):
                if task_name and description:
                    maintenance.add_task(task_name, description, frequency)
                    st.success("Task added!")
                    st.rerun()
                else:
                    st.error("Fill all fields")
    
    with tab3:
        tasks = maintenance.get_upcoming_tasks(days_ahead=365)
        if tasks:
            task_id = st.selectbox(
                "Select Task",
                options=[task['id'] for task in tasks],
                format_func=lambda x: next(task['task_name'] for task in tasks if task['id'] == x)
            )
            
            history = maintenance.get_task_history(task_id)
            if history:
                for entry in history:
                    st.write(f"✓ {entry['completed_at'].strftime('%Y-%m-%d')}")
                    if entry['notes']:
                        st.info(entry['notes'])
            else:
                st.info("No history for this task")

def render_remote_access_section():
    st.header("🔒 Remote Access")
    
    connection_info = remote_access.get_connection_info()
    
    st.success("✅ Remote Access Active")
    
    with st.expander("📡 Connection Info", expanded=True):
        st.write("**Access URL:**")
        st.code(connection_info['url'])
        st.write("**Security:**")
        st.info("• HTTPS encrypted\n• Read-only access\n• Activity logged")
    
    st.subheader("📊 Recent Access")
    logs = remote_access.get_access_logs(limit=5)
    if logs:
        for log in logs:
            st.text(f"{log['timestamp'].strftime('%H:%M:%S')} - {log['client']}")
    else:
        st.info("No access logs")

    st.subheader("⚙️ Settings")
    st.checkbox("📧 Email Alerts", help="Get email when accessed")
    st.slider("🔄 Refresh (sec)", 5, 60, 10)

def main():
    st.title("🌊 Hot Tub Monitor")
    
    # Sidebar with larger touch targets
    with st.sidebar:
        st.header("⚙️ Controls")
        update_interval = st.slider("Update Speed", 1, 60, 5)
        show_historical = st.checkbox("📈 Show History", True)
        
        st.header("🎯 Calibration")
        sensor_type = st.selectbox(
            "Sensor", 
            ["ph", "temperature", "turbidity", "orp", "conductivity", 
             "free_chlorine", "total_chlorine"]
        )
        offset = st.number_input(f"Offset", -10.0, 10.0, 0.0, 0.1)
        scale = st.number_input(f"Scale", 0.1, 2.0, 1.0, 0.1)
        
        if st.button("Apply", use_container_width=True):
            sensor_simulator.update_calibration(sensor_type, offset, scale)
            db.update_calibration(sensor_type, offset, scale)
            st.success("Updated!")

    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Monitor", "🔧 Maintain", "🔒 Remote"])
    
    with tab1:
        try:
            readings = sensor_simulator.get_readings()
            alerts = sensor_simulator.check_alerts(readings)
            
            # Display readings in 2x4 grid for better touch interaction
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "pH Level",
                    f"{readings['ph']:.1f}",
                    f"{readings['ph'] - 7.0:.1f}"
                )
                st.metric(
                    "Temperature",
                    f"{readings['temperature']:.1f}°C",
                    f"{readings['temperature'] - 37.5:.1f}°C"
                )
                st.metric(
                    "Turbidity",
                    f"{readings['turbidity']:.1f} NTU",
                    f"{readings['turbidity'] - 2.0:.1f}"
                )
                st.metric(
                    "ORP Level",
                    f"{readings['orp']:.0f} mV",
                    f"{readings['orp'] - 700.0:.0f}"
                )
            
            with col2:
                st.metric(
                    "TDS",
                    f"{readings['conductivity']:.0f} ppm",
                    f"{readings['conductivity'] - 600.0:.0f}"
                )
                st.metric(
                    "Free Chlorine",
                    f"{readings['free_chlorine']:.1f} ppm",
                    f"{readings['free_chlorine'] - 2.0:.1f}"
                )
                st.metric(
                    "Total Chlorine",
                    f"{readings['total_chlorine']:.1f} ppm",
                    f"{readings['total_chlorine'] - 3.0:.1f}"
                )

            # Process and display alerts
            current_alerts = alert_system.process_alerts(alerts)
            alert_system.display_alerts()

            # Display recommendations
            st.header("📋 Recommendations")
            recommendations = recommender.get_recommendations(readings)
            
            for rec in recommendations:
                if rec['status'] == 'optimal':
                    st.success(f"✅ {rec['parameter']}: {rec['action']}")
                else:
                    with st.expander(f"⚠️ {rec['parameter']} ({rec['status'].title()})"):
                        st.write(f"**Action:** {rec['action']}")
                        st.info(f"**Details:** {rec['details']}")

            # Log readings
            db.log_reading(
                readings['ph'], readings['temperature'], readings['turbidity'],
                readings['orp'], readings['conductivity'], readings['free_chlorine'],
                readings['total_chlorine']
            )

            # Historical visualization
            if show_historical:
                st.header("📈 History")
                historical_data = db.get_historical_data(hours=24)
                
                if historical_data:
                    df = pd.DataFrame(historical_data)
                    df.columns = ['timestamp', 'ph_level', 'temperature', 'turbidity', 
                                'orp_level', 'conductivity', 'free_chlorine', 'total_chlorine']
                    
                    # Create a more touch-friendly graph
                    fig = go.Figure()
                    
                    for col, color in [
                        ('ph_level', 'blue'),
                        ('temperature', 'red'),
                        ('turbidity', 'green'),
                        ('orp_level', 'purple'),
                        ('conductivity', 'orange'),
                        ('free_chlorine', 'cyan'),
                        ('total_chlorine', 'magenta')
                    ]:
                        fig.add_trace(go.Scatter(
                            x=df['timestamp'],
                            y=df[col],
                            name=col.replace('_', ' ').title(),
                            line=dict(color=color, width=3)
                        ))
                    
                    fig.update_layout(
                        title='24-Hour History',
                        height=400,
                        hovermode='x unified',
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        margin=dict(l=10, r=10, t=30, b=10)
                    )
                    
                    # Make the plot more touch-friendly
                    fig.update_layout(
                        dragmode='pan',  # Enable touch-drag to pan
                        selectdirection='h',  # Horizontal selection
                        modebar=dict(orientation='v')  # Vertical modebar
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={
                        'scrollZoom': True,
                        'displayModeBar': True,
                        'modeBarButtonsToRemove': [
                            'select2d', 'lasso2d', 'resetScale2d'
                        ]
                    })
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    with tab2:
        render_maintenance_section()
        
    with tab3:
        render_remote_access_section()

if __name__ == "__main__":
    main()
