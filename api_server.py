"""
AgroMonitor - API Server
Backend Flask que sirve datos del dashboard desde PostgreSQL

Ejecutar: python api_server.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import json

# Importar configuración de BD
from db_config import get_connection

app = Flask(__name__)
CORS(app)  # Permitir requests desde el dashboard

# ============================================
# ENDPOINTS DE LA API
# ============================================

@app.route('/')
def home():
    """Endpoint de bienvenida"""
    return jsonify({
        'name': 'AgroMonitor API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': [
            '/api/weather',
            '/api/weather/history',
            '/api/soil',
            '/api/soil/history',
            '/api/ndvi',
            '/api/ndvi/history',
            '/api/forecast',
            '/api/stats'
        ]
    })

@app.route('/api/weather')
def get_weather():
    """Obtiene el último registro de clima"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, temperature_c, feels_like_c, temp_min_c, temp_max_c,
                   humidity_percent, pressure_hpa, wind_speed_ms, wind_deg,
                   clouds_percent, weather_main, weather_description
            FROM weather_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'timestamp': row[0].isoformat() if row[0] else None,
                'temperature_c': float(row[1]) if row[1] else None,
                'feels_like_c': float(row[2]) if row[2] else None,
                'temp_min_c': float(row[3]) if row[3] else None,
                'temp_max_c': float(row[4]) if row[4] else None,
                'humidity_percent': row[5],
                'pressure_hpa': row[6],
                'wind_speed_ms': float(row[7]) if row[7] else None,
                'wind_deg': row[8],
                'clouds_percent': row[9],
                'weather_main': row[10],
                'weather_description': row[11]
            })
        return jsonify({'message': 'No data available'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather/history')
def get_weather_history():
    """Obtiene historial de clima"""
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, temperature_c, humidity_percent, 
                   wind_speed_ms, weather_main
            FROM weather_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
            LIMIT %s
        """, (days, limit))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'timestamp': row[0].isoformat(),
            'temperature_c': float(row[1]) if row[1] else None,
            'humidity_percent': row[2],
            'wind_speed_ms': float(row[3]) if row[3] else None,
            'weather_main': row[4]
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil')
def get_soil():
    """Obtiene el último registro de suelo"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, soil_temp_c, soil_moisture, soil_moisture_percent
            FROM soil_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'timestamp': row[0].isoformat() if row[0] else None,
                'soil_temp_c': float(row[1]) if row[1] else None,
                'soil_moisture': float(row[2]) if row[2] else None,
                'soil_moisture_percent': float(row[3]) if row[3] else None
            })
        return jsonify({'message': 'No data available'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/soil/history')
def get_soil_history():
    """Obtiene historial de suelo"""
    days = request.args.get('days', 7, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, soil_temp_c, soil_moisture_percent
            FROM soil_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'timestamp': row[0].isoformat(),
            'soil_temp_c': float(row[1]) if row[1] else None,
            'soil_moisture_percent': float(row[2]) if row[2] else None
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ndvi')
def get_ndvi():
    """Obtiene el último registro de NDVI"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, image_date, ndvi_mean, ndvi_min, ndvi_max,
                   ndvi_std, ndwi_mean, cloud_coverage
            FROM ndvi_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            return jsonify({
                'timestamp': row[0].isoformat() if row[0] else None,
                'image_date': row[1].isoformat() if row[1] else None,
                'ndvi_mean': float(row[2]) if row[2] else None,
                'ndvi_min': float(row[3]) if row[3] else None,
                'ndvi_max': float(row[4]) if row[4] else None,
                'ndvi_std': float(row[5]) if row[5] else None,
                'ndwi_mean': float(row[6]) if row[6] else None,
                'cloud_coverage': float(row[7]) if row[7] else None
            })
        return jsonify({'message': 'No data available'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ndvi/history')
def get_ndvi_history():
    """Obtiene historial de NDVI"""
    days = request.args.get('days', 30, type=int)
    
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, image_date, ndvi_mean, ndwi_mean
            FROM ndvi_data
            WHERE timestamp > NOW() - INTERVAL '%s days'
            ORDER BY timestamp DESC
        """, (days,))
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'timestamp': row[0].isoformat(),
            'image_date': row[1].isoformat() if row[1] else None,
            'ndvi_mean': float(row[2]) if row[2] else None,
            'ndwi_mean': float(row[3]) if row[3] else None
        } for row in rows]
        
        return jsonify({'count': len(data), 'data': data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/forecast')
def get_forecast():
    """Obtiene el pronóstico más reciente"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT forecast_date, temp_min_c, temp_max_c, temp_avg_c,
                   humidity_avg, precipitation_mm
            FROM forecast_data
            WHERE forecast_date >= CURRENT_DATE
            ORDER BY forecast_date
            LIMIT 5
        """)
        
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        data = [{
            'date': row[0].isoformat(),
            'temp_min_c': float(row[1]) if row[1] else None,
            'temp_max_c': float(row[2]) if row[2] else None,
            'temp_avg_c': float(row[3]) if row[3] else None,
            'humidity_avg': row[4],
            'precipitation_mm': float(row[5]) if row[5] else None
        } for row in rows]
        
        total_precip = sum(d['precipitation_mm'] or 0 for d in data)
        
        return jsonify({
            'days': len(data),
            'total_precipitation_mm': round(total_precip, 1),
            'forecast': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Obtiene estadísticas generales"""
    conn = get_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        
        # Contar registros
        stats = {}
        for table in ['weather_data', 'soil_data', 'ndvi_data', 'forecast_data']:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table.replace('_data', '_records')] = cur.fetchone()[0]
        
        # Última actualización
        cur.execute("SELECT MAX(timestamp) FROM weather_data")
        last_update = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return jsonify({
            'records': stats,
            'last_update': last_update.isoformat() if last_update else None,
            'database': 'Neon PostgreSQL'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("  AgroMonitor API Server")
    print("=" * 50)
    print("  Endpoints disponibles:")
    print("    GET /api/weather        - Clima actual")
    print("    GET /api/weather/history - Historial clima")
    print("    GET /api/soil           - Suelo actual")
    print("    GET /api/soil/history   - Historial suelo")
    print("    GET /api/ndvi           - NDVI actual")
    print("    GET /api/ndvi/history   - Historial NDVI")
    print("    GET /api/forecast       - Pronóstico 5 días")
    print("    GET /api/stats          - Estadísticas")
    print("=" * 50)
    print("  Iniciando servidor en http://localhost:5000")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
