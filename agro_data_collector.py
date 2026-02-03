#!/usr/bin/env python3
"""
AgroMonitor - Data Collector
Recolecta datos de clima, suelo e índices NDVI/NDWI y los guarda en archivos CSV y JSON.

Ejecutar: python agro_data_collector.py
"""

import requests
import json
import csv
import os
from datetime import datetime
from pathlib import Path

# Configuración
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "polygon_config.json"
DATA_DIR = SCRIPT_DIR / "data"

# Crear directorio de datos si no existe
DATA_DIR.mkdir(exist_ok=True)

def load_config():
    """Carga la configuración desde polygon_config.json"""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            raw_config = json.load(f)
        
        # Extraer valores de la estructura anidada
        config = {
            'api_key': raw_config.get('api', {}).get('api_key'),
            'polygon_id': raw_config.get('polygon', {}).get('id'),
            'polygon_name': raw_config.get('polygon', {}).get('nombre'),
            'location': {
                'lat': raw_config.get('polygon', {}).get('ubicacion', {}).get('latitud'),
                'lon': raw_config.get('polygon', {}).get('ubicacion', {}).get('longitud'),
                'altitude': raw_config.get('polygon', {}).get('ubicacion', {}).get('altitud_msnm'),
                'region': raw_config.get('polygon', {}).get('ubicacion', {}).get('region'),
                'country': raw_config.get('polygon', {}).get('ubicacion', {}).get('pais'),
                'description': raw_config.get('polygon', {}).get('descripcion')
            },
            'crops': raw_config.get('polygon', {}).get('cultivos', {})
        }
        return config
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo {CONFIG_FILE}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: El archivo {CONFIG_FILE} no es un JSON válido")
        return None

