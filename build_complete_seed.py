import csv
import glob
import re
import html

# 1. Canonical departments
departamentos = {
    'MATE': 'Departamento de Matemática',
    'FIS': 'Departamento de Física',
    'QUI': 'Departamento de Química',
    'COMP': 'Departamento de Computación',
    'ELEC': 'Departamento de Electrónica',
    'ENER': 'Departamento de Energía',
    'ESTA': 'Departamento de Estabilidad',
    'GEST': 'Departamento de Gestión',
    'AGRI': 'Departamento de Agrimensura',
    'MECA': 'Departamento de Ingeniería Mecánica',
    'IQUI': 'Departamento de Ingeniería Química',
    'TIND': 'Departamento de Tecnología Industrial',
    'NAVA': 'Departamento de Ingeniería Naval',
    'CONS': 'Departamento de Construcciones y Estructuras',
    'HIDR': 'Departamento de Hidráulica',
    'TRAN': 'Departamento de Transporte',
    'IDIO': 'Departamento de Idiomas',
    'STAM': 'Departamento de Seguridad del Trabajo y Ambiente',
    'FCEN': 'Facultad de Ciencias Exactas y Naturales (FCEN)',
    'FFYB': 'Facultad de Farmacia y Bioquímica (FFyB)',
    'FAUBA': 'Facultad de Agronomía (FAUBA)'
}

dept_map = {
    'matemática': 'MATE', 'mate': 'MATE',
    'física': 'FIS', 'fisi': 'FIS', 'fis': 'FIS',
    'química': 'QUI', 'quim': 'QUI', 'qui': 'QUI',
    'computación': 'COMP', 'comp': 'COMP',
    'electrónica': 'ELEC', 'elec': 'ELEC',
    'energía': 'ENER', 'ener': 'ENER',
    'estabilidad': 'ESTA', 'esta': 'ESTA',
    'gestión': 'GEST', 'gest': 'GEST',
    'agrimensura': 'AGRI', 'agri': 'AGRI',
    'ingeniería mecánica': 'MECA', 'mecánica': 'MECA', 'meca': 'MECA',
    'ingeniería química': 'IQUI', 'iqui': 'IQUI',
    'tecnología industrial': 'TIND', 'tecnologia industrial': 'TIND', 'tind': 'TIND',
    'ingeniería naval': 'NAVA', 'nava': 'NAVA',
    'construcciones y estructuras': 'CONS', 'cons': 'CONS',
    'hidráulica': 'HIDR', 'hidraulica': 'HIDR', 'hidr': 'HIDR',
    'transporte': 'TRAN', 'tran': 'TRAN',
    'idiomas': 'IDIO', 'idio': 'IDIO',
    'seguridad del trabajo y ambiente': 'STAM', 'seguridad trabajo y ambiente': 'STAM', 'seguridad de trabajo y ambiente': 'STAM', 'stam': 'STAM',
    'fcen': 'FCEN',
    'ffyb': 'FFYB',
    'fauba': 'FAUBA'
}

def clean_dept(raw):
    raw_lower = raw.lower().strip()
    return dept_map.get(raw_lower, 'MATE')

def sql_str(val):
    if val is None:
        return 'NULL'
    val = html.unescape(str(val)).strip()
    if val == '' or val == '0':
        return 'NULL'
    escaped = val.replace("'", "''")
    return f"'{escaped}'"

def infer_tipo(titulo, info):
    t = (titulo + " " + info).lower()
    if 'libro' in t or 'capítulo' in t or 'edición' in t or 'isbn' in t:
        return 'Libro / Capítulo'
    elif 'guía' in t or 'guia' in t or 'prácticos' in t:
        return 'Guía de TP / Problemas'
    elif 'apunte' in t or 'notas de clase' in t or 'borradores' in t:
        return 'Apuntes de Cátedra'
    elif 'video' in t or 'clases teóricas' in t or 'clases prácticas' in t:
        return 'Video / Multimedia'
    elif 'aula virtual' in t or 'campus' in t:
        return 'Aula Virtual'
    elif 'parcial' in t or 'examen' in t or 'integrador' in t:
        return 'Exámenes / Evaluaciones'
    elif 'diapositiva' in t or 'presentaci' in t:
        return 'Presentación'
    return 'Material Complementario'

