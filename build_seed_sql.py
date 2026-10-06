import re
import html

sheets = [
    ("MATEST 2026 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/120/content.md"),
    ("MATEST 2025 2C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/126/content.md"),
    ("MATEST 2025 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/128/content.md"),
    ("MATEST 2024 2C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/130/content.md"),
    ("MATEST 2024 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/132/content.md"),
    ("MATEST 2023 2C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/134/content.md"),
    ("MATEST 2023 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/136/content.md")
]

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

departamentos = {
    'MATE': 'Departamento de Matemática',
    'FIS': 'Departamento de Física',
    'QUI': 'Departamento de Química'
}

docentes = {}
periodos = {}
asignaturas = {}
agrupamientos = {}
agrup_asig = set()
planificaciones = {}
materiales = []

for sheet_name, path in sheets:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    parsed = []
    for r in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)
        cleaned = [html.unescape(re.sub(r'<[^>]+>', '', c).strip()) for c in cells]
        parsed.append(cleaned)
    
    for r in parsed[2:]:
        if len(r) > 2 and r[1].startswith('AGPLA'):
            id_agrup = r[1].strip()
            id_planes = r[2].strip() if len(r) > 2 else ''
            completa_str = r[3].strip() if len(r) > 3 else ''
            depto_raw = r[5].strip() if len(r) > 5 else ''
            cod_asig = r[6].strip() if len(r) > 6 else ''
            nom_asig = r[7].strip() if len(r) > 7 else ''
            docente_nom = r[8].strip() if len(r) > 8 else ''
            email = r[9].strip().lower() if len(r) > 9 else ''
            nom_agrup = r[10].strip() if len(r) > 10 else ''
            file_link = r[11].strip() if len(r) > 11 else ''
            titulo = r[12].strip() if len(r) > 12 else ''
            autores = r[13].strip() if len(r) > 13 else ''
            isbn = r[14].strip() if len(r) > 14 else ''
            anio_ed = r[15].strip() if len(r) > 15 else ''
            info_adic = r[16].strip() if len(r) > 16 else ''
            modalidad = r[17].strip() if len(r) > 17 else ''
            aux_cant = r[18].strip() if len(r) > 18 else ''
            periodo_str = r[19].strip() if len(r) > 19 else sheet_name.replace('MATEST ', '')
            
            if not periodo_str:
                periodo_str = sheet_name.replace('MATEST ', '')

            depto_code = 'MATE'
            if 'fís' in depto_raw.lower() or 'fis' in depto_raw.lower():
                depto_code = 'FIS'
            elif 'quím' in depto_raw.lower() or 'qui' in depto_raw.lower():
                depto_code = 'QUI'
            elif 'mate' in depto_raw.lower():
                depto_code = 'MATE'
            elif id_agrup in ('AGPLA0018', 'AGPLA0019', 'AGPLA0024', 'AGPLA0025', 'AGPLA0027', 'AGPLA0036'):
                depto_code = 'FIS'
            
            parts = periodo_str.split()
            anio = int(parts[0]) if parts and parts[0].isdigit() else 2026
            cuat = parts[1] if len(parts) > 1 else '1C'
            periodos[periodo_str] = {'codigo': periodo_str, 'anio': anio, 'cuatrimestre': cuat}
            
            if email and email.endswith('@fi.uba.ar'):
                if email not in docentes or (len(docente_nom) > len(docentes[email]['nombre'])):
                    docentes[email] = {'nombre': docente_nom, 'email': email}
            
            if cod_asig and nom_asig:
                if cod_asig not in asignaturas or len(nom_asig) > len(asignaturas[cod_asig]['nombre']):
                    asignaturas[cod_asig] = {'codigo': cod_asig, 'nombre': nom_asig, 'depto': depto_code}
            
            if not nom_agrup:
                nom_agrup = f"{id_planes} - {nom_asig}" if nom_asig else id_planes
            if id_agrup not in agrupamientos or len(nom_agrup) > len(agrupamientos[id_agrup]['denominacion']):
                agrupamientos[id_agrup] = {
                    'codigo': id_agrup,
                    'codigo_planes': id_planes,
                    'denominacion': nom_agrup,
                    'depto': depto_code
                }
            
            if cod_asig:
                agrup_asig.add((id_agrup, cod_asig))
            for sub_code in id_planes.replace('/', '-').split('-'):
                sub_code = sub_code.strip()
                if sub_code and len(sub_code) >= 4 and sub_code in asignaturas:
                    agrup_asig.add((id_agrup, sub_code))
            
            plan_key = (id_agrup, periodo_str)
            cant_int = int(aux_cant) if aux_cant.isdigit() else 0
            is_completa = True if completa_str.lower() in ('si', 'sí', 'true', '1') or cant_int > 0 or bool(titulo) else False
            
            if plan_key not in planificaciones:
                planificaciones[plan_key] = {
                    'id_agrup': id_agrup,
                    'periodo': periodo_str,
                    'docente_email': email,
                    'completa': is_completa,
                    'file_link': file_link,
                    'cant_declarada': cant_int
                }
            else:
                if is_completa:
                    planificaciones[plan_key]['completa'] = True
                if file_link and not planificaciones[plan_key]['file_link']:
                    planificaciones[plan_key]['file_link'] = file_link
                if cant_int > planificaciones[plan_key]['cant_declarada']:
                    planificaciones[plan_key]['cant_declarada'] = cant_int
                if email and not planificaciones[plan_key]['docente_email']:
                    planificaciones[plan_key]['docente_email'] = email
            
            if titulo and titulo != '0':
                materiales.append({
                    'id_agrup': id_agrup,
                    'periodo': periodo_str,
                    'titulo': titulo,
                    'autores': autores,
                    'isbn': isbn,
                    'anio_edicion': anio_ed,
                    'tipo_material': infer_tipo(titulo, info_adic),
                    'info_adicional': info_adic,
                    'modalidad_acceso': modalidad
                })

