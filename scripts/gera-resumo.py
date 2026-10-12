#!/usr/bin/env python3
"""Gera resumo.html — a viagem inteira em uma página, para leitura rápida do grupo.

A ideia é responder, sem rolagem longa e sem abrir dia por dia: onde se dorme
cada noite, a que horas o carro pega a estrada e onde fica cada atração.

A cadeia de camas, os títulos e as datas saem do próprio trip.json, para não
descolarem do roteiro. A coluna "onde" é curada aqui — é a informação de
localização que o bloco do roteiro dá em texto corrido.

Rode SEMPRE depois do build.py:
    python3 ~/.claude/skills/agente-viagem/scripts/build.py site
    python3 scripts/gera-resumo.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.expanduser('~/.claude/skills/agente-viagem/scripts'))
import build as B  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site')
trip = json.load(open(os.path.join(ROOT, 'trip.json'), encoding='utf-8'))

PAGE = 'resumo.html'

PAGES = [('index.html', '🗓️ Roteiro')]
if (trip.get('costs') or {}).get('categories'):
    PAGES.append(('custos.html', '💰 Custos'))
if (trip.get('lodging') or {}).get('locations'):
    PAGES.append(('hospedagem.html', '🏨 Hospedagem'))
if (trip.get('features') or {}).get('map', True) and trip.get('stops'):
    PAGES.append(('mapa.html', '🌍 Mapa'))
for _e in trip['meta'].get('extraPages') or []:
    PAGES.append((_e['file'], _e['label']))

DIAS_SEMANA = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

# Onde se dorme na véspera da viagem e na última noite.
CASA = 'Casa, em Juazeiro'

# ─────────────────────────────────────────────────────────────────────────────
# A programação curada: (horário, ícone, o quê, onde, destaque)
# destaque: 'estrada' pinta a linha de saída do carro; 'hora' marca prazo duro.
# ─────────────────────────────────────────────────────────────────────────────
PROGRAMA = {
    1: [('06h30', '🚗', '<strong>Pega a estrada.</strong> BR-407 → BR-242 → BA-849',
         '526 km · 8h31 de volante', 'estrada'),
        ('~12h', '🍽️', 'Almoço e abastecimento no caminho',
         'Senhor do Bonfim ou Jacobina', ''),
        ('15h30', '⛽', '<strong>Parada obrigatória:</strong> último posto e último caixa',
         'Palmeiras (sede)', 'hora'),
        ('16h', '🛏️', 'Check-in', 'Vila de Caeté-Açu, distrito de Palmeiras', ''),
        ('19h', '🍽️', 'Jantar na vila', 'A pé, na vila — só em espécie', '')],
    2: [('07h', '☕', 'Café combinado na véspera', 'Pousada no Capão', ''),
        ('07h30', '🚗', '3 km até a portaria', 'Estrada Caeté-Açu → Palmeiras', 'estrada'),
        ('08h–13h', '🥾', '<strong>Cachoeira da Fumaça por cima</strong> · 6 km por sentido, '
         '2 km de subida · guia obrigatório', 'Portaria a 3 km da vila, Vale do Capão', 'hora'),
        ('13h–14h30', '🍽️', 'Almoço', 'Vila de Caeté-Açu', ''),
        ('14h30', '🚗', '<strong>Pega a estrada</strong> · 47 km · ~1h',
         'Serra até Palmeiras + BR-242', 'estrada'),
        ('15h45–17h50', '⛰️', '<strong>Morro do Pai Inácio</strong> · subida liberada '
         '<strong>só até 17h</strong> · pôr do sol 17h42',
         'Beira da BR-242, município de Palmeiras', 'hora'),
        ('17h50–18h45', '🌙', '29 km de BR-242 no escuro — a única exceção aceita',
         'Até Lençóis', ''),
        ('19h30', '🍽️', 'Jantar e centro histórico', 'A pé, centro de Lençóis', '')],
    3: [('09h30', '🚗', '<strong>Pega a estrada</strong> com as malas · ~95 km · 1h40',
         'Lençóis → Nova Redenção', 'estrada'),
        ('11h30–14h', '💧', '<strong>Poço Azul</strong> · raios na água <strong>12h30–14h</strong> '
         '· 20 a 30 min por grupo', 'Nova Redenção', 'hora'),
        ('~12h', '🍽️', 'Almoço no APA Restaurante, anexo ao poço', 'Poço Azul', ''),
        ('14h15', '🚗', '~66 km · ~1h30 — parte do acesso é de terra', 'BA-245 → BA-142', 'estrada'),
        ('16h', '🛏️', 'Check-in e centro histórico a pé', 'Mucugê', ''),
        ('Após o jantar', '⛪', 'Cemitério Bizantino iluminado', 'Entrada da cidade', '')],
    4: [('08h30–12h30', '⛏️', '<strong>Parque Municipal</strong>: Museu Vivo do Garimpo, '
         'Cachoeira da Piabinha e Cachoeira do Tiburtino · um ingresso cobre tudo',
         'Saída para Andaraí, menos de 2 km do centro de Mucugê', ''),
        ('12h30–14h', '🍽️', 'Almoço e check-out — as malas vão para o carro',
         'Centro de Mucugê', ''),
        ('14h–15h', '⛪', '<strong>Cemitério Bizantino</strong> de dia · rápido e gratuito',
         'Beira da BA-142, na entrada da cidade', ''),
        ('15h30', '🚗', '<strong>Pega a estrada</strong> · 78,2 km · <strong>1h06</strong> · '
         'BA-142, asfalto inteiro', 'Mucugê → Ibicoara', 'estrada'),
        ('~16h40', '🛏️', 'Check-in — <strong>1h de folga antes do pôr do sol</strong>',
         'Ibicoara', ''),
        ('19h', '🍽️', 'Jantar na vila', 'Centro de Ibicoara', '')],
    5: [('07h30', '☕', 'Café — as malas ficam, hoje se volta para a mesma cama',
         'Pousada em Ibicoara', ''),
        ('08h', '🚗', '<strong>Pega a estrada</strong> · 28 km de terra · ~1h · encontro '
         'com o condutor da ACVIB', 'Ibicoara → portaria', 'estrada'),
        ('09h–13h', '🏞️', '<strong>Cachoeira do Buracão</strong> · 3 km por sentido, quase '
         'plano · queda de 85 m no cânion · <strong>última entrada 11h, com 2h de margem</strong>',
         'Distrito de Cascavel, município de Ibicoara', 'hora'),
        ('13h–14h', '🚗', 'Volta, 28 km de terra com sol alto', 'Até Ibicoara', ''),
        ('14h–15h', '🍽️', 'Almoço tardio', 'Centro de Ibicoara', ''),
        ('15h30–17h30', '🍓', '<strong>Sítio Canjerana</strong> · morango, cafezal e '
         'degustação · exige agendamento', 'Beira da rodovia, minutos do centro', ''),
        ('19h', '🍽️', 'Jantar', 'Ibicoara', '')],
    6: [('07h', '🚗', '<strong>Pega a estrada</strong> · ~215–230 km · ~4h15 · BA-142 por '
         'Mucugê e Andaraí, depois BR-242', 'Ibicoara → Iraquara', 'estrada'),
        ('11h15', '🔀', 'Ponto de decisão: a Lapa Doce entra <strong>só</strong> se chegarem '
         'até esta hora', 'Iraquara', 'hora'),
        ('11h30–16h', '💦', '<strong>Fazenda Pratinha e Gruta Azul</strong> · das 12h às 15h30 '
         'cobre todas as janelas de luz · entrada até 16h', 'Iraquara, 10,8 km da Lapa Doce', 'hora'),
        ('16h–16h30', '🚗', 'Sair nesta janela · ~46 km · ~1h', 'Pratinha → Lençóis', 'estrada'),
        ('~17h30', '🛏️', 'Check-in', 'Centro de Lençóis', ''),
        ('19h', '🍽️', 'Jantar de despedida', 'A pé, centro de Lençóis', '')],
    7: [('08h', '🚗', '<strong>Pega a estrada</strong> · 489 km · ~7h10',
         'Lençóis → Juazeiro', 'estrada'),
        ('10h45–11h30', '💦', 'Ferro Doido — parada opcional de ~40 min, '
         '<strong>provavelmente seco em outubro</strong>',
         '18 km do centro de Morro do Chapéu', ''),
        ('13h–14h', '🍽️', 'Almoço', 'Jacobina', ''),
        ('~16h', '🏠', 'Chegada', 'Juazeiro', '')],
}

# Observação curta por dia, exibida sob o cabeçalho do card.
RECADO = {
    1: 'Dia inteiro de estrada: a tarde acaba no check-in.',
    2: 'Dorme-se a 3 km da trilha — por isso o despertador é às 7h, e não às 5h30.',
    3: 'A única hora que manda no dia é 12h30, no Poço Azul.',
    4: 'A mudança de base acontece no fim do dia, com uma hora de sol de sobra.',
    5: 'O único dia em que não se desfaz a mala.',
    6: 'O dia mais longo de estrada no meio da viagem.',
    7: 'Chegada com sol, e o fim de semana em casa começa aí.',
}


def nome_base(loc_id):
    for loc in (trip.get('lodging') or {}).get('locations') or []:
        if loc['id'] == loc_id:
            return loc['name'].split(' — ')[0]
    return loc_id


def data_br(iso):
    a, m, dd = iso.split('-')
    return '%s/%s' % (dd, m)


def dia_semana(iso):
    import datetime
    a, m, dd = (int(x) for x in iso.split('-'))
    return DIAS_SEMANA[datetime.date(a, m, dd).weekday()]


dias = trip['days']

# ── a cadeia de camas, derivada de days[].location ──
camas = []
for i, dia in enumerate(dias):
    dorme = nome_base(dia.get('location')) if i < len(dias) - 1 else CASA
    acorda = CASA if i == 0 else camas[i - 1][1]
    camas.append((acorda, dorme))

linhas_cama = []
for i, dia in enumerate(dias):
    acorda, dorme = camas[i]
    muda = 'sim' if i < len(dias) - 1 and dorme != camas[i + 1][1] else 'não'
    if i == len(dias) - 1:
        muda = '—'
    cls = ' class="res-fica"' if muda == 'não' else ''
    linhas_cama.append(
        '<tr%s><td class="res-dia">%s %s</td><td><strong>%s</strong></td>'
        '<td class="res-muda">%s</td></tr>'
        % (cls, dia_semana(dia['date']), data_br(dia['date']), B.esc(dorme), muda))

tabela_camas = (
    '<div class="res-camas-wrap"><table class="res-camas">'
    '<thead><tr><th>Noite</th><th>Onde dorme</th><th>Troca no dia seguinte?</th></tr></thead>'
    '<tbody>' + ''.join(linhas_cama) + '</tbody></table></div>')

# ── os cards de cada dia ──
cards = []
for i, dia in enumerate(dias):
    acorda, dorme = camas[i]
    linhas = []
    for hora, ico, oque, onde, destaque in PROGRAMA.get(dia['num'], []):
        cls = (' res-l-estrada' if destaque == 'estrada'
               else ' res-l-hora' if destaque == 'hora' else '')
        linhas.append(
            '<tr class="res-linha%s"><td class="res-hora">%s</td>'
            '<td class="res-oque"><span class="res-ico">%s</span>%s</td>'
            '<td class="res-onde">%s</td></tr>' % (cls, B.esc(hora), ico, oque, B.esc(onde)))
    cards.append(
        '<article class="res-dia-card fade-in" id="dia-%d">'
        '<header class="res-cab">'
        '<span class="res-chip">%s %s</span>'
        '<h2 class="res-tit">%s %s</h2>'
        '<p class="res-rota">%s</p>'
        '<p class="res-camas-linha">🛏️ <strong>Acorda:</strong> %s '
        '&nbsp;·&nbsp; <strong>Dorme:</strong> %s</p>'
        '<p class="res-recado">%s</p>'
        '</header>'
        '<div class="res-tab-wrap"><table class="res-tab"><tbody>%s</tbody></table></div>'
        '</article>'
        % (dia['num'], dia_semana(dia['date']), data_br(dia['date']),
           dia.get('emoji', ''), B.esc(dia['title']),
           B.esc(dia.get('route') or ''),
           B.esc(acorda), B.esc(dorme),
           B.esc(RECADO.get(dia['num'], '')),
           ''.join(linhas)))

corpo = (
    B.page_header(
        trip, 'A viagem em uma página', 'Resumo',
        'Onde se dorme cada noite, a que horas o carro pega a estrada e onde fica cada passeio. '
        'Para quem quiser conferir tudo sem abrir dia por dia.', PAGE)
    + B.nav_html(trip, PAGES, PAGE)
    + '<section class="section fade-in">'
      '<h2 class="res-h2">🛏️ As camas da viagem</h2>'
      '<p class="res-intro">A regra do roteiro: <strong>a troca de cidade acontece sempre no fim '
      'do dia anterior</strong>, para que nenhuma manhã seja gasta em estrada antes de um passeio. '
      'São cinco bases, e só Ibicoara tem duas noites.</p>'
    + tabela_camas
    + '</section>'
    + '<section class="section">'
      '<h2 class="res-h2">🗓️ Dia a dia</h2>'
      '<p class="res-intro">As linhas em destaque são as horas em que o carro sai '
      '(<span class="res-leg res-l-estrada">estrada</span>) e os prazos que não dão para perder '
      '(<span class="res-leg res-l-hora">hora marcada</span>).</p>'
    + ''.join(cards)
    + '</section>'
    + B.footer_html(trip, PAGES)
)

B.write(os.path.join(ROOT, PAGE), B.shell(trip, 'Resumo', corpo, PAGE, PAGES))
print('✅ %s — %d dias · %d linhas de programação'
      % (PAGE, len(dias), sum(len(v) for v in PROGRAMA.values())))
