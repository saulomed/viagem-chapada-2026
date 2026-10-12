# Revisão geral do site — 12/10/2026

Varredura completa do roteiro, da hospedagem, da curadoria de restaurantes e do mapa, pedida depois que a mudança da terça (arquivo `11-deslocamento-na-vespera.md`) foi aplicada. O objetivo era achar furos: horários que não fecham, textos que a última alteração deixou para trás, trechos de estrada com número errado e lacunas de pesquisa.

Método: conferência de cada bloco de `days[]` contra o relógio, cruzamento de cada par origem→destino no **roteador OSRM** e, onde houve divergência, **medição no Google Maps**, par a par, em 12/10/2026.

---

## O furo grave: a volta de sexta estava 1h subestimada

O roteiro trazia **489 km · ~7h10** para o dia 7, com a rota descrita como *Lençóis → Morro do Chapéu → Jacobina → Juazeiro*. Os dois dados não combinam: **489 km é a rota direta pela BR-242**, a mesma da ida ao contrário, que não passa por Morro do Chapéu. O OSRM dá exatamente 489,0 km · 7h02 para ela, o que confirma a origem do número.

Medição no Google Maps em 12/10/2026, do caminho que o roteiro de fato planeja:

| Trecho | Roteiro antigo | Google Maps 12/10 | Diferença |
|---|---|---|---|
| Lençóis → Morro do Chapéu | 177 km · ~2h40 | **176 km · 2h40** | ok |
| Morro do Chapéu → Jacobina | 108 km · ~1h55 | **108 km · 1h30** | 25 min a menos |
| Jacobina → Juazeiro | ~204 km · ~2h30 | **236 km · 3h43** | **+32 km e +1h13** |
| **Total** | 489 km · 7h10 | **520 km · 7h53** | **+31 km e +43 min** |

O erro está concentrado no último trecho. Com 7h53 de volante, uma parada no Ferro Doido e um almoço, sair às 8h significaria chegar depois das 18h30 — fora da regra da luz do dia que o grupo adotou.

**Correção aplicada:** a saída de sexta desceu de 8h para **7h**, o Ferro Doido virou parada explicitamente opcional (custa ~1h ao dia, porque fica 18 km adiante do centro de Morro do Chapéu) e a chegada passou a ser declarada como **16h30 sem a cachoeira, 17h30 com ela**. Os dois casos ainda têm sol — o pôr do sol é às 17h42.

**Alternativa registrada no roteiro, para o grupo decidir na véspera:** voltar direto pela BR-242 e BR-407, 489 km e cerca de 7h, com almoço em Senhor do Bonfim ou Capim Grosso. São 31 km e quase uma hora a menos, ao custo de perder Morro do Chapéu, o Ferro Doido e Jacobina.

---

## Jacobina não está no caminho da ida

O dia 1 dizia *"Senhor do Bonfim e Jacobina têm a melhor estrutura da rota"*. Medindo a distância de Jacobina ao traçado real da ida: **48 km fora**. A ida pela BR-407 passa por **Senhor do Bonfim** (4 km do traçado) e **Capim Grosso** (0,8 km), e pega a BR-242 para o oeste sem chegar perto de Jacobina. Jacobina só entra na volta, na sexta.

Texto corrigido no roteiro, na página de atrações e na aba de restaurantes.

---

## A aritmética da chegada do sábado

Google Maps, 12/10: **Juazeiro → Palmeiras = 507 km · 7h44**. Com os ~20 km de serra até Caeté-Açu, fecha os 526 km · 8h31 que o grupo já tinha medido.

Saindo às 6h30, com ~1h de paradas, Palmeiras fica por volta das **15h15**; com 30 min de parada obrigatória (posto e caixa) e 40 min de serra, a chegada é **16h30**, não 16h. Os rótulos dos três blocos da tarde foram corrigidos. Continua sobrando mais de uma hora de sol.

---

## Textos que a mudança da terça deixou para trás

