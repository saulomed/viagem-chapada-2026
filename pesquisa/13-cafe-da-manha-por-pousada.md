# Café da manhã por pousada — levantamento de 12/10/2026

A aba de hospedagem virou **uma tabela comparativa por base** e ganhou uma coluna **☕ Café**. Este arquivo registra de onde veio esse dado e onde ele é frágil.

## O que a coluna significa

O que a **Booking.com mostrava em 12/10/2026 para o quarto mais barato disponível** de cada acomodação, nas datas exatas da base. Três estados:

- **☕ incluído** — o card da Booking trazia "Café da manhã incluído" no quarto cotado
- **— não** — não trazia
- **? confirmar** — a cotação anterior dizia que incluía e a checagem de 12/10 não mostrou

**A ressalva que importa:** a Booking marca o café **por quarto**, não por acomodação. Uma pousada pode ter um quarto com café e outro sem, e o que aparece é o do quarto mais barato do dia. Por isso a coluna serve para comparar, não para fechar — na hora de reservar, confirmar na própria tarifa escolhida.

## Por que isso importa neste roteiro

Três manhãs saem cedo e o café decide se o grupo sai alimentado ou procurando padaria: **domingo 18** (café às 7h, trilha da Fumaça às 8h), **quarta 21** (saída às 8h para o Buracão) e **sexta 23** (saída às 7h para a volta de 520 km). No Vale do Capão isso pesa mais ainda — a vila janta cedo, abre tarde e não tem caixa eletrônico.

## Resultado

| Base | Opções | Com café | Sem café | A confirmar |
|---|---|---|---|---|
| Vale do Capão | 11 | 5 | 6 | — |
| Lençóis (18/10) | 11 | 5 | 6 | — |
| Mucugê | 9 | 2 | 6 | 1 |
| Ibicoara | 9 | 1 | 8 | — |
| Lençóis (22/10) | 10 | 6 | 3 | 1 |
| **Total** | **50** | **19** | **29** | **2** |

**Com café, por base:** Capão — Tarumim, Entre Montanhas, Terras do Poente, Zazen e Pousada do Capão. Lençóis 18/10 — Piçarras, Chapada Casas da Izete, Mansão Mascarenhas, Vila Serrano e Hotel de Lençóis. Mucugê — Escalada Hospedagens e Monte Azul. Ibicoara — só o **Chalé Canto do Sabiá**. Lençóis 22/10 — Pousada da Rita, Villa Allma, Mansão Mascarenhas, Alto do Cajueiro, Pouso da Trilha e Vila Serrano.

**Ibicoara é o buraco:** de nove opções, uma só serve café, e é justamente a base da manhã de quarta, que sai às 8h para o Buracão. Vale combinar café com a pousada na véspera ou levar alguma coisa de Mucugê.

**As casas e chalés inteiros nunca têm café** — Chalé Diamante, Casinha da Torre, Casa Temporada Josy, Vila Azul, Vila Sincorá, O Galpão Casa Flor. É o preço de resolver os dois casais numa reserva só.

## As duas divergências

- **Casa di Vó (Mucugê)** — a cotação de 06/10 dizia "quarto família com café da manhã incluído"; o card de 12/10 não mostra café no quarto mais barato. Pode ser que o café esteja na tarifa de R$ 350 e não na mais barata do dia. Marcada como **? confirmar**.
- **Vila Caribé (Lençóis 22/10)** — mesma situação. Marcada como **? confirmar**.
- **Aurora Suítes (Lençóis 18/10)** — a descrição dizia café incluído, mas a checagem de hoje deu **não** duas vezes, pela busca e pela página da acomodação. A descrição foi corrigida.

## Achado fora do escopo: a Mansão Mascarenhas voltou

O alerta do site dizia que a **Mansão Mascarenhas** (9,7, 143 avaliações) não tinha vaga em 18/10 — era verdade na consulta de 10/10. Em **12/10 ela voltou a aparecer**: Quarto Duplo Deluxe com Varanda, café incluído, **R$ 345 a diária**, com mais duas unidades no mesmo preço.

Isso muda a recomendação: ela volta a ser a pousada que resolve **as duas estadias de Lençóis** numa só — R$ 345 no domingo e R$ 329 na quinta, café incluído nas duas. Foi acrescentada à lista de 18/10 e o alerta foi reescrito.

## Método

A página de cada acomodação na Booking **não serve** para isso: carregada fora de um navegador com sessão, ela não renderiza a tabela de quartos, só avaliações e comodidades. Testado e descartado — chegou a dar "não" para o Hotel de Lençóis, que a busca mostra com café incluído.

O que funciona é o **card da busca**, que traz a tarifa do quarto mais barato. Foram cinco buscas por cidade (uma por base) mais 22 buscas por nome, para as acomodações que não couberam nos 15 resultados que a Booking renderiza por página.

## Mudança no gerador

A tabela foi implementada em `build_lodging()` na **skill `agente-viagem`**, não no `customCss` do projeto — a página de hospedagem passa a ser uma tabela em qualquer viagem gerada pela skill. O campo `breakfast` (`true` / `false` / ausente) entrou no `references/schema-dados.md`.

As linhas continuam sendo `.hotel-card[data-hotel]` com `data-location`, `data-name`, `.js-book` e `.js-booking-info`, então o fluxo de "marcar como reservado" e o espelhamento no roteiro seguem funcionando sem mudança no `app.js`. Abaixo de 760 px a tabela vira uma lista de fichas com rótulo em cada campo, sem rolagem lateral.

## Fontes

- Booking.com — buscas por cidade nas datas de cada base (Vale do Capão 17–18/10, Lençóis 18–19/10, Mucugê 19–20/10, Ibicoara 20–22/10, Lençóis 22–23/10), 1 quarto, 2 adultos — consultadas em 12/10/2026
- Booking.com — buscas por nome das 22 acomodações que não apareceram nas buscas por cidade — consultadas em 12/10/2026
