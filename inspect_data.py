import re
import json

sheets = [
    ("MATEST 2026 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/120/content.md"),
    ("MATEST 2025 2C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/126/content.md"),
    ("MATEST 2025 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/128/content.md"),
    ("MATEST 2024 2C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/130/content.md"),
    ("MATEST 2024 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/132/content.md"),
    ("MATEST 2023 2C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/134/content.md"),
    ("MATEST 2023 1C", "/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/136/content.md")
]

all_records = []

for name, path in sheets:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    parsed = []
    for r in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)
        cleaned = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        parsed.append(cleaned)
    
    # Headers in row 1
    raw_headers = parsed[1] if len(parsed) > 1 else []
    # Find columns index
    # Data rows start at row index 3
    for r in parsed[2:]:
        if len(r) > 2 and r[1].startswith('AGPLA'):
            all_records.append({
                "sheet": name,
                "row_num": r[0] if len(r) > 0 else "",
                "id_agrup_plani": r[1] if len(r) > 1 else "",
                "id": r[2] if len(r) > 2 else "",
                "completa_si_no": r[3] if len(r) > 3 else "",
                "agrupamiento": r[4] if len(r) > 4 else "",
                "departamento": r[5] if len(r) > 5 else "",
                "codigo_asignatura": r[6] if len(r) > 6 else "",
                "asignatura": r[7] if len(r) > 7 else "",
                "docente_responsable": r[8] if len(r) > 8 else "",
                "email": r[9] if len(r) > 9 else "",
                "nombre_agrupamiento": r[10] if len(r) > 10 else "",
                "file_link": r[11] if len(r) > 11 else "",
                "titulo": r[12] if len(r) > 12 else "",
                "autores": r[13] if len(r) > 13 else "",
                "isbn": r[14] if len(r) > 14 else "",
                "anio_edicion": r[15] if len(r) > 15 else "",
                "info_adicional": r[16] if len(r) > 16 else "",
                "modalidad_acceso": r[17] if len(r) > 17 else "",
                "aux_cantidad": r[18] if len(r) > 18 else "",
                "anio_cuat": r[19] if len(r) > 19 else ""
            })

print(f"Total total de registros recolectados de las 7 pestañas: {len(all_records)}")

# Let's inspect unique departments, subjects, docentes, periods, etc.
periods = set(r['anio_cuat'] for r in all_records if r['anio_cuat'])
print("Períodos (AÑO CUAT):", sorted(periods))

depts = set(r['departamento'] for r in all_records if r['departamento'])
print("Departamentos:", depts)

docentes = set((r['docente_responsable'], r['email']) for r in all_records if r['docente_responsable'])
print(f"Docentes únicos ({len(docentes)}):")
for doc, em in sorted(docentes):
    print(f"  - {doc} ({em})")

asignaturas = set((r['codigo_asignatura'], r['asignatura'], r['departamento']) for r in all_records if r['codigo_asignatura'])
print(f"Asignaturas únicas ({len(asignaturas)}):")
for cod, nom, dep in sorted(asignaturas):
    print(f"  - [{dep}] {cod}: {nom}")

agrupamientos = set((r['id_agrup_plani'], r['nombre_agrupamiento']) for r in all_records if r['id_agrup_plani'])
print(f"Agrupamientos únicos ({len(agrupamientos)}):")
for id_ag, nom_ag in sorted(agrupamientos):
    print(f"  - {id_ag}: {nom_ag}")

# Sample records to inspect file_link, modalidad_acceso, titulo
print("\nEjemplo de 3 registros con material cargado:")
con_material = [r for r in all_records if r['titulo']]
print(f"Registros con título de material: {len(con_material)}")
for r in con_material[:3]:
    print(json.dumps(r, indent=2, ensure_ascii=False))
