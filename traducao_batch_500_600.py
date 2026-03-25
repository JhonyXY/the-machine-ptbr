#!/usr/bin/env python3
"""
traducao_batch_500_600.py — strings 501–600
Lê traducao.csv, preenche traducao_pt para #501–600, salva e aplica no ROM.
"""

import csv, os

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

TRADUCOES = {
    501: "Jukebox",
    502: " O JUKEBOX é\n GRÁTIS pois você\n tem VIP PASS!",
    503: "Pagar %00.25 pra\numa música no\njukebox?",
    504: "Erro: rollover\nneg.- jogador sem\ndinheiro sufic.",
    505: "Ficou sem\ntrocado!",
    506: "Quem diabos é\nvocê? O que é\nesse traje?",
    507: "Ei, se for espião\nme ajude e\nperturbe a MSS!",
    508: "Sempre quis poder\nbagunçar tudo\no que eles fazem",
    509: "por dentro...\n \n ",
    510: "Agora sabemos\nde que lado está.",
    511: "Perdemos os paus\nda mesa.",
    512: "Não era tão\ndivertido assim.",
    513: "A física é\ndifícil calcular.",
    514: "O que você\nestá fazendo aqui?",
    515: "Por que não vai\nlamber as botas?",
    516: "Nada como uma\nbeba boa depois",
    517: "de trabalhar\nmuito!",
    518: "Eu? Gosto das\ncorridas.",
    519: "Posso apostar pra\nvocê quando estou",
    520: "lá no\nhipódromo.",
    521: "Quer apostar na\ncorrida?",
    522: "O que acha?\n",
    523: " Apostar na\n corrida?",
    524: "Você é do\nmeu tipo!",
    525: "Quanto vai\napostar?",
    526: "Pode perder\ntudo...",
    527: "MAS se ganhar\nvocê leva",
    528: "QUATRO VEZES\no apostado.",
    529: "Quanto vai\napostar? ",
    530: "Erro rollover\nneg.- verifique se\no jogador tem",
    531: "dinheiro\nantes de executar\nesse script.",
    532: "Parece que\nestamos no mesmo\nbarco...",
    533: "Não dá pra ganhar\ngrande sem grana\nassim...",
    534: "...em qual cavalo\nvocê aposta\no seu dinheiro?",
    535: "Certo, boa\nsorte!",
    536: "Pra mim tanto\nfaz mesmo!",
    537: "Só ia fazer\ncomo um favor!",
    538: "Sabe... as\nmeninas me amam\nde verdade!",
    539: "Infelizmente elas\nnão vêm a este\nlixeiro aqui...",
    540: "Alguém apoia o\nPartido Ovelha.",
    541: "Parabéns GIRT!\nEspero que consiga",
    542: "boas leis\naprovar.",
    543: "Estou bem\nsurpreso que um\nchanceler VOLF",
    544: "tenha taxado\nos ricos...\n ",
    545: "Trabalho incrivel\napoiando as\nUNIÕES!",
    546: "Nunca pensei que\ndiria isso pra um\nchanceler VOLF",
    547: "...mas tem meu\nvoto!\n ",
    548: " Estou surpreso\n que mostraria\n a cara aqui.",
    549: "Não sei por que\ntanto cara da\nMSS aqui...",
    550: "Boa sorte na\ncampanha,\nsenhor!",
    551: "Estamos todos\ncom você\na cem por cento.",
    552: "Qualquer um do\nsindicato pode\nusar o quarto.",
    553: "Só... não faça\nnada muito louco\nlá dentro.",
    554: "É uma honra\nte conhecer, sir.\n ",
    555: "MAWA vai prover\nsegurança extra\npara você.",
    556: "-Não confiamos\n na MSS.-\n ",
    557: "Pode entrar,\nsir!",
    558: "Mostrou a\nCARTEIRA DA UNIÃO.",
    559: "Oi Girt- Bom te\nver- Pode entrar.",
    560: "Desculpa, o\nquarto dos fundos\né restrito.",
    561: "...e você parece\nbastante\nsuspeito.",
    562: "A MSS vai fazer\ntudo que puder",
    563: "pela sua\nsegurança, sir!",
    564: "Vai andando,\namigo.",
    565: "Vim tomar uma beba\ndepois do trampo.",
    566: "Como todo\nmundo.",
    567: "Quer que a\ngente te leve\npara casa agora?",
    568: "Sinto muito, sir.\nPela sua segurança",
    569: "não posso deixar\nvocê sair agora.",
    570: "Te levaremos pra\ncasa ao final do",
    571: "dia.",
    572: "GIRT! Não\nfuja antes",
    573: "de completar\na missão!",
    574: "Ok, aja natural\ne espere",
    575: "para o bar\nabrir.",
    576: "Bom que pôde\nvir.\n ",
    577: "Droga...\nPensei que era\num de nós.",
    578: "O que eles\ndiscutiram,\nGIRT?",
    579: "Não é bom...\nEssas\norganizações",
    580: "ameaçar a\nSEGURANÇA\nda máquina!",
    581: "Creio que foi\ninfo errada.\n ",
    582: "Vamos tratar\nessa fonte\ncom mais",
    583: "desconfiança\nno futuro.\n ",
    584: "Bem, acabou\npor hoje.\nDescanse um pouco.",
    585: "Te vejo\nde volta no QG\nda MSS amanhã.",
    586: "Temos ordens de\nte prender,\nGIRT.",
    587: "EU SABIA que não\npodíamos confiar!",
    588: "Não pode prender\nalguém\nsem motivo!",
    589: "Temos muitos\nmotivos...\nMentiras, traição",
    590: "...o que mais\ninventarmos.\n ",
    591: "Afinal temos\npoder agora.\n ",
    592: "Estou seguindo\nas ordens do\nchanceler eleito",
    593: "Pega ele.\n \n ",
    594: "TIO BOP: É aqui\nque vão",
    595: "te transformar\nnum policial.",
    596: "Fique longe\nde encrenca! ",
    597: "TIO BOP: Tenho\norgulho de você.",
    598: "Te acompanho\nde volta até",
    599: "até a delegacia.",
    600: "TIO BOP: Acabou\no treinamento,\nhein?",
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
    avail = size_csv
    used  = byte_count(tr) + 1
    if used > avail:
        return f"#{num}: {used} bytes > {avail} disponíveis"
    return None


def update_csv(path: str) -> list[dict]:
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
        if any(len(l) > 30 for l in original.split("\n")):
            print(f"  #{num}: pulado (dev comment)")
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
        print(f"Erros: {len(erros)}")
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
        if num not in range(501, 601):
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
    print("=== traducao_batch_500_600.py ===")
    rows = update_csv(CSV_IO)
    print("\nAplicando no ROM...")
    aplicadas, erros_rom = apply_to_rom(rows)
    print(f"Strings gravadas na ROM: {aplicadas}")
    for e in erros_rom:
        print(e)
    print(f"\nROM salva em: {ROM_OUT}")
    print("Concluído.")


if __name__ == "__main__":
    main()
