#!/usr/bin/env python3
"""
Visualizador + Editor de Tiles — The Machine (GBC)
Clique num tile para editar os pixels direto no ROM.
"""

import tkinter as tk
from tkinter import messagebox
import os

ROM_PATH  = os.path.join(os.path.dirname(__file__), "The Machine (U) [C].gbc")
TILE_SIZE = 16
SCALE     = 5
TILE_W    = 8 * SCALE
PALETTE_RGB = ["#FFFFFF", "#AAAAAA", "#555555", "#000000"]
PALETTE_NAMES = ["branco (fundo)", "cinza claro", "cinza escuro", "preto (tinta)"]


def decode_tile(data, offset):
    pixels = []
    for r in range(8):
        lo = data[offset + r*2]
        hi = data[offset + r*2 + 1]
        row = []
        for bit in range(7, -1, -1):
            row.append((((hi >> bit) & 1) << 1) | ((lo >> bit) & 1))
        pixels.append(row)
    return pixels


def encode_tile(pixels):
    result = []
    for row in pixels:
        lo = hi = 0
        for bit, color in enumerate(row):
            b = 7 - bit
            if color & 1: lo |= (1 << b)
            if color & 2: hi |= (1 << b)
        result.extend([lo, hi])
    return bytes(result)


class TileViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Editor de Tiles — The Machine (GBC)")
        self.resizable(False, False)

        with open(ROM_PATH, "rb") as f:
            self.rom = bytearray(f.read())

        self.base         = 0x018000
        self.pair_mode    = tk.BooleanVar(value=True)
        self.selected_off = None   # offset do tile selecionado no editor
        self.edit_pixels  = None   # grade 8x8 do tile em edição
        self.draw_color   = tk.IntVar(value=3)  # cor atual do lápis
        self.unsaved      = False
        self.clipboard    = None   # tile copiado (lista 8x8)

        self._build_ui()
        self._draw_grid()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Barra de navegação ──
        nav = tk.Frame(self, pady=5, padx=8)
        nav.pack(fill=tk.X)

        tk.Label(nav, text="Offset:").pack(side=tk.LEFT)
        self.ent = tk.Entry(nav, width=10)
        self.ent.insert(0, f"0x{self.base:06X}")
        self.ent.pack(side=tk.LEFT, padx=4)
        self.ent.bind("<Return>", lambda _: self._jump())

        for label, delta in [("◀◀-4KB",-0x1000),("◀-512",-512),("▶+512",512),("▶▶+4KB",0x1000)]:
            tk.Button(nav, text=label, command=lambda d=delta: self._step(d)).pack(side=tk.LEFT, padx=2)

        tk.Checkbutton(nav, text="Modo par (16px)", variable=self.pair_mode,
                       command=self._draw_grid).pack(side=tk.LEFT, padx=10)

        # ── Área principal: grade + editor lado a lado ──
        main = tk.Frame(self)
        main.pack(fill=tk.BOTH, padx=8, pady=4)

        # Grade de tiles (esquerda)
        grid_frame = tk.Frame(main)
        grid_frame.pack(side=tk.LEFT)

        self.COLS = 16
        self.ROWS = 6
        cw = self.COLS * (TILE_W + 2) + 2
        ch = self.ROWS * (TILE_W + 2) + 2
        self.canvas = tk.Canvas(grid_frame, width=cw, height=ch, bg="#BBBBAA", cursor="hand2")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._on_grid_click)
        self.canvas.bind("<Motion>",   self._on_grid_hover)

        # Info do tile sob cursor
        self.lbl_hover = tk.Label(grid_frame, text="Passe o mouse sobre um tile",
                                  font=("Consolas", 9), anchor=tk.W)
        self.lbl_hover.pack(fill=tk.X, pady=2)

        # ── Editor de pixels (direita) ──
        edit_frame = tk.Frame(main, padx=12)
        edit_frame.pack(side=tk.LEFT, anchor=tk.N)

        tk.Label(edit_frame, text="Editor de Tile", font=("", 11, "bold")).pack()
        self.lbl_edit_info = tk.Label(edit_frame, text="Nenhum tile selecionado",
                                       font=("Consolas", 9), fg="gray")
        self.lbl_edit_info.pack()

        # Canvas do editor (8x8 pixels, cada pixel = 32px)
        EPIX = 32
        self.EPIX = EPIX
        self.edit_canvas = tk.Canvas(edit_frame, width=8*EPIX, height=8*EPIX,
                                      bg="#CCCCCC", cursor="pencil",
                                      relief=tk.SUNKEN, bd=2)
        self.edit_canvas.pack(pady=6)
        self.edit_canvas.bind("<Button-1>",       self._on_edit_click)
        self.edit_canvas.bind("<B1-Motion>",      self._on_edit_drag)
        self.edit_canvas.bind("<Button-3>",       self._on_edit_click_right)
        self.edit_canvas.bind("<B3-Motion>",      self._on_edit_drag_right)

        # Seletor de cor do lápis
        color_frame = tk.LabelFrame(edit_frame, text="Cor do lápis")
        color_frame.pack(fill=tk.X, pady=4)
        for i, (rgb, name) in enumerate(zip(PALETTE_RGB, PALETTE_NAMES)):
            tk.Radiobutton(color_frame, text=name, variable=self.draw_color, value=i,
                           bg=rgb, activebackground=rgb,
                           selectcolor=rgb).pack(anchor=tk.W)

        tk.Label(edit_frame, text="Clique esquerdo = cor selecionada\n"
                                   "Clique direito  = branco (apagar)",
                 font=("", 8), fg="#555", justify=tk.LEFT).pack()

        # ── Copiar tile de outro offset ──
        copy_frame = tk.LabelFrame(edit_frame, text="Copiar tile como base")
        copy_frame.pack(fill=tk.X, pady=4)

        copy_row = tk.Frame(copy_frame)
        copy_row.pack(fill=tk.X, padx=4, pady=2)
        tk.Label(copy_row, text="Offset:").pack(side=tk.LEFT)
        self.ent_copy = tk.Entry(copy_row, width=10)
        self.ent_copy.pack(side=tk.LEFT, padx=4)
        tk.Button(copy_row, text="Copiar",
                  command=self._copy_from_offset).pack(side=tk.LEFT)

        copy_row2 = tk.Frame(copy_frame)
        copy_row2.pack(fill=tk.X, padx=4, pady=2)
        tk.Button(copy_row2, text="📋 Colar no editor atual",
                  command=self._paste_tile).pack(side=tk.LEFT)
        tk.Button(copy_row2, text="📌 Copiar tile atual",
                  command=self._copy_current).pack(side=tk.LEFT, padx=4)
        self.lbl_clipboard = tk.Label(copy_frame, text="Área de transferência: vazia",
                                       font=("Consolas", 8), fg="gray")
        self.lbl_clipboard.pack(anchor=tk.W, padx=4, pady=2)

        # ── Mover pixels ──
        move_frame = tk.LabelFrame(edit_frame, text="Mover pixels")
        move_frame.pack(fill=tk.X, pady=4)
        move_row1 = tk.Frame(move_frame)
        move_row1.pack(pady=2)
        tk.Button(move_row1, text="⬆", width=3,
                  command=lambda: self._shift(0, -1)).pack(side=tk.LEFT, padx=2)
        move_row2 = tk.Frame(move_frame)
        move_row2.pack(pady=2)
        tk.Button(move_row2, text="⬅", width=3,
                  command=lambda: self._shift(-1, 0)).pack(side=tk.LEFT, padx=2)
        tk.Button(move_row2, text="⬇", width=3,
                  command=lambda: self._shift(0, 1)).pack(side=tk.LEFT, padx=2)
        tk.Button(move_row2, text="➡", width=3,
                  command=lambda: self._shift(1, 0)).pack(side=tk.LEFT, padx=2)

        # Botões do editor
        btn_frame = tk.Frame(edit_frame)
        btn_frame.pack(fill=tk.X, pady=6)
        tk.Button(btn_frame, text="💾 Salvar tile no ROM",
                  bg="#28a745", fg="white", font=("", 10, "bold"),
                  command=self._save_tile).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="↩ Desfazer (recarregar original)",
                  command=self._reload_tile).pack(fill=tk.X, pady=2)
        tk.Button(btn_frame, text="🗑 Limpar tile (tudo branco)",
                  command=self._clear_tile).pack(fill=tk.X, pady=2)

        # Info de offset do tile selecionado
        self.lbl_saved = tk.Label(edit_frame, text="", fg="green",
                                   font=("Consolas", 9))
        self.lbl_saved.pack()

        # Dica
        tk.Label(edit_frame,
                 text="Após editar todos os tiles,\n"
                      "feche e rode font_import.py\n"
                      "ou use os offsets listados.",
                 font=("", 8), fg="#555", justify=tk.CENTER).pack(pady=8)

    # ── Navegação ─────────────────────────────────────────────────────────────

    def _step(self, delta):
        self.base = max(0, min(self.base + delta, len(self.rom) - 1))
        self.ent.delete(0, tk.END)
        self.ent.insert(0, f"0x{self.base:06X}")
        self._draw_grid()

    def _jump(self):
        raw = self.ent.get().strip()
        try:
            self.base = int(raw, 16)
            self._draw_grid()
        except ValueError:
            messagebox.showerror("Erro", f"Offset inválido: {raw}")

    # ── Grade ─────────────────────────────────────────────────────────────────

    def _draw_grid(self):
        self.canvas.delete("all")
        cols, rows = self.COLS, self.ROWS

        for t in range(cols * rows):
            off = self.base + t * TILE_SIZE
            if off + TILE_SIZE > len(self.rom):
                break
            col, row = t % cols, t // cols
            x0 = col * (TILE_W + 2) + 1
            y0 = row * (TILE_W + 2) + 1
            self._blit_tile(off, x0, y0)
            outline = "#FF4444" if off == self.selected_off else "#888"
            width   = 2         if off == self.selected_off else 1
            self.canvas.create_rectangle(x0, y0, x0+TILE_W, y0+TILE_W,
                                          outline=outline, width=width)

    def _blit_tile(self, offset, x0, y0):
        pixels = decode_tile(self.rom, offset)
        for py in range(8):
            for px in range(8):
                c = PALETTE_RGB[pixels[py][px]]
                self.canvas.create_rectangle(
                    x0+px*SCALE, y0+py*SCALE,
                    x0+px*SCALE+SCALE, y0+py*SCALE+SCALE,
                    fill=c, outline="")

    def _tile_at(self, x, y):
        col = x // (TILE_W + 2)
        row = y // (TILE_W + 2)
        if col >= self.COLS or row >= self.ROWS:
            return None
        t = row * self.COLS + col
        off = self.base + t * TILE_SIZE
        return off if off + TILE_SIZE <= len(self.rom) else None

    def _on_grid_hover(self, event):
        off = self._tile_at(event.x, event.y)
        if off is None:
            return
        t = (off - self.base) // TILE_SIZE
        ascii_code = 0x20 + t
        ch = chr(ascii_code) if 0x20 <= ascii_code <= 0x7E else "?"
        pair_info = ""
        if self.pair_mode.get():
            pair_idx = t // 2
            side = "ESQ" if t % 2 == 0 else "DIR"
            char_code = 0x20 + pair_idx
            char_ch = chr(char_code) if 0x20 <= char_code <= 0x7E else "?"
            pair_info = f"  |  Par: '{char_ch}' (0x{char_code:02X}) lado {side}"
        self.lbl_hover.config(
            text=f"Offset: 0x{off:06X}  tile#{t}  char '{ch}' (0x{ascii_code:02X}){pair_info}")

    def _on_grid_click(self, event):
        off = self._tile_at(event.x, event.y)
        if off is None:
            return
        self._load_tile_to_editor(off)

    # ── Editor ────────────────────────────────────────────────────────────────

    def _load_tile_to_editor(self, offset):
        if self.unsaved:
            if not messagebox.askyesno("Tile não salvo",
                    "O tile atual tem alterações não salvas. Descartar?"):
                return
        self.selected_off = offset
        self.edit_pixels  = decode_tile(self.rom, offset)
        self.unsaved      = False

        t = (offset - self.base) // TILE_SIZE
        ascii_code = 0x20 + t
        ch = chr(ascii_code) if 0x20 <= ascii_code <= 0x7E else "?"
        self.lbl_edit_info.config(
            text=f"Tile: offset 0x{offset:06X}  char '{ch}' (0x{ascii_code:02X})",
            fg="black")
        self.lbl_saved.config(text="")
        self._redraw_editor()
        self._draw_grid()

    def _redraw_editor(self):
        self.edit_canvas.delete("all")
        if self.edit_pixels is None:
            return
        E = self.EPIX
        for py in range(8):
            for px in range(8):
                color = PALETTE_RGB[self.edit_pixels[py][px]]
                self.edit_canvas.create_rectangle(
                    px*E, py*E, px*E+E, py*E+E,
                    fill=color, outline="#CCCCCC", width=1)

    def _px_at(self, x, y):
        E = self.EPIX
        px, py = x // E, y // E
        if 0 <= px < 8 and 0 <= py < 8:
            return px, py
        return None, None

    def _paint(self, x, y, color):
        if self.edit_pixels is None:
            return
        px, py = self._px_at(x, y)
        if px is None:
            return
        if self.edit_pixels[py][px] == color:
            return
        self.edit_pixels[py][px] = color
        self.unsaved = True
        E = self.EPIX
        self.edit_canvas.create_rectangle(
            px*E, py*E, px*E+E, py*E+E,
            fill=PALETTE_RGB[color], outline="#CCCCCC", width=1)

    def _on_edit_click(self, event):
        self._paint(event.x, event.y, self.draw_color.get())

    def _on_edit_drag(self, event):
        self._paint(event.x, event.y, self.draw_color.get())

    def _on_edit_click_right(self, event):
        self._paint(event.x, event.y, 0)   # botão direito = apagar (branco)

    def _on_edit_drag_right(self, event):
        self._paint(event.x, event.y, 0)

    def _save_tile(self):
        if self.edit_pixels is None or self.selected_off is None:
            messagebox.showwarning("Aviso", "Nenhum tile selecionado.")
            return
        tile_bytes = encode_tile(self.edit_pixels)
        self.rom[self.selected_off : self.selected_off + TILE_SIZE] = tile_bytes
        # Salva no arquivo ROM imediatamente
        with open(ROM_PATH, "wb") as f:
            f.write(self.rom)
        self.unsaved = False
        self.lbl_saved.config(
            text=f"✓ Salvo em 0x{self.selected_off:06X}  no ROM", fg="green")
        self._draw_grid()

    def _reload_tile(self):
        if self.selected_off is None:
            return
        self.edit_pixels = decode_tile(self.rom, self.selected_off)
        self.unsaved = False
        self._redraw_editor()

    def _clear_tile(self):
        if self.edit_pixels is None:
            return
        self.edit_pixels = [[0]*8 for _ in range(8)]
        self.unsaved = True
        self._redraw_editor()

    # ── Copiar / Colar tile ───────────────────────────────────────────────────

    def _copy_current(self):
        """Copia o tile que está no editor para a área de transferência."""
        if self.edit_pixels is None:
            messagebox.showwarning("Aviso", "Nenhum tile no editor para copiar.")
            return
        self.clipboard = [row[:] for row in self.edit_pixels]
        self.lbl_clipboard.config(
            text=f"Área de transferência: tile 0x{self.selected_off:06X}", fg="blue")

    def _copy_from_offset(self):
        """Lê um tile diretamente do ROM pelo offset digitado e guarda no clipboard."""
        raw = self.ent_copy.get().strip()
        try:
            off = int(raw, 16)
        except ValueError:
            messagebox.showerror("Erro", f"Offset inválido: {raw}")
            return
        if off + TILE_SIZE > len(self.rom):
            messagebox.showerror("Erro", f"Offset 0x{off:06X} fora do ROM.")
            return
        self.clipboard = decode_tile(self.rom, off)
        self.lbl_clipboard.config(
            text=f"Área de transferência: tile 0x{off:06X}", fg="blue")

    def _shift(self, dx, dy):
        """Move todos os pixels do tile dx colunas e dy linhas (wrap = pixels somem na borda)."""
        if self.edit_pixels is None:
            return
        new = [[0]*8 for _ in range(8)]
        for py in range(8):
            for px in range(8):
                nx, ny = px + dx, py + dy
                if 0 <= nx < 8 and 0 <= ny < 8:
                    new[ny][nx] = self.edit_pixels[py][px]
        self.edit_pixels = new
        self.unsaved = True
        self._redraw_editor()

    def _paste_tile(self):
        """Cola o tile do clipboard no editor (substitui pixels atuais)."""
        if self.clipboard is None:
            messagebox.showwarning("Aviso", "Área de transferência vazia.")
            return
        if self.edit_pixels is None:
            messagebox.showwarning("Aviso", "Selecione um tile no grid primeiro.")
            return
        self.edit_pixels = [row[:] for row in self.clipboard]
        self.unsaved = True
        self._redraw_editor()


if __name__ == "__main__":
    if not os.path.exists(ROM_PATH):
        import tkinter.messagebox as mb
        mb.showerror("ROM não encontrada", f"Esperada em:\n{ROM_PATH}")
    else:
        TileViewer().mainloop()