def safe_print(text):
    """Print seguro para Windows (evita errores de codificación con emojis)"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'replace').decode('ascii'))

def get_weather_data(api_key, polygon_id):
    """Obtiene datos del clima actual"""
    url = f"http://api.agromonitoring.com/agro/1.0/weather?polyid={polygon_id}&appid={api_key}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'temperature_c': round(data['main']['temp'] - 273.15, 2),
            'feels_like_c': round(data['main']['feels_like'] - 273.15, 2),
            'temp_min_c': round(data['main']['temp_min'] - 273.15, 2),
            'temp_max_c': round(data['main']['temp_max'] - 273.15, 2),
            'humidity_percent': data['main']['humidity'],
            'pressure_hpa': data['main']['pressure'],
            'wind_speed_ms': data['wind']['speed'],
            'wind_deg': data['wind'].get('deg', 0),
            'clouds_percent': data['clouds']['all'],
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description']
        }
    except Exception as e:
        safe_print(f"Error obteniendo clima: {e}")
        return None

def get_soil_data(api_key, polygon_id):
    """Obtiene datos del suelo"""
    url = f"http://api.agromonitoring.com/agro/1.0/soil?polyid={polygon_id}&appid={api_key}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'soil_temp_c': round(data.get('t10', 273.15) - 273.15, 2),
            'soil_moisture': round(data.get('moisture', 0), 4),
            'soil_moisture_percent': round(data.get('moisture', 0) * 100, 2)
        }
    except Exception as e:
        safe_print(f"Error obteniendo datos del suelo: {e}")
        return None

def get_ndvi_data(api_key, polygon_id):
    """Obtiene el último dato de NDVI disponible"""
    import time
    end = int(time.time())
    start = end - (30 * 24 * 60 * 60)  # Últimos 30 días
    
    url = f"http://api.agromonitoring.com/agro/1.0/image/search?start={start}&end={end}&polyid={polygon_id}&appid={api_key}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        images = response.json()
        
        if images and len(images) > 0:
            latest_image = images[0]
            
            # Obtener estadísticas NDVI
            ndvi_stats = None
            ndwi_stats = None
            
            if latest_image.get('stats', {}).get('ndvi'):
                stats_response = requests.get(latest_image['stats']['ndvi'], timeout=30)
                ndvi_stats = stats_response.json()
            
            if latest_image.get('stats', {}).get('ndwi'):
                stats_response = requests.get(latest_image['stats']['ndwi'], timeout=30)
                ndwi_stats = stats_response.json()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'image_date': datetime.fromtimestamp(latest_image['dt']).isoformat(),
                'ndvi_mean': round(ndvi_stats.get('mean', 0), 4) if ndvi_stats else None,
                'ndvi_min': round(ndvi_stats.get('min', 0), 4) if ndvi_stats else None,
                'ndvi_max': round(ndvi_stats.get('max', 0), 4) if ndvi_stats else None,
                'ndvi_std': round(ndvi_stats.get('std', 0), 4) if ndvi_stats else None,
                'ndwi_mean': round(ndwi_stats.get('mean', 0), 4) if ndwi_stats else None,
                'cloud_coverage': latest_image.get('cl', 0)
            }
    except Exception as e:
        safe_print(f"Error obteniendo NDVI: {e}")
        return None

def get_forecast_data(api_key, polygon_id):
    """Obtiene datos del pronóstico"""
    url = f"http://api.agromonitoring.com/agro/1.0/weather/forecast?polyid={polygon_id}&appid={api_key}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Procesar pronóstico por día
        daily_forecast = {}
        total_precip = 0
        
        for item in data:
            date = datetime.fromtimestamp(item['dt'])
            day_key = date.strftime('%Y-%m-%d')
            
            if day_key not in daily_forecast:
                daily_forecast[day_key] = {
                    'temps': [],
                    'precip': 0,
                    'humidity': []
                }
            
            daily_forecast[day_key]['temps'].append(item['main']['temp'] - 273.15)
            daily_forecast[day_key]['humidity'].append(item['main']['humidity'])
            
            if 'rain' in item and '3h' in item['rain']:
                daily_forecast[day_key]['precip'] += item['rain']['3h']
                total_precip += item['rain']['3h']
        
        # Calcular resumen
        forecast_summary = []
        for day, values in list(daily_forecast.items())[:5]:
            forecast_summary.append({
                'date': day,
                'temp_min': round(min(values['temps']), 1),
                'temp_max': round(max(values['temps']), 1),
                'temp_avg': round(sum(values['temps']) / len(values['temps']), 1),
                'humidity_avg': round(sum(values['humidity']) / len(values['humidity']), 0),
                'precipitation_mm': round(values['precip'], 1)
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_5day_precip_mm': round(total_precip, 1),
            'daily_forecast': forecast_summary
        }
    except Exception as e:
        safe_print(f"Error obteniendo pronóstico: {e}")
        return None

def save_to_csv(data, filename, fieldnames):
    """Guarda datos en un archivo CSV (append)"""
    file_path = DATA_DIR / filename
    file_exists = file_path.exists()
    
    try:
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        return True
    except Exception as e:
        safe_print(f"Error guardando CSV {filename}: {e}")
        return False

def save_to_json(data, filename):
    """Guarda datos en un archivo JSON (append a array)"""
    file_path = DATA_DIR / filename
    
    try:
        # Cargar datos existentes
        existing_data = []
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # Agregar nuevo dato
        existing_data.append(data)
        
        # Guardar
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        safe_print(f"Error guardando JSON {filename}: {e}")
        return False

# ============================================
# FUNCIONES PARA GUARDAR EN POSTGRESQL (NEON)
# ============================================

def get_db_connection():
    """Obtiene conexión a la base de datos"""
    try:
        from db_config import get_connection
        return get_connection()
    except ImportError:
        safe_print("   [AVISO] db_config.py no encontrado - solo guardando en CSV")
        return None
    except Exception as e:
        safe_print(f"   [AVISO] Error conexión BD: {e}")
        return None

def save_weather_to_db(data, polygon_id):
    """Guarda datos del clima en PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO weather_data (
                polygon_id, temperature_c, feels_like_c, temp_min_c, temp_max_c,
                humidity_percent, pressure_hpa, wind_speed_ms, wind_deg,
                clouds_percent, weather_main, weather_description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            polygon_id,
            data.get('temperature_c'),
            data.get('feels_like_c'),
            data.get('temp_min_c'),
            data.get('temp_max_c'),
            data.get('humidity_percent'),
            data.get('pressure_hpa'),
            data.get('wind_speed_ms'),
            data.get('wind_deg'),
            data.get('clouds_percent'),
            data.get('weather_main'),
            data.get('weather_description')
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        safe_print(f"   [ERROR BD] weather: {e}")
        conn.rollback()
        conn.close()
        return False

def save_soil_to_db(data, polygon_id):
    """Guarda datos del suelo en PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO soil_data (
                polygon_id, soil_temp_c, soil_moisture, soil_moisture_percent
            ) VALUES (%s, %s, %s, %s)
        """, (
            polygon_id,
            data.get('soil_temp_c'),
            data.get('soil_moisture'),
            data.get('soil_moisture_percent')
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        safe_print(f"   [ERROR BD] soil: {e}")
        conn.rollback()
        conn.close()
        return False

def save_ndvi_to_db(data, polygon_id):
    """Guarda datos de NDVI en PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        # Convertir image_date string a timestamp
        image_date = data.get('image_date')
        
        cur.execute("""
            INSERT INTO ndvi_data (
                polygon_id, image_date, ndvi_mean, ndvi_min, ndvi_max,
                ndvi_std, ndwi_mean, cloud_coverage
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            polygon_id,
            image_date,
            data.get('ndvi_mean'),
            data.get('ndvi_min'),
            data.get('ndvi_max'),
            data.get('ndvi_std'),
            data.get('ndwi_mean'),
            data.get('cloud_coverage')
        ))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        safe_print(f"   [ERROR BD] ndvi: {e}")
        conn.rollback()
        conn.close()
        return False

def save_forecast_to_db(forecast_data, polygon_id):
    """Guarda datos del pronóstico en PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        for day in forecast_data.get('daily_forecast', []):
            cur.execute("""
                INSERT INTO forecast_data (
                    polygon_id, forecast_date, temp_min_c, temp_max_c,
                    temp_avg_c, humidity_avg, precipitation_mm
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                polygon_id,
                day.get('date'),
                day.get('temp_min'),
                day.get('temp_max'),
                day.get('temp_avg'),
                day.get('humidity_avg'),
                day.get('precipitation_mm')
            ))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        safe_print(f"   [ERROR BD] forecast: {e}")
        conn.rollback()
        conn.close()
        return False