A troca de base para Ibicoara na tarde de terça tirou uma noite de Mucugê, mas estes textos ainda falavam em duas:

- `days[3]`: *"Base das próximas duas noites"* e *"Vale para as duas noites em Mucugê"* — **Mucugê é uma noite só**, a de 19/10.
- `gera-atracoes.py` d3: a ficha do Paraguassu repetia a mesma informação.
- `gera-atracoes.py` d4: a âncora dizia *"Nenhuma. Tudo a até 2 km do centro de Mucugê"* — mas a terça agora carrega 78,2 km de estrada às 15h30.
- `gera-atracoes.py` d4: o Café Igaraçu era oferecido *"se a tarde de terça sobrar"* — ela já não sobra. Reescrito como troca pelo Cemitério Bizantino, já que fica justamente no caminho Mucugê → Ibicoara.
- `gera-atracoes.py` d4: o plano B do Poço Azul não dizia o que cai quando é acionado. Agora diz: cai o Parque Municipal, não o deslocamento.
- `gera-atracoes.py` d5: a âncora ainda começava em Mucugê.
- `gera-restaurantes.py`: o subtítulo de Ibicoara falava só no dia 5; são os dias 4 e 5.

---

## Horários que não fechavam

- **Dia 6:** a Fazenda Pratinha estava marcada das 11h30 às 16h30 e a volta para Lençóis das 16h às 17h30 — meia hora contada duas vezes. A Pratinha passou a terminar às 16h e a volta a ser 16h–17h.
- **Dia 5:** havia um vazio das 14h às 15h30, com o almoço aparecendo só como item solto do bloco de volta do Buracão. Virou bloco próprio, 14h–15h15.
- **Dia 7:** reconstruído inteiro, como descrito acima.

---

## O Buracão: o aplicativo erra, as fontes locais acertam

O Google Maps mede **89 km e 2h40** de Ibicoara até o pino da Cachoeira do Buracão, pela "Estr. das Cachoeiras", e o OSRM dá 52 km por um desvio de asfalto (BR-330/BR-030). Nenhum dos dois pega a estrada que o grupo vai usar.

As fontes locais são consistentes entre si: **28 a 30 km de estrada de terra, de 40 min a 1h**, confirmado pelo Guia Chapada Diamantina, pela Associação Bicho do Mato (29 km, média de 1h) e por guias de Ibicoara. O valor do roteiro (`~28 km de terra · ~1h`, com status *estimado*) está certo.

Foi acrescentado um aviso no bloco do dia 5: **seguir o condutor, não o aplicativo**. E o Buracão ficou de fora do traçado do mapa, com um pino e uma nota explicando por quê.

---

## Hospedagem — completa

As cinco bases têm busca feita e opções cotadas, todas com data de consulta registrada em `sources{}`:

| Base | Noites | Opções | Consulta |
|---|---|---|---|
| Vale do Capão | 1 · 17/10 | 11 | 10/10/2026 |
| Lençóis | 1 · 18/10 | 10 | 10/10/2026 |
| Mucugê | 1 · 19/10 | 9 | 12/10/2026 |
| Ibicoara | 2 · 20 e 21/10 | 9 | 12/10/2026 |
| Lençóis (volta) | 1 · 22/10 | 10 | 06/10/2026 |

Nenhuma lacuna. A base de 22/10 é a única com cotação de 06/10 — vale recotar perto de fechar as reservas, mas é a noite com mais disponibilidade do roteiro (quinta, fora do fim de semana).

---

## Restaurantes — uma lacuna real, sem solução inventada

São 70 estabelecimentos em 8 zonas, e todas as refeições do roteiro têm cobertura. A exceção é **Nova Redenção / Poço Azul, com uma única opção**: o APA Restaurante, a 200 m do poço.

