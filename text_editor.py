#!/usr/bin/env python3
"""
The Machine (GBC) - Editor de Texto para Tradução PT-BR
Estilo Advance Text: lê a ROM, mostra strings com limites, permite substituição.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import csv
import os
import struct

# ─── Constantes da ROM ────────────────────────────────────────────────────────
ROM_TEXT_START   = 0x77772
ROM_TEXT_END     = 0xBE9AE
CTRL_BYTES       = {0x02, 0x03}       # bytes de controle antes de strings
TERMINATOR       = 0x00
LINE_BREAK       = 0x0A
MAX_DEV_COMMENT  = 30                 # strings > N chars = comentário de dev
DIALOG_LINE_LIMIT = 19                # limite sugerido por linha de diálogo

# ─── Mapeamento de acentos PT-BR → bytes do ROM ──────────────────────────────
# Tiles editados manualmente no tile_viewer.py (offset 0x018860+, stride 16):
#   byte = 0x20 + (tile_offset - 0x018000) / 16
ACCENT_MAP = {
    'ã': '\xa6', 'Ã': '\xa6',
    'ç': '\xa7', 'Ç': '\xa7',
    'é': '\xa8', 'É': '\xa8',
    'ó': '\xa9', 'Ó': '\xa9',
    'á': '\xaa', 'Á': '\xaa',
    'ú': '\xab', 'Ú': '\xab',
    'ê': '\xac', 'Ê': '\xac',
    'ô': '\xad', 'Ô': '\xad',
    'õ': '\xae', 'Õ': '\xae',
    'à': '\xaf', 'À': '\xaf',
    'í': '\xb1', 'Í': '\xb1',
    'â': '\xb2', 'Â': '\xb2',
}

# Mapeamento inverso: bytes do ROM → chars PT-BR (para exibir a ROM traduzida)
REVERSE_ACCENT = {0xa6: 'ã', 0xa7: 'ç', 0xa8: 'é', 0xa9: 'ó',
                  0xaa: 'á', 0xab: 'ú', 0xac: 'ê', 0xad: 'ô',
                  0xae: 'õ', 0xaf: 'à', 0xb1: 'í', 0xb2: 'â'}


def decode_rom_text(raw_bytes: bytes):
    """Decodifica bytes da ROM para string PT-BR. Retorna None se byte inválido."""
    result = []
    for b in raw_bytes:
        if 0x20 <= b <= 0x7E or b == 0x0A:
            result.append(chr(b))
        elif b in REVERSE_ACCENT:
            result.append(REVERSE_ACCENT[b])
        else:
            return None
    return "".join(result)
ACCENT_CHARS    = set(ACCENT_MAP.keys())
FONT_PATCH_ACTIVE = True

# ─── Cores ────────────────────────────────────────────────────────────────────
COLOR_OK          = "#d4edda"   # verde claro  — traduzido e cabe
COLOR_TOO_LONG    = "#f8d7da"   # vermelho     — tradução muito longa
COLOR_UNTRANSLATED = "#ffffff"  # branco       — sem tradução ainda
COLOR_SKIP        = "#e8e8e8"   # cinza        — comentário de dev (pular)
COLOR_SELECTED    = "#cce5ff"   # azul claro   — selecionado


def parse_rom(data: bytes) -> list[dict]:
    """Extrai todas as strings da região de texto do ROM."""
    strings = []
    i = ROM_TEXT_START

    while i < ROM_TEXT_END:
        byte = data[i]

        # Espera byte de controle
        if byte not in CTRL_BYTES:
            i += 1
            continue

        ctrl = byte
        i += 1
        if i >= ROM_TEXT_END:
            break

        # Lê a string até o terminador
        start = i
        chars = []
        while i < ROM_TEXT_END and data[i] != TERMINATOR:
            chars.append(data[i])
            i += 1

        # inclui o \x00 terminador
        end = i  # posição do \x00
        i += 1   # avança além do \x00

        # Decodifica: ASCII imprimível, \x0A, e bytes de acento PT-BR (0xA6–0xAF)
        raw_bytes = bytes(chars)
        text = decode_rom_text(raw_bytes)
        if text is None:
            continue

        # Ignora strings vazias
        if not text.strip():
            continue

        # Tamanho disponível = len(chars) + 1 (para o \x00)
        size = len(chars) + 1

        strings.append({
            "offset":    start,
            "offset_hex": f"0x{start:06X}",
            "ctrl":      f"{ctrl:02X}",
            "size":      size,          # bytes disponíveis (inclui \x00)
            "original":  text,
            "traducao":  "",
            "skip":      max((len(l) for l in text.split("\n")), default=0) > MAX_DEV_COMMENT,
        })

    return strings


def apply_translations(data: bytearray, strings: list[dict]) -> tuple:
    """Insere as traduções no bytearray da ROM, ignorando limites de tamanho."""
    errors = []
    applied = 0
    for s in strings:
        tr = s["traducao"].strip()
        if not tr or s["skip"]:
            continue

        # Converte acentos PT-BR para os bytes do ROM
        tr_rom = "".join(ACCENT_MAP.get(c, c) for c in tr)
        tr_bytes = tr_rom.encode("latin-1", errors="replace") + b"\x00"
        avail = s["size"]

        # Se for maior, avisamos no log de erros, mas NÃO paramos a execução
        if len(tr_bytes) > avail:
            errors.append(f"PERIGO 0x{s['offset']:06X}: \"{tr}\" ({len(tr_bytes)}b > {avail}b) - SOBRESCREVENDO DADOS!")

        # Aplica exatamente o que foi digitado no offset
        # Nota: data[start:end] = payload vai ajustar o tamanho do bytearray se o payload for maior,
        # o que corromperia todos os offsets seguintes da ROM. 
        # Por isso, usamos um loop ou slice fixo para manter a integridade do tamanho total da ROM:
        for j, byte in enumerate(tr_bytes):
            if (s["offset"] + j) < len(data):
                data[s["offset"] + j] = byte
        
        applied += 1

    return data, applied, errors


# ─── GUI ──────────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("The Machine - Editor de Tradução PT-BR")
        self.geometry("1200x700")
        self.minsize(900, 500)

        self.rom_path: str = ""
        self.rom_data: bytes = b""
        self.strings:  list[dict] = []
        self.filtered: list[int] = []   # índices em self.strings
        self._current_idx: int = -1
        self._ignore_edit = False

        self._build_ui()
        self._bind_keys()

    # ── Construção da UI ──────────────────────────────────────────────────────

    def _build_ui(self):
        # Barra de ferramentas
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="📂 Abrir ROM",      command=self.open_rom).pack(side=tk.LEFT, padx=4, pady=3)
        tk.Button(toolbar, text="💾 Exportar CSV",   command=self.export_csv).pack(side=tk.LEFT, padx=4, pady=3)
        tk.Button(toolbar, text="📥 Importar CSV",   command=self.import_csv).pack(side=tk.LEFT, padx=4, pady=3)
        tk.Button(toolbar, text="✅ Aplicar no ROM", command=self.apply_rom,
                  bg="#28a745", fg="white", font=("", 9, "bold")).pack(side=tk.LEFT, padx=8, pady=3)

        # Filtros
        filter_frame = tk.Frame(toolbar)
        filter_frame.pack(side=tk.LEFT, padx=16)
        tk.Label(filter_frame, text="Filtro:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="todos")
        for val, label in [("todos","Todos"), ("sem_trad","Sem tradução"),
                           ("traduzido","Traduzidos"), ("longa","Muito longa"), ("skip","Dev/Skip")]:
            tk.Radiobutton(filter_frame, text=label, variable=self.filter_var,
                           value=val, command=self._apply_filter).pack(side=tk.LEFT)

        # Busca
        search_frame = tk.Frame(toolbar)
        search_frame.pack(side=tk.LEFT, padx=12)
        tk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_filter())
        tk.Entry(search_frame, textvariable=self.search_var, width=22).pack(side=tk.LEFT, padx=3)

        # Status bar
        self.status_var = tk.StringVar(value="Abra uma ROM para começar.")
        status_bar = tk.Label(self, textvariable=self.status_var, bd=1, relief=tk.SUNKEN,
                              anchor=tk.W, font=("Consolas", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Painel principal: lista + editor
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True)

        # ── Lista de strings ──
        list_frame = tk.Frame(paned)
        paned.add(list_frame, minsize=540)

        cols = ("idx", "offset", "size", "original", "traducao")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("idx",      text="#")
        self.tree.heading("offset",   text="Offset")
        self.tree.heading("size",     text="Bytes")
        self.tree.heading("original", text="Original (EN)")
        self.tree.heading("traducao", text="Tradução (PT)")

        self.tree.column("idx",      width=50,  anchor=tk.CENTER, stretch=False)
        self.tree.column("offset",   width=80,  anchor=tk.CENTER, stretch=False)
        self.tree.column("size",     width=50,  anchor=tk.CENTER, stretch=False)
        self.tree.column("original", width=280, anchor=tk.W)
        self.tree.column("traducao", width=280, anchor=tk.W)

        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,   command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Cores por tag
        self.tree.tag_configure("ok",         background=COLOR_OK)
        self.tree.tag_configure("too_long",   background=COLOR_TOO_LONG)
        self.tree.tag_configure("untranslated",background=COLOR_UNTRANSLATED)
        self.tree.tag_configure("skip",       background=COLOR_SKIP, foreground="#888")

        # ── Painel de edição ──
        edit_frame = tk.Frame(paned, padx=10, pady=8)
        paned.add(edit_frame, minsize=300)

        mono = font.Font(family="Consolas", size=11)

        # Informações do registro
        info_font = font.Font(family="Consolas", size=10)
        self.lbl_offset = tk.Label(edit_frame, text="Offset: —", font=info_font, anchor=tk.W)
        self.lbl_offset.pack(fill=tk.X)
        self.lbl_size   = tk.Label(edit_frame, text="Bytes disponíveis: —", font=info_font, anchor=tk.W)
        self.lbl_size.pack(fill=tk.X)
        self.lbl_ctrl   = tk.Label(edit_frame, text="Ctrl byte: —", font=info_font, anchor=tk.W)
        self.lbl_ctrl.pack(fill=tk.X)

        ttk.Separator(edit_frame).pack(fill=tk.X, pady=6)

        # Texto original
        tk.Label(edit_frame, text="Original (EN):", font=("", 10, "bold"), anchor=tk.W).pack(fill=tk.X)
        self.txt_orig = tk.Text(edit_frame, height=5, font=mono, state=tk.DISABLED,
                                bg="#f0f0f0", relief=tk.FLAT, bd=1)
        self.txt_orig.pack(fill=tk.X, pady=(0, 8))

        # Tradução
        tk.Label(edit_frame, text="Tradução (PT-BR):", font=("", 10, "bold"), anchor=tk.W).pack(fill=tk.X)
        self.txt_tr = tk.Text(edit_frame, height=5, font=mono, relief=tk.SOLID, bd=1)
        self.txt_tr.pack(fill=tk.X)
        self.txt_tr.tag_configure("invalid",      foreground="red",    underline=True)
        self.txt_tr.tag_configure("line_overflow", background="#ffe0b2")  # laranja suave
        self.txt_tr.bind("<<Modified>>", self._on_edit)

        # Contagem de chars por linha
        self.lbl_lines = tk.Label(edit_frame, text="", font=info_font,
                                  anchor=tk.W, fg="#555", justify=tk.LEFT)
        self.lbl_lines.pack(fill=tk.X, pady=(2, 0))

        # Indicador de bytes totais
        self.lbl_count = tk.Label(edit_frame, text="0 / 0 bytes", font=info_font,
                                  anchor=tk.W, fg="gray")
        self.lbl_count.pack(fill=tk.X, pady=(0, 6))

        # Aviso de limite
        self.lbl_warn = tk.Label(edit_frame, text="", font=("", 10, "bold"),
                                 fg="red", anchor=tk.W, wraplength=320, justify=tk.LEFT)
        self.lbl_warn.pack(fill=tk.X)

        # Botões do editor
        btn_row = tk.Frame(edit_frame)
        btn_row.pack(fill=tk.X, pady=8)
        tk.Button(btn_row, text="💾 Salvar",   command=self._save_current, bg="#007bff", fg="white").pack(side=tk.LEFT, padx=3)
        tk.Button(btn_row, text="🔄 Restaurar",command=self._restore_current).pack(side=tk.LEFT, padx=3)
        tk.Button(btn_row, text="⏭ Próximo sem tradução", command=self._next_untranslated).pack(side=tk.LEFT, padx=3)

        # Progresso
        ttk.Separator(edit_frame).pack(fill=tk.X, pady=6)
        self.lbl_progress = tk.Label(edit_frame, text="Progresso: — / —", font=info_font, anchor=tk.W)
        self.lbl_progress.pack(fill=tk.X)
        self.progress_bar = ttk.Progressbar(edit_frame, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=4)

    def _bind_keys(self):
        self.bind("<Control-s>", lambda _: self._save_current())
        self.bind("<Control-n>", lambda _: self._next_untranslated())
        self.bind("<Alt-Down>",  lambda _: self._move_selection(1))
        self.bind("<Alt-Up>",    lambda _: self._move_selection(-1))

    # ── Lógica principal ──────────────────────────────────────────────────────

    def open_rom(self):
        path = filedialog.askopenfilename(
            title="Abrir ROM",
            filetypes=[("Game Boy Color", "*.gbc *.gb"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "rb") as f:
                self.rom_data = f.read()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a ROM:\n{e}")
            return

        self.rom_path = path
        self.title(f"The Machine - Editor de Tradução PT-BR  [{os.path.basename(path)}]")
        self.status_var.set("Analisando ROM...")
        self.update()

        self.strings = parse_rom(self.rom_data)
        self._apply_filter()
        self._update_progress()
        self.status_var.set(
            f"ROM carregada: {len(self.strings)} strings encontradas  "
            f"({len([s for s in self.strings if not s['skip']])} traduzíveis)")

    def _apply_filter(self):
        query  = self.search_var.get().lower()
        filt   = self.filter_var.get()
        result = []

        for i, s in enumerate(self.strings):
            # Filtro de categoria
            if filt == "sem_trad"  and (s["traducao"] or s["skip"]):
                continue
            if filt == "traduzido" and not s["traducao"]:
                continue
            if filt == "longa"     and not self._is_too_long(s):
                continue
            if filt == "skip"      and not s["skip"]:
                continue

            # Busca textual
            if query and query not in s["original"].lower() and query not in s["traducao"].lower():
                continue

            result.append(i)

        self.filtered = result
        self._rebuild_tree()

    def _rebuild_tree(self):
        self.tree.delete(*self.tree.get_children())
        for row_idx, str_idx in enumerate(self.filtered):
            s    = self.strings[str_idx]
            tag  = self._tag_for(s)
            orig = s["original"].replace("\n", "↵")
            trad = s["traducao"].replace("\n", "↵")
            self.tree.insert("", tk.END, iid=str(row_idx), values=(
                str_idx + 1,
                s["offset_hex"],
                s["size"],
                orig[:60] + ("…" if len(orig) > 60 else ""),
                trad[:60] + ("…" if len(trad) > 60 else ""),
            ), tags=(tag,))

    def _tag_for(self, s: dict) -> str:
        if s["skip"]:
            return "skip"
        if not s["traducao"]:
            return "untranslated"
        if self._is_too_long(s):
            return "too_long"
        return "ok"

    def _is_too_long(self, s: dict) -> bool:
        if not s["traducao"]:
            return False
        tr_rom = "".join(ACCENT_MAP.get(c, c) for c in s["traducao"])
        tr_bytes = tr_rom.encode("latin-1", errors="replace") + b"\x00"
        return len(tr_bytes) > s["size"]

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        row_idx = int(sel[0])
        str_idx = self.filtered[row_idx]
        self._load_entry(str_idx)

    def _load_entry(self, str_idx: int):
        self._current_idx = str_idx
        s = self.strings[str_idx]

        self.lbl_offset.config(text=f"Offset:  {s['offset_hex']}")
        self.lbl_size.config(text=f"Bytes disponíveis: {s['size']}  (máx. de tradução: {s['size'] - 1} chars)")
        self.lbl_ctrl.config(text=f"Ctrl byte: 0x{s['ctrl']}")

        self.txt_orig.config(state=tk.NORMAL)
        self.txt_orig.delete("1.0", tk.END)
        self.txt_orig.insert("1.0", s["original"])
        self.txt_orig.config(state=tk.DISABLED)

        self._ignore_edit = True
        self.txt_tr.delete("1.0", tk.END)
        self.txt_tr.insert("1.0", s["traducao"])
        self.txt_tr.edit_modified(False)
        self._ignore_edit = False

        self._update_count()

    def _on_edit(self, _event=None):
        if self._ignore_edit:
            return
        if not self.txt_tr.edit_modified():
            return
        self.txt_tr.edit_modified(False)
        self._update_count()

    def _update_count(self):
        if self._current_idx < 0:
            return
        s  = self.strings[self._current_idx]
        tr = self.txt_tr.get("1.0", "end-1c")
        tr_rom = "".join(ACCENT_MAP.get(c, c) for c in tr)
        n  = len(tr_rom.encode("latin-1", errors="replace")) + 1   # +1 para o \x00
        avail = s["size"]

        color = "green" if n <= avail else "red"
        self.lbl_count.config(text=f"Bytes: {n} / {avail}", fg=color)

        # Remove tags anteriores
        self.txt_tr.tag_remove("invalid",       "1.0", tk.END)
        self.txt_tr.tag_remove("line_overflow",  "1.0", tk.END)

        lines = tr.split("\n")
        invalid_chars = []
        line_info_parts = []
        any_line_over = False

        for line_idx, line in enumerate(lines):
            llen = len(line)
            over = llen > DIALOG_LINE_LIMIT

            if over:
                any_line_over = True
                # Destaca do char 18 em diante com fundo laranja
                start_pos = f"{line_idx + 1}.{DIALOG_LINE_LIMIT}"
                end_pos   = f"{line_idx + 1}.end"
                self.txt_tr.tag_add("line_overflow", start_pos, end_pos)

            # Indicador por linha: verde se ok, vermelho se passou
            indicator = "✓" if not over else "✗"
            fg_code   = "green" if not over else "red"
            line_info_parts.append((f"Linha {line_idx+1}: {llen}/{DIALOG_LINE_LIMIT} {indicator}", fg_code))

            # Chars inválidos (acentos mapeados pelo font patch são permitidos)
            for col_idx, ch in enumerate(line):
                is_ascii = 0x20 <= ord(ch) <= 0x7E
                is_mapped = ch in ACCENT_CHARS and FONT_PATCH_ACTIVE
                if not is_ascii and not is_mapped:
                    pos = f"{line_idx + 1}.{col_idx}"
                    self.txt_tr.tag_add("invalid", pos, f"{pos}+1c")
                    invalid_chars.append(ch)

        # Monta label de linhas (texto simples, usamos cores via fg do label agregado)
        line_summary = "   ".join(t for t, _ in line_info_parts)
        # Cor do label: vermelho se alguma linha passou, verde se tudo ok
        summary_color = "red" if any_line_over else ("green" if tr else "gray")
        self.lbl_lines.config(text=line_summary, fg=summary_color)

        warnings = []
        if n > avail:
            warnings.append(f"⚠ Bytes: excede em {n - avail}!")
        if any_line_over:
            warnings.append(f"⚠ Linha(s) com mais de {DIALOG_LINE_LIMIT} chars — texto vai transbordar no jogo!")
        if invalid_chars:
            unique = "".join(dict.fromkeys(invalid_chars))
            if FONT_PATCH_ACTIVE:
                warnings.append(f"⚠ Chars sem suporte: {unique}  (suportados: ã ç é ó á ú ê ô õ à í â)")
            else:
                warnings.append(f"⚠ Chars inválidos: {unique}  — rode font_patch_apply.py para habilitar acentos PT-BR")
        self.lbl_warn.config(text="\n".join(warnings))

    def _save_current(self, _event=None):
        if self._current_idx < 0:
            return
        s = self.strings[self._current_idx]
        s["traducao"] = self.txt_tr.get("1.0", "end-1c")
        self._refresh_row(self._current_idx)
        self._update_progress()

    def _restore_current(self):
        if self._current_idx < 0:
            return
        self._load_entry(self._current_idx)

    def _next_untranslated(self, _event=None):
        """Seleciona a próxima string sem tradução."""
        start = (self._current_idx + 1) if self._current_idx >= 0 else 0
        for i in range(start, len(self.strings)):
            s = self.strings[i]
            if not s["traducao"] and not s["skip"]:
                # Encontra na lista filtrada
                if i in self.filtered:
                    row = self.filtered.index(i)
                    self.tree.selection_set(str(row))
                    self.tree.see(str(row))
                    self._load_entry(i)
                    return
                # Não está no filtro atual: muda para "todos"
                self.filter_var.set("todos")
                self._apply_filter()
                row = self.filtered.index(i)
                self.tree.selection_set(str(row))
                self.tree.see(str(row))
                self._load_entry(i)
                return
        messagebox.showinfo("Pronto!", "Nenhuma string sem tradução encontrada.")

    def _move_selection(self, delta: int):
        sel = self.tree.selection()
        if not sel:
            return
        row = int(sel[0]) + delta
        row = max(0, min(row, len(self.filtered) - 1))
        self._save_current()
        self.tree.selection_set(str(row))
        self.tree.see(str(row))
        self._load_entry(self.filtered[row])

    def _refresh_row(self, str_idx: int):
        if str_idx not in self.filtered:
            return
        row_idx = self.filtered.index(str_idx)
        s   = self.strings[str_idx]
        tag = self._tag_for(s)
        orig = s["original"].replace("\n", "↵")
        trad = s["traducao"].replace("\n", "↵")
        self.tree.item(str(row_idx), values=(
            str_idx + 1,
            s["offset_hex"],
            s["size"],
            orig[:60] + ("…" if len(orig) > 60 else ""),
            trad[:60] + ("…" if len(trad) > 60 else ""),
        ), tags=(tag,))

    def _update_progress(self):
        translatable = [s for s in self.strings if not s["skip"]]
        done = sum(1 for s in translatable if s["traducao"])
        total = len(translatable)
        pct = (done / total * 100) if total else 0
        self.lbl_progress.config(text=f"Progresso: {done} / {total} strings traduzidas ({pct:.1f}%)")
        self.progress_bar["value"] = pct

    # ── CSV ───────────────────────────────────────────────────────────────────

    def export_csv(self):
        if not self.strings:
            messagebox.showwarning("Aviso", "Carregue uma ROM primeiro.")
            return
        path = filedialog.asksaveasfilename(
            title="Exportar CSV",
            defaultextension=".csv",
            initialfile="traducao.csv",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["#", "offset_hex", "ctrl", "size", "original_en", "traducao_pt", "skip"])
                for i, s in enumerate(self.strings):
                    w.writerow([
                        i + 1,
                        s["offset_hex"],
                        s["ctrl"],
                        s["size"],
                        s["original"],
                        s["traducao"],
                        "1" if s["skip"] else "0",
                    ])
            messagebox.showinfo("Exportado", f"CSV salvo em:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def import_csv(self):
        path = filedialog.askopenfilename(
            title="Importar CSV",
            filetypes=[("CSV", "*.csv"), ("Todos", "*.*")])
        if not path:
            return

        # Se não há strings carregadas, tenta detectar e carregar a ROM primeiro
        if not self.strings:
            # Tenta carregar ROM do mesmo diretório
            rom_guess = os.path.join(os.path.dirname(path), "The Machine (U) [C].gbc")
            if os.path.exists(rom_guess):
                self.rom_path = rom_guess
                with open(rom_guess, "rb") as f:
                    self.rom_data = f.read()
                self.strings = parse_rom(self.rom_data)
            else:
                messagebox.showwarning("Aviso", "Carregue a ROM antes de importar o CSV.")
                return

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    offset_hex = row.get("offset_hex", "").strip()
                    traducao   = row.get("traducao_pt", "").strip()
                    for s in self.strings:
                        if s["offset_hex"] == offset_hex:
                            s["traducao"] = traducao
                            count += 1
                            break
            self._apply_filter()
            self._update_progress()
            messagebox.showinfo("Importado", f"{count} traduções importadas.")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # ── Aplicar no ROM ────────────────────────────────────────────────────────

    def apply_rom(self):
        if not self.rom_data:
            messagebox.showwarning("Aviso", "Carregue uma ROM primeiro.")
            return

        self._save_current()

        long_count = sum(1 for s in self.strings if self._is_too_long(s))
        if long_count:
            # Mudamos de "serão ignoradas" para "causarão corrupção"
            resp = messagebox.askyesno(
                "PERIGO DE CORRUPÇÃO",
                f"Há {long_count} tradução(ões) que excedem o limite.\n"
                "Gravar estas strings pode corromper a ROM e travar o jogo.\n\n"
                "Deseja gravar assim mesmo?")
            if not resp:
                return

        # Escolhe o arquivo de saída
        base = os.path.splitext(self.rom_path)[0] if self.rom_path else "rom"
        out_path = filedialog.asksaveasfilename(
            title="Salvar ROM traduzida",
            defaultextension=".gbc",
            initialfile=os.path.basename(base) + "_PTBR.gbc",
            filetypes=[("Game Boy Color", "*.gbc"), ("Todos", "*.*")])
        if not out_path:
            return

        data = bytearray(self.rom_data)
        data, applied, errors = apply_translations(data, self.strings)

        try:
            with open(out_path, "wb") as f:
                f.write(data)
        except Exception as e:
            messagebox.showerror("Erro ao salvar", str(e))
            return

        msg = f"ROM salva em:\n{out_path}\n\n{applied} tradução(ões) aplicada(s)."
        if errors:
            msg += f"\n\n{len(errors)} string(s) ignorada(s) por exceder o limite:\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                msg += f"\n… e mais {len(errors) - 10}"
        messagebox.showinfo("ROM salva!", msg)


# ─── Entrada ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()

    # Tenta auto-carregar a ROM do mesmo diretório
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_rom = os.path.join(script_dir, "The Machine (U) [C].gbc")
    if os.path.exists(default_rom):
        app.after(100, lambda: app.open_rom.__func__(app) or setattr(app, "_auto", True))
        # Carrega diretamente
        try:
            with open(default_rom, "rb") as f:
                app.rom_data = f.read()
            app.rom_path = default_rom
            app.title(f"The Machine - Editor de Tradução PT-BR  [{os.path.basename(default_rom)}]")
            app.strings = parse_rom(app.rom_data)
            app.after(200, app._apply_filter)
            app.after(200, app._update_progress)
            app.after(200, lambda: app.status_var.set(
                f"ROM carregada automaticamente: {len(app.strings)} strings encontradas  "
                f"({len([s for s in app.strings if not s['skip']])} traduzíveis)"))
        except Exception:
            pass

    app.mainloop()