# Periodos
periodos_dict = {
    '2023 1C': {'codigo': '2023 1C', 'anio': 2023, 'cuatrimestre': '1C'},
    '2023 2C': {'codigo': '2023 2C', 'anio': 2023, 'cuatrimestre': '2C'},
    '2024 1C': {'codigo': '2024 1C', 'anio': 2024, 'cuatrimestre': '1C'},
    '2024 2C': {'codigo': '2024 2C', 'anio': 2024, 'cuatrimestre': '2C'},
    '2025 1C': {'codigo': '2025 1C', 'anio': 2025, 'cuatrimestre': '1C'},
    '2025 2C': {'codigo': '2025 2C', 'anio': 2025, 'cuatrimestre': '2C'},
    '2026 1C': {'codigo': '2026 1C', 'anio': 2026, 'cuatrimestre': '1C'},
}

docentes = {} # email -> {nombre, email}
asignaturas = {} # cod -> {codigo, nombre, depto}
agrupamientos = {} # id_agrup -> {codigo, codigo_planes, denominacion, depto}
agrup_asig = set() # (id_agrup, cod_asig)
planificaciones = {} # (id_agrup, periodo) -> {...}
materiales = []

print("1. Parsing Historial_Agrup_Planis.csv...")
with open('raw_csvs/Historial_Agrup_Planis.csv', mode='r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        id_agr = r.get('ID Agrupamiento PLANI', '').strip()
        cod_as = r.get('Código Asignatura', '').strip()
        nom_as = r.get('Denominación Asignatura', '').strip()
        planes = r.get('Agrupamiento', '').strip()
        denom = r.get('Código y Denominación agrupamiento', '').strip()
        depto_raw = r.get('Departamento', '').strip()
        depto_code = clean_dept(depto_raw)

        if cod_as and nom_as:
            if cod_as not in asignaturas or len(nom_as) > len(asignaturas[cod_as]['nombre']):
                asignaturas[cod_as] = {'codigo': cod_as, 'nombre': nom_as, 'depto': depto_code}

        if id_agr:
            if id_agr not in agrupamientos or len(denom) > len(agrupamientos[id_agr]['denominacion']):
                agrupamientos[id_agr] = {
                    'codigo': id_agr,
                    'codigo_planes': planes,
                    'denominacion': denom if denom else f"{planes} - {nom_as}",
                    'depto': depto_code
                }
            if cod_as:
                agrup_asig.add((id_agr, cod_as))

print(f"   Historial loaded: {len(agrupamientos)} agrupamientos, {len(asignaturas)} asignaturas.")

print("2. Parsing semester CSVs for planificaciones...")
for fpath in sorted(glob.glob('raw_csvs/MATEST_*.csv')):
    with open(fpath, mode='r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for r in reader:
            id_agr = r.get('ID AGRUP PLANI', '').strip()
            per = r.get('AÑO CUAT', '').strip()
            if not id_agr or not per:
                continue
            
            depto_raw = r.get('DEPARTAMENTO DOCENTE', '').strip()
            depto_code = clean_dept(depto_raw) if depto_raw else None
            
            doc_nom = r.get('DOCENTE RESPONSABLE SIN CARGO', '').strip()
            email = r.get('E-Mail', '').strip().lower()
            if not email and doc_nom:
                slug = re.sub(r'[^a-z0-9]', '', doc_nom.lower())
                email = f"{slug}@docente.fi.uba.ar"

            if email:
                if email not in docentes or (len(doc_nom) > len(docentes[email]['nombre'])):
                    docentes[email] = {'nombre': doc_nom if doc_nom else email, 'email': email}

            comp_str = r.get('COMPLETA SI/NO', '').strip().lower()
            link = r.get('[Document Studio] File Link', '').strip()
            cant_str = r.get('AUX Contar cantidad de material de estudio cargado', '').strip()
            cant = int(cant_str) if cant_str.isdigit() else 0
            is_comp = comp_str in ('si', 'sí', 'true', '1') or cant > 0 or bool(link)

            # Asignatura & Agrupamiento checks
            cod_as = r.get('CÓDIGO ASIGNATURA', '').strip()
            nom_as = r.get('ASIGNATURA', '').strip()
            id_planes = r.get('AGRUPAMIENTO', '').strip() or r.get('ID', '').strip()
            nom_agr = r.get('Nombre agrupamiento', '').strip()

            if cod_as and nom_as and cod_as not in asignaturas:
                asignaturas[cod_as] = {'codigo': cod_as, 'nombre': nom_as, 'depto': depto_code or 'MATE'}
            if id_agr not in agrupamientos:
                agrupamientos[id_agr] = {
                    'codigo': id_agr,
                    'codigo_planes': id_planes,
                    'denominacion': nom_agr if nom_agr else f"{id_planes} - {nom_as}",
                    'depto': depto_code or 'MATE'
                }
            if cod_as:
                agrup_asig.add((id_agr, cod_as))

            k = (id_agr, per)
            if k not in planificaciones:
                planificaciones[k] = {
                    'id_agrup': id_agr,
                    'periodo': per,
                    'docente_email': email,
                    'completa': is_comp,
                    'link': link,
                    'cant': cant
                }
            else:
                if is_comp:
                    planificaciones[k]['completa'] = True
                if link and not planificaciones[k]['link']:
                    planificaciones[k]['link'] = link
                if cant > planificaciones[k]['cant']:
                    planificaciones[k]['cant'] = cant
                if email and not planificaciones[k]['docente_email']:
                    planificaciones[k]['docente_email'] = email

print(f"   Semester planificaciones: {len(planificaciones)} entries.")

print("3. Parsing TODOS.csv for materials and updates...")
with open('raw_csvs/TODOS.csv', mode='r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
    for r in reader:
        id_agr = r.get('ID AGRUP PLANI', '').strip()
        per = r.get('AÑO CUAT', '').strip()
        if not id_agr:
            continue

        depto_raw = r.get('DEPARTAMENTO DOCENTE', '').strip()
        depto_code = clean_dept(depto_raw) if depto_raw else None
        
        cod_as = r.get('CÓDIGO ASIGNATURA', '').strip()
        nom_as = r.get('ASIGNATURA', '').strip()
        id_planes = r.get('AGRUPAMIENTO', '').strip() or r.get('ID', '').strip()
        nom_agr = r.get('Nombre agrupamiento', '').strip()

        if cod_as and nom_as and (cod_as not in asignaturas or len(nom_as) > len(asignaturas[cod_as]['nombre'])):
            asignaturas[cod_as] = {'codigo': cod_as, 'nombre': nom_as, 'depto': depto_code or 'MATE'}

        if id_agr not in agrupamientos:
            agrupamientos[id_agr] = {
                'codigo': id_agr,
                'codigo_planes': id_planes,
                'denominacion': nom_agr if nom_agr else f"{id_planes} - {nom_as}",
                'depto': depto_code or 'MATE'
            }
        if cod_as:
            agrup_asig.add((id_agr, cod_as))

        doc_nom = r.get('DOCENTE RESPONSABLE SIN CARGO', '').strip()
        email = r.get('E-Mail', '').strip().lower()
        if not email and doc_nom:
            slug = re.sub(r'[^a-z0-9]', '', doc_nom.lower())
            email = f"{slug}@docente.fi.uba.ar"

        if email:
            if email not in docentes or (len(doc_nom) > len(docentes[email]['nombre'])):
                docentes[email] = {'nombre': doc_nom if doc_nom else email, 'email': email}

        link = r.get('[Document Studio] File Link', '').strip()
        comp_str = r.get('COMPLETA SI/NO', '').strip().lower()
        cant_str = r.get('CANTIDAD', '').strip()
        cant = int(cant_str) if cant_str.isdigit() else 0

        titulo = r.get('TITULO', '').strip()
        is_comp = comp_str in ('si', 'sí', 'true', '1') or cant > 0 or bool(link) or bool(titulo and titulo != '0')

        if per:
            k = (id_agr, per)
            if k not in planificaciones:
                planificaciones[k] = {
                    'id_agrup': id_agr,
                    'periodo': per,
                    'docente_email': email,
                    'completa': is_comp,
                    'link': link,
                    'cant': cant
                }
            else:
                if is_comp:
                    planificaciones[k]['completa'] = True
                if link and not planificaciones[k]['link']:
                    planificaciones[k]['link'] = link
                if cant > planificaciones[k]['cant']:
                    planificaciones[k]['cant'] = cant
                if email and not planificaciones[k]['docente_email']:
                    planificaciones[k]['docente_email'] = email

        if titulo and titulo != '0' and per:
            autores = r.get('AUTOR/ES', '').strip()
            # handle newline in header for ISBN
            isbn = r.get('ISBN\n(Código identificador único para libros)', '').strip() or r.get('ISBN', '').strip()
            anio_ed = r.get('AÑO DE ÚLTIMA EDICIÓN', '').strip()
            info_adic = r.get('INFORMACIÓN ADICIONAL', '').strip()
            modalidad = r.get('MODALIDAD DE ACCESO\n(Indicar link)', '').strip() or r.get('MODALIDAD DE ACCESO', '').strip()

            materiales.append({
                'id_agrup': id_agr,
                'periodo': per,
                'titulo': titulo,
                'autores': autores,
                'isbn': isbn,
                'anio_edicion': anio_ed,
                'tipo_material': infer_tipo(titulo, info_adic),
                'info_adicional': info_adic,
                'modalidad_acceso': modalidad
            })

print(f"Total docentes: {len(docentes)}")
print(f"Total asignaturas: {len(asignaturas)}")
print(f"Total agrupamientos: {len(agrupamientos)}")
print(f"Total planificaciones: {len(planificaciones)}")
print(f"Total materiales de estudio: {len(materiales)}")

# Generate SQL
sql_lines = [
    "-- ============================================================",
    "-- BASE DE DATOS: material_estudio",
    "-- ESQUEMA Y CARGA COMPLETA (3FN)",
    "-- ============================================================",
    "BEGIN;",
    "",
    "DROP TABLE IF EXISTS materiales_estudio CASCADE;",
    "DROP TABLE IF EXISTS planificaciones_periodo CASCADE;",
    "DROP TABLE IF EXISTS agrupamiento_asignaturas CASCADE;",
    "DROP TABLE IF EXISTS agrupamientos CASCADE;",
    "DROP TABLE IF EXISTS asignaturas CASCADE;",
    "DROP TABLE IF EXISTS periodos CASCADE;",
    "DROP TABLE IF EXISTS docentes CASCADE;",
    "DROP TABLE IF EXISTS departamentos CASCADE;",
    "",
    "CREATE TABLE departamentos (",
    "    id SERIAL PRIMARY KEY,",
    "    codigo VARCHAR(20) UNIQUE NOT NULL,",
    "    nombre VARCHAR(150) NOT NULL",
    ");",
    "",
    "CREATE TABLE docentes (",
    "    id SERIAL PRIMARY KEY,",
    "    nombre_completo VARCHAR(255) NOT NULL,",
    "    email VARCHAR(255) UNIQUE NOT NULL,",
    "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ");",
    "",
    "CREATE TABLE periodos (",
    "    id SERIAL PRIMARY KEY,",
    "    codigo VARCHAR(20) UNIQUE NOT NULL,",
    "    anio INT NOT NULL,",
    "    cuatrimestre VARCHAR(10) NOT NULL",
    ");",
    "",
    "CREATE TABLE asignaturas (",
    "    id SERIAL PRIMARY KEY,",
    "    codigo VARCHAR(30) UNIQUE NOT NULL,",
    "    nombre VARCHAR(255) NOT NULL,",
    "    departamento_id INT REFERENCES departamentos(id) ON DELETE SET NULL",
    ");",
    "",
    "CREATE TABLE agrupamientos (",
    "    id SERIAL PRIMARY KEY,",
    "    codigo_agrupamiento VARCHAR(30) UNIQUE NOT NULL,",
    "    codigo_planes TEXT,",
    "    denominacion TEXT NOT NULL,",
    "    departamento_id INT REFERENCES departamentos(id) ON DELETE SET NULL",
    ");",
    "",
    "CREATE TABLE agrupamiento_asignaturas (",
    "    agrupamiento_id INT REFERENCES agrupamientos(id) ON DELETE CASCADE,",
    "    asignatura_id INT REFERENCES asignaturas(id) ON DELETE CASCADE,",
    "    PRIMARY KEY (agrupamiento_id, asignatura_id)",
    ");",
    "",
    "CREATE TABLE planificaciones_periodo (",
    "    id SERIAL PRIMARY KEY,",
    "    agrupamiento_id INT REFERENCES agrupamientos(id) ON DELETE CASCADE,",
    "    periodo_id INT REFERENCES periodos(id) ON DELETE CASCADE,",
    "    docente_responsable_id INT REFERENCES docentes(id) ON DELETE SET NULL,",
    "    completa BOOLEAN DEFAULT FALSE,",
    "    drive_file_link TEXT,",
    "    cantidad_declarada INT DEFAULT 0,",
    "    UNIQUE (agrupamiento_id, periodo_id)",
    ");",
    "",
    "CREATE TABLE materiales_estudio (",
    "    id SERIAL PRIMARY KEY,",
    "    planificacion_periodo_id INT REFERENCES planificaciones_periodo(id) ON DELETE CASCADE,",
    "    titulo TEXT NOT NULL,",
    "    autores TEXT,",
    "    isbn TEXT,",
    "    anio_edicion TEXT,",
    "    tipo_material TEXT,",
    "    informacion_adicional TEXT,",
    "    modalidad_acceso TEXT,",
    "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    ");",
    "",
    "CREATE INDEX idx_asignaturas_codigo ON asignaturas(codigo);",
    "CREATE INDEX idx_agrupamientos_codigo ON agrupamientos(codigo_agrupamiento);",
    "CREATE INDEX idx_planificaciones_periodo ON planificaciones_periodo(periodo_id, agrupamiento_id);",
    "CREATE INDEX idx_materiales_planificacion ON materiales_estudio(planificacion_periodo_id);",
    "CREATE INDEX idx_materiales_titulo ON materiales_estudio USING gin(to_tsvector('spanish', titulo));",
    "",
    "-- 1. INSERT DEPARTAMENTOS"
]

dept_id_map = {}
for idx, (cod, nom) in enumerate(departamentos.items(), start=1):
    dept_id_map[cod] = idx
    nom_sql = sql_str(nom)
    sql_lines.append(f"INSERT INTO departamentos (id, codigo, nombre) VALUES ({idx}, '{cod}', {nom_sql});")

sql_lines.append("SELECT setval('departamentos_id_seq', (SELECT max(id) FROM departamentos));")

sql_lines.append("\n-- 2. INSERT PERIODOS")
periodo_id_map = {}
for idx, (cod, p) in enumerate(periodos_dict.items(), start=1):
    periodo_id_map[cod] = idx
    sql_lines.append(f"INSERT INTO periodos (id, codigo, anio, cuatrimestre) VALUES ({idx}, '{cod}', {p['anio']}, '{p['cuatrimestre']}');")

sql_lines.append("SELECT setval('periodos_id_seq', (SELECT max(id) FROM periodos));")

sql_lines.append("\n-- 3. INSERT DOCENTES")
docente_id_map = {}
doc_rows = []
for idx, (email, d) in enumerate(sorted(docentes.items()), start=1):
    docente_id_map[email] = idx
    doc_rows.append(f"({idx}, {sql_str(d['nombre'])}, {sql_str(email)})")

# Batch insert docentes in chunks of 500
for i in range(0, len(doc_rows), 500):
    chunk = doc_rows[i:i+500]
    sql_lines.append(f"INSERT INTO docentes (id, nombre_completo, email) VALUES\n" + ",\n".join(chunk) + ";")

sql_lines.append("SELECT setval('docentes_id_seq', (SELECT max(id) FROM docentes));")

sql_lines.append("\n-- 4. INSERT ASIGNATURAS")
asig_id_map = {}
asig_rows = []
for idx, (cod, a) in enumerate(sorted(asignaturas.items()), start=1):
    asig_id_map[cod] = idx
    dept_id = dept_id_map.get(a['depto'], 1)
    asig_rows.append(f"({idx}, {sql_str(cod)}, {sql_str(a['nombre'])}, {dept_id})")

for i in range(0, len(asig_rows), 500):
    chunk = asig_rows[i:i+500]
    sql_lines.append(f"INSERT INTO asignaturas (id, codigo, nombre, departamento_id) VALUES\n" + ",\n".join(chunk) + ";")

sql_lines.append("SELECT setval('asignaturas_id_seq', (SELECT max(id) FROM asignaturas));")

sql_lines.append("\n-- 5. INSERT AGRUPAMIENTOS")
agrup_id_map = {}
agrup_rows = []
for idx, (cod, ag) in enumerate(sorted(agrupamientos.items()), start=1):
    agrup_id_map[cod] = idx
    dept_id = dept_id_map.get(ag['depto'], 1)
    agrup_rows.append(f"({idx}, {sql_str(cod)}, {sql_str(ag['codigo_planes'])}, {sql_str(ag['denominacion'])}, {dept_id})")

for i in range(0, len(agrup_rows), 500):
    chunk = agrup_rows[i:i+500]
    sql_lines.append(f"INSERT INTO agrupamientos (id, codigo_agrupamiento, codigo_planes, denominacion, departamento_id) VALUES\n" + ",\n".join(chunk) + ";")

sql_lines.append("SELECT setval('agrupamientos_id_seq', (SELECT max(id) FROM agrupamientos));")

sql_lines.append("\n-- 6. INSERT AGRUPAMIENTO_ASIGNATURAS")
agrup_asig_rows = []
for (id_agr, cod_as) in sorted(agrup_asig):
    ag_id = agrup_id_map.get(id_agr)
    as_id = asig_id_map.get(cod_as)
    if ag_id and as_id:
        agrup_asig_rows.append(f"({ag_id}, {as_id})")

for i in range(0, len(agrup_asig_rows), 500):
    chunk = agrup_asig_rows[i:i+500]
    sql_lines.append(f"INSERT INTO agrupamiento_asignaturas (agrupamiento_id, asignatura_id) VALUES\n" + ",\n".join(chunk) + " ON CONFLICT DO NOTHING;")

sql_lines.append("\n-- 7. INSERT PLANIFICACIONES_PERIODO")
plan_id_map = {}
plan_rows = []
curr_plan_id = 1
for (id_agr, per), pl in sorted(planificaciones.items()):
    ag_id = agrup_id_map.get(id_agr)
    per_id = periodo_id_map.get(per)
    if not ag_id or not per_id:
        continue
    plan_id_map[(id_agr, per)] = curr_plan_id
    doc_id = docente_id_map.get(pl['docente_email']) if pl['docente_email'] else None
    doc_val = str(doc_id) if doc_id else 'NULL'
    comp_val = 'TRUE' if pl['completa'] else 'FALSE'
    link_val = sql_str(pl['link'])
    cant_val = pl['cant']
    plan_rows.append(f"({curr_plan_id}, {ag_id}, {per_id}, {doc_val}, {comp_val}, {link_val}, {cant_val})")
    curr_plan_id += 1

for i in range(0, len(plan_rows), 500):
    chunk = plan_rows[i:i+500]
    sql_lines.append(f"INSERT INTO planificaciones_periodo (id, agrupamiento_id, periodo_id, docente_responsable_id, completa, drive_file_link, cantidad_declarada) VALUES\n" + ",\n".join(chunk) + ";")

sql_lines.append("SELECT setval('planificaciones_periodo_id_seq', (SELECT max(id) FROM planificaciones_periodo));")

sql_lines.append("\n-- 8. INSERT MATERIALES_ESTUDIO")
mat_rows = []
curr_mat_id = 1
for m in materiales:
    pl_id = plan_id_map.get((m['id_agrup'], m['periodo']))
    if not pl_id:
        continue
    tit_sql = sql_str(m['titulo'])
    aut_sql = sql_str(m['autores'])
    isbn_sql = sql_str(m['isbn'])
    anio_sql = sql_str(m['anio_edicion'])
    tipo_sql = sql_str(m['tipo_material'])
    info_sql = sql_str(m['info_adicional'])
    mod_sql = sql_str(m['modalidad_acceso'])
    mat_rows.append(f"({curr_mat_id}, {pl_id}, {tit_sql}, {aut_sql}, {isbn_sql}, {anio_sql}, {tipo_sql}, {info_sql}, {mod_sql})")
    curr_mat_id += 1

for i in range(0, len(mat_rows), 500):
    chunk = mat_rows[i:i+500]
    sql_lines.append(f"INSERT INTO materiales_estudio (id, planificacion_periodo_id, titulo, autores, isbn, anio_edicion, tipo_material, informacion_adicional, modalidad_acceso) VALUES\n" + ",\n".join(chunk) + ";")

sql_lines.append("SELECT setval('materiales_estudio_id_seq', (SELECT max(id) FROM materiales_estudio));")

sql_lines.append("\nCOMMIT;")

with open('seed_data.sql', 'w', encoding='utf-8') as f:
    f.write("\n".join(sql_lines))

print(f"seed_data.sql successfully written with {len(sql_lines)} lines!")
print(f"Total inserted materiales: {len(mat_rows)}")
print(f"Total inserted planificaciones: {len(plan_rows)}")
