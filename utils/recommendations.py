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
            'total_chlorine': {'min': 2.0, 'max': 4.0, 'unit': 'ppm'}
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

        # Add chlorine-specific recommendations
        if readings['free_chlorine'] < self.optimal_ranges['free_chlorine']['min']:
            recommendations.append({
                'parameter': 'Free Chlorine',
                'status': 'low',
                'action': 'Add chlorine sanitizer to increase free chlorine levels.',
                'details': 'Low free chlorine reduces sanitizing effectiveness and can lead to bacterial growth.'
            })
        elif readings['free_chlorine'] > self.optimal_ranges['free_chlorine']['max']:
            recommendations.append({
                'parameter': 'Free Chlorine',
                'status': 'high',
                'action': 'Stop adding chlorine and allow levels to naturally decrease. Consider partial water change.',
                'details': 'High free chlorine can cause skin and eye irritation.'
            })

        # Calculate and check combined chlorine
        combined_chlorine = readings['total_chlorine'] - readings['free_chlorine']
        if combined_chlorine > 0.5:  # Standard threshold for combined chlorine
            recommendations.append({
                'parameter': 'Combined Chlorine',
                'status': 'high',
                'action': 'Shock treat the water with high dose of chlorine (superchlorination).',
                'details': 'High combined chlorine indicates presence of chloramines, which can cause odor and irritation.'
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
