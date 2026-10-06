import re

path = '/home/dracero/.gemini/antigravity-ide/brain/8df9ce2b-e689-42c5-9e51-dcc040a982e9/.system_generated/steps/339/content.md'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Title
title = re.findall(r'<title>(.*?)</title>', text)
print("Title:", title)

# Sheet tabs from HTML tab bar
tabs = re.findall(r'docs-sheet-tab-caption">([^<]+)<', text)
print("Tab captions in bar:", tabs)

# Search for GIDs and sheet names in JS chunks
# Pattern: [index, 0, "gid", [{"1":[[0,0,"TabName"]
matches = re.findall(r'\[(\d+),0,\\\"(\d+)\\\",\[\{\\\"1\\\":\[\[0,0,\\\"([^\\\"]+)\\\"', text)
print("\nGIDs and names mapped:")
for idx, gid, name in matches:
    print(f"  [{idx}] GID: {gid:12} -> {name}")

# Also check table rows rendered in this active tab
rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
print(f"\nTotal HTML rows rendered in initial view: {len(rows)}")
for idx, r in enumerate(rows[:5]):
    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL)
    cleaned = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
    print(f"  Row {idx+1}:", [c for c in cleaned if c][:8])
