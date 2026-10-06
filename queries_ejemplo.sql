-- ============================================================
-- CONSULTAS DE EJEMPLO PARA LA BASE DE DATOS `material_estudio`
-- ============================================================

-- 1. Resumen de registros por tabla
SELECT 'departamentos' AS entidad, count(*) AS total FROM departamentos
UNION ALL
SELECT 'periodos', count(*) FROM periodos
UNION ALL
SELECT 'docentes', count(*) FROM docentes
UNION ALL
SELECT 'asignaturas', count(*) FROM asignaturas
UNION ALL
SELECT 'agrupamientos', count(*) FROM agrupamientos
UNION ALL
SELECT 'planificaciones_periodo', count(*) FROM planificaciones_periodo
UNION ALL
SELECT 'materiales_estudio', count(*) FROM materiales_estudio;

-- 2. Evolución temporal de materiales por departamento y cuatrimestre
SELECT 
    p.codigo AS periodo,
    d.nombre AS departamento,
    COUNT(m.id) AS total_materiales,
    COUNT(DISTINCT pl.agrupamiento_id) AS agrupamientos_con_material
FROM periodos p
JOIN planificaciones_periodo pl ON pl.periodo_id = p.id
JOIN agrupamientos a ON a.id = pl.agrupamiento_id
LEFT JOIN departamentos d ON d.id = a.departamento_id
JOIN materiales_estudio m ON m.planificacion_periodo_id = pl.id
GROUP BY p.codigo, p.anio, p.cuatrimestre, d.nombre
ORDER BY p.anio DESC, p.cuatrimestre DESC, total_materiales DESC;

-- 3. Distribución por tipo de recurso pedagógico
SELECT 
    tipo_material,
    COUNT(*) AS total_items,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS porcentaje
FROM materiales_estudio
GROUP BY tipo_material
ORDER BY total_items DESC;

-- 4. Docentes con mayor cantidad de materiales aportados
SELECT 
    doc.nombre_completo,
    doc.email,
    COUNT(m.id) AS total_materiales,
    COUNT(DISTINCT pl.periodo_id) AS cuatrimestres_activos
FROM docentes doc
JOIN planificaciones_periodo pl ON pl.docente_responsable_id = doc.id
JOIN materiales_estudio m ON m.planificacion_periodo_id = pl.id
GROUP BY doc.id, doc.nombre_completo, doc.email
ORDER BY total_materiales DESC;

-- 5. Búsqueda de materiales para una materia específica (ej. 'MATEMÁTICA DISCRETA')
SELECT 
    p.codigo AS periodo,
    ag.codigo_agrupamiento,
    ag.denominacion,
    m.titulo,
    m.autores,
    m.tipo_material,
    m.isbn,
    m.informacion_adicional
FROM materiales_estudio m
JOIN planificaciones_periodo pl ON pl.id = m.planificacion_periodo_id
JOIN periodos p ON p.id = pl.periodo_id
JOIN agrupamientos ag ON ag.id = pl.agrupamiento_id
WHERE ag.denominacion ILIKE '%discreta%'
ORDER BY p.anio DESC, m.id;

-- 6. Asignaturas y su correspondencia con agrupamientos (Relación N:M)
SELECT 
    ag.codigo_agrupamiento,
    ag.denominacion AS agrupamiento,
    asig.codigo AS codigo_asignatura,
    asig.nombre AS asignatura,
    dep.nombre AS departamento
FROM agrupamiento_asignaturas aa
JOIN agrupamientos ag ON ag.id = aa.agrupamiento_id
JOIN asignaturas asig ON asig.id = aa.asignatura_id
LEFT JOIN departamentos dep ON dep.id = ag.departamento_id
ORDER BY ag.codigo_agrupamiento, asig.codigo;
