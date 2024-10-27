import os
import psycopg2
from datetime import datetime
from typing import Dict, List, Tuple

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ['PGDATABASE'],
            user=os.environ['PGUSER'],
            password=os.environ['PGPASSWORD'],
            host=os.environ['PGHOST'],
            port=os.environ['PGPORT']
        )
        self._create_tables()

    def _create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ph_level FLOAT,
                    temperature FLOAT,
                    turbidity FLOAT
                );
                
                CREATE TABLE IF NOT EXISTS sensor_calibration (
                    id SERIAL PRIMARY KEY,
                    sensor_type VARCHAR(50),
                    offset_value FLOAT,
                    scale_factor FLOAT,
                    last_calibrated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            self.conn.commit()

    def log_reading(self, ph: float, temp: float, turbidity: float):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sensor_readings (ph_level, temperature, turbidity) VALUES (%s, %s, %s)",
                (ph, temp, turbidity)
            )
            self.conn.commit()

    def get_historical_data(self, hours: int = 24) -> List[Tuple]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT timestamp, ph_level, temperature, turbidity 
                FROM sensor_readings 
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC
            """, (hours,))
            return cur.fetchall()

    def update_calibration(self, sensor_type: str, offset: float, scale: float):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sensor_calibration (sensor_type, offset_value, scale_factor)
                VALUES (%s, %s, %s)
                ON CONFLICT (sensor_type) DO UPDATE 
                SET offset_value = %s, scale_factor = %s, last_calibrated = CURRENT_TIMESTAMP
            """, (sensor_type, offset, scale, offset, scale))
            self.conn.commit()
