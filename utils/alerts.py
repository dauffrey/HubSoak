from typing import Dict, List
import streamlit as st

class AlertSystem:
    def __init__(self):
        self.alert_history: List[Dict] = []
        
    def process_alerts(self, alerts: Dict[str, tuple]):
        current_alerts = []
        
        for sensor, (is_alert, message) in alerts.items():
            if is_alert:
                current_alerts.append({
                    'sensor': sensor,
                    'message': message,
                    'severity': 'high' if 'too high' in message else 'low'
                })
                
        if current_alerts:
            self.alert_history.extend(current_alerts)
            # Keep only last 100 alerts
            self.alert_history = self.alert_history[-100:]
            
        return current_alerts

    def display_alerts(self):
        if not self.alert_history:
            st.info("No recent alerts")
            return

        st.subheader("Recent Alerts")
        for alert in reversed(self.alert_history[-5:]):
            color = "🔴" if alert['severity'] == 'high' else "🟡"
            st.warning(f"{color} {alert['message']}")
