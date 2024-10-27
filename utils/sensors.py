import random
from datetime import datetime
from typing import Dict, Tuple

class SensorSimulator:
    def __init__(self):
        self.calibration = {
            'ph': {'offset': 0.0, 'scale': 1.0},
            'temperature': {'offset': 0.0, 'scale': 1.0},
            'turbidity': {'offset': 0.0, 'scale': 1.0},
            'orp': {'offset': 0.0, 'scale': 1.0},
            'conductivity': {'offset': 0.0, 'scale': 1.0},
            'free_chlorine': {'offset': 0.0, 'scale': 1.0},
            'total_chlorine': {'offset': 0.0, 'scale': 1.0},
            'bromine': {'offset': 0.0, 'scale': 1.0},
            'uv_intensity': {'offset': 0.0, 'scale': 1.0}
        }

    def get_readings(self) -> Dict[str, float]:
        # Simulate sensor readings with realistic values
        raw_readings = {
            'ph': random.uniform(6.8, 7.8),
            'temperature': random.uniform(35.0, 40.0),
            'turbidity': random.uniform(0.5, 5.0),
            'orp': random.uniform(650.0, 750.0),  # ORP in millivolts (mV)
            'conductivity': random.uniform(200.0, 1000.0),  # TDS in ppm
            'free_chlorine': random.uniform(1.0, 5.0),  # Free chlorine in ppm
            'total_chlorine': random.uniform(2.0, 6.0),  # Total chlorine in ppm
            'bromine': random.uniform(2.0, 6.0),  # Bromine in ppm
            'uv_intensity': random.uniform(15.0, 40.0)  # UV intensity in mW/cm²
        }

        # Ensure total chlorine is always higher than free chlorine
        raw_readings['total_chlorine'] = max(
            raw_readings['total_chlorine'],
            raw_readings['free_chlorine'] + random.uniform(0.5, 1.5)
        )

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
            'orp': {'min': 650.0, 'max': 750.0, 'unit': 'mV'},
            'conductivity': {'min': 200.0, 'max': 1000.0, 'unit': 'ppm'},
            'free_chlorine': {'min': 1.0, 'max': 3.0, 'unit': 'ppm'},
            'total_chlorine': {'min': 2.0, 'max': 4.0, 'unit': 'ppm'},
            'bromine': {'min': 2.0, 'max': 6.0, 'unit': 'ppm'},
            'uv_intensity': {'min': 20.0, 'max': 35.0, 'unit': 'mW/cm²'}
        }

        for sensor, value in readings.items():
            threshold = thresholds[sensor]
            if value < threshold['min']:
                alerts[sensor] = (True, f"{sensor.replace('_', ' ').title()} too low: {value:.1f} {threshold['unit']}")
            elif value > threshold['max']:
                alerts[sensor] = (True, f"{sensor.replace('_', ' ').title()} too high: {value:.1f} {threshold['unit']}")
            else:
                alerts[sensor] = (False, f"{sensor.replace('_', ' ').title()} normal: {value:.1f} {threshold['unit']}")

        # Add combined chlorine alert
        if 'total_chlorine' in readings and 'free_chlorine' in readings:
            combined_chlorine = readings['total_chlorine'] - readings['free_chlorine']
            if combined_chlorine > 0.5:  # Standard threshold for combined chlorine
                alerts['combined_chlorine'] = (True, f"Combined Chlorine high: {combined_chlorine:.1f} ppm")
            else:
                alerts['combined_chlorine'] = (False, f"Combined Chlorine normal: {combined_chlorine:.1f} ppm")

        return alerts
