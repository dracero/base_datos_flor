import re
import csv
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

for name, path in sheets:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    parsed = []
    for r in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)
        cleaned = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        parsed.append(cleaned)
    
    header = [c for c in parsed[1] if c] if len(parsed) > 1 else []
    # count non-empty data rows
    data_rows = [r for r in parsed[2:] if any(r) and len(r) > 2 and r[1].startswith('AGPLA')]
    print(f"[{name}] Total table rows: {len(parsed)} | Headers: {len(header)} | Filas AGPLA: {len(data_rows)}")
    print(f"  Headers: {header[:6]} ... {header[-4:]}")
