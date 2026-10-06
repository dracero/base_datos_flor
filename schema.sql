-- ============================================================
-- BASE DE DATOS: material_estudio
-- ESQUEMA RELACIONAL NORMALIZADO (3FN)
-- ============================================================

DROP TABLE IF EXISTS materiales_estudio CASCADE;
DROP TABLE IF EXISTS planificaciones_periodo CASCADE;
DROP TABLE IF EXISTS agrupamiento_asignaturas CASCADE;
DROP TABLE IF EXISTS agrupamientos CASCADE;
DROP TABLE IF EXISTS asignaturas CASCADE;
DROP TABLE IF EXISTS periodos CASCADE;
DROP TABLE IF EXISTS docentes CASCADE;
DROP TABLE IF EXISTS departamentos CASCADE;

-- 1. Departamentos académicos
CREATE TABLE departamentos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL
);

-- 2. Docentes
CREATE TABLE docentes (
    id SERIAL PRIMARY KEY,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Períodos Académicos (Cuatrimestres)
CREATE TABLE periodos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,    -- ej. '2026 1C', '2025 2C'
    anio INT NOT NULL,                     -- ej. 2026
    cuatrimestre VARCHAR(10) NOT NULL      -- ej. '1C', '2C'
);

-- 4. Asignaturas individuales de los planes de estudio
CREATE TABLE asignaturas (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(30) UNIQUE NOT NULL,    -- ej. '6106', '8111', 'CB001'
    nombre VARCHAR(255) NOT NULL,
    departamento_id INT REFERENCES departamentos(id) ON DELETE SET NULL
);

-- 5. Agrupamientos de Planificación (Cátedras / Comisiones unificadas)
CREATE TABLE agrupamientos (
    id SERIAL PRIMARY KEY,
    codigo_agrupamiento VARCHAR(30) UNIQUE NOT NULL,  -- ej. 'AGPLA0001', 'AGPLA0002'
    codigo_planes VARCHAR(100),                        -- ej. '6106', '6107-8111'
    denominacion TEXT NOT NULL,                        -- ej. '8111 - MATEMÁTICA DISCRETA / 6107 - MATEMÁTICA DISCRETA'
    departamento_id INT REFERENCES departamentos(id) ON DELETE SET NULL
);

-- 6. Relación N:M Agrupamientos <-> Asignaturas
CREATE TABLE agrupamiento_asignaturas (
    agrupamiento_id INT REFERENCES agrupamientos(id) ON DELETE CASCADE,
    asignatura_id INT REFERENCES asignaturas(id) ON DELETE CASCADE,
    PRIMARY KEY (agrupamiento_id, asignatura_id)
);

-- 7. Planificación por período académico
CREATE TABLE planificaciones_periodo (
    id SERIAL PRIMARY KEY,
    agrupamiento_id INT REFERENCES agrupamientos(id) ON DELETE CASCADE,
    periodo_id INT REFERENCES periodos(id) ON DELETE CASCADE,
    docente_responsable_id INT REFERENCES docentes(id) ON DELETE SET NULL,
    completa BOOLEAN DEFAULT FALSE,
    drive_file_link TEXT,
    cantidad_declarada INT DEFAULT 0,
    UNIQUE (agrupamiento_id, periodo_id)
);

-- 8. Materiales de Estudio (Libros, Apuntes, Guías, Videos, Aulas Virtuales)
CREATE TABLE materiales_estudio (
    id SERIAL PRIMARY KEY,
    planificacion_periodo_id INT REFERENCES planificaciones_periodo(id) ON DELETE CASCADE,
    titulo TEXT NOT NULL,
    autores TEXT,
    isbn TEXT,
    anio_edicion TEXT,
    tipo_material TEXT,
    informacion_adicional TEXT,
    modalidad_acceso TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización de consultas
CREATE INDEX idx_asignaturas_codigo ON asignaturas(codigo);
CREATE INDEX idx_agrupamientos_codigo ON agrupamientos(codigo_agrupamiento);
CREATE INDEX idx_planificaciones_periodo ON planificaciones_periodo(periodo_id, agrupamiento_id);
CREATE INDEX idx_materiales_planificacion ON materiales_estudio(planificacion_periodo_id);
CREATE INDEX idx_materiales_titulo ON materiales_estudio USING gin(to_tsvector('spanish', titulo));
