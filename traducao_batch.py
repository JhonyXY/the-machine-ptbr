#!/usr/bin/env python3
"""
traducao_batch.py — aplica traduções PT-BR hardcoded nas primeiras 100 strings.
Lê strings_100.csv, grava traducao.csv (parcial a cada 10) e aplica no ROM.
"""

import csv
import os
import struct

ROM_DIR   = os.path.dirname(os.path.abspath(__file__))
ROM_IN    = os.path.join(ROM_DIR, "The Machine (U) [C].gbc")
ROM_OUT   = os.path.join(ROM_DIR, "The Machine (U) [C]_PTBR.gbc")
CSV_IN    = os.path.join(ROM_DIR, "strings_100.csv")
CSV_OUT   = os.path.join(ROM_DIR, "traducao.csv")

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

# ── Traduções hardcoded — chave = num (coluna "num" do strings_100.csv) ────────
# Regras: máx 18 chars/linha, mesma qtd de \n do original, bytes ≤ original
TRADUCOES = {
     1: "Seu apartamento\nestá aqui.",
     2: "GIRT, aqui é\nKALT. \n ",
     3: "Temos um problema\nno setor EAST\nB2.",
     4: "Va já lá embaixo\no mais rápido\nque puder.",
     5: " Este é o\n HEART NEXUS.\n ",
     6: " Bombeia\n combustivel\n liquido",
     7: " por toda a\n MÁQUINA.\n ",
     8: "Com licença! você\nestá PROIBIDO de\ndistribuir",
     9: "material\npolitico perto\nda cabine!",
    10: "Olá! GIRT, hein?\nVeja só aqui...",
    11: "Parece que você\njá votou!",
    12: "Não está tentando\nvotar duas vezes",
    13: "você? Isso é\ncrime!",
    14: "Ah sim, já vejo.\nVocê mora no B2.",
    15: "Ah sim, já vejo.\nVocê mora no B1.",
    16: "Ah sim, já vejo.\nVocê mora no L.",
    17: "Parece que sua\nresidência é",
    18: "privada por\nrazões de sigilo.",
    19: "Parece que você\nainda não votou.",
    20: "Gostaria de\nvotar agora?",
    21: "Veja...aqui\nestá sua cédula.",
    22: "Vote antes que o\nprazo acabe",
    23: "eleição acabe!\nTodo voto conta!",
    24: "É melhor descansar\nantes de",
    25: "seu grande dia\namanhã!",
    26: " Um coração...\n gang do amor.",
    27: " Farto do\n sistema,",
    28: " GIRT enveredou\n pelo crime.",
    # 29: skip (dev comment)
    30: "TIO BOP: Ei\nGirt... Ouvi que\nvocê reprovou.",
    31: "Não se preocupe.\nEu reprovei\ntambém.",
    32: "Me peguei\ncolando, se você\nacreditar nisso.",
    33: "Posso te arranjar\num emprego na\npolicia.",
    34: "TIO BOP: Ei\nGirt... Ouvi que\nvocê saiu da feira",
    35: "Não se preocupe.\nAlgumas pessoas\nsimplesmente",
    36: "não são feitas\npara isso.\n ",
    37: "Ei, só entre nós\ndois...",
    38: "Você não quer\nnada com isso",
    39: "com a policia...\nSe você fugir",
    40: "da policia,\neu te arrumo",
    41: "emprego na\nfábrica.",
    42: "O que acha?",
    43: "Acho que você fez\na escolha certa",
    44: "Não ganhamos\nmuito dinheiro...",
    45: "Trabalhamos\nmuito duro..",
    46: "mas às vezes\nnos divertimos.",
    47: "...nas pausas\nnossas.",
    48: "Tudo bem. É a\nsua decisão.\nBoa sorte.",
    49: "Tomara que\ntenha feito\na certa.",
    50: "Ei GIRT... Vá\npara o NORTE ver\na bagunça.",
    51: "TIO BOP: Bem-vindo\nao esquadrão!\n ",
    52: "Te vejo\nno amanhecer\nde amanhã.",
    53: "Então, o que acha?\nQuer ser",
    54: "um policial como\nseu tio?",
    55: "Vou deixar a\ndecisão pra você.",
    56: "Um panfleto do\nPart. MaWA",
    57: "Um panfleto do\nPart. Volf",
    58: "Um panfleto do\nPart. Wolf",
    59: "Um panfleto do\nPart. Sheep",
    60: "É um mapa do\nsistema de trem.\n  ",
    61: "Melhor não\naparecer",
    62: "Spy",
    63: "pela escola\nagora não.",
    64: "O auditório\nestá fechado.",
    65: "Novo emprego\nna fábrica\npor aqui.",
    66: "Você precisará\npegar o trem",
    67: "de volta ao\nseu apartamento.",
    68: "Ei, cara!\nTem um trocado?\n ",
    69: "Essa carteira\nparece bem\ncheia.",
    70: "Parece que\nALGUÉM ficou\ncom sorte ",
    71: "apostando no jogo.\n \n ",
    72: " Você deu\n seu DINHEIRO.",
    73: "Uau, rico!\nBem, pode ter\ncustado bem caro",
    74: "mas aprendeu\numa lição dura\nhoje.",
    75: "Da próxima vez\nque ver caras\nsuspeitas",
    76: "só vá pelo\noutro lado...\n ",
    77: "Isso foi uma\nLIÇÃO BARATA\npra você...",
    78: "Uau, que cara\nrico! Dá pra\nentender porque ",
    79: "queria largar\nseu dinheiro!\nRapazes...",
    80: " \nEstamos RICOS!\n ",
    81: "Vamos trocar\ne gastar tudo\nno Froggie's.",
    82: "É isso!? A gente\nmatou um cara por\nTROCADO!",
    83: "Por que ele não\nentregou sua\ncarteira?",
    84: "Isso não é de\nmúltipla escolha\naqui.",
    85: "Dê o dinheiro\nou você morre.\n ",
    86: "Não falamos\nque não avisamos",
    87: "Vamos nos mandar\ndaqui, logo!",
    88: "GIRT achou\num colega fedor\nchamado TOE.",
    89: "Ele era dificil\nde conviver.\n ",
    90: "GIRT morou naquele\napartamento até\nmorrer.",
    91: "e logo...\n \n ",
    92: "GIRT conseguiu\nvoltar para o \nAPTO DO TOE.",
    93: "Ele morou naquele\napartamento até\nmorrer.",
    94: "Desculpa,\nGirt...",
    95: "Odeio fazer\nisso contigo..mas",
    96: "você não pode\nficar aqui se",
    97: "não ajudar\ncom as contas.",
    98: "Girt, espera!",
    99: "Conheço um\ncara, o HUD.",
   100: "Não o suporto\nmas",
}


