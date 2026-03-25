#!/usr/bin/env python3
"""Extrai as primeiras 100 strings traduzíveis do ROM e salva como CSV."""
import os, csv

ROM_PATH = os.path.join(os.path.dirname(__file__), "The Machine (U) [C].gbc")
TEXT_START = 0x77772
TEXT_END   = 0xBE9AE
MAX_STRINGS = 100

ACCENT_MAP = {
    '\xa6':'ã','\xa7':'ç','\xa8':'é','\xa9':'ó',
    '\xaa':'á','\xab':'ú','\xac':'ê','\xad':'ô',
    '\xae':'õ','\xaf':'à',
}

with open(ROM_PATH, "rb") as f:
    rom = f.read()

def is_valid_text_byte(b):
    return (0x20 <= b <= 0x7E) or b in (0x0A,) or b in range(0xA6, 0xB0)

def decode_str(raw):
    out = []
    for b in raw:
        c = chr(b)
        out.append(ACCENT_MAP.get(c, c))
    return "".join(out)

rows = []
i = TEXT_START
while i < TEXT_END and len(rows) < MAX_STRINGS:
    ctrl = rom[i]
    if ctrl not in (0x02, 0x03):
        i += 1
        continue
    j = i + 1
    raw = []
    while j < TEXT_END and rom[j] != 0x00:
        raw.append(rom[j])
        j += 1
    if j >= TEXT_END:
        i += 1
        continue
    # Validate: all bytes must be valid text
    if not raw or not all(is_valid_text_byte(b) for b in raw):
        i = j + 1
        continue
    text = decode_str(raw)
    size = len(raw)
    # Dev comment check: any single line > 30 chars
    lines = text.split('\n')
    is_dev = any(len(l) > 30 for l in lines)
    offset_hex = f"0x{i+1:07X}"  # offset of text (after ctrl byte)
    rows.append({
        "num": len(rows) + 1,
        "offset": f"0x{i:07X}",
        "text_offset": offset_hex,
        "ctrl": f"0x{ctrl:02X}",
        "size": size,
        "original": text,
        "skip": "SIM" if is_dev else ""
    })
    i = j + 1

# Print to console
for r in rows:
    flag = " [SKIP]" if r["skip"] else ""
    print(f"{r['num']:3d} | {r['offset']} | size={r['size']:3d} | {repr(r['original'])}{flag}")

# Save CSV
out_path = os.path.join(os.path.dirname(__file__), "strings_100.csv")
with open(out_path, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["num","offset","text_offset","ctrl","size","original","skip"])
    w.writeheader()
    w.writerows(rows)

print(f"\n{len(rows)} strings salvas em strings_100.csv")
