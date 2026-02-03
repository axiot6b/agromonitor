"""
AgroMonitor - Scheduler
Ejecuta el recolector de datos automáticamente cada hora

Ejecutar: python scheduler.py
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def collect_data_job():
    """Job que ejecuta la recolección de datos"""
    from agro_data_collector import collect_and_save_all_data
    
    logger.info("=" * 50)
    logger.info("Iniciando recolección programada de datos...")
    logger.info("=" * 50)
    
    try:
        result = collect_and_save_all_data()
        if result:
            logger.info("Recolección completada exitosamente")
        else:
            logger.warning("Recolección completada con errores")
    except Exception as e:
        logger.error(f"Error en recolección: {e}")
    
    logger.info(f"Próxima ejecución en 1 hora")
    logger.info("=" * 50 + "\n")

def main():
    """Punto de entrada principal del scheduler"""
    print("=" * 60)
    print("  AGROMONITOR - SCHEDULER AUTOMATICO")
    print("=" * 60)
    print(f"  Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Frecuencia: Cada 1 hora")
    print("  Presiona Ctrl+C para detener")
    print("=" * 60 + "\n")
    
    # Crear scheduler
    scheduler = BlockingScheduler()
    
    # Agregar job cada hora
    scheduler.add_job(
        collect_data_job,
        trigger=IntervalTrigger(hours=1),
        id='data_collector',
        name='Recolector de datos cada hora',
        replace_existing=True,
        next_run_time=datetime.now()  # Ejecutar inmediatamente la primera vez
    )
    
    logger.info("Scheduler iniciado. Primera ejecución ahora...")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n" + "=" * 60)
        print("  Scheduler detenido por el usuario")
        print("=" * 60)
        scheduler.shutdown()

if __name__ == "__main__":
    main()
