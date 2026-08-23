# Chapada Diamantina 2026

Roteiro interativo da viagem a Chapada Diamantina, Bahia (17/10 a 22/10).

🔒 Site local — não publicado. Para publicar, defina `features.publish` como `"pages"` ou `"netlify"` no `trip.json` e rode o build de novo.

## Páginas

- `index.html` — 🗓️ Roteiro
- `hospedagem.html` — 🏨 Hospedagem
- `mapa.html` — 🌍 Mapa
- `opcoes.html` — 🍽️ Cardápio de opções

## Como atualizar

O conteúdo vem todo de `trip.json`. **Não edite o HTML gerado** — ele é sobrescrito a cada build.

```bash
# 1. edite trip.json
python3 <caminho-da-skill>/scripts/build.py    # 2. regenere o site
git add -A && git commit -m "Atualiza roteiro" && git push   # 3. versione
```

Não há deploy configurado: o `git push` só versiona os arquivos.

## Stack

HTML + CSS + JavaScript vanilla, sem build step em runtime. Gerado pela skill `agente-viagem`.
