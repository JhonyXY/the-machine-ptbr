#!/usr/bin/env python3
"""
traducao_batch_2.py — strings 101–200
Lê strings_101_200.csv, grava traducao.csv (append/merge) e aplica no ROM.
"""

import csv, os

ROM_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_IN  = os.path.join(ROM_DIR, "The Machine (U) [C].gbc")
ROM_OUT = os.path.join(ROM_DIR, "The Machine (U) [C]_PTBR.gbc")
CSV_IN  = os.path.join(ROM_DIR, "strings_101_200.csv")
CSV_OUT = os.path.join(ROM_DIR, "traducao.csv")

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

TRADUCOES = {
    101: "Ele mora nesse\napartamento na",
    102: "nivel baixo.",
    103: "Talvez possa\nmorar lá?",
    104: "Ah, só porque\nconseguiu um\nemprego novo",
    105: "bom demais pra\nesse lugar?\n",
    106: "Já entendi.\nAchou alguém\npara substituir?",
    107: "alugar seu quarto?\nSim, imaginei\nque não.",
    108: "Pode tipo...\n",
    109: "Me arranja um\nemprego? ",
    110: "Quero grana\ntambém.",
    111: "Durma na sua\ncama um pouco",
    112: "antes do\nemprego!",
    113: "É seu primeiro\ndia de trabalho.",
    114: "Não se\natrase!",
    115: " Vá à\n ACADEMIA POLICIAL",
    116: " terminar\n treinamento.",
    117: "É seu primeiro\ndia de trabalho.\n ",
    118: "Vá para a\ndelegacia\nde policia!",
    119: " Vá ao seu novo\n emprego pra\n GHAN!",
    120: " Fica na\n MANSÃO do GHAN\n no andar L.",
    121: " Foi marcado\n no seu\n mapa.",
    122: " Um POLICIAL\n esteve aqui\n te procurando.",
    123: " Que loucura\n você está\n se metendo?",
    124: "Este é TOE.\nEle é seu\ncolega.",
    125: "Desculpe as\nunhas dos dedos\nna pia.",
    126: "Vou limpar isso\namanhã.\n",
    127: "Sei que você\nprecisa ir\npelo meu quarto",
    128: "pra ir ao\nbanheiro...\n",
    129: "mas peça antes\nde entrar,\nok.",
    130: "Acho que é\nsua vez",
    131: "de levar o lixo\npara fora.",
    132: "Cara, tem algo\ncheirando na\ncozinha...",
    133: "Acho que vi um\nrato antes",
    134: "mas perdi ele\nde vista.",
    135: "A pia não\nfunciona. Está\nentupida.",
    136: "A banheira...\nSeria bom se o\nTOE a usasse de",
    137: "vez em quando..",
    138: "Não há porta no\nbanheiro, então\nvocê",
    139: "vai quando o\nTOE estiver na\ncozinha.",
    140: "Usar o privada?",
    141: "Você segurou\nisso por um\ntempo.",
    142: "Muito cedo pra\ndormir. Melhor\nir fazer coisas!",
    143: "Não dá pra dormir.\nÉ o meio do\ndia agora.",
    144: "Ir dormir\npela noite?",
    145: "TOE ficaria\nbravo se você\ndormisse lá.",
    146: " TOE comeu\n sua comida.\n ",
    147: " Mas deixou\n toda sua comida\n podre.",
    148: " Você não está\n com TANTA fome.\n ",
    149: "É sua nova\nPEDRA PET!",
    150: "É sua nova\nFORMIGUEIRO!",
    151: "É sua nova\nPEIXEIRA!",
    152: "É seu novo\nCLICADOR!",
    153: "É sua nova\nBLOB LAMP!",
    154: "Pedra Pet",
    155: "Formigas",
    156: "Aquário",
    157: "Clicador",
    158: "Blob Lamp",
    159: "Oh! Estão\nsorteando os\nnúmeros!",
    160: "Quer ver dicas\nsobre onde ir",
    161: "ou o que fazer\na seguir?",
    162: " TUTORIAIS    $\n ATIVADOS",
    163: " TUTORIAIS     )\n DESATIV.",
    164: "Sair para\na tela\ninicial?",
    165: "Perderá o\nprogresso\nnão salvo.",
    166: "               $\nDADOS SALVOS\n",
    167: "Alguns\nprotestaram as\ncondições brutais",
    168: "que trabalhavam,\nmas a midia\nvirou a população",
    169: "a população\ncontra eles.\n ",
    170: "A policia\nprendeu todos.\n ",
    171: "Agora que acabou\no trabalho,\nvocê pode",
    172: "o que quiser\npelo resto\ndo dia.",
    173: "Quando acabar,\nvá pra casa \ndormir.",
    174: "Ei Girt.. Estamos\nfuriosos com\naquele concurso",
    175: "que o TERP fez\npara aumentar\na cota.",
    176: "Vamos ter uma\nreunião sobre\nisso.",
    177: "É no bar.\nQuer nos juntar?\n ",
    178: "que o TERP fez\ntentando aumentar\na cota.",
    179: " Eles ainda\n planejam\n aumentar.",
    180: " Sei que se\n você fez MAIS\n de DEZ, ele",
    181: " teria feito\n a cota ficar\n  PERMANENTE",
    182: "  em vez de\n  temporária...\n ",
    183: "OK, ótimo! Vamos\ntento chegar lá\nantes de começar",
    184: "Tudo bem... se\nvocê mudar\nde ideia",
    185: "estaremos aqui\nno bar.\n ",
    186: "Sabe.. depois que\najudou Terp",
    187: "a impor uma\ncota bem alta..",
    188: "Pode fazer os\ntrabalhadores te",
    189: "gostar de você\nse juntar....",
    190: "Bom dia, GIRT!\nTemos um grande\ndia à frente.",
    191: "Temos que filiar\ntodos no\nsindicato.",
    192: "Faça assinar\numa ficha\ndo sindicato",
    193: "Ei Girt... Eu\nsei que não quer\nentrar no",
    194: "sindicato... mas\ntenho um favor\na pedir,",
    195: "como amigo. Por\nfavor não diga ao\nTERP",
    196: "nada sobre o\nsindicato.\n ",
    197: "Lembre que nem\ntodos querem\nentrar...",
    198: "Então seja\nesperto na hora\nde perguntar.",
    199: "Serei demitido\nse você\nmencionar.",
    200: "OK, tomara que\nrecrutamos\ngente suficiente",
}


