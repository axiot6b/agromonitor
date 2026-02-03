-- ============================================
-- AgroMonitor - Database Schema for Neon PostgreSQL
-- ============================================

-- Tabla de datos del clima
CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    polygon_id VARCHAR(50) NOT NULL,
    temperature_c DECIMAL(5,2),
    feels_like_c DECIMAL(5,2),
    temp_min_c DECIMAL(5,2),
    temp_max_c DECIMAL(5,2),
    humidity_percent INTEGER,
    pressure_hpa INTEGER,
    wind_speed_ms DECIMAL(5,2),
    wind_deg INTEGER,
    clouds_percent INTEGER,
    weather_main VARCHAR(50),
    weather_description VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla de datos del suelo
CREATE TABLE IF NOT EXISTS soil_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    polygon_id VARCHAR(50) NOT NULL,
    soil_temp_c DECIMAL(5,2),
    soil_moisture DECIMAL(6,4),
    soil_moisture_percent DECIMAL(5,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla de datos NDVI/NDWI
CREATE TABLE IF NOT EXISTS ndvi_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    polygon_id VARCHAR(50) NOT NULL,
    image_date TIMESTAMPTZ,
    ndvi_mean DECIMAL(6,4),
    ndvi_min DECIMAL(6,4),
    ndvi_max DECIMAL(6,4),
    ndvi_std DECIMAL(6,4),
    ndwi_mean DECIMAL(6,4),
    cloud_coverage DECIMAL(5,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tabla de pronósticos diarios
CREATE TABLE IF NOT EXISTS forecast_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    polygon_id VARCHAR(50) NOT NULL,
    forecast_date DATE NOT NULL,
    temp_min_c DECIMAL(5,2),
    temp_max_c DECIMAL(5,2),
    temp_avg_c DECIMAL(5,2),
    humidity_avg INTEGER,
    precipitation_mm DECIMAL(6,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_weather_timestamp ON weather_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_weather_polygon ON weather_data(polygon_id);
CREATE INDEX IF NOT EXISTS idx_soil_timestamp ON soil_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ndvi_timestamp ON ndvi_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_forecast_date ON forecast_data(forecast_date);

-- Vista para el último registro de cada tipo
CREATE OR REPLACE VIEW latest_weather AS
SELECT DISTINCT ON (polygon_id) *
FROM weather_data
ORDER BY polygon_id, timestamp DESC;

CREATE OR REPLACE VIEW latest_soil AS
SELECT DISTINCT ON (polygon_id) *
FROM soil_data
ORDER BY polygon_id, timestamp DESC;

CREATE OR REPLACE VIEW latest_ndvi AS
SELECT DISTINCT ON (polygon_id) *
FROM ndvi_data
ORDER BY polygon_id, timestamp DESC;
