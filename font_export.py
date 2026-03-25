#!/usr/bin/env python3
"""
Exporta os 5 slots de acentos da fonte como PNG para edição manual.
Cada arquivo = 1 caractere (16x8 pixels, ampliado 8x = 128x64).

Slots exportados:
  slot_7B.png → ã  (byte 0x7B, atualmente '{')
  slot_7C.png → ç  (byte 0x7C, atualmente '|')
  slot_7D.png → é  (byte 0x7D, atualmente '}')
  slot_7E.png → ó  (byte 0x7E, atualmente '~')
  slot_22.png → ú  (byte 0x22, atualmente '"')
"""

import os
try:
    from PIL import Image
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"])
    from PIL import Image

ROM_PATH  = os.path.join(os.path.dirname(__file__), "The Machine (U) [C].gbc")
OUT_DIR   = os.path.join(os.path.dirname(__file__), "font_tiles")
FONT_BASE = 0x018000
TILE_SIZE = 16
SCALE     = 8   # cada pixel do tile vira 8x8 pixels no PNG

# Paleta GBC → RGB  (0=branco/fundo, 3=preto/tinta)
PALETTE = {0: (255,255,255), 1: (170,170,170), 2: (85,85,85), 3: (0,0,0)}

# Slots a exportar: (nome_arquivo, ascii_byte, índice_na_fonte)
SLOTS = [
    ("slot_7B_a_til.png",  0x7B, 0x7B - 0x20),  # ã
    ("slot_7C_c_ced.png",  0x7C, 0x7C - 0x20),  # ç
    ("slot_7D_e_agu.png",  0x7D, 0x7D - 0x20),  # é
    ("slot_7E_o_agu.png",  0x7E, 0x7E - 0x20),  # ó
    ("slot_22_u_agu.png",  0x22, 0x22 - 0x20),  # ú
]

# Também exporta as letras base para referência visual
BASES = [
    ("ref_a.png", 0x61, 0x61 - 0x20),
    ("ref_c.png", 0x63, 0x63 - 0x20),
    ("ref_e.png", 0x65, 0x65 - 0x20),
    ("ref_o.png", 0x4F, 0x4F - 0x20),  # 'O' maiúsculo (o minúsculo tem poucos pixels)
    ("ref_u.png", 0x75, 0x75 - 0x20),
]

os.makedirs(OUT_DIR, exist_ok=True)

with open(ROM_PATH, "rb") as f:
    rom = f.read()

def export_tile_pair(idx, path):
    """Lê o par de tiles (esquerdo+direito = 16x8) e salva como PNG ampliado."""
    off_l = FONT_BASE + idx * 2 * TILE_SIZE
    off_r = off_l + TILE_SIZE

    img = Image.new("RGB", (16 * SCALE, 8 * SCALE), (255, 255, 255))

    for tile_x, off in [(0, off_l), (8, off_r)]:
        for r in range(8):
            lo = rom[off + r*2]
            hi = rom[off + r*2 + 1]
            for bit in range(8):
                b = 7 - bit
                color_idx = (((hi >> b) & 1) << 1) | ((lo >> b) & 1)
                rgb = PALETTE[color_idx]
                px = tile_x + bit
                py = r
                for sy in range(SCALE):
                    for sx in range(SCALE):
                        img.putpixel((px*SCALE + sx, py*SCALE + sy), rgb)

    img.save(path)
    print(f"  Salvo: {os.path.basename(path)}  (offset ROM: 0x{off_l:06X})")

print("=== Exportando slots para edição ===")
for fname, byte_val, idx in SLOTS:
    export_tile_pair(idx, os.path.join(OUT_DIR, fname))

print("\n=== Exportando letras base para referência ===")
for fname, byte_val, idx in BASES:
    export_tile_pair(idx, os.path.join(OUT_DIR, fname))

print(f"\nArquivos salvos em: {OUT_DIR}")
print("\nInstruções:")
print("  1. Abra os arquivos slot_*.png no seu editor de imagem (Paint, Photoshop, GIMP, etc.)")
print("  2. Use APENAS preto (#000000) para pixels de tinta e branco (#FFFFFF) para fundo")
print("  3. Consulte os ref_*.png para ver o estilo das letras base")
print("  4. Salve no mesmo nome e pasta")
print("  5. Execute font_import.py para inserir de volta no ROM")
