#!/usr/bin/env python3
"""
Importa os tiles editados de font_tiles/slot_*.png de volta para o ROM.
Gera The Machine (U) [C]_PTBR.gbc com os novos glifos.
"""

import os
try:
    from PIL import Image
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image

ROM_SRC   = os.path.join(os.path.dirname(__file__), "The Machine (U) [C].gbc")
ROM_DST   = os.path.join(os.path.dirname(__file__), "The Machine (U) [C]_PTBR.gbc")
TILES_DIR = os.path.join(os.path.dirname(__file__), "font_tiles")
FONT_BASE = 0x018000
TILE_SIZE = 16
SCALE     = 8

SLOTS = [
    ("slot_7B_a_til.png",  0x7B - 0x20),
    ("slot_7C_c_ced.png",  0x7C - 0x20),
    ("slot_7D_e_agu.png",  0x7D - 0x20),
    ("slot_7E_o_agu.png",  0x7E - 0x20),
    ("slot_22_u_agu.png",  0x22 - 0x20),
]

def rgb_to_color(r, g, b):
    """Converte RGB do PNG para índice de cor GBC (0-3)."""
    brightness = (r + g + b) / 3
    if brightness >= 192:  return 0  # branco → cor 0 (fundo)
    if brightness >= 128:  return 1
    if brightness >= 64:   return 2
    return 3               # preto → cor 3 (tinta)

def encode_tile(pixels_8x8):
    """Converte grade 8x8 de índices de cor (0-3) para 16 bytes 2BPP GB."""
    result = []
    for row in pixels_8x8:
        lo = hi = 0
        for bit, color in enumerate(row):
            b = 7 - bit
            if color & 1: lo |= (1 << b)
            if color & 2: hi |= (1 << b)
        result.extend([lo, hi])
    return bytes(result)

def import_png(path, idx, data):
    """Lê PNG 128x64 (16px × 8px ampliado SCALE×), converte e escreve no ROM."""
    img = Image.open(path).convert("RGB")
    w, h = img.size

    # Aceita qualquer múltiplo: recalcula scale
    scale_x = w // 16
    scale_y = h // 8

    off_l = FONT_BASE + idx * 2 * TILE_SIZE
    off_r = off_l + TILE_SIZE

    for tile_x, off in [(0, off_l), (8, off_r)]:
        pixels_8x8 = []
        for py in range(8):
            row = []
            for px in range(8):
                # Pega o pixel central do bloco ampliado
                sx = (tile_x + px) * scale_x + scale_x // 2
                sy = py * scale_y + scale_y // 2
                r, g, b = img.getpixel((sx, sy))
                row.append(rgb_to_color(r, g, b))
            pixels_8x8.append(row)
        tile_bytes = encode_tile(pixels_8x8)
        data[off:off + TILE_SIZE] = tile_bytes

# Usa ROM_DST se já existir (preserva traduções), senão copia da original
base = ROM_DST if os.path.exists(ROM_DST) else ROM_SRC
with open(base, "rb") as f:
    data = bytearray(f.read())

print("=== Importando tiles editados ===\n")
imported = 0
for fname, idx in SLOTS:
    path = os.path.join(TILES_DIR, fname)
    if not os.path.exists(path):
        print(f"  PULADO (não encontrado): {fname}")
        continue
    import_png(path, idx, data)
    print(f"  Importado: {fname}  → offset ROM 0x{FONT_BASE + idx*2*TILE_SIZE:06X}")
    imported += 1

with open(ROM_DST, "wb") as f:
    f.write(data)

print(f"\n{imported} tile(s) importado(s).")
print(f"ROM salva: {ROM_DST}")