def encode_rom(text: str) -> bytes:
    """Converte texto PT-BR para bytes do ROM (acentos → bytes especiais)."""
    mapped = "".join(ACCENT_MAP.get(c, c) for c in text)
    return mapped.encode("latin-1", errors="replace")


def byte_count(text: str) -> int:
    """Conta bytes que a tradução ocupa no ROM (sem o \x00 final)."""
    return len(encode_rom(text))


def validate(num: int, tr: str, original: str, size_csv: int) -> str | None:
    """
    Verifica regras:
    - mesma qtd de \n
    - máx 18 chars por linha
    - byte_count(tr) + 1 ≤ size_csv + 1  (text_editor usa size = len+1)
    Retorna mensagem de erro ou None se OK.
    """
    orig_lines = original.split("\n")
    tr_lines   = tr.split("\n")
    if len(orig_lines) != len(tr_lines):
        return f"#{num}: linhas orig={len(orig_lines)} tr={len(tr_lines)}"
    for i, ln in enumerate(tr_lines):
        if len(ln) > 18:
            return f"#{num} linha {i+1}: '{ln}' ({len(ln)} chars > 18)"
    avail = size_csv + 1          # text_editor.py convention: size includes \x00
    used  = byte_count(tr) + 1    # +1 for \x00
    if used > avail:
        return f"#{num}: {used} bytes > {avail} disponíveis"
    return None


