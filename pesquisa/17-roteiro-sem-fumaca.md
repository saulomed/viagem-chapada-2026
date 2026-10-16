# Roteiro sem a Fumaça — decisão de 16/10/2026

Decidido por Saulo em 16/10/2026, depois das alternativas de `16-alternativas-sem-fumaca.md`. É uma variação da Opção 2 dele: a Torrinha entra junto com a Lapa Doce, e o Pai Inácio vai para o domingo.

## O que mudou

| Dia | Antes | Agora | Dorme |
|---|---|---|---|
| Sáb 17 | Juazeiro → Vale do Capão (526 km · 8h31) | **Juazeiro → Lençóis (489 km · 7h38)**, tarde livre | Lençóis — Hospedagem do Sítio |
| Dom 18 | Fumaça por cima, almoço no Capão, Pai Inácio, Lençóis | **Lapa Doce e Torrinha de manhã, pausa na pousada, Pai Inácio no pôr do sol** | Lençóis — Hospedagem do Sítio |
| Seg 19 a Qua 21 | — | sem mudança | — |
| Qui 22 | Ibicoara → Iraquara, Lapa Doce decidida na hora, Pratinha | **Ibicoara → Pratinha direto** | Lençóis — Alto do Cajueiro |

## Hospedagem

- **Canceladas pelo grupo:** Pousada Bela Vista do Capão (17/10) e Pousada Alto do Cajueiro (18/10). A Alto do Cajueiro de 22/10 continua valendo.
- **Nova reserva:** Hospedagem do Sítio, Lençóis, noites de 17 e 18/10. Fica a 0,6 km do centro, com nota 9,6 na Booking (128 avaliações).
- **Valor fechado:** R$ 660 o quarto pelas duas noites (R$ 330 a diária, R$ 1.320 os dois casais), informado por Saulo em 16/10/2026. Café da manhã e prazo de cancelamento ainda não foram informados.
- Total das seis diárias: **R$ 3.767,50**, ou R$ 1.883,75 por casal. A conta é R$ 1.320 + R$ 769,50 + R$ 1.160 + R$ 518.
- O total anterior, de R$ 3.697,50, não fechava com as linhas da época: a soma delas dava R$ 3.541,50. O número novo foi refeito do zero a partir das reservas.

## Distâncias medidas no Google Maps em 16/10/2026

| Trecho | Distância | Tempo |
|---|---|---|
| Lençóis → Gruta Lapa Doce | 67,1 km | 1h22 |
| Gruta Lapa Doce → Caverna Torrinha | 2,7 km | 6 min |
| Caverna Torrinha → Lençóis | 64,0 km | 1h21 |
| Lençóis → Morro do Pai Inácio | 29,2 km | 44 min |
| Ibicoara → Fazenda Pratinha (BA-142 e BR-242) | 248 km | 3h49 |
| Fazenda Pratinha → Lençóis | 48,0 km | 1h10 |

- **Rota mais curta de Ibicoara:** o Maps também oferece 167 km e 3h09 entre Ibicoara e a Pratinha. Pela distância, é o atalho por Guiné e Palmeiras, com ~60 km de terra, que o grupo já tinha descartado (`07-roteiro-definido.md`). O roteiro segue pela BR-242.
- **Pai Inácio:** o tempo Lençóis → Pai Inácio veio 44 min, contra os ~35 min anteriores. O Maps indicava trânsito mais lento que o normal na hora da consulta.

## O domingo, hora a hora

O domingo tem dois relógios. No domingo, a Lapa Doce tem o último grupo às 12h, segundo uma avaliação recente da própria página; o site oficial não publica horário. A subida do Pai Inácio só é liberada até as 17h.

| Hora | Programa |
|---|---|
| 07h30 | Saída de Lençóis |
| 09h–11h | Gruta da Lapa Doce |
| 11h–12h | Almoço no restaurante da Lapa Doce |
| 12h15–13h30 | Caverna Torrinha, num circuito de até ~1h15 (aberta todos os dias das 8h às 17h, R$ 30 a R$ 150 por circuito, segundo o site oficial) |
| 13h30–14h50 | Volta para Lençóis |
| 14h50–15h45 | Pausa na pousada |
| 15h45 | Saída para o Pai Inácio, com chegada ~16h30 |
| 17h42 | Pôr do sol |
| ~18h30 | Chegada a Lençóis |

**Plano B:** se as grutas atrasarem, o grupo vai da Torrinha direto ao Pai Inácio, que fica no caminho da volta, e passa na pousada depois do pôr do sol.

## O estado sincronizado (Netlify Blobs)

O documento `trip-state/chapada2026` guardava duas reservas marcadas no site antes da troca: a Bela Vista do Capão (17/10) e a Alto do Cajueiro (18/10). Como o app dava prioridade à marcação do aparelho, o dia 18 continuaria mostrando a Alto do Cajueiro mesmo depois da troca no `trip.json`.

- **Correção na skill:** o `app.js` da skill agora descarta qualquer marcação de reserva cuja base ou pousada não exista mais no `trip.json`. Vale para o roteiro e para o checklist.
- **Teste local:** a correção foi testada no site local com as duas marcações antigas injetadas, e o dia 18 mostrou a Hospedagem do Sítio.
- **Blob em produção:** limpo em 16/10/2026, com autorização de Saulo, por um PUT em `/api/state` feito pelo navegador já logado. As listas `lencois` e `capao` de `chapada2026_bookings` ficaram vazias, e o checklist sincronizado (`geral-carro`) não foi mexido.

## Ainda por confirmar

- Café da manhã e prazo de cancelamento da Hospedagem do Sítio.
- Horário de abertura e preço da Lapa Doce no domingo, pelo WhatsApp (75) 9 9821-9929.
- Forma de pagamento e prazo de cancelamento da Capão do Mel (pendência de `15-troca-hospedagem-ibicoara.md`).

## Fontes

- [Caverna Torrinha — site oficial](https://cavernatorrinha.com.br/) — consultado em 16/10/2026
- [Gruta Lapa Doce — site oficial](https://grutalapadoce.com.br/) — consultado em 16/10/2026
- Google Maps, trechos acima, consultados em 16/10/2026
- `09-hospedagem-cotacao-06-10.md` — cotação da Hospedagem do Sítio
