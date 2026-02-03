#!/usr/bin/env python3
"""
AgroMonitor - Data Collector for GitHub Actions
Versión simplificada para ejecutar en GitHub Actions
Lee credenciales desde variables de entorno (secrets)
"""

import requests
import os
from datetime import datetime
import time

# Leer credenciales desde variables de entorno (GitHub Secrets)
API_KEY = os.environ.get('AGROMONITORING_API_KEY', '')
POLYGON_ID = os.environ.get('POLYGON_ID', '')
DATABASE_URL = os.environ.get('DATABASE_URL', '')

def get_db_connection():
    """Conecta a PostgreSQL"""
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        parsed = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"[ERROR] DB connection: {e}")
        return None

def get_weather_data():
    """Obtiene datos del clima"""
    url = f"http://api.agromonitoring.com/agro/1.0/weather?polyid={POLYGON_ID}&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
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
        print(f"[ERROR] Weather: {e}")
        return None

def get_soil_data():
    """Obtiene datos del suelo"""
    url = f"http://api.agromonitoring.com/agro/1.0/soil?polyid={POLYGON_ID}&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        return {
            'soil_temp_c': round(data.get('t10', 273.15) - 273.15, 2),
            'soil_moisture': round(data.get('moisture', 0), 4),
            'soil_moisture_percent': round(data.get('moisture', 0) * 100, 2)
        }
    except Exception as e:
        print(f"[ERROR] Soil: {e}")
        return None

def get_ndvi_data():
    """Obtiene datos de NDVI"""
    end = int(time.time())
    start = end - (30 * 24 * 60 * 60)
    
    url = f"http://api.agromonitoring.com/agro/1.0/image/search?start={start}&end={end}&polyid={POLYGON_ID}&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        images = response.json()
        
        if images and len(images) > 0:
            latest = images[0]
            ndvi_stats = None
            ndwi_stats = None
            
            if latest.get('stats', {}).get('ndvi'):
                stats_resp = requests.get(latest['stats']['ndvi'], timeout=30)
                ndvi_stats = stats_resp.json()
            
            if latest.get('stats', {}).get('ndwi'):
                stats_resp = requests.get(latest['stats']['ndwi'], timeout=30)
                ndwi_stats = stats_resp.json()
            
            return {
                'image_date': datetime.fromtimestamp(latest['dt']).isoformat(),
                'ndvi_mean': round(ndvi_stats.get('mean', 0), 4) if ndvi_stats else None,
                'ndvi_min': round(ndvi_stats.get('min', 0), 4) if ndvi_stats else None,
                'ndvi_max': round(ndvi_stats.get('max', 0), 4) if ndvi_stats else None,
                'ndvi_std': round(ndvi_stats.get('std', 0), 4) if ndvi_stats else None,
                'ndwi_mean': round(ndwi_stats.get('mean', 0), 4) if ndwi_stats else None,
                'cloud_coverage': latest.get('cl', 0)
            }
    except Exception as e:
        print(f"[ERROR] NDVI: {e}")
    return None

def get_forecast_data():
    """Obtiene pronóstico"""
    url = f"http://api.agromonitoring.com/agro/1.0/weather/forecast?polyid={POLYGON_ID}&appid={API_KEY}"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        daily_forecast = {}
        for item in data:
            date = datetime.fromtimestamp(item['dt'])
            day_key = date.strftime('%Y-%m-%d')
            
            if day_key not in daily_forecast:
                daily_forecast[day_key] = {'temps': [], 'precip': 0, 'humidity': []}
            
            daily_forecast[day_key]['temps'].append(item['main']['temp'] - 273.15)
            daily_forecast[day_key]['humidity'].append(item['main']['humidity'])
            
            if 'rain' in item and '3h' in item['rain']:
                daily_forecast[day_key]['precip'] += item['rain']['3h']
        
        forecast_list = []
        for day, values in list(daily_forecast.items())[:5]:
            forecast_list.append({
                'date': day,
                'temp_min': round(min(values['temps']), 1),
                'temp_max': round(max(values['temps']), 1),
                'temp_avg': round(sum(values['temps']) / len(values['temps']), 1),
                'humidity_avg': round(sum(values['humidity']) / len(values['humidity']), 0),
                'precipitation_mm': round(values['precip'], 1)
            })
        
        return forecast_list
    except Exception as e:
        print(f"[ERROR] Forecast: {e}")
        return None

