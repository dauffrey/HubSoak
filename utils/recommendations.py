from typing import Dict, List

class WaterQualityRecommender:
    def __init__(self):
        # Define optimal ranges for each parameter
        self.optimal_ranges = {
            'ph': {'min': 7.2, 'max': 7.6, 'unit': 'pH'},
            'temperature': {'min': 37.0, 'max': 39.0, 'unit': '°C'},
            'turbidity': {'min': 0.5, 'max': 3.0, 'unit': 'NTU'},
            'orp': {'min': 650, 'max': 750, 'unit': 'mV'},
            'conductivity': {'min': 400, 'max': 800, 'unit': 'ppm'},
            'free_chlorine': {'min': 1.0, 'max': 3.0, 'unit': 'ppm'},
            'total_chlorine': {'min': 2.0, 'max': 4.0, 'unit': 'ppm'},
            'bromine': {'min': 2.0, 'max': 6.0, 'unit': 'ppm'},
            'uv_intensity': {'min': 20.0, 'max': 35.0, 'unit': 'mW/cm²'}
        }

    def get_recommendations(self, readings: Dict[str, float]) -> List[Dict[str, str]]:
        recommendations = []

        # Previous recommendations code...
        if readings['ph'] < self.optimal_ranges['ph']['min']:
            recommendations.append({
                'parameter': 'pH',
                'status': 'low',
                'action': 'Add pH increaser (sodium carbonate). Test after 4 hours.',
                'details': 'Low pH can cause eye irritation and corrode equipment.'
            })
        elif readings['ph'] > self.optimal_ranges['ph']['max']:
            recommendations.append({
                'parameter': 'pH',
                'status': 'high',
                'action': 'Add pH decreaser (sodium bisulfate). Test after 4 hours.',
                'details': 'High pH reduces sanitizer effectiveness and can cause scaling.'
            })

        if readings['temperature'] < self.optimal_ranges['temperature']['min']:
            recommendations.append({
                'parameter': 'Temperature',
                'status': 'low',
                'action': 'Increase heater temperature setting.',
                'details': 'Low temperature can make bathing uncomfortable and affect sanitizer effectiveness.'
            })
        elif readings['temperature'] > self.optimal_ranges['temperature']['max']:
            recommendations.append({
                'parameter': 'Temperature',
                'status': 'high',
                'action': 'Reduce heater temperature setting or use cooling mode if available.',
                'details': 'High temperature increases chemical consumption and can be uncomfortable.'
            })

        if readings['turbidity'] > self.optimal_ranges['turbidity']['max']:
            recommendations.append({
                'parameter': 'Turbidity',
                'status': 'high',
                'action': 'Clean or replace filter. Add water clarifier if needed.',
                'details': 'High turbidity indicates presence of suspended particles and possible contamination.'
            })

        if readings['orp'] < self.optimal_ranges['orp']['min']:
            recommendations.append({
                'parameter': 'ORP',
                'status': 'low',
                'action': 'Add sanitizer (chlorine/bromine). Check for organic contamination.',
                'details': 'Low ORP indicates insufficient sanitizer levels for proper disinfection.'
            })
        elif readings['orp'] > self.optimal_ranges['orp']['max']:
            recommendations.append({
                'parameter': 'ORP',
                'status': 'high',
                'action': 'Reduce sanitizer addition. Wait for levels to decrease naturally.',
                'details': 'High ORP may cause skin/eye irritation and equipment damage.'
            })

        if readings['conductivity'] < self.optimal_ranges['conductivity']['min']:
            recommendations.append({
                'parameter': 'Conductivity/TDS',
                'status': 'low',
                'action': 'Add mineral balancer to increase TDS levels.',
                'details': 'Low TDS levels may result in poor water conditioning and reduced therapeutic benefits.'
            })
        elif readings['conductivity'] > self.optimal_ranges['conductivity']['max']:
            recommendations.append({
                'parameter': 'Conductivity/TDS',
                'status': 'high',
                'action': 'Partially drain and refill with fresh water to reduce TDS levels.',
                'details': 'High TDS levels can cause equipment corrosion and reduce sanitizer effectiveness.'
            })

        # Add bromine-specific recommendations
        if readings['bromine'] < self.optimal_ranges['bromine']['min']:
            recommendations.append({
                'parameter': 'Bromine',
                'status': 'low',
                'action': 'Add sodium bromide and activate with oxidizer. Test after 2 hours.',
                'details': 'Low bromine levels reduce sanitizing effectiveness and can lead to bacterial growth.'
            })
        elif readings['bromine'] > self.optimal_ranges['bromine']['max']:
            recommendations.append({
                'parameter': 'Bromine',
                'status': 'high',
                'action': 'Stop adding bromine and allow levels to naturally decrease. Consider partial water change.',
                'details': 'High bromine levels can cause skin and eye irritation.'
            })

        # Add UV system recommendations
        if readings['uv_intensity'] < self.optimal_ranges['uv_intensity']['min']:
            recommendations.append({
                'parameter': 'UV System',
                'status': 'low',
                'action': 'Clean UV lamp and quartz sleeve. Check lamp age and replace if over 12 months old.',
                'details': 'Low UV intensity reduces sterilization effectiveness. Could be due to mineral buildup or aging lamp.'
            })
        elif readings['uv_intensity'] > self.optimal_ranges['uv_intensity']['max']:
            recommendations.append({
                'parameter': 'UV System',
                'status': 'high',
                'action': 'Check UV sensor calibration and verify proper lamp wattage.',
                'details': 'Unusually high UV readings may indicate sensor calibration issues.'
            })

        # If everything is optimal
        if not recommendations:
            recommendations.append({
                'parameter': 'All Parameters',
                'status': 'optimal',
                'action': 'Continue regular maintenance schedule.',
                'details': 'All water quality parameters are within optimal ranges.'
            })

        return recommendations