sql_lines = [
    "-- ============================================================",
    "-- POBLADO DE DATOS (SEED DATA) NORMALIZADOS",
    "-- ============================================================",
    "BEGIN;",
    "",
    "-- 1. Departamentos"
]

for cod, nom in departamentos.items():
    sql_lines.append(f"INSERT INTO departamentos (codigo, nombre) VALUES ('{cod}', '{nom}') ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre;")

sql_lines.append("\n-- 2. Periodos")
for cod, p in sorted(periodos.items(), key=lambda x: (x[1]['anio'], x[1]['cuatrimestre'])):
    sql_lines.append(f"INSERT INTO periodos (codigo, anio, cuatrimestre) VALUES ('{p['codigo']}', {p['anio']}, '{p['cuatrimestre']}') ON CONFLICT (codigo) DO NOTHING;")

sql_lines.append("\n-- 3. Docentes")
for em, d in sorted(docentes.items()):
    nom_sql = sql_str(d['nombre'])
    sql_lines.append(f"INSERT INTO docentes (nombre_completo, email) VALUES ({nom_sql}, '{em}') ON CONFLICT (email) DO UPDATE SET nombre_completo = EXCLUDED.nombre_completo;")

sql_lines.append("\n-- 4. Asignaturas")
for cod, a in sorted(asignaturas.items()):
    nom_sql = sql_str(a['nombre'])
    sql_lines.append(f"INSERT INTO asignaturas (codigo, nombre, departamento_id) VALUES ('{cod}', {nom_sql}, (SELECT id FROM departamentos WHERE codigo = '{a['depto']}')) ON CONFLICT (codigo) DO UPDATE SET nombre = EXCLUDED.nombre;")

sql_lines.append("\n-- 5. Agrupamientos")
for cod, ag in sorted(agrupamientos.items()):
    denom_sql = sql_str(ag['denominacion'])
    planes_sql = sql_str(ag['codigo_planes'])
    sql_lines.append(f"INSERT INTO agrupamientos (codigo_agrupamiento, codigo_planes, denominacion, departamento_id) VALUES ('{cod}', {planes_sql}, {denom_sql}, (SELECT id FROM departamentos WHERE codigo = '{ag['depto']}')) ON CONFLICT (codigo_agrupamiento) DO UPDATE SET denominacion = EXCLUDED.denominacion, codigo_planes = EXCLUDED.codigo_planes;")

sql_lines.append("\n-- 6. Agrupamiento <-> Asignaturas")
for id_ag, cod_as in sorted(agrup_asig):
    sql_lines.append(f"INSERT INTO agrupamiento_asignaturas (agrupamiento_id, asignatura_id) VALUES ((SELECT id FROM agrupamientos WHERE codigo_agrupamiento = '{id_ag}'), (SELECT id FROM asignaturas WHERE codigo = '{cod_as}')) ON CONFLICT DO NOTHING;")

sql_lines.append("\n-- 7. Planificaciones por Periodo")
for key, plan in sorted(planificaciones.items()):
    id_ag = plan['id_agrup']
    per = plan['periodo']
    comp_sql = 'TRUE' if plan['completa'] else 'FALSE'
    link_sql = sql_str(plan['file_link'])
    cant = plan['cant_declarada']
    doc_subquery = f"(SELECT id FROM docentes WHERE email = '{plan['docente_email']}')" if plan['docente_email'] else "NULL"
    
    sql_lines.append(
        f"INSERT INTO planificaciones_periodo (agrupamiento_id, periodo_id, docente_responsable_id, completa, drive_file_link, cantidad_declarada) "
        f"VALUES ((SELECT id FROM agrupamientos WHERE codigo_agrupamiento = '{id_ag}'), (SELECT id FROM periodos WHERE codigo = '{per}'), {doc_subquery}, {comp_sql}, {link_sql}, {cant}) "
        f"ON CONFLICT (agrupamiento_id, periodo_id) DO UPDATE SET completa = EXCLUDED.completa, drive_file_link = COALESCE(EXCLUDED.drive_file_link, planificaciones_periodo.drive_file_link), cantidad_declarada = EXCLUDED.cantidad_declarada;"
    )

sql_lines.append("\n-- 8. Materiales de Estudio")
for m in materiales:
    id_ag = m['id_agrup']
    per = m['periodo']
    tit_sql = sql_str(m['titulo'])
    aut_sql = sql_str(m['autores'])
    isbn_sql = sql_str(m['isbn'])
    anio_sql = sql_str(m['anio_edicion'])
    tipo_sql = sql_str(m['tipo_material'])
    info_sql = sql_str(m['info_adicional'])
    mod_sql = sql_str(m['modalidad_acceso'])
    
    plan_subquery = f"(SELECT id FROM planificaciones_periodo WHERE agrupamiento_id = (SELECT id FROM agrupamientos WHERE codigo_agrupamiento = '{id_ag}') AND periodo_id = (SELECT id FROM periodos WHERE codigo = '{per}'))"
    sql_lines.append(
        f"INSERT INTO materiales_estudio (planificacion_periodo_id, titulo, autores, isbn, anio_edicion, tipo_material, informacion_adicional, modalidad_acceso) "
        f"VALUES ({plan_subquery}, {tit_sql}, {aut_sql}, {isbn_sql}, {anio_sql}, {tipo_sql}, {info_sql}, {mod_sql});"
    )

sql_lines.append("\nCOMMIT;")

with open('seed_data.sql', 'w', encoding='utf-8') as f:
    f.write("\n".join(sql_lines))

print(f"seed_data.sql generado con exito con {len(sql_lines)} lineas!")
