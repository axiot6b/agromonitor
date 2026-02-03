@echo off
REM AgroMonitor - Recolector de datos automatizado
REM Este script se ejecuta desde Windows Task Scheduler

cd /d "C:\Users\EfrainTorres\Documents\agro proyect"

REM Ejecutar el recolector de datos
python agro_data_collector.py

REM Guardar log
echo [%date% %time%] Recoleccion completada >> logs\scheduler_log.txt