def save_to_db(weather, soil, ndvi, forecast):
    """Guarda todos los datos en PostgreSQL"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Weather
        if weather:
            cur.execute("""
                INSERT INTO weather_data (
                    polygon_id, temperature_c, feels_like_c, temp_min_c, temp_max_c,
                    humidity_percent, pressure_hpa, wind_speed_ms, wind_deg,
                    clouds_percent, weather_main, weather_description
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (POLYGON_ID, weather['temperature_c'], weather['feels_like_c'],
                  weather['temp_min_c'], weather['temp_max_c'], weather['humidity_percent'],
                  weather['pressure_hpa'], weather['wind_speed_ms'], weather['wind_deg'],
                  weather['clouds_percent'], weather['weather_main'], weather['weather_description']))
            print("[OK] Weather saved to DB")
        
        # Soil
        if soil:
            cur.execute("""
                INSERT INTO soil_data (polygon_id, soil_temp_c, soil_moisture, soil_moisture_percent)
                VALUES (%s, %s, %s, %s)
            """, (POLYGON_ID, soil['soil_temp_c'], soil['soil_moisture'], soil['soil_moisture_percent']))
            print("[OK] Soil saved to DB")
        
        # NDVI
        if ndvi:
            cur.execute("""
                INSERT INTO ndvi_data (
                    polygon_id, image_date, ndvi_mean, ndvi_min, ndvi_max,
                    ndvi_std, ndwi_mean, cloud_coverage
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (POLYGON_ID, ndvi['image_date'], ndvi['ndvi_mean'], ndvi['ndvi_min'],
                  ndvi['ndvi_max'], ndvi['ndvi_std'], ndvi['ndwi_mean'], ndvi['cloud_coverage']))
            print("[OK] NDVI saved to DB")
        
        # Forecast
        if forecast:
            for day in forecast:
                cur.execute("""
                    INSERT INTO forecast_data (
                        polygon_id, forecast_date, temp_min_c, temp_max_c,
                        temp_avg_c, humidity_avg, precipitation_mm
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (POLYGON_ID, day['date'], day['temp_min'], day['temp_max'],
                      day['temp_avg'], day['humidity_avg'], day['precipitation_mm']))
            print("[OK] Forecast saved to DB")
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Saving to DB: {e}")
        conn.rollback()
        conn.close()
        return False

def main():
    """Función principal"""
    print("=" * 50)
    print("AGROMONITOR - GitHub Actions Collector")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 50)
    
    # Verificar credenciales
    if not API_KEY or not POLYGON_ID or not DATABASE_URL:
        print("[ERROR] Missing environment variables!")
        print(f"  API_KEY: {'Set' if API_KEY else 'MISSING'}")
        print(f"  POLYGON_ID: {'Set' if POLYGON_ID else 'MISSING'}")
        print(f"  DATABASE_URL: {'Set' if DATABASE_URL else 'MISSING'}")
        return False
    
    print(f"Polygon ID: {POLYGON_ID}")
    print("-" * 50)
    
    # Recolectar datos
    print("\n[1/4] Collecting weather data...")
    weather = get_weather_data()
    if weather:
        print(f"  Temperature: {weather['temperature_c']}C")
        print(f"  Humidity: {weather['humidity_percent']}%")
    
    print("\n[2/4] Collecting soil data...")
    soil = get_soil_data()
    if soil:
        print(f"  Soil temp: {soil['soil_temp_c']}C")
        print(f"  Soil moisture: {soil['soil_moisture_percent']}%")
    
    print("\n[3/4] Collecting NDVI data...")
    ndvi = get_ndvi_data()
    if ndvi:
        print(f"  NDVI mean: {ndvi['ndvi_mean']}")
    
    print("\n[4/4] Collecting forecast...")
    forecast = get_forecast_data()
    if forecast:
        print(f"  Days: {len(forecast)}")
    
    # Guardar en BD
    print("\n[SAVING] To PostgreSQL...")
    success = save_to_db(weather, soil, ndvi, forecast)
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"  Weather: {'OK' if weather else 'ERROR'}")
    print(f"  Soil: {'OK' if soil else 'ERROR'}")
    print(f"  NDVI: {'OK' if ndvi else 'ERROR'}")
    print(f"  Forecast: {'OK' if forecast else 'ERROR'}")
    print(f"  Database: {'OK' if success else 'ERROR'}")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    main()
