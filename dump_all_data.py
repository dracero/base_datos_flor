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

for name, path in sheets:
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    parsed = []
    for r in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)
        cleaned = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        parsed.append(cleaned)
    
    # Let's count how many rows have a title
    with_title = []
    for r in parsed[2:]:
        if len(r) > 12 and r[12]:
            with_title.append((r[1], r[10] if len(r)>10 else '', r[12], r[13] if len(r)>13 else ''))
    
    print(f"\n==========================================")
    print(f"{name} -> {len(with_title)} materiales cargados:")
    for ag, nom, tit, aut in with_title:
        print(f"  [{ag}] {tit[:50]} (por {aut[:30]})")
