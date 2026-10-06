import pg from 'pg';

const { Pool } = pg;

export const pool = new Pool({
  host: process.env.PGHOST || 'localhost',
  port: parseInt(process.env.PGPORT || '5432', 10),
  user: process.env.PGUSER || 'postgres',
  password: process.env.PGPASSWORD || 'postgres',
  database: process.env.PGDATABASE || 'material_estudio',
  max: 10,
  idleTimeoutMillis: 30000,
});

export async function query<T = any>(text: string, params?: any[]) {
  const start = Date.now();
  const res = await pool.query<T>(text, params);
  const duration = Date.now() - start;
  return { rows: res.rows, duration, rowCount: res.rowCount };
}

// 1. Estadísticas globales del sistema
export async function getStats() {
  const res = await query(`
    SELECT
      (SELECT count(*) FROM asignaturas) AS total_materias,
      (SELECT count(*) FROM agrupamientos) AS total_agrupamientos,
      (SELECT count(*) FROM materiales_estudio) AS total_materiales,
      (SELECT count(*) FROM docentes) AS total_docentes,
      (SELECT count(*) FROM periodos) AS total_periodos,
      (SELECT count(*) FROM planificaciones_periodo WHERE completa = true) AS planificaciones_completas
  `);
  return res.rows[0];
}

// 2. Departamentos
export async function getDepartamentos() {
  const res = await query(`
    SELECT d.id, d.codigo, d.nombre,
      COUNT(DISTINCT a.id) AS cant_asignaturas,
      COUNT(DISTINCT m.id) AS cant_materiales
    FROM departamentos d
    LEFT JOIN asignaturas a ON a.departamento_id = d.id
    LEFT JOIN agrupamientos ag ON ag.departamento_id = d.id
    LEFT JOIN planificaciones_periodo pl ON pl.agrupamiento_id = ag.id
    LEFT JOIN materiales_estudio m ON m.planificacion_periodo_id = pl.id
    GROUP BY d.id, d.codigo, d.nombre
    ORDER BY d.nombre
  `);
  return res.rows;
}

// 3. Períodos académicos
export async function getPeriodos() {
  const res = await query(`
    SELECT p.id, p.codigo, p.anio, p.cuatrimestre,
      COUNT(DISTINCT pl.agrupamiento_id) AS cant_agrupamientos,
      COUNT(m.id) AS cant_materiales
    FROM periodos p
    LEFT JOIN planificaciones_periodo pl ON pl.periodo_id = p.id
    LEFT JOIN materiales_estudio m ON m.planificacion_periodo_id = pl.id
    GROUP BY p.id, p.codigo, p.anio, p.cuatrimestre
    ORDER BY p.anio DESC, p.cuatrimestre DESC
  `);
  return res.rows;
}

// 4. Tipos de material disponibles con recuento
export async function getTiposMaterial() {
  const res = await query(`
    SELECT tipo_material, COUNT(*) as cantidad
    FROM materiales_estudio
    GROUP BY tipo_material
    ORDER BY cantidad DESC
  `);
  return res.rows;
}

// 5. Lista de materias / asignaturas
export async function getMaterias(filtroDepto?: string) {
  let sql = `
    SELECT 
      a.id,
      a.codigo,
      a.nombre,
      d.nombre AS departamento,
      d.codigo AS departamento_codigo,
      COALESCE(STRING_AGG(DISTINCT ag.codigo_agrupamiento, ', '), '-') AS agrupamientos,
      COUNT(DISTINCT m.id) AS total_materiales,
      COUNT(DISTINCT pl.periodo_id) AS total_cuatrimestres
    FROM asignaturas a
    LEFT JOIN departamentos d ON d.id = a.departamento_id
    LEFT JOIN agrupamiento_asignaturas aa ON aa.asignatura_id = a.id
    LEFT JOIN agrupamientos ag ON ag.id = aa.agrupamiento_id
    LEFT JOIN planificaciones_periodo pl ON pl.agrupamiento_id = ag.id
    LEFT JOIN materiales_estudio m ON m.planificacion_periodo_id = pl.id
  `;
  const params: any[] = [];
  if (filtroDepto) {
    sql += ` WHERE d.codigo = $1 `;
    params.push(filtroDepto);
  }
  sql += `
    GROUP BY a.id, a.codigo, a.nombre, d.nombre, d.codigo
    ORDER BY d.nombre, a.codigo
  `;
  const res = await query(sql, params);
  return res.rows;
}

