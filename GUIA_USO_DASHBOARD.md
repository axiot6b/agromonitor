# 🌱 Guía de Uso - Dashboard AgroMonitor para tu Finca en Veraguas

## 📋 Descripción General

Este dashboard te permite monitorear en tiempo real tus 2 hectáreas en Veraguas (379.62 msnm) utilizando la API gratuita de Agromonitoring. El sistema está optimizado para tu plan de cultivo Año 1:

- **1 hectárea**: Plátano 🍌
- **0.5 hectárea**: Hortalizas 🌶️ (tomate, pimentón)
- **0.5 hectárea**: Tubérculos 🥔 (yuca, ñame) + frutales jóvenes

---

## 🚀 Configuración Inicial

### Paso 1: Obtener tu API Key

1. Ve a [https://agromonitoring.com](https://agromonitoring.com)
2. Crea una cuenta gratuita
3. En tu dashboard, copia tu API Key

### Paso 2: Inicializar el Dashboard

1. Abre el archivo `agro-dashboard.html` en tu navegador
2. Pega tu API Key en el campo correspondiente
3. Deja el campo "ID del Polígono" vacío (se creará automáticamente)
4. Haz clic en "🚀 Inicializar Dashboard"

El sistema creará automáticamente un polígono de 2 hectáreas centrado en tus coordenadas: **8.439227, -81.191935**

---

## 📊 Funcionalidades del Dashboard

### 🗺️ Mapa de tu Finca

- **Vista satelital** de tus 2 hectáreas
- **Polígono verde** que delimita tu área
- **Marcador central** con información básica
- El mapa es interactivo: puedes hacer zoom y mover

### ☀️ Clima Actual

Muestra en tiempo real:
- Temperatura actual y sensación térmica
- Humedad relativa
- Presión atmosférica
- Velocidad del viento
- Nubosidad

**Actualización**: Cada 2 horas
**Uso**: Planificar actividades diarias (riego, aplicaciones, cosecha)

### 📅 Pronóstico 5 Días

Pronóstico meteorológico con:
- Temperatura por día
- Condiciones climáticas
- Precipitación esperada (mm)

**Actualización**: 2 veces al día
**Uso**: Planificar riego, aplicaciones de fertilizantes, cosechas

### 🌿 NDVI - Salud Vegetal

El **NDVI** (Índice de Vegetación de Diferencia Normalizada) mide la salud de tus cultivos:

#### Interpretación de valores:
- **-1.0 a 0.2**: ⚠️ Vegetación escasa o suelo desnudo
- **0.2 a 0.4**: 📊 Vegetación moderada (requiere atención)
- **0.4 a 0.6**: 🌿 Vegetación saludable
- **0.6 a 0.8**: 🌱 Vegetación muy saludable
- **0.8 a 1.0**: ✨ Vegetación óptima

#### Selector de Zonas:
Puedes ver el NDVI por zona de cultivo:
- 🍌 **Plátano** (1 ha)
- 🌶️ **Hortalizas** (0.5 ha)
- 🥔 **Tubérculos** (0.5 ha)

**Actualización**: 2 veces al día (imágenes satelitales cada 3-5 días)
**Uso**: 
- Detectar áreas con problemas de crecimiento
- Identificar plagas o enfermedades temprano
- Optimizar fertilización

### 💧 NDWI - Estrés Hídrico

El **NDWI** (Índice de Agua de Diferencia Normalizada) mide el contenido de agua en las plantas:

#### Interpretación de valores:
- **< -0.3**: 🌵 Muy seco - Estrés hídrico severo
- **-0.3 a 0**: 💧 Seco - Necesita riego
- **0 a 0.2**: 💚 Hidratación adecuada
- **> 0.2**: 🌊 Bien hidratado

**Actualización**: Cada vez que hay imagen satelital nueva
**Uso**:
- Determinar cuándo regar
- Detectar problemas de drenaje
- Optimizar uso de agua

### 🌍 Datos del Suelo

Monitorea:
- **Temperatura del suelo** (a 10cm de profundidad)
- **Humedad del suelo** (% de saturación)

#### Niveles óptimos de humedad:
- **< 30%**: Seco - programar riego
- **30-70%**: Ideal para la mayoría de cultivos
- **> 80%**: Saturado - verificar drenaje

**Actualización**: 2 veces al día
**Uso**:
- Programación precisa de riego
- Identificar zonas con mal drenaje
- Optimizar aplicación de nutrientes

### 📊 Histórico NDVI (30 días)

Gráfica de tendencia que muestra:
- Evolución de la salud vegetal en el último mes
- Detección de patrones estacionales
- Efectividad de tratamientos aplicados

**Uso**:
- Comparar productividad entre semanas
- Evaluar impacto de fertilizaciones
- Detectar problemas antes de que sean visibles

### 🔔 Alertas y Recomendaciones

El sistema genera alertas automáticas basadas en:

#### Tipos de alertas:

1. **Temperatura**
   - 🌡️ Alta (>32°C): Aumentar riego en hortalizas
   - 🌡️ Baja (<18°C): Proteger cultivos sensibles

2. **Humedad del Suelo**
   - 💧 Baja (<30%): Programar riego
   - 💧 Alta (>80%): Verificar drenaje
   - ✅ Óptima (30-70%): Mantener

3. **Pronóstico de Lluvia**
   - 🌧️ Lluvia significativa (>20mm): Suspender riego
   - ☀️ Sin lluvia + suelo seco: Planificar riego

4. **Recomendaciones por Cultivo**
   - 🍌 Plátano: Monitoreo de Sigatoka
   - 🌶️ Hortalizas: Control de plagas, fertilización
   - 🥔 Tubérculos: Estado de raíces

---

## ⚙️ Límites del Plan Gratuito

Recuerda que el plan gratuito de Agromonitoring tiene estas restricciones:

### Llamadas al API:
- **60 llamadas por minuto** (datos satelitales)
- **500 llamadas por día** (datos meteorológicos)

### Polígonos:
- **Máximo 10 polígonos por mes**
- Tú solo necesitas 1 para tus 2 hectáreas ✅

### Actualización de Datos:
- **Datos satelitales**: 2 veces al día
- **Imágenes nuevas**: Cada 3-5 días (satélites Sentinel-2 y Landsat-8)
- **Datos de clima**: Cada 2 horas
- **Datos de suelo**: 2 veces al día

El dashboard está configurado para actualizar automáticamente cada 10 minutos sin exceder estos límites.

---

## 📱 Uso Recomendado por Día

### 🌅 Mañana (6:00 - 8:00 AM)
1. Revisar **clima actual** y **pronóstico**
2. Verificar **humedad del suelo**
3. Chequear **alertas** del sistema
4. Planificar actividades del día (riego, aplicaciones)

### 🌞 Mediodía (12:00 - 1:00 PM)
1. Revisar **temperatura actual**
2. Verificar si hay nuevas **alertas de temperatura alta**
3. Ajustar riego si es necesario

### 🌆 Tarde (5:00 - 6:00 PM)
1. Revisar **NDVI** y **NDWI** por zona
2. Analizar **gráfico histórico**
3. Planificar actividades del día siguiente

---

## 🎯 Casos de Uso Específicos

### 1. Planificación de Riego

**Objetivo**: Determinar cuándo y cuánto regar

**Datos a revisar**:
- Humedad del suelo actual
- NDWI (estrés hídrico)
- Pronóstico de lluvia 5 días
- Temperatura actual

**Decisión**:
- Humedad <30% + NDWI <0 + sin lluvia prevista = **REGAR HOY**
- Humedad >40% + lluvia prevista >10mm = **NO REGAR**

### 2. Detección Temprana de Problemas

**Objetivo**: Identificar plagas, enfermedades o deficiencias nutricionales

**Datos a revisar**:
- NDVI por zona (comparar entre zonas)
- Tendencia del gráfico histórico (¿está bajando?)
- Alertas del sistema

**Señales de alerta**:
- NDVI que baja consistentemente
- Diferencia significativa de NDVI entre zonas con mismo cultivo
- NDVI <0.4 cuando debería estar >0.6

**Acción**: Inspección visual en campo + tratamiento específico

### 3. Optimización de Fertilización

**Objetivo**: Aplicar fertilizantes en el momento óptimo

**Datos a revisar**:
- NDVI actual (si está bajo, puede necesitar nutrientes)
- Humedad del suelo (debe estar >40% para aplicar)
- Pronóstico de lluvia (evitar aplicar antes de lluvia fuerte)

**Momento ideal**:
- Humedad suelo 40-60%
- Sin lluvia fuerte en próximas 48h
- NDVI mostrando leve descenso

### 4. Preparación para Eventos Climáticos

**Objetivo**: Proteger cultivos antes de condiciones adversas

**Datos a revisar**:
- Pronóstico 5 días
- Alertas de temperatura
- Alertas de lluvia excesiva

**Acciones preventivas**:
- Lluvia >50mm prevista: Mejorar drenaje, suspender riego
- Temperatura >35°C: Riego extra, aplicar mulch
- Viento fuerte: Apuntalar plátanos jóvenes

---

## 🔧 Solución de Problemas

### Problema: "No hay datos satelitales disponibles"
**Causa**: Las imágenes satelitales se toman cada 3-5 días
**Solución**: Espera 2-3 días, las imágenes se actualizarán automáticamente

### Problema: "Error cargando datos del clima"
**Causa**: Posible problema de conexión o límite de API alcanzado
**Solución**: 
1. Verifica tu conexión a Internet
2. Espera 5-10 minutos y recarga la página
3. Verifica que no hayas excedido las 500 llamadas diarias

### Problema: El polígono no se creó automáticamente
**Causa**: Error en la API o permisos
**Solución**: 
1. Ve a [https://agromonitoring.com/dashboard](https://agromonitoring.com/dashboard)
2. Crea manualmente el polígono dibujándolo en el mapa
3. Copia el ID del polígono
4. Pégalo en el campo "ID del Polígono" del dashboard

### Problema: Los valores de NDVI parecen incorrectos
**Causa**: Imágenes con mucha nubosidad
**Solución**: 
1. Revisa el % de nubosidad en la información de la imagen
2. Si >30%, espera la próxima imagen más clara
3. El sistema ya filtra automáticamente las imágenes muy nubladas

---

## 📈 Interpretación de Datos por Cultivo

### 🍌 Plátano (1 hectárea)

**NDVI esperado**:
- Plantas jóvenes (0-3 meses): 0.3-0.5
- Desarrollo (3-6 meses): 0.5-0.7
- Producción (6+ meses): 0.7-0.85

**NDWI esperado**: 0.1-0.3 (requiere buena hidratación)

**Humedad suelo ideal**: 50-70%

**Alertas críticas**:
- NDVI <0.4 en plantas de 4+ meses = revisar Sigatoka
- NDWI <0 = estrés hídrico, regar urgente
- Temperatura >34°C = proteger con mulch

### 🌶️ Hortalizas (0.5 hectárea)

**NDVI esperado**:
- Plántulas: 0.2-0.4
- Desarrollo: 0.5-0.7
- Producción: 0.6-0.8

**NDWI esperado**: 0.05-0.25

**Humedad suelo ideal**: 40-60% (riego más frecuente)

**Alertas críticas**:
- NDVI bajando rápido = posible plaga o enfermedad
- Humedad <30% = regar en 24h
- Temperatura >32°C = riego extra al atardecer

### 🥔 Tubérculos (0.5 hectárea)

**NDVI esperado**:
- Brotación: 0.3-0.5
- Desarrollo: 0.5-0.7
- Pre-cosecha: 0.4-0.6 (baja cuando maduran)

**NDWI esperado**: -0.1-0.2

**Humedad suelo ideal**: 45-65%

**Alertas críticas**:
- Humedad >75% = riesgo de pudrición
- NDVI >0.75 en etapa de cosecha = retrasar cosecha
- Temperatura suelo <15°C = desarrollo lento

---

## 🌟 Consejos para Máximo Aprovechamiento

1. **Revisa el dashboard diariamente** - Al menos en la mañana y tarde
2. **Compara zonas** - Usa los botones de zona para comparar NDVI entre cultivos
3. **Sigue las tendencias** - El gráfico histórico es tu mejor herramienta predictiva
4. **Actúa sobre las alertas** - El sistema te avisa con anticipación
5. **Registra tus acciones** - Anota cuándo riegas, fertilizas o aplicas tratamientos
6. **Correlaciona datos** - Cruza NDVI + clima + humedad para decisiones inteligentes
7. **Planifica semanalmente** - Usa el pronóstico de 5 días para planificar la semana

---

## 📞 Recursos Adicionales

### Documentación de Agromonitoring:
- API Documentation: [https://agromonitoring.com/api](https://agromonitoring.com/api)
- Dashboard: [https://agromonitoring.com/dashboard](https://agromonitoring.com/dashboard)

### Sobre los Índices:
- **NDVI**: [https://es.wikipedia.org/wiki/NDVI](https://es.wikipedia.org/wiki/NDVI)
- **NDWI**: Mide el contenido de agua en plantas

### Soporte:
- Email Agromonitoring: info@openweathermap.org
- Foro de usuarios: [https://community.openweathermap.org](https://community.openweathermap.org)

---

## 🔄 Actualizaciones Futuras

A medida que tu finca crezca, puedes:

1. **Agregar más polígonos** (hasta 10 gratis)
2. **Crear zonas específicas** para cada tipo de cultivo
3. **Integrar con otros sistemas** (sensores IoT, drones)
4. **Exportar datos** para análisis más profundo
5. **Upgrade a plan pago** si necesitas:
   - Más llamadas al API
   - Datos históricos completos
   - Imágenes de mayor resolución
   - Más polígonos

---

## ✅ Checklist de Inicio

- [ ] Crear cuenta en Agromonitoring
- [ ] Obtener API Key
- [ ] Inicializar dashboard
- [ ] Verificar que el polígono se creó correctamente
- [ ] Revisar todos los paneles funcionan
- [ ] Configurar recordatorio para revisar el dashboard 2x al día
- [ ] Anotar los valores iniciales de NDVI por zona
- [ ] Familiarizarse con las alertas
- [ ] Leer la interpretación de datos por cultivo
- [ ] Planificar la primera semana de riego basado en los datos

---

## 📊 Registro Sugerido

Mantén un registro semanal simple:

| Fecha | NDVI Plátano | NDVI Hortalizas | NDVI Tubérculos | Lluvia (mm) | Acciones Tomadas |
|-------|--------------|-----------------|-----------------|-------------|------------------|
| Sem 1 |              |                 |                 |             |                  |
| Sem 2 |              |                 |                 |             |                  |
| Sem 3 |              |                 |                 |             |                  |
| Sem 4 |              |                 |                 |             |                  |

Esto te ayudará a ver patrones y tomar mejores decisiones.

---

## 🎓 Aprendizaje Continuo

Con el tiempo, notarás:
- Patrones de NDVI según la etapa de crecimiento de cada cultivo
- Correlación entre lluvia y humedad del suelo en tu terreno específico
- Cuándo exactamente tus cultivos necesitan riego (varía según suelo)
- Efectividad de tus fertilizaciones (mejora en NDVI)
- Detección temprana de problemas (antes de verlos a simple vista)

**El dashboard te da datos, pero tú desarrollarás la experiencia para interpretarlos en el contexto de tu finca específica.**

---

¡Éxito con tu proyecto agrícola en Veraguas! 🌱🇵🇦