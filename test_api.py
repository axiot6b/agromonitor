#!/usr/bin/env python3
"""
Script de prueba - Verifica conexion con Agromonitoring API
"""

import requests
import json

# Configuracion desde el archivo
with open('polygon_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

API_KEY = config['api']['api_key']
POLYGON_ID = config['polygon']['id']

print("=" * 60)
print("PRUEBA DE CONEXION - AgroMonitor")
print("=" * 60)
print(f"Polygon ID: {POLYGON_ID}")
print(f"API Key: {API_KEY[:10]}...")
print("=" * 60)

# Test 1: Obtener info del poligono
print("\n[TEST 1] Obteniendo info del poligono...")
url = f"http://api.agromonitoring.com/agro/1.0/polygons/{POLYGON_ID}?appid={API_KEY}"
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"  EXITO - Nombre: {data.get('name', 'N/A')}")
        print(f"  Area: {data.get('area', 'N/A')} hectareas")
        if 'center' in data:
            print(f"  Centro: {data['center'][1]:.6f}, {data['center'][0]:.6f}")
    else:
        print(f"  ERROR - Codigo: {response.status_code}")
        print(f"  Mensaje: {response.text}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 2: Obtener clima actual
print("\n[TEST 2] Obteniendo clima actual...")
url = f"http://api.agromonitoring.com/agro/1.0/weather?polyid={POLYGON_ID}&appid={API_KEY}"
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp_k = data.get('main', {}).get('temp', 0)
        temp_c = temp_k - 273.15
        humidity = data.get('main', {}).get('humidity', 0)
        print(f"  EXITO - Temperatura: {temp_c:.1f} C")
        print(f"  Humedad: {humidity}%")
        print(f"  Condicion: {data.get('weather', [{}])[0].get('description', 'N/A')}")
    else:
        print(f"  ERROR - Codigo: {response.status_code}")
except Exception as e:
    print(f"  ERROR: {e}")

# Test 3: Datos del suelo
print("\n[TEST 3] Obteniendo datos del suelo...")
url = f"http://api.agromonitoring.com/agro/1.0/soil?polyid={POLYGON_ID}&appid={API_KEY}"
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        soil_temp = data.get('t10', 0) - 273.15
        soil_moisture = data.get('moisture', 0) * 100
        print(f"  EXITO - Temp suelo (10cm): {soil_temp:.1f} C")
        print(f"  Humedad suelo: {soil_moisture:.1f}%")
    else:
        print(f"  ERROR - Codigo: {response.status_code}")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n" + "=" * 60)
print("PRUEBAS COMPLETADAS")
print("=" * 60)
