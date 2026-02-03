#!/usr/bin/env python3
"""
Script para obtener el ID de tus polígonos en Agromonitoring
"""

import requests
import json

def get_polygons(api_key):
    """Lista todos los polígonos de tu cuenta"""
    url = f"http://api.agromonitoring.com/agro/1.0/polygons?appid={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        polygons = response.json()
        
        print("=" * 70)
        print("TUS POLÍGONOS EN AGROMONITORING")
        print("=" * 70)
        print()
        
        if not polygons:
            print("❌ No tienes polígonos creados aún")
            return
        
        for i, poly in enumerate(polygons, 1):
            print(f"Polígono #{i}")
            print(f"  📍 Nombre: {poly.get('name', 'Sin nombre')}")
            print(f"  🆔 ID: {poly['id']}")
            print(f"  📏 Área: {poly.get('area', 'N/A')} hectáreas")
            
            # Mostrar coordenadas del centro
            if 'center' in poly:
                center = poly['center']
                print(f"  📌 Centro: {center[1]:.6f}, {center[0]:.6f}")
            
            print(f"  📅 Creado: {poly.get('created_at', 'N/A')}")
            print()
            print("-" * 70)
            print()
        
        # Buscar específicamente "Los Valles"
        valles = [p for p in polygons if 'valles' in p.get('name', '').lower()]
        if valles:
            print("✨ POLÍGONO 'LOS VALLES' ENCONTRADO:")
            print("=" * 70)
            for v in valles:
                print(f"🆔 ID: {v['id']}")
                print(f"📍 Nombre: {v.get('name')}")
                print()
                print(f"👉 Copia este ID y úsalo en el dashboard: {v['id']}")
                print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar con el API: {e}")
        print("Verifica que tu API Key sea correcta")
    except json.JSONDecodeError:
        print("❌ Error al procesar la respuesta del servidor")

def main():
    print("🌱 Obtener IDs de Polígonos - Agromonitoring")
    print()
    
    api_key = input("Ingresa tu API Key de Agromonitoring: ").strip()
    
    if not api_key:
        print("❌ La API Key es requerida")
        return
    
    get_polygons(api_key)

if __name__ == "__main__":
    main()
