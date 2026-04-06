# The Machine (GBC) — Tradução PT-BR

Projeto comunitário de tradução do jogo **The Machine** (Game Boy Color) para o **Português Brasileiro**.

> ⚠️ Este repositório **não contém a ROM**. Você precisa obter o arquivo `.gbc` original por conta própria.

## Release PT-BR

A build final da tradução já foi fechada e validada localmente. Para jogar, aplique o patch `IPS` em uma dump limpa de **The Machine (U) [C].gbc**.

- Patch: [`The Machine (U) [C]_PTBR.ips`](./The%20Machine%20%28U%29%20%5BC%5D_PTBR.ips)
- Status: `7.857/7.857` strings traduzidas
- Validação: patch testado em ROM limpa e conferido byte a byte contra a build final
- Guia técnico: [`RELEASE-NOTES.md`](./RELEASE-NOTES.md)

Se você quiser ajudar com revisão, ajustes de linha ou correções de contexto, o fluxo recomendado é abrir PR em cima de `traducao.csv` e seguir os limites de texto do projeto.

---

## Progresso

| Total de strings | Traduzidas | Progresso |
|---|---|---|
| 7.857 | 7.857 | 100% |

```
[████████████████████████████████████████████████] 100%
```

---

## Requisitos

- Python 3.10+
- ROM original: `The Machine (U) [C].gbc` (você precisa providenciar)

---

## Ferramentas

### `text_editor.py` — Editor visual de strings
Interface gráfica para editar e aplicar traduções na ROM.

```
python text_editor.py
```

- Lista todas as strings do jogo com status visual (branco = sem tradução, verde = traduzido, cinza = dev comment)
- Indicadores de limite de linha (máx. 18 chars) e espaço em bytes
- Importar/exportar `traducao.csv`
- Botão "Aplicar no ROM" → gera `The Machine (U) [C]_PTBR.gbc`

**Atalhos:**
| Tecla | Ação |
|---|---|
| `Ctrl+S` | Salvar tradução atual |
| `Ctrl+N` | Próxima string sem tradução |
| `Alt+↑ / ↓` | Navegar entre strings |

---

### `tile_viewer.py` — Editor de tiles da fonte
Edita os pixels dos caracteres no ROM (usado para desenhar os acentos PT-BR).

```
python tile_viewer.py
```

---

### `extract_strings.py` — Extrator de strings
Extrai todas as strings de texto da ROM para CSV.

---

## Acentos suportados

Os seguintes acentos PT-BR foram desenhados manualmente nos tiles da fonte:

| Char | Byte ROM |
|------|----------|
| ã / Ã | `0xA6` |
| ç / Ç | `0xA7` |
| é / É | `0xA8` |
| ó / Ó | `0xA9` |
| á / Á | `0xAA` |
| ú / Ú | `0xAB` |
| ê / Ê | `0xAC` |
| ô / Ô | `0xAD` |
| õ / Õ | `0xAE` |
| à / À | `0xAF` |
| í / Í | `0xB1` |
| â / Â | `0xB2` |

---

## Como contribuir

1. Clone o repositório
2. Coloque a ROM original (`The Machine (U) [C].gbc`) na pasta do projeto
3. Execute `python text_editor.py`
4. Traduza ou ajuste as strings respeitando as regras abaixo
5. Exporte `traducao.csv` e abra um Pull Request

### Regras de tradução

- **Máx. 18 chars por linha** — o jogo não faz word-wrap
- **Mesma quantidade de `\n` que o original** — não adicionar quebras extras
- **Bytes da tradução ≤ bytes do original** — não pode exceder o espaço disponível
- Cada acento conta como **1 byte** (igual a uma letra normal)
- Use apenas os acentos da tabela acima

### Build e patch

- O patch distribuível é `The Machine (U) [C]_PTBR.ips`
- A ROM traduzida é gerada apenas para validação local
- Para testes, sempre parta de uma dump limpa da ROM original

---

## Estrutura do repositório

```
.
├── text_editor.py          # Editor de texto principal
├── tile_viewer.py          # Editor de tiles da fonte
├── extract_strings.py      # Extrator de strings da ROM
├── traducao.csv            # Arquivo mestre de traduções
└── README.md
```

---

## Licença

Este projeto é distribuído sob a licença MIT. A ROM do jogo **não está incluída** e é propriedade de seus respectivos detentores de direitos. Use este projeto apenas com uma cópia legítima do jogo.
