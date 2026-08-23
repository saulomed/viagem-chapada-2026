#!/usr/bin/env python3
"""Gera opcoes.html — o cardápio completo de opções da viagem.

Rode SEMPRE depois do build.py:
    python3 ~/.claude/skills/agente-viagem/scripts/build.py site
    python3 scripts/gera-opcoes.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.expanduser('~/.claude/skills/agente-viagem/scripts'))
import build as B  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site')
trip = json.load(open(os.path.join(ROOT, 'trip.json'), encoding='utf-8'))

PAGE = 'opcoes.html'

# Mesmo catálogo de navegação que o build.py monta, na mesma ordem.
PAGES = [('index.html', '🗓️ Roteiro')]
if (trip.get('costs') or {}).get('categories'):
    PAGES.append(('custos.html', '💰 Custos'))
if (trip.get('lodging') or {}).get('locations'):
    PAGES.append(('hospedagem.html', '🏨 Hospedagem'))
if (trip.get('features') or {}).get('map', True) and trip.get('stops'):
    PAGES.append(('mapa.html', '🌍 Mapa'))
for _e in trip['meta'].get('extraPages') or []:
    PAGES.append((_e['file'], _e['label']))

# ─────────────────────────────────────────────────────────────────────────────
# O catálogo. status: escolhida | ambigua | disponivel | conflito
# ─────────────────────────────────────────────────────────────────────────────

DIAS = [
    {
        'id': 'd1', 'rotulo': 'Sáb 17', 'titulo': 'A estrada',
        'ancora': 'Juazeiro → Lençóis, 489 km · ~7h10. Não cabe passeio.',
        'opcoes': [
            {'nome': 'Jantar no Quilombola', 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Centro de Lençóis', 'nota': 'Godó de banana verde, cortado de palma. Cozinha baiana que quase não se acha fora daqui.'},
            {'nome': 'Volta pelo centro histórico iluminado', 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'A pé', 'nota': 'Mesa na calçada, costuma ter música ao vivo.'},
            {'nome': 'Paraguassu — menu degustação', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Centro de Lençóis', 'nota': 'Tradicional aos sábados, e este é o único sábado da viagem. Alternativa ao Quilombola, não soma.'},
            {'nome': 'Direto para a pousada', 'tipo': 'leve', 'status': 'disponivel',
             'onde': '—', 'nota': 'Escolha legítima depois de 7h ao volante.'},
        ],
    },
    {
        'id': 'd2', 'rotulo': 'Dom 18', 'titulo': 'Grutas e mirante',
        'ancora': 'Nenhuma. Base em Lençóis, tudo a até 1h30 de carro.',
        'opcoes': [
            {'nome': 'Grutas de Iraquara — Lapa Doce, Pratinha e Gruta Azul', 'tipo': 'principal', 'status': 'escolhida',
             'onde': '68 km · ~1h30', 'nota': 'Dia inteiro. Guia obrigatório na Lapa Doce. A Pratinha resolve o almoço e tem flutuação.'},
            {'nome': 'Morro do Pai Inácio', 'tipo': 'leve', 'status': 'conflito',
             'onde': '26 km · ~30–40 min', 'nota': 'Fica na BR-242, no caminho de volta das grutas — sem quilômetro extra. <strong>No pôr do sol a volta cai por volta das 18h45, no escuro.</strong> Subindo às 16h, resolve.'},
            {'nome': 'Ribeirão do Meio', 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Trilha curta de Lençóis', 'nota': 'Escorregador natural de pedra. O programa mais divertido de menor esforço da viagem.'},
            {'nome': 'Poço do Diabo', 'tipo': 'principal', 'status': 'disponivel',
             'onde': '19,6 km · ~25 min', 'nota': 'Trilha de ~20 min à beira do rio até piscina natural com queda. Sugestão da Michele em 09/08.'},
            {'nome': 'Cachoeira do Mosquito + almoço na Fazenda Santo Antônio', 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Norte de Lençóis', 'nota': 'Fogão a lenha e redário. Comida como passeio — combina com o objetivo secundário de gastronomia.'},
            {'nome': 'Casa de Cultura Afrânio Peixoto + Mercado Cultural', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'A pé', 'nota': 'Acervo do escritor lençoense da ABL; artesanato no mercado. ~2h.'},
            {'nome': 'Nada. Pousada, rede, livro', 'tipo': 'leve', 'status': 'disponivel',
             'onde': '—', 'nota': 'Ritmo tranquilo é isso.'},
        ],
    },
    {
        'id': 'd3', 'rotulo': 'Seg 19', 'titulo': 'Descida para o sul',
        'ancora': 'Mudança de base: Lençóis → Mucugê. Se o Poço Azul entrar, ele manda no dia — 12h30 às 14h.',
        'opcoes': [
            {'nome': 'Poço Azul — flutuação na caverna alagada', 'tipo': 'principal', 'status': 'ambigua',
             'onde': '~95 km · ~1h40', 'nota': 'A lista da Michele diz "se não foi no dia 19" <em>dentro</em> do próprio dia 19 — herança do cardápio antigo. <strong>Este é o último encaixe possível:</strong> a janela dos raios fecha em 20/10 e o dia 20 virou o Buracão.'},
            {'nome': 'Gruna do Brejo', 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Igatu', 'nota': 'Mina de garimpo escavada à mão, visitada à luz de velas, com guia.'},
            {'nome': 'Vila de Igatu e as ruínas', 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Igatu, a pé', 'nota': 'Becos de pedra encaixada sem argamassa e as ruínas do bairro Luís dos Santos. Acesso livre.'},
            {'nome': 'Galeria Arte e Memória', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu', 'nota': 'Esculturas e utensílios de garimpeiros. Ter a dom, 10h às 18h.'},
            {'nome': 'Casa de Lindaura', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu', 'nota': 'Histórias de família do garimpo, com bolinho de chuva e café.'},
            {'nome': 'Casa de Amarildo dos Santos', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu', 'nota': 'Livros feitos à mão sobre a vila.'},
            {'nome': 'Igreja de São Sebastião', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu', 'nota': 'Erguida em pedra em 1844. Ponto de partida da trilha histórica Igatu–Andaraí.'},
            {'nome': 'Marimbus — canoa no "pantanal baiano"', 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Sai de Andaraí', 'nota': 'Alternativa se o Poço Azul for descartado. Esforço zero.'},
        ],
    },
    {
        'id': 'd4', 'rotulo': 'Ter 20', 'titulo': 'O Buracão',
        'ancora': 'Ibicoara. 118 km · ~2h30 por trecho — o dia é dedicado.',
        'opcoes': [
            {'nome': 'Cachoeira do Buracão', 'tipo': 'principal', 'status': 'escolhida',
             'onde': '118 km · ~2h30', 'nota': '3 km de trilha fácil e quase plana até a queda de 85 m no cânion. No final, cada um escolhe: entrar nadando ou ficar no mirante. Guia obrigatório.'},
            {'nome': 'Cachoeira do Licuri', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mesmo complexo', 'nota': 'Costuma sair no mesmo passeio do Buracão.'},
            {'nome': 'Cachoeira Véu de Noiva', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'No caminho', 'nota': 'Queda alta com mirante.'},
            {'nome': 'Projeto Sempre-Viva', 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Mucugê', 'nota': 'Alternativa leve para quem não quiser o Buracão: 1,5 km de trilha fácil até a Cachoeira do Tiburtino. O grupo pode se dividir.'},
        ],
    },
    {
        'id': 'd5', 'rotulo': 'Qua 21', 'titulo': 'Mucugê e volta ao norte',
        'ancora': 'Mucugê → Lençóis, 114 km · ~2h20. Cabe uma coisa em Mucugê antes de sair.',
        'opcoes': [
            {'nome': 'Rio Serrano e Salão de Areias Coloridas', 'tipo': 'principal', 'status': 'escolhida',
             'onde': 'Lençóis, a pé', 'nota': 'Piscinas na pedra dentro do perímetro urbano. O encaixe mais confortável do roteiro — chega-se de Mucugê e vai a pé.'},
            {'nome': 'Centro histórico de Mucugê', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mucugê, a pé', 'nota': 'Conjunto tombado pelo IPHAN em 1980: 300 casas térreas e 10 sobrados em três ruas.'},
            {'nome': 'Cemitério Santa Isabel ("Bizantino")', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mucugê', 'nota': 'Mausoléus brancos que imitam igrejas em miniatura na encosta. Único das Américas nesse estilo.'},
            {'nome': 'Igreja Matriz de Santa Isabel', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mucugê', 'nota': 'Meados do século XIX. Custa 20 min, ao lado do centro.'},
            {'nome': 'Igatu, o que faltou da segunda', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'No caminho', 'nota': 'A rota Mucugê → Lençóis passa por Andaraí e Igatu. É a segunda chance da vila.'},
            {'nome': 'Ribeirão do Meio', 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Lençóis', 'nota': 'Se não tiver acontecido no domingo, ainda cabe nesta tarde.'},
        ],
    },
    {
        'id': 'd6', 'rotulo': 'Qui 22', 'titulo': 'Volta para casa',
        'ancora': 'Lençóis → Juazeiro, 489 km · ~7h10. Saindo às 8h, chega-se por volta das 16h.',
        'opcoes': [
            {'nome': 'Sair às 8h direto para casa', 'tipo': 'principal', 'status': 'escolhida',
             'onde': '—', 'nota': 'Chegada por volta das 16h com a parada de almoço incluída, ainda com sol.'},
            {'nome': 'Sushi à noite em Juazeiro', 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Juazeiro', 'nota': 'O fim de semana em casa começa na quinta à noite.'},
            {'nome': 'Almoço em Jacobina', 'tipo': 'leve', 'status': 'ambigua',
             'onde': '~4h30 depois da saída', 'nota': 'O encaixe natural de horário e a melhor estrutura da rota. <strong>Restaurante ainda não escolhido</strong> — é a pergunta em aberto da Michele.'},
            {'nome': 'Cachoeira do Ferro Doido', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Morro do Chapéu, 18 km do centro', 'nota': 'Voltou ao roteiro: Morro do Chapéu está na estrada de casa. Mirante sobre queda de 90 m. Abre seg a sex, 8h–18h — quinta serve. Custa ~40 min e adia a chegada para ~17h.'},
            {'nome': 'Buraco do Possidônio', 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Morro do Chapéu', 'nota': 'Cratera com mata nativa no fundo. Parada rápida, se estiver no caminho.'},
            {'nome': 'Senhor do Bonfim, almoço mais tarde', 'tipo': 'leve', 'status': 'disponivel',
             'onde': '~1h depois de Jacobina', 'nota': 'Alternativa a Jacobina, para quem preferir esticar antes de parar.'},
        ],
    },
]

FORA = [
    ('Poço Encantado (Itaetê)', 'Fora da janela dos raios em outubro. Descartado pelo grupo em 08/08.'),
    ('Cachoeira da Fumaça', '12 km ida e volta, 2 km iniciais de subida íngreme, guia obrigatório. Fora do perfil por larga margem.'),
    ('Vale do Capão', 'Caiu junto com a Fumaça. Sobrava o Riachinho, que não justifica 2h de carro e 20 km de terra.'),
    ('Cachoeira do Sossego', '14 km ida e volta sobre leito de rio.'),
    ('Rio de Contas', 'O centro histórico mais rico dos três, mas a 128 km de Mucugê — mais de 2h por trecho.'),
    ('Pernoite em Morro do Chapéu', 'Cortado em 23/08 com a volta na quinta. A cidade continua no roteiro, como parada da estrada de casa.'),
    ('Trilha de descida à base do Ferro Doido', 'O mirante já entrega a vista, e o dia da volta não tem folga para isso.'),
]

RESTAURANTES = [
    ('Lençóis', ['Quilombola — godó de banana verde, cortado de palma',
                 'Paraguassu — menu degustação, tradicional aos sábados',
                 'Cozinha Aberta', 'Bodega',
                 'Lampião Cozinha Nordestina — moquecas e carne de sol',
                 'Garimpo Gourmet — regional farto',
                 'Bistrô do Mato — massas e pratos leves',
                 'Via Terra Bistrô']),
    ('No caminho', ['APA Restaurante — anexo ao Poço Azul, resolve o almoço do dia da flutuação',
                    'Fazenda Santo Antônio — fogão a lenha e redário, ligada à Cachoeira do Mosquito']),
    ('Mucugê', ['Jantar no centro — melhor gastronomia do eixo sul']),
    ('Volta', ['Jacobina — a definir', 'Senhor do Bonfim — alternativa mais tarde']),
]

SELOS = {
    'escolhida': ('✅', 'Escolha da Michele', 'sel-ok'),
    'ambigua': ('❓', 'Precisa de decisão', 'sel-duv'),
    'conflito': ('⚠️', 'Conflita com o horário', 'sel-conf'),
    'disponivel': ('○', 'Na mesa', 'sel-livre'),
}


def card(op):
    emoji, rotulo, cls = SELOS[op['status']]
    tipo = 'Principal' if op['tipo'] == 'principal' else 'Leve'
    return (
        f'<article class="opt-card fade-in {cls}" data-status="{op["status"]}">'
        f'<div class="opt-top"><span class="opt-selo">{emoji} {B.esc(rotulo)}</span>'
        f'<span class="opt-tipo">{tipo}</span></div>'
        f'<h3 class="opt-nome">{B.esc(op["nome"])}</h3>'
        f'<p class="opt-onde">{B.esc(op["onde"])}</p>'
        f'<p class="opt-nota">{op["nota"]}</p>'
        f'</article>'
    )


def bloco_dia(d):
    cards = ''.join(card(o) for o in d['opcoes'])
    return (
        f'<div class="dia-bloco" data-dia="{d["id"]}">'
        f'<div class="dia-cab"><h2 class="dia-tit"><span class="dia-chip">{d["rotulo"]}</span>{B.esc(d["titulo"])}</h2>'
        f'<p class="dia-ancora">⚓ {B.esc(d["ancora"])}</p></div>'
        f'<div class="opt-grid">{cards}</div>'
        f'</div>'
    )


total = sum(len(d['opcoes']) for d in DIAS)
escolhidas = sum(1 for d in DIAS for o in d['opcoes'] if o['status'] == 'escolhida')
pendentes = sum(1 for d in DIAS for o in d['opcoes'] if o['status'] in ('ambigua', 'conflito'))

filtros = ''.join(
    f'<button class="filtro-btn" data-dia="{d["id"]}">{d["rotulo"]}</button>' for d in DIAS
)

fora_html = ''.join(
    f'<div class="kv"><span class="k">{B.esc(n)}</span><span class="v">{B.esc(m)}</span></div>'
    for n, m in FORA
)

rest_html = ''.join(
    '<div class="info-card fade-in"><h3>' + B.esc(cidade) + '</h3><ul class="rest-lista">'
    + ''.join(f'<li>{B.esc(r)}</li>' for r in lista) + '</ul></div>'
    for cidade, lista in RESTAURANTES
)

corpo = (
    B.page_header(
        trip, 'Tudo o que está sobre a mesa',
        'Cardápio de opções',
        f'{total} opções levantadas até 23/08/2026, filtradas por dia. '
        f'{escolhidas} já escolhidas pela Michele, {pendentes} esperando decisão.',
        PAGE)
    + B.nav_html(trip, PAGES, PAGE)
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Como ler</span>'
      '<h2 class="section-title">Uma âncora por dia, o resto é escolha</h2>'
      '<p class="section-desc">A âncora é o deslocamento que não se move. O resto cabe naquele dia — '
      'geograficamente e no relógio. A regra do ritmo tranquilo é <strong>no máximo uma principal e uma leve por dia</strong>. '
      'Nada aqui está reservado.</p>'
      '</div>'
      f'<div class="filtros"><button class="filtro-btn ativo" data-dia="todos">Todos os dias</button>{filtros}</div>'
    + ''.join(bloco_dia(d) for d in DIAS)
    + '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Comida</span>'
      '<h2 class="section-title">Onde comer, por trecho</h2>'
      '<p class="section-desc">Levantamento gastronômico acumulado, incluindo o que a Michele trouxe em 09/08.</p>'
      '</div>'
      f'<div class="info-grid">{rest_html}</div>'
      '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Descartado</span>'
      '<h2 class="section-title">O que ficou de fora, e por quê</h2>'
      '<p class="section-desc">Para ninguém achar que foi esquecimento.</p>'
      '</div>'
      f'<div class="info-card fade-in">{fora_html}</div>'
      '</section>'
    + B.footer_html(trip, PAGES)
)

SCRIPT = """
(function () {
  var botoes = document.querySelectorAll('.filtro-btn');
  var blocos = document.querySelectorAll('.dia-bloco');
  botoes.forEach(function (b) {
    b.addEventListener('click', function () {
      botoes.forEach(function (o) { o.classList.remove('ativo'); });
      b.classList.add('ativo');
      var alvo = b.getAttribute('data-dia');
      blocos.forEach(function (bl) {
        var mostrar = alvo === 'todos' || bl.getAttribute('data-dia') === alvo;
        bl.style.display = mostrar ? '' : 'none';
        if (mostrar && window.revelar) {
          bl.querySelectorAll('.fade-in').forEach(function (el) { window.revelar(el); });
        }
      });
    });
  });
})();
"""

B.write(os.path.join(ROOT, PAGE),
        B.shell(trip, 'Cardápio de opções', corpo, PAGE, PAGES, scripts=SCRIPT))
print(f'✅ {PAGE} gerado — {total} opções, {escolhidas} escolhidas, {pendentes} pendentes')
