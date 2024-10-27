import os
import streamlit as st
from datetime import datetime

class RemoteAccessManager:
    def __init__(self):
        self.web_port = 5000
        self._access_logs = []
        
    def get_connection_info(self):
        """Get remote access connection information"""
        return {
            'web_port': self.web_port,
            'url': f"https://{os.environ.get('REPL_SLUG', 'your-repl')}.{os.environ.get('REPL_OWNER', 'user')}.repl.co",
            'status': 'running'  # Streamlit is always running
        }
    
    def log_access(self, client_info):
        """Log remote access attempts"""
        self._access_logs.append({
            'timestamp': datetime.now(),
            'client': client_info
        })
    
    def get_access_logs(self, limit=10):
        """Get recent access logs"""
        return sorted(self._access_logs, key=lambda x: x['timestamp'], reverse=True)[:limit]

# Create a singleton instance
remote_access = RemoteAccessManager()