def encode_rom(text: str) -> bytes:
    mapped = "".join(ACCENT_MAP.get(c, c) for c in text)
    return mapped.encode("latin-1", errors="replace")


def byte_count(text: str) -> int:
    return len(encode_rom(text))


def validate(num: int, tr: str, original: str, size_csv: int) -> str | None:
    orig_lines = original.split("\n")
    tr_lines   = tr.split("\n")
    if len(orig_lines) != len(tr_lines):
        return f"#{num}: linhas orig={len(orig_lines)} tr={len(tr_lines)}"
    for i, ln in enumerate(tr_lines):
        if len(ln) > 18:
            return f"#{num} linha {i+1}: '{ln}' ({len(ln)} chars > 18)"
    avail = size_csv + 1
    used  = byte_count(tr) + 1
    if used > avail:
        return f"#{num}: {used} bytes > {avail} disponíveis"
    return None


def read_csv(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            raw_offset = row.get("text_offset", row.get("offset_hex", "")).strip()
            val = int(raw_offset, 16)
            skip_val = row.get("skip", "0").strip().upper()
            skip = skip_val in ("1", "SIM", "YES", "TRUE")
            original = row.get("original", "")
            if not skip and any(len(l) > 30 for l in original.split("\n")):
                skip = True
            rows.append({
                "num":        int(row["num"]),
                "offset_hex": f"0x{val:06X}",
                "ctrl":       row["ctrl"].strip(),
                "size":       int(row["size"]),
                "original":   original,
                "traducao":   "",
                "skip":       skip,
            })
    return rows


def load_existing_csv(path: str) -> dict:
    """Retorna dict offset_hex -> traducao_pt das traduções já salvas."""
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {r["offset_hex"]: r.get("traducao_pt", "") for r in csv.DictReader(f)}


def save_csv(rows: list[dict], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["#", "offset_hex", "ctrl", "size", "original_en", "traducao_pt", "skip"])
        for r in rows:
            w.writerow([r["num"], r["offset_hex"], r["ctrl"], r["size"] + 1,
                        r["original"], r["traducao"], "1" if r["skip"] else "0"])


def apply_to_rom(rows: list[dict]) -> tuple[int, list[str]]:
    if not os.path.exists(ROM_IN):
        print(f"ERRO: ROM não encontrada: {ROM_IN}")
        return 0, []

    # Se _PTBR já existe (batch anterior), parte dela; senão usa original
    src = ROM_OUT if os.path.exists(ROM_OUT) else ROM_IN
    with open(src, "rb") as f:
        data = bytearray(f.read())

    applied, errors = 0, []
    for r in rows:
        tr = r["traducao"].strip()
        if not tr or r["skip"]:
            continue
        tr_bytes = encode_rom(tr) + b"\x00"
        avail    = r["size"] + 1
        if len(tr_bytes) > avail:
            errors.append(f"  {r['offset_hex']}: '{tr}' ({len(tr_bytes)}b > {avail}b)")
            continue
        offset  = int(r["offset_hex"], 16)
        payload = tr_bytes + b"\x00" * (avail - len(tr_bytes))
        data[offset : offset + avail] = payload
        applied += 1

    with open(ROM_OUT, "wb") as f:
        f.write(data)
    return applied, errors


def main():
    print("=== traducao_batch_2.py (strings 101–200) ===")

    rows = read_csv(CSV_IN)
    print(f"Strings carregadas: {len(rows)}")

    erros, traduzidas = [], 0
    for r in rows:
        if r["skip"]:
            continue
        tr = TRADUCOES.get(r["num"])
        if tr is None:
            continue
        err = validate(r["num"], tr, r["original"], r["size"])
        if err:
            erros.append(err)
            print(f"  [ERRO] {err}")
            continue
        r["traducao"] = tr
        traduzidas += 1
        if traduzidas % 10 == 0:
            save_csv(rows, CSV_OUT)
            print(f"  [{traduzidas:3d}] CSV parcial salvo")

    save_csv(rows, CSV_OUT)
    print(f"\nTraduções aplicadas: {traduzidas}")
    if erros:
        print(f"Erros de validação: {len(erros)}")
        for e in erros:
            print(f"  {e}")

    print("\nAplicando no ROM...")
    aplicadas, erros_rom = apply_to_rom(rows)
    print(f"Strings gravadas: {aplicadas}")
    if erros_rom:
        for e in erros_rom:
            print(e)

    print(f"\nROM salva: {ROM_OUT}")
    print("Concluído.")


if __name__ == "__main__":
    main()
