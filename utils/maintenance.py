from datetime import datetime, timedelta
from typing import Dict, List
import psycopg2
import os

class MaintenanceScheduler:
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
                CREATE TABLE IF NOT EXISTS maintenance_tasks (
                    id SERIAL PRIMARY KEY,
                    task_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    frequency_days INTEGER NOT NULL,
                    last_completed TIMESTAMP,
                    next_due TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS maintenance_history (
                    id SERIAL PRIMARY KEY,
                    task_id INTEGER REFERENCES maintenance_tasks(id),
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT
                );
            """)
            self.conn.commit()

    def add_task(self, task_name: str, description: str, frequency_days: int):
        with self.conn.cursor() as cur:
            next_due = datetime.now() + timedelta(days=frequency_days)
            cur.execute("""
                INSERT INTO maintenance_tasks 
                (task_name, description, frequency_days, next_due)
                VALUES (%s, %s, %s, %s)
            """, (task_name, description, frequency_days, next_due))
            self.conn.commit()

    def get_upcoming_tasks(self, days_ahead: int = 7) -> List[Dict]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, task_name, description, frequency_days, last_completed, next_due
                FROM maintenance_tasks
                WHERE next_due <= NOW() + INTERVAL '%s days'
                ORDER BY next_due ASC
            """, (days_ahead,))
            
            tasks = []
            for row in cur.fetchall():
                tasks.append({
                    'id': row[0],
                    'task_name': row[1],
                    'description': row[2],
                    'frequency_days': row[3],
                    'last_completed': row[4],
                    'next_due': row[5]
                })
            return tasks

    def complete_task(self, task_id: int, notes: str = ""):
        with self.conn.cursor() as cur:
            # Get the task's frequency
            cur.execute("SELECT frequency_days FROM maintenance_tasks WHERE id = %s", (task_id,))
            frequency_days = cur.fetchone()[0]

            # Update the task
            next_due = datetime.now() + timedelta(days=frequency_days)
            cur.execute("""
                UPDATE maintenance_tasks 
                SET last_completed = CURRENT_TIMESTAMP, next_due = %s
                WHERE id = %s
            """, (next_due, task_id))

            # Log in history
            cur.execute("""
                INSERT INTO maintenance_history (task_id, notes)
                VALUES (%s, %s)
            """, (task_id, notes))
            
            self.conn.commit()

    def get_task_history(self, task_id: int) -> List[Dict]:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT completed_at, notes
                FROM maintenance_history
                WHERE task_id = %s
                ORDER BY completed_at DESC
            """, (task_id,))
            
            history = []
            for row in cur.fetchall():
                history.append({
                    'completed_at': row[0],
                    'notes': row[1]
                })
            return history

    def get_default_tasks(self) -> List[Dict]:
        return [
            {
                'name': 'Clean Filter',
                'description': 'Remove and clean the hot tub filter thoroughly',
                'frequency_days': 30
            },
            {
                'name': 'Test Water Chemistry',
                'description': 'Complete water chemistry test including pH, alkalinity, and sanitizer levels',
                'frequency_days': 7
            },
            {
                'name': 'Drain and Refill',
                'description': 'Complete water change and system cleaning',
                'frequency_days': 90
            },
            {
                'name': 'Clean Cover',
                'description': 'Clean and condition the hot tub cover',
                'frequency_days': 30
            },
            {
                'name': 'Inspect Equipment',
                'description': 'Check pumps, heaters, and other equipment for proper operation',
                'frequency_days': 14
            }
        ]