Busca de 12/10 não encontrou nenhum segundo restaurante avaliado em Nova Redenção. Listas de sites de turismo citam nomes ("Cantina Típica", "Sabor da Terra", "Peixaria do Lago") sem endereço, avaliação ou qualquer dado verificável — **não entraram na curadoria**. Em vez de inventar alternativa, o roteiro e a aba de restaurantes passaram a dizer o plano B honesto: se o APA estiver fechado, esticar e almoçar em Mucugê, por volta das 15h45.

---

## Mapa — era uma linha reta, agora são as estradas

O `trip.json` não tinha o campo `route`, e sem ele o gerador cai no comportamento antigo: uma linha reta pontilhada ligando as cinco paradas. Era literalmente um traçado geométrico, não um caminho.

**O que foi construído:**

- **Traçado real das estradas**, do roteador OpenStreetMap (OSRM), em 722 pontos (~35 KB), simplificado por Douglas-Peucker a ~165 m de tolerância para não pesar nas páginas offline.
- **Quatro rotas selecionáveis** na barra do mapa: *Roteiro completo* (1.637 km · 27h29), *Ida · dia 1* (526 km · 8h31), *Na Chapada · dias 2 a 6* (591 km · 11h06) e *Volta · dia 7* (520 km · 7h53).
- **Dez cidades e atrativos de passagem** como pinos, com nota de contexto: Senhor do Bonfim, Capim Grosso, Palmeiras, Morro do Pai Inácio, Poço Azul, Andaraí, Cachoeira do Buracão, Fazenda Pratinha, Morro do Chapéu e Jacobina. Antes o mapa só mostrava as cinco bases e nenhum dos destinos de passeio.

**Honestidade do dado:** o traçado é do OSRM, mas **as distâncias e os tempos dos botões são os do Google Maps**, medidos par a par — é o que está escrito na barra do mapa. Onde o OSRM diverge do caminho real (Buracão, e o trecho Morro do Chapéu → Jacobina, que o OSM parece não mapear inteiro pela BA-144), isso está anotado.

**Sem pontos de apoio no mapa:** `route.pois` ficou vazio. Postos e restaurantes de estrada exigiriam coordenada verificada de cada um, e a curadoria de restaurantes não guarda coordenadas. Fica como pendência, não como invenção.

---

## O que não mudou, e por quê

- **Lençóis → Poço Azul:** o roteiro diz ~95 km · ~1h40; o Maps confirma **94,9 km · 1h29**. O OSRM dava 70 km por um atalho que inclui terra. Mantido.
- **Poço Azul → Mucugê, Mucugê → Ibicoara, Pratinha → Lençóis:** OSRM e Maps batem com o roteiro. Mantidos.
- **`costs`** segue vazio e o site não gera aba de custos, porque `features.currency` está desligado. Decisão anterior do grupo, não é furo.

---

## Fontes

- Google Maps — Lençóis → Poço Azul, Lençóis → Morro do Chapéu, Morro do Chapéu → Jacobina, Morro do Chapéu → Jacobina → Juazeiro, Jacobina → Juazeiro, Juazeiro → Palmeiras, Ibicoara → Cachoeira do Buracão — consultados em 12/10/2026
- Roteador OpenStreetMap (OSRM) — geometria das estradas de todos os trechos e conferência cruzada — consultado em 12/10/2026
- Nominatim / OpenStreetMap — coordenadas das cidades e atrativos de passagem — consultado em 12/10/2026
- [Guia Chapada Diamantina — Cachoeira do Buracão](https://www.guiachapadadiamantina.com.br/cachoeira-do-buracao/) — acesso de Ibicoara, 28 km de chão
- [Associação Bicho do Mato — Ecoturismo em Ibicoara](http://www.bichodomato.org/p/ecoturismo.html) — 29 km de estrada de terra, média de 1h
- [Conecta Chapada — a trilha da Cachoeira do Buracão](https://conectachapada.com.br/trilha-da-cachoeira-do-buracao/) — tempo de carro e de trilha
- Booking.com — datas de cada base, conforme registrado em `sources{}` do `trip.json`
