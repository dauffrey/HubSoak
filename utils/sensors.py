import random
from datetime import datetime
from typing import Dict, Tuple

class SensorSimulator:
    def __init__(self):
        self.calibration = {
            'ph': {'offset': 0.0, 'scale': 1.0},
            'temperature': {'offset': 0.0, 'scale': 1.0},
            'turbidity': {'offset': 0.0, 'scale': 1.0},
            'orp': {'offset': 0.0, 'scale': 1.0}
        }

    def get_readings(self) -> Dict[str, float]:
        # Simulate sensor readings with realistic values
        raw_readings = {
            'ph': random.uniform(6.8, 7.8),
            'temperature': random.uniform(35.0, 40.0),
            'turbidity': random.uniform(0.5, 5.0),
            'orp': random.uniform(650.0, 750.0)  # ORP in millivolts (mV)
        }

        # Apply calibration
        calibrated_readings = {
            sensor: (value + self.calibration[sensor]['offset']) * self.calibration[sensor]['scale']
            for sensor, value in raw_readings.items()
        }

        return calibrated_readings

    def update_calibration(self, sensor_type: str, offset: float, scale: float):
        if sensor_type in self.calibration:
            self.calibration[sensor_type]['offset'] = offset
            self.calibration[sensor_type]['scale'] = scale

    def check_alerts(self, readings: Dict[str, float]) -> Dict[str, Tuple[bool, str]]:
        alerts = {}
        
        # Define threshold values
        thresholds = {
            'ph': {'min': 7.0, 'max': 7.8, 'unit': 'pH'},
            'temperature': {'min': 35.0, 'max': 40.0, 'unit': '°C'},
            'turbidity': {'min': 0.0, 'max': 4.0, 'unit': 'NTU'},
            'orp': {'min': 650.0, 'max': 750.0, 'unit': 'mV'}
        }

        for sensor, value in readings.items():
            threshold = thresholds[sensor]
            if value < threshold['min']:
                alerts[sensor] = (True, f"{sensor.title()} too low: {value:.1f} {threshold['unit']}")
            elif value > threshold['max']:
                alerts[sensor] = (True, f"{sensor.title()} too high: {value:.1f} {threshold['unit']}")
            else:
                alerts[sensor] = (False, f"{sensor.title()} normal: {value:.1f} {threshold['unit']}")

        return alerts