// 6. Detalle de una asignatura por código
export async function getMateriaDetail(codigo: string) {
  const resMateria = await query(`
    SELECT 
      a.id, a.codigo, a.nombre,
      d.nombre AS departamento, d.codigo AS departamento_codigo
    FROM asignaturas a
    LEFT JOIN departamentos d ON d.id = a.departamento_id
    WHERE a.codigo = $1
  `, [codigo]);

  if (resMateria.rows.length === 0) return null;
  const materia = resMateria.rows[0];

  // Agrupamientos asociados
  const resAgrups = await query(`
    SELECT ag.id, ag.codigo_agrupamiento, ag.codigo_planes, ag.denominacion
    FROM agrupamientos ag
    JOIN agrupamiento_asignaturas aa ON aa.agrupamiento_id = ag.id
    WHERE aa.asignatura_id = $1
  `, [materia.id]);

  // Historial de planificaciones
  const resPlanis = await query(`
    SELECT 
      pl.id,
      p.codigo AS periodo,
      p.anio,
      p.cuatrimestre,
      doc.nombre_completo AS docente_responsable,
      doc.email AS docente_email,
      pl.completa,
      pl.drive_file_link,
      pl.cantidad_declarada,
      ag.codigo_agrupamiento,
      ag.denominacion AS agrupamiento_nombre,
      COUNT(m.id) AS total_materiales
    FROM planificaciones_periodo pl
    JOIN periodos p ON p.id = pl.periodo_id
    JOIN agrupamientos ag ON ag.id = pl.agrupamiento_id
    JOIN agrupamiento_asignaturas aa ON aa.agrupamiento_id = ag.id
    LEFT JOIN docentes doc ON doc.id = pl.docente_responsable_id
    LEFT JOIN materiales_estudio m ON m.planificacion_periodo_id = pl.id
    WHERE aa.asignatura_id = $1
    GROUP BY pl.id, p.codigo, p.anio, p.cuatrimestre, doc.nombre_completo, doc.email, pl.completa, pl.drive_file_link, pl.cantidad_declarada, ag.codigo_agrupamiento, ag.denominacion
    ORDER BY p.anio DESC, p.cuatrimestre DESC
  `, [materia.id]);

  // Materiales de estudio
  const resMateriales = await query(`
    SELECT 
      m.id,
      m.titulo,
      m.autores,
      m.isbn,
      m.anio_edicion,
      m.tipo_material,
      m.informacion_adicional,
      m.modalidad_acceso,
      p.codigo AS periodo,
      ag.codigo_agrupamiento,
      doc.nombre_completo AS docente_responsable
    FROM materiales_estudio m
    JOIN planificaciones_periodo pl ON pl.id = m.planificacion_periodo_id
    JOIN periodos p ON p.id = pl.periodo_id
    JOIN agrupamientos ag ON ag.id = pl.agrupamiento_id
    JOIN agrupamiento_asignaturas aa ON aa.agrupamiento_id = ag.id
    LEFT JOIN docentes doc ON doc.id = pl.docente_responsable_id
    WHERE aa.asignatura_id = $1
    ORDER BY p.anio DESC, p.cuatrimestre DESC, m.tipo_material, m.titulo
  `, [materia.id]);

  return {
    ...materia,
    agrupamientos: resAgrups.rows,
    planificaciones: resPlanis.rows,
    materiales: resMateriales.rows,
  };
}