def collect_and_save_all_data():
    """Función principal: recolecta y guarda todos los datos"""
    safe_print("\n" + "=" * 60)
    safe_print("  AGROMONITOR - RECOLECTOR DE DATOS")
    safe_print("=" * 60)
    safe_print(f"  Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    safe_print("=" * 60 + "\n")
    
    # Cargar configuración
    config = load_config()
    if not config:
        return False
    
    api_key = config.get('api_key')
    polygon_id = config.get('polygon_id')
    
    if not api_key or not polygon_id:
        safe_print("ERROR: API Key o Polygon ID no configurados")
        return False
    
    safe_print(f"Poligono: {config.get('polygon_name', 'N/A')}")
    safe_print(f"Ubicacion: {config.get('location', {}).get('description', 'N/A')}")
    safe_print("-" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'polygon_name': config.get('polygon_name'),
        'weather': None,
        'soil': None,
        'ndvi': None,
        'forecast': None
    }
    
    # Variables para tracking de BD
    db_weather_ok = False
    db_soil_ok = False
    db_ndvi_ok = False
    db_forecast_ok = False
    
    # 1. Recolectar datos del clima
    safe_print("\n[1/4] Recolectando datos del clima...")
    weather = get_weather_data(api_key, polygon_id)
    if weather:
        results['weather'] = weather
        save_to_csv(weather, 'weather_history.csv', list(weather.keys()))
        db_weather_ok = save_weather_to_db(weather, polygon_id)
        safe_print(f"   Temperatura: {weather['temperature_c']}C")
        safe_print(f"   Humedad: {weather['humidity_percent']}%")
        safe_print(f"   Condicion: {weather['weather_description']}")
        safe_print(f"   [CSV] OK | [PostgreSQL] {'OK' if db_weather_ok else 'SKIP'}")
    
    # 2. Recolectar datos del suelo
    safe_print("\n[2/4] Recolectando datos del suelo...")
    soil = get_soil_data(api_key, polygon_id)
    if soil:
        results['soil'] = soil
        save_to_csv(soil, 'soil_history.csv', list(soil.keys()))
        db_soil_ok = save_soil_to_db(soil, polygon_id)
        safe_print(f"   Temperatura suelo: {soil['soil_temp_c']}C")
        safe_print(f"   Humedad suelo: {soil['soil_moisture_percent']}%")
        safe_print(f"   [CSV] OK | [PostgreSQL] {'OK' if db_soil_ok else 'SKIP'}")
    
    # 3. Recolectar datos de NDVI
    safe_print("\n[3/4] Recolectando datos de NDVI/NDWI...")
    ndvi = get_ndvi_data(api_key, polygon_id)
    if ndvi:
        results['ndvi'] = ndvi
        # Para NDVI solo guardamos si hay datos válidos
        ndvi_csv = {k: v for k, v in ndvi.items() if v is not None}
        if ndvi_csv:
            save_to_csv(ndvi_csv, 'ndvi_history.csv', list(ndvi_csv.keys()))
            db_ndvi_ok = save_ndvi_to_db(ndvi, polygon_id)
            safe_print(f"   NDVI promedio: {ndvi.get('ndvi_mean', 'N/A')}")
            safe_print(f"   NDWI promedio: {ndvi.get('ndwi_mean', 'N/A')}")
            safe_print(f"   Fecha imagen: {ndvi.get('image_date', 'N/A')}")
            safe_print(f"   [CSV] OK | [PostgreSQL] {'OK' if db_ndvi_ok else 'SKIP'}")
    
    # 4. Recolectar pronóstico
    safe_print("\n[4/4] Recolectando pronostico (5 dias)...")
    forecast = get_forecast_data(api_key, polygon_id)
    if forecast:
        results['forecast'] = forecast
        db_forecast_ok = save_forecast_to_db(forecast, polygon_id)
        safe_print(f"   Precipitacion total 5 dias: {forecast['total_5day_precip_mm']} mm")
        safe_print(f"   [PostgreSQL] {'OK' if db_forecast_ok else 'SKIP'}")
    
    # 5. Guardar registro completo en JSON
    safe_print("\n[GUARDANDO] Registro completo...")
    save_to_json(results, 'complete_records.json')
    safe_print("   [OK] Guardado en complete_records.json")
    
    # Resumen
    safe_print("\n" + "=" * 60)
    safe_print("  RESUMEN DE RECOLECCION")
    safe_print("=" * 60)
    safe_print(f"  Clima:       {'OK' if weather else 'ERROR'} (BD: {'OK' if db_weather_ok else '-'})")
    safe_print(f"  Suelo:       {'OK' if soil else 'ERROR'} (BD: {'OK' if db_soil_ok else '-'})")
    safe_print(f"  NDVI/NDWI:   {'OK' if ndvi else 'ERROR'} (BD: {'OK' if db_ndvi_ok else '-'})")
    safe_print(f"  Pronostico:  {'OK' if forecast else 'ERROR'} (BD: {'OK' if db_forecast_ok else '-'})")
    safe_print("=" * 60)
    safe_print(f"\n  Datos guardados en: {DATA_DIR}")
    safe_print("  Base de datos: PostgreSQL (Neon)")
    safe_print("=" * 60 + "\n")
    
    return True

def main():
    """Punto de entrada principal"""
    import sys
    
    # Si se pasa --loop, ejecutar continuamente cada hora
    if len(sys.argv) > 1 and sys.argv[1] == '--loop':
        import time
        safe_print("Modo LOOP activado - Recolectando datos cada hora")
        safe_print("Presiona Ctrl+C para detener\n")
        
        while True:
            try:
                collect_and_save_all_data()
                safe_print(f"\nProxima recoleccion en 1 hora...")
                safe_print("(Presiona Ctrl+C para detener)\n")
                time.sleep(3600)  # 1 hora
            except KeyboardInterrupt:
                safe_print("\nRecoleccion detenida por el usuario.")
                break
    else:
        # Ejecución única
        collect_and_save_all_data()
        safe_print("Ejecuta con '--loop' para recolectar datos continuamente cada hora.")

if __name__ == "__main__":
    main()
