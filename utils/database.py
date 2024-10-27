import os
import psycopg2
from datetime import datetime
from typing import Dict, List, Tuple
from contextlib import contextmanager

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

    @contextmanager
    def get_cursor(self):
        """Context manager for database operations that handles transactions."""
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()

    def _create_tables(self):
        try:
            with self.get_cursor() as cur:
                # Drop and recreate sensor_calibration table
                cur.execute("""
                    DROP TABLE IF EXISTS sensor_calibration CASCADE;
                    
                    CREATE TABLE IF NOT EXISTS sensor_readings (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ph_level FLOAT,
                        temperature FLOAT,
                        turbidity FLOAT,
                        orp_level FLOAT,
                        conductivity FLOAT DEFAULT 0.0,
                        free_chlorine FLOAT DEFAULT 0.0,
                        total_chlorine FLOAT DEFAULT 0.0,
                        bromine FLOAT DEFAULT 0.0
                    );

                    CREATE TABLE sensor_calibration (
                        id SERIAL PRIMARY KEY,
                        sensor_type VARCHAR(50),
                        offset_value FLOAT,
                        scale_factor FLOAT,
                        last_calibrated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT unique_sensor_type_constraint UNIQUE (sensor_type)
                    );

                    -- Initialize default calibration values if needed
                    INSERT INTO sensor_calibration (sensor_type, offset_value, scale_factor)
                    VALUES 
                        ('ph', 0.0, 1.0),
                        ('temperature', 0.0, 1.0),
                        ('turbidity', 0.0, 1.0),
                        ('orp', 0.0, 1.0),
                        ('conductivity', 0.0, 1.0),
                        ('free_chlorine', 0.0, 1.0),
                        ('total_chlorine', 0.0, 1.0),
                        ('bromine', 0.0, 1.0)
                    ON CONFLICT ON CONSTRAINT unique_sensor_type_constraint DO NOTHING;
                """)
        except psycopg2.Error as e:
            raise Exception(f"Database error creating tables: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error creating tables: {str(e)}")

    def log_reading(self, ph: float, temp: float, turbidity: float, orp: float, conductivity: float, 
                   free_chlorine: float, total_chlorine: float, bromine: float):
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    """INSERT INTO sensor_readings 
                       (ph_level, temperature, turbidity, orp_level, conductivity, free_chlorine, total_chlorine, bromine) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (ph, temp, turbidity, orp, conductivity, free_chlorine, total_chlorine, bromine)
                )
        except Exception as e:
            raise Exception(f"Error logging sensor reading: {str(e)}")

    def get_historical_data(self, hours: int = 24) -> List[Tuple]:
        try:
            with self.get_cursor() as cur:
                cur.execute("""
                    SELECT timestamp, ph_level, temperature, turbidity, orp_level, conductivity, 
                           free_chlorine, total_chlorine, bromine 
                    FROM sensor_readings 
                    WHERE timestamp > NOW() - INTERVAL '%s hours'
                    ORDER BY timestamp DESC
                """, (hours,))
                return cur.fetchall()
        except Exception as e:
            raise Exception(f"Error retrieving historical data: {str(e)}")

    def update_calibration(self, sensor_type: str, offset: float, scale: float):
        try:
            with self.get_cursor() as cur:
                cur.execute("""
                    INSERT INTO sensor_calibration (sensor_type, offset_value, scale_factor)
                    VALUES (%s, %s, %s)
                    ON CONFLICT ON CONSTRAINT unique_sensor_type_constraint
                    DO UPDATE SET 
                        offset_value = EXCLUDED.offset_value,
                        scale_factor = EXCLUDED.scale_factor,
                        last_calibrated = CURRENT_TIMESTAMP
                    """, (sensor_type, offset, scale))
        except psycopg2.Error as e:
            raise Exception(f"Database error updating calibration: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error updating calibration: {str(e)}")

    def __del__(self):
        """Ensure database connection is closed when object is destroyed."""
        if hasattr(self, 'conn'):
            try:
                self.conn.close()
            except:
                pass
