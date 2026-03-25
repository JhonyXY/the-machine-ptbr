#!/usr/bin/env python3
"""
traducao_batch_400_500.py — strings 400–500
Lê traducao.csv, preenche traducao_pt para #400–500, salva e aplica no ROM.
"""

import csv, os, io

ROM_DIR = os.path.dirname(os.path.abspath(__file__))
ROM_IN  = os.path.join(ROM_DIR, "The Machine (U) [C].gbc")
ROM_OUT = os.path.join(ROM_DIR, "The Machine (U) [C]_PTBR.gbc")
CSV_IO  = os.path.join(ROM_DIR, "traducao.csv")

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

# Regras: máx 18 chars/linha, mesma qtd de \n do original,
#         byte_count(tr)+1 ≤ size (traducao.csv já inclui \x00 no size)
TRADUCOES = {
    400: "O candidato da\nMAWA foi\nbaleado!",
    401: "Eu sei... É\ninsano!\n ",
    402: "...e olha o\ndetalhe...\n ",
    403: "Querem que\nachemos alguém\npara substituir.",
    404: "Pelo visto,\nnossa união\nfez impacto",
    405: "impressão no\npartido.\n ",
    406: "Quem você quer\nindicar para\no cargo?",
    407: "Você... Vai\nnomear a\nsi mesmo?",
    408: "Isso não parece\num tanto\ninteresseiro?",
    409: "Sendo honesto,\nGIRT...\n ",
    410: "Não acho que\neu apoiaria\nessa decisão.",
    411: "Aposto que a\nmaioria da união\ntambém não.",
    412: "Vou dizer o\nque você quis,\nmas não acho",
    413: "que você vai\nser eleito.\n ",
    414: "Uau! Você ia\nme escolher?\nValeu GIRT!",
    415: "Darei o meu\nmelhor. Valeu\npelo apoio",
    416: "por me oferecer\nessa chance. Não\nvou esquecer!",
    417: "Acho que devo\ncomeçar a\ncampanha!",
    418: "Como sou o\nlider da\nunião...",
    419: "Eu te escolho.\nÉ em você\nque confio.",
    420: "E aí, o que\nacha? Vai se\ncandidatar?",
    421: "Incrivel! Tenho\ntotal fé em\nvocê.",
    422: "Vai ser uma\ngrande mudança.\nVocê vai poder",
    423: "ter um lugar\nmaior!\n ",
    424: "Vou sentir\nfalta de você\nna fábrica.",
    425: "Boa sorte, GIRT!\n \n ",
    426: "OK, respeito\nsua decisão. Só\nprecisava",
    427: "te oferecer\no cargo\nprimeiro.",
    428: "Relaxa.\nVou achar\noutra pessoa.",
    # 429: skip — dev comment
    430: "GIRT! Não se\ndistraia!",
    431: "Esta negociação\né importante!",
    432: "Ei, você!",
    433: "Com licença",
    434: "Posso dizer,\nguri... Curti\nseu estilo!",
    435: "Você não deixa\nessa galera\nda união",
    436: "te atropelar.\nVocê cuida\nde si mesmo.",
    437: "Que tal vir\nfalar comigo\nno escritório?",
    438: "Os caras do bar\njá sabiam.",
    439: "Você fez isso,\nGIRT! Deu\nesperança a todos",
    440: "de novo!\nTalvez possamos\nmelhorar a Máquina",
    441: "um lugar melhor\npra todos\nviverem!",
    442: " Bebidas\n POR CONTA\n DA CASA!!!",
    443: "Oi, Girt.\nQue bom que\nvocê veio.",
    444: "Então, temos\nfalado sobre\ncomo",
    445: "tudo no trabalho\nsó piora a\ncada dia.",
    446: "Eles ficam pedindo\nmais a cada dia\ne o nosso",
    447: "salário não\nsobe.\n ",
    448: "Vamos tentar\ncomeçar um\nsindicato.",
    449: "Vai exigir que\nenfrentemos\nalgum risco.",
    450: "Você toparia\ndar uma\nmão?",
    451: "Que ótimo!\nFalamos mais\namanhã.",
    452: "Aqui está sua\ncarteirinha.\n ",
    453: "Droga, Girt...\nJulgava você\num de nós.",
    454: "Obrigado por\nentrar! Até\namanhã.",
    455: "Você perdeu\na reunião.",
    456: "OK GIRT... Fique\nperto do canto\nda máquina",
    457: "de vendas no\nfim do bar.\n ",
    458: "Não pode dar\npanfletos aqui\nno bar.",
    459: "Todos aqui\nsão MAWA mesmo.\n ",
    460: "DUKE é aposta\ncerta! Que\ncavalo saudável!",
    461: "DAISY está de\nvolta à glória!",
    462: "PEPPER é uma\ncuringa! Nunca",
    463: "se sabe o que\nesperar.",
    464: "Sempre tive um\ncarinho por\nHANK.",
    465: "Uau!...a\n DUMPY ganhou",
    466: "Nunca imaginei\nque veria isso.",
    467: "Sua carteira está\ncheia! Deposite\ndinheiro no banco.",
    468: " Ganhou %4.00",
    469: " Ganhou %8.00",
    470: " Ganhou %20.00",
    471: "Conquista\nDesbloqueada\n      #ALL-OUT",
    472: " Ganhou %40.00",
    473: "Mais sorte da\npróxima vez!\n ",
    474: "Ouvi um boato\nque DUKE é uma\nboa aposta.",
    475: "Ouvi um boato\nque DAISY é uma\nboa aposta.",
    476: "Ouvi um boato\nque PEPPER é uma\nboa aposta.",
    477: "Ouvi um boato\nque HANK é uma\nboa aposta.",
    478: "Ouvi um boato\nque DUMPY é uma\nboa aposta.",
    479: " Espera... Você é\n CHANCELER\n agora?",
    480: " Droga- Devia\n ter me mantido\n informado!",
    481: "Sim, sim, sim,\njá entendi...\nvocê é chanceler..",
    482: " Vai esfregando\n isso sim,\n seu metido.",
    483: " Como vai você,\n Girt?",
    484: " Vivendo o\n sonho?",
    485: "  Saúde,\n  amigo!",
    486: " Queima ao\n descer.\n ",
    487: " Uma sensação\n agradável\n te invade.",
    488: " Não era muito\n forte.",
    489: " Talvez um pouco\n aguado...",
    490: " ...mas serve\n bem.",
    491: " Por algum motivo\n tem um gosto",
    492: " amargo. Mas\n tudo bem.",
    493: "ERRO: Não\ntem dinheiro",
    494: " Sinto, GIRT, você\n não tem o",
    495: " dinheiro...e não\n posso fazer",
    496: " uma conta mais\n pra você.",
    497: " Boa viagem,\n amigo.",
    498: "Máq. de vendas",
    499: "É uma máquina\nvelha e estragada.",
    500: "Interação Sapo",
}