// 7. Búsqueda y filtrado general de materiales
export async function searchMateriales(filters: {
  q?: string;
  depto?: string;
  periodo?: string;
  tipo?: string;
  codigoAsig?: string;
  limit?: number;
}) {
  const { q, depto, periodo, tipo, codigoAsig, limit = 50 } = filters;
  const whereClauses: string[] = [];
  const params: any[] = [];
  let paramIdx = 1;

  if (q && q.trim()) {
    whereClauses.push(`(
      m.titulo ILIKE $${paramIdx} OR 
      m.autores ILIKE $${paramIdx} OR 
      COALESCE(m.isbn, '') ILIKE $${paramIdx} OR 
      COALESCE(m.informacion_adicional, '') ILIKE $${paramIdx} OR
      ag.denominacion ILIKE $${paramIdx} OR
      COALESCE(asig.nombre, '') ILIKE $${paramIdx}
    )`);
    params.push(`%${q.trim()}%`);
    paramIdx++;
  }

  if (depto && depto !== 'ALL') {
    whereClauses.push(`dep.codigo = $${paramIdx}`);
    params.push(depto);
    paramIdx++;
  }

  if (periodo && periodo !== 'ALL') {
    whereClauses.push(`p.codigo = $${paramIdx}`);
    params.push(periodo);
    paramIdx++;
  }

  if (tipo && tipo !== 'ALL') {
    whereClauses.push(`m.tipo_material = $${paramIdx}`);
    params.push(tipo);
    paramIdx++;
  }

  if (codigoAsig) {
    whereClauses.push(`asig.codigo = $${paramIdx}`);
    params.push(codigoAsig);
    paramIdx++;
  }

  const whereSql = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

  const sql = `
    SELECT 
      m.id,
      m.titulo,
      m.autores,
      m.isbn,
      m.anio_edicion,
      m.tipo_material,
      m.informacion_adicional,
      m.modalidad_acceso,
      p.codigo AS periodo,
      p.anio,
      p.cuatrimestre,
      ag.codigo_agrupamiento,
      ag.denominacion AS agrupamiento,
      COALESCE(asig.codigo, ag.codigo_planes) AS materia_codigo,
      COALESCE(asig.nombre, ag.denominacion) AS materia_nombre,
      dep.nombre AS departamento,
      dep.codigo AS departamento_codigo,
      doc.nombre_completo AS docente_responsable,
      doc.email AS docente_email,
      pl.drive_file_link
    FROM materiales_estudio m
    JOIN planificaciones_periodo pl ON pl.id = m.planificacion_periodo_id
    JOIN periodos p ON p.id = pl.periodo_id
    JOIN agrupamientos ag ON ag.id = pl.agrupamiento_id
    LEFT JOIN departamentos dep ON dep.id = ag.departamento_id
    LEFT JOIN docentes doc ON doc.id = pl.docente_responsable_id
    LEFT JOIN LATERAL (
      SELECT as_sub.codigo, as_sub.nombre 
      FROM agrupamiento_asignaturas aa_sub 
      JOIN asignaturas as_sub ON as_sub.id = aa_sub.asignatura_id 
      WHERE aa_sub.agrupamiento_id = ag.id 
      LIMIT 1
    ) asig ON true
    ${whereSql}
    ORDER BY p.anio DESC, p.cuatrimestre DESC, m.tipo_material, m.id
    LIMIT $${paramIdx}
  `;
  params.push(limit);

  const res = await query(sql, params);
  return res.rows;
}

// 8. Planificaciones por Cuatrimestre
export async function getPlanificaciones(filtroPeriodo?: string, filtroDepto?: string) {
  const whereClauses: string[] = [];
  const params: any[] = [];
  let idx = 1;

  if (filtroPeriodo && filtroPeriodo !== 'ALL') {
    whereClauses.push(`p.codigo = $${idx}`);
    params.push(filtroPeriodo);
    idx++;
  }

  if (filtroDepto && filtroDepto !== 'ALL') {
    whereClauses.push(`dep.codigo = $${idx}`);
    params.push(filtroDepto);
    idx++;
  }

  const whereSql = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

  const sql = `
    SELECT 
      pl.id,
      p.codigo AS periodo,
      p.anio,
      p.cuatrimestre,
      ag.codigo_agrupamiento,
      ag.codigo_planes,
      ag.denominacion AS agrupamiento,
      dep.nombre AS departamento,
      dep.codigo AS departamento_codigo,
      doc.nombre_completo AS docente_responsable,
      doc.email AS docente_email,
      pl.completa,
      pl.drive_file_link,
      pl.cantidad_declarada,
      COUNT(m.id) AS total_materiales_reales
    FROM planificaciones_periodo pl
    JOIN periodos p ON p.id = pl.periodo_id
    JOIN agrupamientos ag ON ag.id = pl.agrupamiento_id
    LEFT JOIN departamentos dep ON dep.id = ag.departamento_id
    LEFT JOIN docentes doc ON doc.id = pl.docente_responsable_id
    LEFT JOIN materiales_estudio m ON m.planificacion_periodo_id = pl.id
    ${whereSql}
    GROUP BY pl.id, p.codigo, p.anio, p.cuatrimestre, ag.codigo_agrupamiento, ag.codigo_planes, ag.denominacion, dep.nombre, dep.codigo, doc.nombre_completo, doc.email, pl.completa, pl.drive_file_link, pl.cantidad_declarada
    ORDER BY p.anio DESC, p.cuatrimestre DESC, dep.nombre, ag.codigo_agrupamiento
  `;
  const res = await query(sql, params);
  return res.rows;
}