def read_strings_100() -> list[dict]:
    rows = []
    with open(CSV_IN, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normaliza offset para 6 dígitos hex (formato text_editor.py)
            raw_offset = row.get("text_offset", row.get("offset_hex", "")).strip()
            val = int(raw_offset, 16)
            offset_hex = f"0x{val:06X}"

            skip_val = row.get("skip", "0").strip().upper()
            skip = skip_val in ("1", "SIM", "YES", "TRUE")

            original = row.get("original", "")
            # Detecta dev comment por linha > 30 chars
            if not skip and any(len(ln) > 30 for ln in original.split("\n")):
                skip = True

            rows.append({
                "num":        int(row["num"]),
                "offset_hex": offset_hex,
                "ctrl":       row["ctrl"].strip(),
                "size":       int(row["size"]),
                "original":   original,
                "traducao":   "",
                "skip":       skip,
            })
    return rows


def save_csv(rows: list[dict], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "offset_hex", "ctrl", "size", "original_en", "traducao_pt", "skip"])
        for r in rows:
            w.writerow([
                r["num"],
                r["offset_hex"],
                r["ctrl"],
                r["size"] + 1,      # text_editor.py: size inclui \x00
                r["original"],
                r["traducao"],
                "1" if r["skip"] else "0",
            ])


def apply_to_rom(rows: list[dict]) -> tuple[int, list[str]]:
    if not os.path.exists(ROM_IN):
        print(f"ERRO: ROM original não encontrada: {ROM_IN}")
        return 0, []

    with open(ROM_IN, "rb") as f:
        data = bytearray(f.read())

    applied = 0
    errors  = []

    for r in rows:
        tr = r["traducao"].strip()
        if not tr or r["skip"]:
            continue

        tr_bytes = encode_rom(tr) + b"\x00"
        avail    = r["size"] + 1   # disponível inclui \x00

        if len(tr_bytes) > avail:
            errors.append(f"  {r['offset_hex']}: '{tr}' ({len(tr_bytes)}b > {avail}b)")
            continue

        offset = int(r["offset_hex"], 16)
        payload = tr_bytes + b"\x00" * (avail - len(tr_bytes))
        data[offset : offset + avail] = payload
        applied += 1

    with open(ROM_OUT, "wb") as f:
        f.write(data)

    return applied, errors


def main():
    print("=== traducao_batch.py ===")

    rows = read_strings_100()
    print(f"Strings carregadas: {len(rows)}")

    erros_validacao = []
    traduzidas = 0

    for r in rows:
        num = r["num"]
        if r["skip"]:
            continue
        tr = TRADUCOES.get(num)
        if tr is None:
            continue

        err = validate(num, tr, r["original"], r["size"])
        if err:
            erros_validacao.append(err)
            print(f"  [ERRO validação] {err}")
            continue

        r["traducao"] = tr
        traduzidas += 1

        # Salva CSV parcial a cada 10 traduções
        if traduzidas % 10 == 0:
            save_csv(rows, CSV_OUT)
            print(f"  [{traduzidas:3d}] CSV parcial salvo ({CSV_OUT})")

    # Salva CSV final
    save_csv(rows, CSV_OUT)
    print(f"\nTraduções aplicadas: {traduzidas}")
    if erros_validacao:
        print(f"Erros de validação: {len(erros_validacao)}")

    # Aplica no ROM
    print(f"\nAplicando no ROM...")
    aplicadas, erros_rom = apply_to_rom(rows)
    print(f"Strings gravadas na ROM: {aplicadas}")
    if erros_rom:
        print(f"Erros ao gravar ({len(erros_rom)}):")
        for e in erros_rom:
            print(e)

    print(f"\nROM salva em: {ROM_OUT}")
    print("Concluído.")


if __name__ == "__main__":
    main()