def encode_rom(text: str) -> bytes:
    mapped = "".join(ACCENT_MAP.get(c, c) for c in text)
    return mapped.encode("latin-1", errors="replace")


def byte_count(text: str) -> int:
    return len(encode_rom(text))


def validate(num: int, tr: str, original: str, size_csv: int) -> str | None:
    """
    size_csv vem de traducao.csv — já inclui o \x00 no total.
    """
    orig_lines = original.split("\n")
    tr_lines   = tr.split("\n")
    if len(orig_lines) != len(tr_lines):
        return f"#{num}: linhas orig={len(orig_lines)} tr={len(tr_lines)}"
    for i, ln in enumerate(tr_lines):
        if len(ln) > 18:
            return f"#{num} linha {i+1}: '{ln}' ({len(ln)} chars > 18)"
    avail = size_csv          # traducao.csv já inclui \x00
    used  = byte_count(tr) + 1
    if used > avail:
        return f"#{num}: {used} bytes > {avail} disponíveis"
    return None


def update_csv(path: str) -> list[dict]:
    """Lê traducao.csv, preenche traduções 400-500, retorna rows e salva."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(dict(row))

    erros, traduzidas = [], 0
    for row in rows:
        num = int(row["#"])
        if num not in TRADUCOES:
            continue
        skip = row.get("skip", "0").strip()
        if skip in ("1", "SIM", "YES", "TRUE"):
            continue

        tr       = TRADUCOES[num]
        original = row.get("original_en", "")
        size_csv = int(row["size"])

        # Detecta dev comment
        if any(len(l) > 30 for l in original.split("\n")):
            print(f"  #{num}: pulado (dev comment detectado)")
            continue

        err = validate(num, tr, original, size_csv)
        if err:
            erros.append(err)
            print(f"  [ERRO] {err}")
            continue

        row["traducao_pt"] = tr
        traduzidas += 1
        if traduzidas % 10 == 0:
            _write_csv(path, fieldnames, rows)
            print(f"  [{traduzidas:3d}] CSV parcial salvo")

    _write_csv(path, fieldnames, rows)
    print(f"\nTraduções válidas: {traduzidas}")
    if erros:
        print(f"Erros de validação: {len(erros)}")
        for e in erros:
            print(f"  {e}")

    return rows


def _write_csv(path: str, fieldnames, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def apply_to_rom(rows: list[dict]) -> tuple[int, list[str]]:
    src = ROM_OUT if os.path.exists(ROM_OUT) else ROM_IN
    if not os.path.exists(src):
        print(f"ERRO: ROM não encontrada: {src}")
        return 0, []

    with open(src, "rb") as f:
        data = bytearray(f.read())

    applied, errors = 0, []
    for row in rows:
        num = int(row["#"])
        if num not in range(400, 501):
            continue
        tr = row.get("traducao_pt", "").strip()
        if not tr:
            continue
        skip = row.get("skip", "0").strip()
        if skip in ("1", "SIM", "YES", "TRUE"):
            continue

        tr_bytes = encode_rom(tr) + b"\x00"
        avail    = int(row["size"])
        if len(tr_bytes) > avail:
            errors.append(f"  {row['offset_hex']}: ({len(tr_bytes)}b > {avail}b)")
            continue

        offset  = int(row["offset_hex"], 16)
        payload = tr_bytes + b"\x00" * (avail - len(tr_bytes))
        data[offset : offset + avail] = payload
        applied += 1

    with open(ROM_OUT, "wb") as f:
        f.write(data)
    return applied, errors


def main():
    print("=== traducao_batch_400_500.py ===")

    if not os.path.exists(CSV_IO):
        print(f"ERRO: {CSV_IO} não encontrado")
        return

    rows = update_csv(CSV_IO)

    print("\nAplicando no ROM...")
    aplicadas, erros_rom = apply_to_rom(rows)
    print(f"Strings gravadas na ROM: {aplicadas}")
    if erros_rom:
        for e in erros_rom:
            print(e)

    print(f"\nROM salva em: {ROM_OUT}")
    print("Concluído.")


if __name__ == "__main__":
    main()
