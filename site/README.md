# Chapada Diamantina 2026

Roteiro interativo da viagem a Chapada Diamantina, Bahia (17/10 a 23/10).

🌐 **[Ver o site](https://chapada-diamantina-2026.netlify.app/)** — hospedado no Netlify

## Páginas

- `index.html` — 🗓️ Roteiro
- `hospedagem.html` — 🏨 Hospedagem
- `mapa.html` — 🌍 Mapa
- `atracoes.html` — 📸 Atrações
- `restaurantes.html` — 🍽️ Restaurantes

## Como atualizar

O conteúdo vem todo de `trip.json`. **Não edite o HTML gerado** — ele é sobrescrito a cada build.

```bash
# 1. edite trip.json
python3 <caminho-da-skill>/scripts/build.py    # 2. regenere o site
git add -A && git commit -m "Atualiza roteiro" && git push   # 3. versione
```

O Netlify republica sozinho a cada push em `main`.

## Stack

HTML + CSS + JavaScript vanilla, sem build step em runtime. Gerado pela skill `agente-viagem`.
