#!/usr/bin/env python3
"""
Script de Análisis Avanzado - AgroMonitor
==========================================

Este script complementa el dashboard HTML con análisis predictivo
y recomendaciones automatizadas basadas en machine learning simple.

Autor: Dashboard AgroMonitor
Fecha: Febrero 2026
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

class AgroAnalyzer:
    """Analizador de datos agrícolas con predicciones básicas"""
    
    def __init__(self, api_key: str, polygon_id: str):
        self.api_key = api_key
        self.polygon_id = polygon_id
        self.base_url = "http://api.agromonitoring.com/agro/1.0"
        
    def get_current_weather(self) -> Dict:
        """Obtiene datos meteorológicos actuales"""
        url = f"{self.base_url}/weather?polyid={self.polygon_id}&appid={self.api_key}"
        response = requests.get(url)
        return response.json()
    
    def get_forecast(self) -> List[Dict]:
        """Obtiene pronóstico de 5 días"""
        url = f"{self.base_url}/weather/forecast?polyid={self.polygon_id}&appid={self.api_key}"
        response = requests.get(url)
        return response.json()
    
    def get_soil_data(self) -> Dict:
        """Obtiene datos del suelo"""
        url = f"{self.base_url}/soil?polyid={self.polygon_id}&appid={self.api_key}"
        response = requests.get(url)
        return response.json()
    
    def get_ndvi_history(self, days: int = 30) -> List[Dict]:
        """Obtiene histórico de NDVI"""
        end = int(datetime.now().timestamp())
        start = int((datetime.now() - timedelta(days=days)).timestamp())
        
        url = f"{self.base_url}/image/search?start={start}&end={end}&polyid={self.polygon_id}&appid={self.api_key}"
        response = requests.get(url)
        images = response.json()
        
        ndvi_data = []
        for image in images:
            if 'ndvi' in image.get('stats', {}):
                try:
                    stats_url = image['stats']['ndvi']
                    stats_response = requests.get(stats_url)
                    stats = stats_response.json()
                    
                    ndvi_data.append({
                        'date': datetime.fromtimestamp(image['dt']),
                        'mean': stats.get('mean', 0),
                        'std': stats.get('std', 0),
                        'min': stats.get('min', 0),
                        'max': stats.get('max', 0)
                    })
                except:
                    continue
        
        return sorted(ndvi_data, key=lambda x: x['date'])
    
    def predict_irrigation_need(self) -> Tuple[str, str, float]:
        """
        Predice necesidad de riego basado en múltiples factores
        
        Returns:
            Tuple[str, str, float]: (nivel_urgencia, recomendación, score)
        """
        soil = self.get_soil_data()
        forecast = self.get_forecast()
        
        # Calcular humedad del suelo (%)
        moisture = soil.get('moisture', 0) * 100
        
        # Calcular lluvia prevista en próximas 48h
        rain_48h = 0
        for item in forecast[:16]:  # 16 períodos de 3h = 48h
            if 'rain' in item and '3h' in item['rain']:
                rain_48h += item['rain']['3h']
        
        # Sistema de puntuación
        score = 0
        
        # Factor 1: Humedad del suelo (40% del score)
        if moisture < 20:
            score += 40
        elif moisture < 30:
            score += 30
        elif moisture < 40:
            score += 20
        elif moisture < 50:
            score += 10
        
        # Factor 2: Lluvia prevista (40% del score)
        if rain_48h < 2:
            score += 40
        elif rain_48h < 5:
            score += 30
        elif rain_48h < 10:
            score += 20
        elif rain_48h < 20:
            score += 10
        
        # Factor 3: Temperatura (20% del score)
        weather = self.get_current_weather()
        temp = weather['main']['temp'] - 273.15
        if temp > 32:
            score += 20
        elif temp > 28:
            score += 10
        
        # Determinar urgencia y recomendación
        if score >= 80:
            urgency = "CRÍTICO"
            recommendation = f"🚨 REGAR HOY - Humedad muy baja ({moisture:.0f}%) y sin lluvia prevista ({rain_48h:.1f}mm)"
        elif score >= 60:
            urgency = "ALTO"
            recommendation = f"⚠️ Regar en próximas 24h - Humedad baja ({moisture:.0f}%), lluvia insuficiente ({rain_48h:.1f}mm)"
        elif score >= 40:
            urgency = "MODERADO"
            recommendation = f"💧 Considerar riego - Humedad {moisture:.0f}%, lluvia prevista {rain_48h:.1f}mm"
        elif score >= 20:
            urgency = "BAJO"
            recommendation = f"✅ Riego opcional - Condiciones aceptables (humedad {moisture:.0f}%)"
        else:
            urgency = "NINGUNO"
            recommendation = f"🌧️ NO regar - Suficiente humedad ({moisture:.0f}%) o lluvia prevista ({rain_48h:.1f}mm)"
        
        return urgency, recommendation, score
    
    def analyze_ndvi_trend(self) -> Dict:
        """
        Analiza tendencia de NDVI para detectar problemas o mejoras
        
        Returns:
            Dict con análisis de tendencia
        """
        history = self.get_ndvi_history(30)
        
        if len(history) < 2:
            return {
                'trend': 'INSUFICIENTE',
                'message': 'No hay suficientes datos para análisis de tendencia',
                'recommendation': 'Espera a tener al menos 2 mediciones satelitales'
            }
        
        # Calcular tendencia lineal simple
        values = [h['mean'] for h in history]
        n = len(values)
        
        # Pendiente de la recta de regresión
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Calcular cambio porcentual
        change = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        
        # Determinar tendencia
        if slope > 0.01:
            trend = "MEJORANDO"
            icon = "📈"
            message = f"Salud vegetal mejorando (+{change:.1f}%). NDVI pasó de {values[0]:.3f} a {values[-1]:.3f}"
            recommendation = "Mantén las prácticas actuales, están funcionando bien"
        elif slope < -0.01:
            trend = "DETERIORANDO"
            icon = "📉"
            message = f"Salud vegetal en descenso ({change:.1f}%). NDVI de {values[0]:.3f} a {values[-1]:.3f}"
            recommendation = "⚠️ REVISAR: Posible plaga, enfermedad o deficiencia nutricional. Inspección visual urgente"
        else:
            trend = "ESTABLE"
            icon = "➡️"
            message = f"Salud vegetal estable. NDVI mantiene ~{values[-1]:.3f}"
            recommendation = "Continuar con manejo normal"
        
        # Análisis de variabilidad
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        
        return {
            'trend': trend,
            'icon': icon,
            'slope': slope,
            'change_percent': change,
            'current_ndvi': values[-1],
            'initial_ndvi': values[0],
            'std_dev': std_dev,
            'n_measurements': n,
            'message': message,
            'recommendation': recommendation,
            'high_variability': std_dev > 0.1
        }
    
    def detect_stress_conditions(self) -> List[Dict]:
        """
        Detecta condiciones de estrés en los cultivos
        
        Returns:
            Lista de condiciones de estrés detectadas
        """
        stresses = []
        
        # Obtener datos
        weather = self.get_current_weather()
        soil = self.get_soil_data()
        
        temp = weather['main']['temp'] - 273.15
        humidity = weather['main']['humidity']
        soil_moisture = soil.get('moisture', 0) * 100
        soil_temp = soil.get('t10', 273.15) - 273.15
        
        # Estrés por temperatura alta
        if temp > 35:
            stresses.append({
                'type': 'CALOR EXTREMO',
                'severity': 'CRÍTICO',
                'icon': '🔥',
                'message': f'Temperatura muy alta: {temp:.1f}°C',
                'action': 'Riego extra, aplicar mulch, considerar sombra temporal'
            })
        elif temp > 32:
            stresses.append({
                'type': 'CALOR ALTO',
                'severity': 'ALTO',
                'icon': '🌡️',
                'message': f'Temperatura alta: {temp:.1f}°C',
                'action': 'Aumentar frecuencia de riego, monitorear plantas sensibles'
            })
        
        # Estrés hídrico
        if soil_moisture < 20:
            stresses.append({
                'type': 'ESTRÉS HÍDRICO SEVERO',
                'severity': 'CRÍTICO',
                'icon': '💧',
                'message': f'Humedad del suelo muy baja: {soil_moisture:.0f}%',
                'action': 'REGAR URGENTE - Riesgo de marchitamiento'
            })
        elif soil_moisture < 30:
            stresses.append({
                'type': 'ESTRÉS HÍDRICO',
                'severity': 'ALTO',
                'icon': '💦',
                'message': f'Humedad del suelo baja: {soil_moisture:.0f}%',
                'action': 'Programar riego en próximas 24h'
            })
        
        # Estrés por baja humedad atmosférica
        if humidity < 40:
            stresses.append({
                'type': 'BAJA HUMEDAD ATMOSFÉRICA',
                'severity': 'MODERADO',
                'icon': '🌵',
                'message': f'Humedad relativa baja: {humidity}%',
                'action': 'Puede aumentar evapotranspiración, ajustar riego'
            })
        
        # Temperatura del suelo inadecuada
        if soil_temp < 15:
            stresses.append({
                'type': 'SUELO FRÍO',
                'severity': 'BAJO',
                'icon': '❄️',
                'message': f'Temperatura del suelo baja: {soil_temp:.1f}°C',
                'action': 'Desarrollo radicular lento, considerar mulch oscuro'
            })
        elif soil_temp > 30:
            stresses.append({
                'type': 'SUELO CALIENTE',
                'severity': 'MODERADO',
                'icon': '♨️',
                'message': f'Temperatura del suelo alta: {soil_temp:.1f}°C',
                'action': 'Aplicar mulch claro para enfriar, aumentar riego'
            })
        
        return stresses
    
    def generate_weekly_report(self) -> str:
        """
        Genera reporte semanal completo en formato texto
        
        Returns:
            str: Reporte formateado
        """
        # Obtener todos los datos
        weather = self.get_current_weather()
        forecast = self.get_forecast()
        soil = self.get_soil_data()
        ndvi_analysis = self.analyze_ndvi_trend()
        irrigation = self.predict_irrigation_need()
        stresses = self.detect_stress_conditions()
        
        # Construir reporte
        report = []
        report.append("=" * 70)
        report.append("REPORTE SEMANAL - FINCA VERAGUAS (2 hectáreas)")
        report.append(f"Fecha: {datetime.now().strftime('%d de %B, %Y - %H:%M')}")
        report.append("=" * 70)
        report.append("")
        
        # Sección 1: Condiciones Actuales
        report.append("📊 CONDICIONES ACTUALES")
        report.append("-" * 70)
        temp = weather['main']['temp'] - 273.15
        report.append(f"  Temperatura: {temp:.1f}°C")
        report.append(f"  Humedad: {weather['main']['humidity']}%")
        report.append(f"  Viento: {weather['wind']['speed']} m/s")
        report.append(f"  Nubosidad: {weather['clouds']['all']}%")
        report.append("")
        
        soil_moisture = soil.get('moisture', 0) * 100
        soil_temp = soil.get('t10', 273.15) - 273.15
        report.append(f"  Humedad del Suelo: {soil_moisture:.0f}%")
        report.append(f"  Temperatura del Suelo: {soil_temp:.1f}°C")
        report.append("")
        
        # Sección 2: Análisis NDVI
        report.append("🌿 ANÁLISIS DE SALUD VEGETAL (NDVI)")
        report.append("-" * 70)
        report.append(f"  Tendencia: {ndvi_analysis['icon']} {ndvi_analysis['trend']}")
        report.append(f"  {ndvi_analysis['message']}")
        report.append(f"  Recomendación: {ndvi_analysis['recommendation']}")
        if ndvi_analysis.get('high_variability'):
            report.append(f"  ⚠️ Alta variabilidad detectada - revisar uniformidad del cultivo")
        report.append("")
        
        # Sección 3: Necesidad de Riego
        report.append("💧 NECESIDAD DE RIEGO")
        report.append("-" * 70)
        urgency, recommendation, score = irrigation
        report.append(f"  Urgencia: {urgency} (Score: {score}/100)")
        report.append(f"  {recommendation}")
        report.append("")
        
        # Sección 4: Condiciones de Estrés
        if stresses:
            report.append("⚠️ CONDICIONES DE ESTRÉS DETECTADAS")
            report.append("-" * 70)
            for stress in stresses:
                report.append(f"  {stress['icon']} {stress['type']} - {stress['severity']}")
                report.append(f"     {stress['message']}")
                report.append(f"     Acción: {stress['action']}")
                report.append("")
        else:
            report.append("✅ NO HAY CONDICIONES DE ESTRÉS DETECTADAS")
            report.append("-" * 70)
            report.append("  Cultivos en condiciones óptimas")
            report.append("")
        
        # Sección 5: Pronóstico
        report.append("📅 PRONÓSTICO PRÓXIMOS 3 DÍAS")
        report.append("-" * 70)
        
        # Agrupar por día
        daily_data = {}
        for item in forecast[:24]:  # 24 períodos de 3h = 3 días
            date = datetime.fromtimestamp(item['dt'])
            day_key = date.strftime('%Y-%m-%d')
            
            if day_key not in daily_data:
                daily_data[day_key] = {
                    'temps': [],
                    'rain': 0,
                    'weather': item['weather'][0]['main']
                }
            
            daily_data[day_key]['temps'].append(item['main']['temp'] - 273.15)
            if 'rain' in item and '3h' in item['rain']:
                daily_data[day_key]['rain'] += item['rain']['3h']
        
        for day, data in list(daily_data.items())[:3]:
            date_obj = datetime.strptime(day, '%Y-%m-%d')
            day_name = date_obj.strftime('%A %d/%m')
            avg_temp = statistics.mean(data['temps'])
            max_temp = max(data['temps'])
            min_temp = min(data['temps'])
            
            report.append(f"  {day_name}:")
            report.append(f"    Temperatura: {min_temp:.1f}°C - {max_temp:.1f}°C (prom: {avg_temp:.1f}°C)")
            report.append(f"    Lluvia: {data['rain']:.1f}mm")
            report.append(f"    Condiciones: {data['weather']}")
            report.append("")
        
        # Sección 6: Recomendaciones por Cultivo
        report.append("🌱 RECOMENDACIONES POR CULTIVO")
        report.append("-" * 70)
        
        # Plátano
        report.append("  🍌 PLÁTANO (1 hectárea):")
        if ndvi_analysis['current_ndvi'] < 0.5:
            report.append("     ⚠️ NDVI bajo - Revisar nutrición y posible Sigatoka")
        else:
            report.append("     ✅ Buen desarrollo vegetativo")
        if temp > 30:
            report.append("     💧 Temperatura alta - Aumentar riego")
        report.append("")
        
        # Hortalizas
        report.append("  🌶️ HORTALIZAS (0.5 hectárea):")
        if soil_moisture < 40:
            report.append("     💧 Requieren riego más frecuente que otros cultivos")
        if temp > 32:
            report.append("     ☀️ Proteger del sol intenso del mediodía si es posible")
        report.append("     📋 Revisar calendario de fertilización")
        report.append("")
        
        # Tubérculos
        report.append("  🥔 TUBÉRCULOS + FRUTALES (0.5 hectárea):")
        if soil_moisture > 70:
            report.append("     ⚠️ Exceso de humedad - Riesgo de pudrición en tubérculos")
        else:
            report.append("     ✅ Humedad adecuada para desarrollo")
        report.append("     🌳 Frutales jóvenes - Mantener área libre de maleza")
        report.append("")
        
        # Sección 7: Acciones Sugeridas
        report.append("📋 ACCIONES SUGERIDAS PARA ESTA SEMANA")
        report.append("-" * 70)
        
        actions = []
        
        if urgency in ["CRÍTICO", "ALTO"]:
            actions.append("1. RIEGO prioritario según recomendación")
        
        if ndvi_analysis['trend'] == "DETERIORANDO":
            actions.append("2. INSPECCIÓN visual detallada de cultivos")
            actions.append("3. Identificar causa del deterioro (plagas/enfermedades/nutrición)")
        
        if any(s['severity'] == 'CRÍTICO' for s in stresses):
            actions.append("4. ATENCIÓN URGENTE a condiciones de estrés críticas")
        
        # Acciones rutinarias
        actions.append(f"{len(actions)+1}. Control de malezas en todas las zonas")
        actions.append(f"{len(actions)+1}. Monitoreo de plagas (especialmente hortalizas)")
        actions.append(f"{len(actions)+1}. Aplicar fertilización según calendario")
        
        for action in actions:
            report.append(f"  {action}")
        
        report.append("")
        report.append("=" * 70)
        report.append("Fin del reporte")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_data_json(self, filename: str = None):
        """
        Exporta todos los datos actuales en formato JSON
        
        Args:
            filename: Nombre del archivo (opcional)
        """
        if filename is None:
            filename = f"agro_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'location': {
                'polygon_id': self.polygon_id,
                'coordinates': [8.439227448107934, -81.19193502522846],
                'altitude': 379.62,
                'area_ha': 2.0
            },
            'weather': self.get_current_weather(),
            'soil': self.get_soil_data(),
            'forecast': self.get_forecast(),
            'ndvi_history': [
                {
                    'date': h['date'].isoformat(),
                    'mean': h['mean'],
                    'std': h['std'],
                    'min': h['min'],
                    'max': h['max']
                }
                for h in self.get_ndvi_history()
            ],
            'analysis': {
                'ndvi_trend': self.analyze_ndvi_trend(),
                'irrigation': {
                    'urgency': self.predict_irrigation_need()[0],
                    'recommendation': self.predict_irrigation_need()[1],
                    'score': self.predict_irrigation_need()[2]
                },
                'stress_conditions': self.detect_stress_conditions()
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Datos exportados a: {filename}")
        return filename


def load_config():
    """Carga la configuración desde polygon_config.json"""
    import os
    config_path = os.path.join(os.path.dirname(__file__), 'polygon_config.json')
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("[ERROR] No se encontro polygon_config.json")
        print("Asegurate de tener el archivo en la misma carpeta")
        return None
    except json.JSONDecodeError:
        print("[ERROR] El archivo polygon_config.json tiene formato invalido")
        return None


def safe_print(text):
    """Imprime texto de forma segura reemplazando emojis en Windows"""
    import sys
    try:
        print(text)
    except UnicodeEncodeError:
        # Reemplazar emojis por texto alternativo para Windows
        replacements = {
            '🌱': '[PLANTA]', '🍌': '[PLATANO]', '🌶️': '[HORTALIZA]', 
            '🥔': '[TUBERCULO]', '📊': '[DATOS]', '💧': '[AGUA]',
            '🌿': '[VERDE]', '⚠️': '[ALERTA]', '✅': '[OK]', 
            '❌': '[X]', '📈': '[SUBIENDO]', '📉': '[BAJANDO]',
            '➡️': '[->]', '🔥': '[CALOR]', '🌡️': '[TEMP]',
            '💦': '[GOTA]', '🌵': '[SECO]', '❄️': '[FRIO]',
            '♨️': '[CALIENTE]', '🚨': '[URGENTE]', '🌧️': '[LLUVIA]',
            '☀️': '[SOL]', '👋': '[ADIOS]', '💾': '[GUARDAR]',
            '📄': '[DOC]', '📅': '[CALENDARIO]', '📋': '[LISTA]',
            '🌳': '[ARBOL]'
        }
        safe_text = text
        for emoji, replacement in replacements.items():
            safe_text = safe_text.replace(emoji, replacement)
        print(safe_text.encode('ascii', 'replace').decode('ascii'))


def main():
    """Funcion principal - carga configuracion automaticamente"""
    import sys
    import io
    
    # Configurar salida UTF-8 para Windows
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except:
            pass
    
    safe_print("=" * 70)
    safe_print("AgroMonitor - Analisis Avanzado")
    safe_print("=" * 70)
    safe_print("")
    
    # Cargar configuracion
    config = load_config()
    if not config:
        return
    
    api_key = config['api']['api_key']
    polygon_id = config['polygon']['id']
    polygon_name = config['polygon']['nombre']
    
    if not api_key or not polygon_id:
        safe_print("[ERROR] API Key y Polygon ID son requeridos en polygon_config.json")
        return
    
    safe_print(f"Poligono: {polygon_name}")
    safe_print(f"ID: {polygon_id}")
    safe_print(f"API Key: {api_key[:10]}...")
    safe_print("")
    
    # Crear analizador
    analyzer = AgroAnalyzer(api_key, polygon_id)
    
    # Menu de opciones
    while True:
        safe_print("\n" + "=" * 70)
        safe_print("OPCIONES:")
        safe_print("1. Ver datos actuales (clima + suelo)")
        safe_print("2. Analisis de tendencia NDVI")
        safe_print("3. Prediccion de necesidad de riego")
        safe_print("4. Detectar condiciones de estres")
        safe_print("5. Generar reporte semanal completo")
        safe_print("6. Exportar datos a JSON")
        safe_print("7. Salir")
        safe_print("=" * 70)
        
        option = input("\nSelecciona una opcion (1-7): ").strip()
        
        try:
            if option == "1":
                safe_print("\n[DATOS] DATOS ACTUALES")
                safe_print("-" * 70)
                weather = analyzer.get_current_weather()
                soil = analyzer.get_soil_data()
                
                temp = weather['main']['temp'] - 273.15
                safe_print(f"Temperatura: {temp:.1f} C")
                safe_print(f"Humedad: {weather['main']['humidity']}%")
                safe_print(f"Viento: {weather['wind']['speed']} m/s")
                safe_print(f"Humedad del Suelo: {soil.get('moisture', 0) * 100:.0f}%")
                safe_print(f"Temperatura del Suelo: {(soil.get('t10', 273.15) - 273.15):.1f} C")
            
            elif option == "2":
                safe_print("\n[VERDE] ANALISIS DE TENDENCIA NDVI")
                safe_print("-" * 70)
                analysis = analyzer.analyze_ndvi_trend()
                safe_print(f"Tendencia: {analysis['trend']}")
                safe_print(f"{analysis['message']}")
                safe_print(f"Recomendacion: {analysis['recommendation']}")
            
            elif option == "3":
                safe_print("\n[AGUA] PREDICCION DE RIEGO")
                safe_print("-" * 70)
                urgency, recommendation, score = analyzer.predict_irrigation_need()
                safe_print(f"Urgencia: {urgency}")
                safe_print(f"Score: {score}/100")
                safe_print(f"{recommendation}")
            
            elif option == "4":
                safe_print("\n[ALERTA] CONDICIONES DE ESTRES")
                safe_print("-" * 70)
                stresses = analyzer.detect_stress_conditions()
                if stresses:
                    for stress in stresses:
                        safe_print(f"\n{stress['type']} - {stress['severity']}")
                        safe_print(f"   {stress['message']}")
                        safe_print(f"   Accion: {stress['action']}")
                else:
                    safe_print("[OK] No hay condiciones de estres detectadas")
            
            elif option == "5":
                safe_print("\n[DOC] GENERANDO REPORTE SEMANAL...")
                report = analyzer.generate_weekly_report()
                # Limpiar emojis del reporte para Windows
                replacements = {
                    '🌱': '', '🍌': '[PLATANO]', '🌶️': '[HORTALIZA]', 
                    '🥔': '[TUBERCULO]', '📊': '', '💧': '[AGUA]',
                    '🌿': '', '⚠️': '[!]', '✅': '[OK]', 
                    '❌': '[X]', '📈': '[+]', '📉': '[-]',
                    '➡️': '[->]', '🔥': '[CALOR]', '🌡️': '',
                    '💦': '', '🌵': '', '❄️': '[FRIO]',
                    '♨️': '', '🚨': '[!]', '🌧️': '[LLUVIA]',
                    '☀️': '[SOL]', '📅': '', '📋': '', '🌳': ''
                }
                clean_report = report
                for emoji, replacement in replacements.items():
                    clean_report = clean_report.replace(emoji, replacement)
                safe_print("\n" + clean_report)
                
                # Opcion de guardar
                save = input("\nGuardar reporte en archivo? (s/n): ").strip().lower()
                if save == 's':
                    filename = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(report)
                    safe_print(f"[OK] Reporte guardado en: {filename}")
            
            elif option == "6":
                safe_print("\n[GUARDAR] EXPORTANDO DATOS...")
                filename = analyzer.export_data_json()
                safe_print(f"[OK] Datos exportados exitosamente")
            
            elif option == "7":
                safe_print("\n[ADIOS] Hasta luego!")
                break
            
            else:
                safe_print("[X] Opcion invalida")
        
        except Exception as e:
            safe_print(f"\n[ERROR] Error: {str(e)}")
            safe_print("Verifica tu conexion y credenciales")


if __name__ == "__main__":
    main()

