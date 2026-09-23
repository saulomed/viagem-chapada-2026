#!/usr/bin/env python3
"""Gera atracoes.html — a ficha de cada lugar da viagem, com curadoria.

Cada atração tem foto, resumo próprio e nível de recomendação (1 a 4),
apurados em blogs de viagem, guias e vídeos em 23/08/2026. Dentro de cada dia
as atrações saem ordenadas da mais recomendada para a menos, pelos sete dias
do roteiro definido pelo grupo.

Cada card tem uma âncora estável (o slug em FICHA): os blocos do roteiro
apontam para ela pelo campo `attraction` do trip.json.

Rode SEMPRE depois do build.py:
    python3 ~/.claude/skills/agente-viagem/scripts/build.py site
    python3 scripts/gera-atracoes.py
"""
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.expanduser('~/.claude/skills/agente-viagem/scripts'))
import build as B  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site')
trip = json.load(open(os.path.join(ROOT, 'trip.json'), encoding='utf-8'))

PAGE = 'atracoes.html'
IMG_DIR = 'imagens/atracoes'

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
# Curadoria
#   rec    1 imperdível · 2 muito recomendado · 3 vale se sobrar · 4 pense duas vezes
#   status escolhida | ambigua | conflito | disponivel
# ─────────────────────────────────────────────────────────────────────────────

REC = {
    1: ('⭐', 'Imperdível', 'rec1'),
    2: ('👍', 'Muito recomendado', 'rec2'),
    3: ('🙂', 'Vale se sobrar tempo', 'rec3'),
    4: ('🤔', 'Pense duas vezes', 'rec4'),
}

SELOS = {
    'escolhida': ('✅', 'No roteiro', 'sel-ok'),
    'ambigua': ('❓', 'Precisa de decisão', 'sel-duv'),
    'conflito': ('⚠️', 'Conflita com o horário', 'sel-conf'),
    'disponivel': ('○', 'Na mesa', 'sel-livre'),
}

# ─────────────────────────────────────────────────────────────────────────────
# Ficha de cada lugar: âncora estável + foto.
#   slug  é o id do card e o alvo do campo `attraction` dos blocos do roteiro.
#         Mudar um slug quebra o link que vem do roteiro — em compensação, ele
#         não precisa acompanhar mudanças no nome da atração.
#   foto  é o nome do arquivo em imagens/atracoes/ (sem extensão). Sem foto, o
#         card cai no cabeçalho gráfico da paleta — nenhum buraco na grade.
# ─────────────────────────────────────────────────────────────────────────────

FICHA = {
    'Morro do Pai Inácio': ('morro-do-pai-inacio', 'morro-do-pai-inacio'),
    'Rio Serrano e Salão de Areias Coloridas': ('rio-serrano', 'rio-serrano'),
    'Jantar no Quilombola': ('quilombola', None),
    'Volta pelo centro histórico iluminado': ('centro-historico-lencois', 'centro-historico-lencois'),
    'Jantar no Paraguassu': ('paraguassu', None),
    'Casa de Cultura Afrânio Peixoto + Mercado Cultural': ('casa-de-cultura', None),
    'Direto para a pousada': ('descanso-lencois', None),
    'Cachoeira da Fumaça por cima': ('cachoeira-da-fumaca', 'cachoeira-da-fumaca'),
    'Cachoeira do Riachinho + vila do Capão': ('cachoeira-do-riachinho', 'cachoeira-do-riachinho'),
    'Almoço na vila de Caeté-Açu': ('caete-acu', 'vale-do-capao'),
    'Poço Azul — flutuação na caverna alagada': ('poco-azul', 'poco-azul'),
    'Centro histórico de Mucugê': ('centro-historico-mucuge', None),
    'Igreja Matriz de Santa Isabel': ('igreja-santa-isabel', 'igreja-santa-isabel'),
    'Parque Municipal de Mucugê — museu, Piabinha e Tiburtino': ('parque-municipal-mucuge', 'parque-municipal-mucuge'),
    'Cemitério Santa Isabel ("Bizantino")': ('cemiterio-bizantino', 'cemiterio-bizantino'),
    'Poço Azul, se a segunda nublar': ('poco-azul-plano-b', 'poco-azul'),
    'Café Igaraçu — do plantio à xícara': ('cafe-igaracu', None),
    'Cachoeira do Buracão': ('cachoeira-do-buracao', 'cachoeira-do-buracao'),
    'Sítio Canjerana — café e morango': ('sitio-canjerana', None),
    'A vila de Ibicoara à noite': ('ibicoara', 'ibicoara'),
    'Cachoeira do Licuri': ('cachoeira-do-licuri', 'cachoeira-do-licuri'),
    'Cachoeira Véu de Noiva': ('cachoeira-veu-de-noiva', None),
    'Gruta da Lapa Doce': ('gruta-da-lapa-doce', 'gruta-da-lapa-doce'),
    'Fazenda Pratinha e Gruta Azul': ('fazenda-pratinha', 'fazenda-pratinha'),
    'Caverna Torrinha': ('caverna-torrinha', 'caverna-torrinha'),
    'Jantar de despedida em Lençóis': ('jantar-despedida', None),
    'Sair às 8h direto para casa': ('volta-direta', None),
    'Sushi à noite em Juazeiro': ('sushi-juazeiro', None),
    'Almoço em Jacobina': ('jacobina', 'jacobina'),
    'Senhor do Bonfim, almoço mais tarde': ('senhor-do-bonfim', None),
    'Buraco do Possidônio': ('buraco-do-possidonio', 'buraco-do-possidonio'),
    'Cachoeira do Ferro Doido': ('cachoeira-ferro-doido', 'cachoeira-ferro-doido'),
}

# Autoria das fotos, lida do Commons na hora do download. CC BY e CC BY-SA
# exigem crédito: a seção de créditos da página é a contrapartida.
FOTOS = {
    'morro-do-pai-inacio': ('Rosino', 'CC BY-SA 2.0',
        'https://commons.wikimedia.org/wiki/File:Sunset_near_Morro_do_Pai_In%C3%A1cio,_Palmeiras,_Bahia.jpg'),
    'rio-serrano': ('Gleidson Santos / MTur Destinos', 'Domínio público',
        'https://commons.wikimedia.org/wiki/File:Gleidson_Santos_PiscinasnaturaisdoRioSerrano_Lencois_BA_(26183259787).jpg'),
    'centro-historico-lencois': ('Diego Carrion Serrano', 'CC BY-SA 3.0',
        'https://commons.wikimedia.org/wiki/File:Luar_sobre_a_cidade_de_Len%C3%A7ois.JPG'),
    'cachoeira-da-fumaca': ('Jack5599', 'CC BY-SA 3.0',
        'https://commons.wikimedia.org/wiki/File:Cachoeira_da_Fuma%C3%A7a,_Chapada_Diamantina.JPG'),
    'cachoeira-do-riachinho': ('Crisferrari1500', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Cachoeira_do_Riachinho.jpg'),
    'vale-do-capao': ('Samory Santos', 'CC BY 3.0',
        'https://commons.wikimedia.org/wiki/File:Vale_do_Capao,_Chapada_Diamantina.jpg'),
    'poco-azul': ('Rodrigo Almeida Fernandes', 'CC BY-SA 3.0',
        'https://commons.wikimedia.org/wiki/File:Po%C3%A7o_Azul,_Chapada_Diamantina.jpg'),
    'igreja-santa-isabel': ('jvc', 'CC BY 2.0',
        'https://commons.wikimedia.org/wiki/File:Igreja_Santa_Isabel_em_Mucug%C3%AA.jpg'),
    'parque-municipal-mucuge': ('Nancy Viegas', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Cachoeira_da_Piabinha,_Projeto_Sempre_Viva,_Mucug%C3%AA_BA.jpg'),
    'cemiterio-bizantino': ('Jardelsliumba', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Cemit%C3%A9rio_Bizantino_de_Mucug%C3%AA,_BA.jpg'),
    'cachoeira-do-buracao': ('Rodolfo Bazetto', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Cachoeira_do_Burac%C3%A3o_-_Chapada_Diamantina.jpg'),
    'ibicoara': ('Arthur.nanni', 'CC BY 4.0',
        'https://commons.wikimedia.org/wiki/File:Ibicoara_na_Bahia.jpg'),
    'cachoeira-do-licuri': ('Alexandre Furcolin Filho', 'CC BY-SA 3.0',
        'https://commons.wikimedia.org/wiki/File:Cachoeira_licuri.jpg'),
    'gruta-da-lapa-doce': ('Heris Luiz Cordeiro Rocha', 'CC BY-SA 3.0',
        'https://commons.wikimedia.org/wiki/File:Gruta_da_Lapa_Doce_na_Chapada_Diamantina.jpg'),
    'fazenda-pratinha': ('Lilian Leyve', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Pratinha,_Iraquara_-_BA.jpg'),
    'caverna-torrinha': ('Lilian Leyve', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Caverna_da_Torrinha.jpg'),
    'cachoeira-ferro-doido': ('Fernandoantoniofotos', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Monumento_Natural_Cachoeira_do_Ferro_Doido_Fernandoantoniofotos_(01).jpg'),
    'buraco-do-possidonio': ('Fran.oliver', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Buraco_do_Pocid%C3%B4nio_no_Parque_Estadual_do_Morro_do_Chap%C3%A9u.jpg'),
    'jacobina': ('Matheus Trabuco Gonzalez', 'CC BY-SA 4.0',
        'https://commons.wikimedia.org/wiki/File:Vista_de_Jacobina_%C3%A0s_18h.jpg'),
}


def slugify(nome):
    """Fallback para atração que ainda não tem entrada em FICHA."""
    s = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode()
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')


def ficha(nome):
    return FICHA.get(nome) or (slugify(nome), None)

DIAS = [
    {
        'id': 'd1', 'rotulo': 'Sáb 17', 'titulo': 'A estrada e o Pai Inácio',
        'ancora': 'Juazeiro → Lençóis, 489 km · ~7h10. A subida do Pai Inácio fecha às 17h: sair de Lençóis às 16h15.',
        'opcoes': [
            {'nome': 'Morro do Pai Inácio', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '26 km · ~30–40 min',
             'desc': 'O cartão-postal da Chapada, e o ponto em que todas as fontes concordam sem ressalva. São 20 a 30 minutos de subida — íngreme em trechos, mas classificada como fácil — até uma vista de 360° com o Morro do Camelo e o Dois Irmãos. <strong>A subida só é liberada até as 17h</strong> e o sol se põe às 17h42, então a saída de Lençóis é às 16h15. A volta de 26 km pela BR-242 acontece no escuro, com o grupo junto: é a exceção que o grupo abriu à regra da luz do dia. A taxa de visitação é de <strong>R$ 20 por pessoa</strong> — subiu de R$ 12 em 06/04/2026, por decisão da Prefeitura de Palmeiras. São R$ 80 pelos quatro.'},
            {'nome': 'Rio Serrano e Salão de Areias Coloridas', 'rec': 2, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Lençóis, a pé',
             'desc': 'Caldeirões e piscinas naturais escavados na pedra pelo Rio Lençóis, com o Salão de Areias Coloridas na mesma caminhada, dentro do perímetro urbano. Não está no roteiro, mas cabe na janela entre o check-in e a saída para o Pai Inácio, para quem ainda tiver perna depois de sete horas de estrada.'},
            {'nome': 'Jantar no Quilombola', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Centro de Lençóis',
             'desc': 'Godó de banana verde e cortado de palma — pratos da cozinha baiana de raiz que praticamente não se encontram fora da região. Começa mais tarde, por volta das 19h30, depois da volta do Pai Inácio.'},
            {'nome': 'Volta pelo centro histórico iluminado', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'A pé',
             'desc': 'O casario colonial de Lençóis ganha outra cara à noite, e a Rua das Pedras concentra mesas na calçada e música ao vivo. Custo zero, esforço zero, e nenhum quilômetro a mais no carro.'},
            {'nome': 'Casa de Cultura Afrânio Peixoto + Mercado Cultural', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'A pé',
             'desc': 'Acervo do escritor lençoense da Academia Brasileira de Letras, e artesanato local no mercado. O encaixe para a tarde de sábado de quem preferir não entrar na água.'},
            {'nome': 'Direto para a pousada', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': '—',
             'desc': 'Escolha perfeitamente legítima: foram sete horas ao volante, e o despertador de domingo toca às 5h30 para a Fumaça.'},
        ],
    },
    {
        'id': 'd2', 'rotulo': 'Dom 18', 'titulo': 'O Cânion da Fumaça',
        'ancora': 'Vale do Capão, ~74 km · ~1h30. Saída às 6h15: a trilha recebe visitantes das 8h às 13h.',
        'opcoes': [
            {'nome': 'Cachoeira da Fumaça por cima', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': 'Vale do Capão · guia R$ 250 para até 4',
             'desc': 'O atrativo mais icônico da Chapada. São 6 km por sentido, com os 2 primeiros quilômetros em subida por degraus de pedra — classificada de moderada a avançada, mínimo de 2h30 subindo e ~1h30 descendo. No alto, a vista é do cânion por cima, a partir da borda de pedra. <strong>Guia obrigatório</strong>, a R$ 250 a diária para grupo de até 4 — contratando direto, um terço do preço de agência. A portaria fica a 3 km da vila de Caeté-Açu.'},
            {'nome': 'Cachoeira do Riachinho + vila do Capão', 'rec': 2, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Vale do Capão',
             'desc': 'A versão leve do mesmo dia, para quem não quiser a subida: trilha de 5 a 10 minutos até o poço e a manhã livre na vila de Caeté-Açu. O grupo se reencontra no almoço, e ninguém precisa subir por obrigação.'},
            {'nome': 'Almoço na vila de Caeté-Açu', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': '3 km da portaria',
             'desc': 'O reencontro do grupo depois da trilha. Sem pressa — mas com o relógio da volta em mente: são 74 km até Lençóis, fora da exceção dos trechos curtos, e é preciso sair do Capão até as 16h.'},
        ],
    },
    {
        'id': 'd3', 'rotulo': 'Seg 19', 'titulo': 'Poço Azul e Mucugê',
        'ancora': 'Mudança de base: Lençóis → Poço Azul → Mucugê. Os raios entram na água das 12h30 às 14h.',
        'opcoes': [
            {'nome': 'Poço Azul — flutuação na caverna alagada', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '~95 km · ~1h40',
             'desc': 'Flutuação sobre uma caverna alagada de 20 m de profundidade e água transparente, com o feixe de sol atravessando a água entre 12h30 e 14h. A taxa de R$ 30 inclui colete e máscara, e exige banho antes de entrar para tirar o protetor solar. <strong>A permanência é curta — 20 a 30 minutos por grupo</strong>. A janela do fenômeno fecha em 20/10: se a segunda amanhecer nublada, a terça ainda serve, a ~1h30 de Mucugê.'},
            {'nome': 'Centro histórico de Mucugê', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Mucugê, a pé',
             'desc': 'Conjunto tombado pelo IPHAN em 1980: cerca de 300 casas térreas e 10 sobrados do século XIX em três ruas planas. Chegando por volta das 16h, dá para percorrer tudo a pé com a luz do fim de tarde — e ver o Cemitério Bizantino iluminado na entrada da cidade depois do jantar.'},
            {'nome': 'Jantar no Paraguassu', 'rec': 2, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Rua Caetité, no centro histórico · 19h às 23h',
             'desc': 'Cozinha contemporânea do chef André Chequer, no hotel Refúgio na Serra, dentro da área tombada '
                     '— o jantar mais elaborado do eixo sul do roteiro, e a poucos passos da pousada. '
                     '<strong>O menu degustação é tradicional aos sábados, e o grupo não passa nenhum sábado em Mucugê</strong>, '
                     'então aqui vale o cardápio normal. Serve almoço das 12h às 15h e jantar das 19h às 23h. '
                     'Vale para as duas noites em Mucugê, a de segunda e a de terça.'},
            {'nome': 'Igreja Matriz de Santa Isabel', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mucugê',
             'desc': 'Meados do século XIX, ao lado do centro. Custa 20 minutos.'},
        ],
    },
    {
        'id': 'd4', 'rotulo': 'Ter 20', 'titulo': 'Garimpo, cemitério e cachoeiras',
        'ancora': 'Nenhuma. Tudo a até 2 km do centro de Mucugê — o dia leve entre a Fumaça e o Buracão.',
        'opcoes': [
            {'nome': 'Parque Municipal de Mucugê — museu, Piabinha e Tiburtino', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': 'Mucugê · R$ 20 · 8h30 às 17h30',
             'desc': 'Uma entrada de R$ 20 cobre tudo o que o grupo escolheu para a manhã: o <strong>Museu Vivo do Garimpo</strong>, montado numa toca de garimpeiro restaurada, com diamantes, carbonados e máquinas de lapidação inglesas do século XIX; a <strong>Cachoeira da Piabinha</strong>, a poucos minutos a pé da sede; e a <strong>Cachoeira do Tiburtino</strong>, a uns 20 minutos pela mesma trilha, larga e praticamente plana, com poço raso de um lado e fundo do outro. Ainda passa pelo Projeto Sempre-Viva e por um trecho da Estrada Real.'},
            {'nome': 'Cemitério Santa Isabel ("Bizantino")', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Beira da BA-142 · gratuito',
             'desc': 'Mausoléus brancos em estilo bizantino, com torres e cruzes em miniatura, encravados ao pé do paredão de pedra — construído entre 1850 e 1886, é apontado como único das Américas nesse estilo. Entrada gratuita, sem guia, visita rápida. Os relatos o descrevem como o ponto mais singular de Mucugê, e ele recebe iluminação à noite.'},
            {'nome': 'Poço Azul, se a segunda nublar', 'rec': 2, 'tipo': 'principal', 'status': 'disponivel',
             'onde': '~66 km · ~1h30',
             'desc': 'O plano B do dia 19. A janela dos raios vai até 20/10, então a terça ainda serve: sair de Mucugê por volta das 10h45 e voltar no meio da tarde. O parque municipal passa para a manhã, que abre às 8h30.'},
            {'nome': 'Café Igaraçu — do plantio à xícara', 'rec': 3, 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Distrito de Cascavel · a partir de R$ 100',
             'desc': 'Vivência guiada do processo do café na Fazenda Matos — plantio, colheita, torra e degustação no cafezal com bolos e biscoitos. Fica entre Mucugê e Ibicoara, com os últimos 10 km por estrada de terra entre eucaliptos, e <strong>exige agendamento</strong>. Mais completa que a do Sítio Canjerana, mas mais cara e mais longe — só vale se a tarde de terça sobrar e o grupo quiser o café com mais profundidade.'},
        ],
    },
    {
        'id': 'd5', 'rotulo': 'Qua 21', 'titulo': 'Buracão e Ibicoara',
        'ancora': 'Mucugê → Ibicoara ~1h15, e mais 28 km de terra até a portaria. O Buracão só aceita entrada até as 11h.',
        'opcoes': [
            {'nome': 'Cachoeira do Buracão', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '28 km de terra de Ibicoara',
             'desc': 'O consenso das fontes é raro nesse grau: está entre os visuais mais impressionantes de toda a Chapada. São 3 km de trilha ao longo do Rio Espalhado, com poucas subidas e terreno quase todo plano — dificuldade leve a moderada, cerca de 1h de caminhada. No trecho final, ou se entra nadando por um cânion estreito até a queda de 85 m se revelar, ou se fica no mirante. Guia obrigatório, da associação de condutores de Ibicoara. <strong>Dormir em Ibicoara é o que tira este dia das 5h de carro</strong> que custava saindo de Mucugê.'},
            {'nome': 'Sítio Canjerana — café e morango', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Beira da rodovia, perto do centro',
             'desc': 'Colheita de morango direto do pé, trilha pelo cafezal sombreado e degustação de café especial na cafeteria do sítio, em cerca de 2h. R$ 80 a primeira pessoa e R$ 50 cada adicional. <strong>Exige agendamento, e a agenda publicada mostra um horário das 13h às 14h30</strong> — que bate com a volta do Buracão. Pedir um horário depois das 15h antes de contar com ele.'},
            {'nome': 'A vila de Ibicoara à noite', 'rec': 3, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Centro, a pé',
             'desc': 'Cidade pequena, de pousadas simples e praça central. Jantar sem esticar: quinta é o dia mais longo de estrada no meio da viagem.'},
            {'nome': 'Cachoeira do Licuri', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': '9 km de carro + 2 km de trilha',
             'desc': 'Queda de 73 m, com trilha de cerca de 30 minutos e esforço moderado. Para quem voltar do Buracão com energia — mas disputa a tarde com o Sítio Canjerana, e as duas não cabem.'},
            {'nome': 'Cachoeira Véu de Noiva', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'No caminho',
             'desc': 'Queda alta com mirante, na estrada para Ibicoara. Parada rápida, se o guia topar.'},
        ],
    },
    {
        'id': 'd6', 'rotulo': 'Qui 22', 'titulo': 'Pratinha, e a Lapa Doce se der',
        'ancora': 'Ibicoara → Pratinha, ~215–230 km · ~4h15 pelo asfalto. A Lapa Doce só entra se o grupo estiver em Iraquara até as 11h15.',
        'opcoes': [
            {'nome': 'Gruta da Lapa Doce', 'rec': 2, 'tipo': 'principal', 'status': 'ambigua',
             'onde': 'Iraquara · ~R$ 60–80',
             'desc': 'Caminhada guiada de 1h30 a 2h por um salão de formações que os relatos descrevem como o mais impressionante do circuito de Iraquara. Guia incluso, sai da portaria. Terreno plano, sem exigência física — só escuro, então lanterna e calçado fechado. <strong>O site oficial não publica tabela</strong>: os R$ 60 a R$ 80 vêm das avaliações recentes da própria página. <strong>Decidida no dia</strong>, na chegada a Iraquara: só entra se o grupo estiver lá até as 11h15 e com disposição.'},
            {'nome': 'Fazenda Pratinha e Gruta Azul', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '10,8 km da Lapa Doce · R$ 90',
             'desc': 'O plano principal da quinta. Rio de água transparente, a Gruta da Pratinha e a Gruta Azul no mesmo complexo, com restaurante e cafeteria. <strong>A luz da Gruta Azul em 22/10 é incerta:</strong> as fontes divergem no horário (entre 12h30 e 15h30) e na época (abril a setembro, ou até outubro) — perguntar à fazenda pelo WhatsApp. Indo só à Pratinha, a tarde inteira cobre todas as janelas citadas. Pela tabela oficial, a entrada é R$ 90 e <strong>a flutuação é cobrada à parte, R$ 100 por pessoa</strong>: R$ 760 para os quatro com flutuação. Entrada até 16h, permanência até 17h.'},
            {'nome': 'Caverna Torrinha', 'rec': 2, 'tipo': 'principal', 'status': 'disponivel',
             'onde': '1,9 km da Lapa Doce · R$ 30 a R$ 150',
             'desc': 'Considerada a caverna de maior diversidade de formações do Brasil, com agulhas de aragonita e flores de gipsita que não existem nas outras duas. Aberta todos os dias das 8h às 17h, com três percursos de 700 m a 2 km. <strong>Troca, não soma:</strong> num dia com 5h30 de carro, só entra no lugar da Lapa Doce.'},
            {'nome': 'Jantar de despedida em Lençóis', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Centro de Lençóis',
             'desc': 'Última noite na Chapada, no melhor polo de comida do roteiro. Lampião, Garimpo Gourmet, Cozinha Aberta e Bistrô do Mato estão na lista.'},
        ],
    },
    {
        'id': 'd7', 'rotulo': 'Sex 23', 'titulo': 'Volta para casa',
        'ancora': 'Lençóis → Juazeiro, 489 km · ~7h10. Saindo às 8h, chega-se por volta das 16h.',
        'opcoes': [
            {'nome': 'Sair às 8h direto para casa', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '—',
             'desc': 'Chegada por volta das 16h com o almoço incluído, ainda com sol — e a sexta à noite já em casa.'},
            {'nome': 'Sushi à noite em Juazeiro', 'rec': 1, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Juazeiro',
             'desc': 'O jantar da chegada. O resto do fim de semana — rio, ilhas, jetski, churrasco — está no arquivo do fim de semana.'},
            {'nome': 'Almoço em Jacobina', 'rec': 2, 'tipo': 'leve', 'status': 'ambigua',
             'onde': '~4h30 depois da saída',
             'desc': 'O encaixe natural de horário e a melhor estrutura da rota, com metade do caminho já feita. <strong>Falta escolher o restaurante.</strong>'},
            {'nome': 'Senhor do Bonfim, almoço mais tarde', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': '~1h depois de Jacobina',
             'desc': 'Alternativa a Jacobina para quem preferir esticar mais antes de parar.'},
            {'nome': 'Buraco do Possidônio', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Morro do Chapéu',
             'desc': 'Cratera com mata nativa no fundo. Parada rápida, se já estiver parando em Morro do Chapéu.'},
            {'nome': 'Cachoeira do Ferro Doido', 'rec': 4, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Morro do Chapéu, 18 km do centro',
             'desc': 'Cânion de mais de 100 m com quedas em degraus, a 650 m de caminhada do estacionamento — dez minutos, esforço leve. Morro do Chapéu está na estrada de casa, e a cachoeira abre de segunda a sexta. <strong>Mas a recomendação não se sustenta em outubro:</strong> os relatos são consistentes em dizer que só vale na estação chuvosa, porque fora dela é raro ter água — e outubro fecha a estação seca. Some-se a isso a falta de sinalização e de estrutura de segurança no local. Vale como aposta de 40 minutos, não como programa contado.'},
        ],
    },
]

RESTAURANTES = [
    ('Lençóis', ['Quilombola — godó de banana verde, cortado de palma',
                 'Cozinha Aberta', 'Bodega',
                 'Lampião Cozinha Nordestina — moquecas e carne de sol',
                 'Garimpo Gourmet — regional farto',
                 'Bistrô do Mato — massas e pratos leves',
                 'Via Terra Bistrô']),
    ('No caminho', ['Vila de Caeté-Açu — almoço depois da Fumaça',
                    'APA Restaurante — anexo ao Poço Azul, resolve o almoço do dia da flutuação',
                    'Gruta Lapa Doce — restaurante no próprio complexo',
                    'Fazenda Pratinha — restaurante e cafeteria']),
    ('Mucugê', ['Paraguassu — contemporâneo, no Refúgio na Serra, na Rua Caetité',
               'Jantar no centro — melhor gastronomia do eixo sul']),
    ('Ibicoara', ['Cafeteria do Sítio Canjerana — café especial', 'Jantar no centro da vila']),
    ('Volta', ['Jacobina — a definir', 'Senhor do Bonfim — alternativa mais tarde']),
]

FONTES_CURADORIA = [
    ('Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/', 'acessos, horários e taxas dos atrativos, incluindo a Fumaça'),
    ('Um Viajante', 'https://www.umviajante.com.br/bahia/', 'relatos de Lapa Doce, Pratinha, Buracão, Pai Inácio e do horário-limite de subida'),
    ('Guia dos Trilheiros — Buracão', 'https://guiadostrilheiros.com.br/cachoeira-do-buracao/', 'última entrada às 11h, ingresso e valor do guia'),
    ('Vivai e Janoo — Ibicoara', 'https://janoo.com.br/lugar/sitiocanjerana', 'Sítio Canjerana e Café Igaraçu: preço, agendamento e horários publicados'),
    ('Conecta Chapada', 'https://conectachapada.com.br/trilha-da-cachoeira-do-buracao/', 'trilha do Buracão e pôr do sol do Pai Inácio'),
    ('Vem Pra Bahia', 'https://vemprabahia.com.br/cemiterio-bizantino-de-mucuge-saiba-a-historia-e-como-visitar/', 'Cemitério Bizantino e Projeto Sempre-Viva'),
    ('TripAdvisor — Ferro Doido', 'https://www.tripadvisor.com.br/Attraction_Review-g2347287-d7182501-Reviews-Cachoeira_Ferro_Doido-Morro_Do_Chapeu_State_of_Bahia.html', 'avaliações que apontam a falta de água fora da estação chuvosa'),
    ('YouTube — Trilha da Cachoeira do Buracão', 'https://www.youtube.com/watch?v=lAvhDwxt8F4', 'vídeo da trilha inteira, útil para calibrar o esforço'),
    ('YouTube — Roteiro de 6 dias saindo de Lençóis', 'https://www.youtube.com/watch?v=UgOb0fI3CgE', 'encadeamento de passeios num roteiro de duração parecida'),
    ('YouTube — Morro do Chapéu e o Ferro Doido', 'https://www.youtube.com/watch?v=oEiFHZ_AfHE', 'estado da cachoeira e do mirante'),
]


# ─────────────────────────────────────────────────────────────────────────────
# Material de avaliação por opção — blogs e vídeos, todos verificados em
# 23/08/2026 (HTTP 200 e, no caso dos vídeos, título conferido via oEmbed).
# A chave é o nome da opção; opção sem entrada aqui simplesmente não mostra links.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Instagram de quem opera o lugar — levantado em 23/09/2026. Só entram perfis
# do próprio atrativo, do restaurante ou da associação que conduz a trilha:
# o Instagram serve para ver o estado atual do lugar e falar com quem atende,
# não para acumular perfis de viajante. Atrativo sem operador (o Cemitério
# Bizantino, a Igreja Matriz, as vilas) fica sem link, e tudo bem.
#   nome da opção -> (rótulo do chip, perfil)
# ─────────────────────────────────────────────────────────────────────────────

INSTAGRAM = {
    'Morro do Pai Inácio': ('Morro do Pai Inácio', 'morrodopaiinaciooficial'),
    'Jantar no Quilombola': ('Quilombola', 'restaurantequilombola'),
    'Jantar no Paraguassu': ('Paraguassu', 'restaurante_paraguassu'),
    'Cachoeira da Fumaça por cima': ('ACV-VC — condutores do Capão', 'acv_vc'),
    'Cachoeira do Riachinho + vila do Capão': ('ACV-VC — condutores do Capão', 'acv_vc'),
    'Poço Azul — flutuação na caverna alagada': ('Poço Azul', 'poco_azul_chapadadiamantina'),
    'Poço Azul, se a segunda nublar': ('Poço Azul', 'poco_azul_chapadadiamantina'),
    'Parque Municipal de Mucugê — museu, Piabinha e Tiburtino': ('Projeto Sempre-Viva', 'projeto_sempreviva'),
    'Café Igaraçu — do plantio à xícara': ('Café Igaraçu', 'agrocafeigaracu'),
    'Cachoeira do Buracão': ('Cachoeira do Buracão', 'cachoeiradoburacao_oficial'),
    'Sítio Canjerana — café e morango': ('Café Canjerana', 'cafe_canjerana'),
    'Gruta da Lapa Doce': ('Gruta Lapa Doce', 'grutalapadoce'),
    'Fazenda Pratinha e Gruta Azul': ('Fazenda Pratinha', 'fazendapratinhaoficial'),
    'Caverna Torrinha': ('Caverna Torrinha', 'cavernatorrinha_oficial'),
    'Cachoeira do Ferro Doido': ('Cachoeira do Ferro Doido', 'cachoeira_do_ferro_doido'),
}


MATERIAL = {
    'Morro do Pai Inácio': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/morro-do-pai-inacio/'),
        ('blog', 'Um Viajante', 'https://www.umviajante.com.br/bahia/7779-morro-do-pai-inacio-na-chapada-diamantina'),
        ('video', 'O Descobridor — Lapa Doce, Pratinha, Gruta Azul e Pai Inácio',
         'https://www.youtube.com/watch?v=W670KR_7TX0'),
    ],
    'Gruta da Lapa Doce': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/gruta-da-lapa-doce/'),
        ('blog', 'Um Viajante — Lapa Doce, Pratinha e Gruta Azul',
         'https://www.umviajante.com.br/bahia/7755-gruta-lapa-doce-pratinha-e-gruta-azul-na-chapada-diamantina'),
        ('blog', 'Melhores Destinos', 'https://guia.melhoresdestinos.com.br/gruta-da-lapa-doce-221-6130-l.html'),
        ('video', 'Chapada Adventure Daniel — o circuito das grutas em um dia',
         'https://www.youtube.com/watch?v=mCM1Fgfu-hA'),
    ],
    'Fazenda Pratinha e Gruta Azul': [
        ('blog', 'Guia Chapada Diamantina — Rio e Gruta Pratinha',
         'https://www.guiachapadadiamantina.com.br/rio-e-gruta-pratinha/'),
        ('blog', 'Melhores Destinos — Pratinha e Gruta Azul',
         'https://guia.melhoresdestinos.com.br/gruta-da-pratinha-e-gruta-azul-221-6131-l.html'),
        ('video', 'O Descobridor — o feixe de luz da Gruta Azul',
         'https://www.youtube.com/watch?v=W670KR_7TX0'),
    ],
    'Ribeirão do Meio': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/ribeirao-do-meio/'),
        ('blog', 'Melhores Destinos',
         'https://guia.melhoresdestinos.com.br/ribeirao-do-meio-ribeirao-de-cima-e-ribeirao-de-baixo-221-6127-l.html'),
    ],
    'Cachoeira do Mosquito + Fazenda Santo Antônio': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/cachoeira-do-mosquito/'),
        ('blog', 'Melhores Destinos', 'https://guia.melhoresdestinos.com.br/cachoeira-do-mosquito-221-6126-l.html'),
    ],
    'Marimbus — canoa no "pantanal baiano"': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/marimbus/'),
    ],
    'Poço Azul — flutuação na caverna alagada': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/poco-azul/'),
        ('video', 'Vamos Trilhar — Poço Azul e Poço Encantado',
         'https://www.youtube.com/watch?v=mWiTlT0Estw'),
        ('video', 'Lyla Pinheiro — como é a flutuação, do começo ao fim',
         'https://www.youtube.com/watch?v=jNV9DsaheLI'),
    ],
    'Vila de Igatu e as ruínas': [
        ('blog', 'Viaje com Norma', 'https://viajecomnorma.com.br/igatu-ba-vila-de-pedra-chapada-diamantina/'),
        ('blog', 'Como Viajei — ruínas, Gruna do Brejo e Mirante do Cruzeiro',
         'https://comoviajeiblog.wordpress.com/2022/10/04/a-gruna-do-brejo-as-ruinas-de-igatu-a-cidade-de-pedra-e-o-mirante-do-cruzeiro/'),
        ('video', 'Três mochilas pelo mundo — a vila inteira a pé',
         'https://www.youtube.com/watch?v=yrujBN-p4q4'),
        ('video', 'Rolê Família — documentário sobre a vila',
         'https://www.youtube.com/watch?v=GH43k6q9xQc'),
    ],
    'Gruna do Brejo': [
        ('blog', 'Como Viajei — a mina visitada no escuro',
         'https://comoviajeiblog.wordpress.com/2022/10/04/a-gruna-do-brejo-as-ruinas-de-igatu-a-cidade-de-pedra-e-o-mirante-do-cruzeiro/'),
    ],
    'Rampa do Caim': [
        ('blog', 'Chapada Trekking — a trilha como as operadoras vendem',
         'https://chapadatrekking.com.br/roteiros-de-2-dias/igatu-rampa-do-caim-andarai/'),
    ],
    'Cachoeira do Buracão': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/cachoeira-do-buracao/'),
        ('blog', 'Conecta Chapada — a trilha passo a passo',
         'https://conectachapada.com.br/trilha-da-cachoeira-do-buracao/'),
        ('video', 'Vamos Trilhar — a trilha inteira, boa para calibrar o esforço',
         'https://www.youtube.com/watch?v=lAvhDwxt8F4'),
    ],
    'Cachoeira do Licuri': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/cachoeira-do-licuri/'),
    ],
    'Parque Municipal de Mucugê — museu, Piabinha e Tiburtino': [
        ('blog', 'Guia Chapada Diamantina — Parque Municipal de Mucugê',
         'https://www.guiachapadadiamantina.com.br/parque-municipal-de-mucuge/'),
        ('blog', 'Wikipédia — Cachoeira da Piabinha', 'https://pt.wikipedia.org/wiki/Cachoeira_da_Piabinha'),
    ],
    'Caverna Torrinha': [
        ('blog', 'Site oficial — horários, percursos e ingressos', 'https://cavernatorrinha.com.br/'),
    ],
    'Cachoeira da Fumaça por cima': [
        ('blog', 'Guia Chapada Diamantina — Fumaça por cima', 'https://www.guiachapadadiamantina.com.br/cachoeira-da-fumaca/'),
    ],
    'Sítio Canjerana — café e morango': [
        ('blog', 'Vivai — a experiência, com preço e agendamento',
         'https://vivaiapp.com.br/experiencia/canjeranacafe-passeio-na-plantacao-cafeteria-em-ibicoara-chapada-diama'),
        ('blog', 'Janoo — horários publicados', 'https://janoo.com.br/lugar/sitiocanjerana'),
    ],
    'Café Igaraçu — do plantio à xícara': [
        ('blog', 'Janoo — Café Igaraçu', 'https://janoo.com.br/lugar/cafeigaracu'),
    ],
    'Poço Azul, se a segunda nublar': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/poco-azul/'),
    ],
    'Rio Serrano e Salão de Areias Coloridas': [
        ('blog', 'Viagens e Caminhos — o que fazer em Lençóis',
         'https://www.viagensecaminhos.com/lencois-ba/'),
        ('video', 'Prefiro Viajar — caldeirões do Serrano e o salão de areias',
         'https://www.youtube.com/watch?v=zH-MD2jO-js'),
        ('video', 'Mixileiros — Serrano, areias coloridas e Poço Halley',
         'https://www.youtube.com/watch?v=YTe9OsczhRA'),
    ],
    'Cemitério Santa Isabel ("Bizantino")': [
        ('blog', 'Vem Pra Bahia — história e como visitar',
         'https://vemprabahia.com.br/cemiterio-bizantino-de-mucuge-saiba-a-historia-e-como-visitar/'),
    ],
    'Centro histórico de Mucugê': [
        ('video', 'Trip Partiu — Mucugê e Igatu no mesmo episódio',
         'https://www.youtube.com/watch?v=alSONfBSk0k'),
    ],
    'Igatu, o que faltou da segunda': [
        ('blog', 'Viaje com Norma', 'https://viajecomnorma.com.br/igatu-ba-vila-de-pedra-chapada-diamantina/'),
        ('video', 'Trip Partiu — Mucugê e Igatu no mesmo episódio',
         'https://www.youtube.com/watch?v=alSONfBSk0k'),
    ],
    'Volta pelo centro histórico iluminado': [
        ('blog', 'Viagens e Caminhos — o que fazer em Lençóis',
         'https://www.viagensecaminhos.com/lencois-ba/'),
    ],
    'Casa de Cultura Afrânio Peixoto + Mercado Cultural': [
        ('blog', 'Viagens e Caminhos — o que fazer em Lençóis',
         'https://www.viagensecaminhos.com/lencois-ba/'),
    ],
    'Buraco do Possidônio': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/buraco-do-possidonio/'),
    ],
    'Cachoeira do Ferro Doido': [
        ('blog', 'Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/cachoeira-do-ferro-doido/'),
        ('blog', 'TripAdvisor — as avaliações que apontam a falta de água',
         'https://www.tripadvisor.com.br/Attraction_Review-g2347287-d7182501-Reviews-Cachoeira_Ferro_Doido-Morro_Do_Chapeu_State_of_Bahia.html'),
        ('video', 'Três mochilas pelo mundo — Morro do Chapéu e o Ferro Doido',
         'https://www.youtube.com/watch?v=oEiFHZ_AfHE'),
    ],
}

# Fotos dos cabeçalhos — Wikimedia Commons, baixadas para o projeto em 23/08/2026.
CREDITOS = [
    ('Capa do roteiro — Morro do Pai Inácio', 'Anne Moraes', 'CC BY-SA 3.0',
     'https://commons.wikimedia.org/wiki/File:Morro_do_Pai_In%C3%A1cio_2015.jpg'),
    ('Atrações — Cachoeira do Buracão', 'Evandro César Cardoso', 'CC BY-SA 4.0',
     'https://commons.wikimedia.org/wiki/File:CACHOEIRA_DO_BURAC%C3%83O.jpg'),
    ('Hospedagem — centro histórico de Lençóis', 'Patricia Laraia', 'CC BY-SA 4.0',
     'https://commons.wikimedia.org/wiki/File:Centro_hist%C3%B3rico_de_Len%C3%A7%C3%B3is_por_Patricia_Laraia.jpg'),
    ('Mapa — Vale do Pai Inácio', 'Joedison Rocha', 'CC BY-SA 4.0',
     'https://commons.wikimedia.org/wiki/File:Vale_do_Pai_In%C3%A1cio.jpg'),
]


# A própria marca do Instagram, como glifo. Vai embutida no HTML — nada de CDN
# de ícones, que quebraria as páginas offline. Caminho de 24×24 do simple-icons,
# em currentColor para seguir a cor do chip.
SVG_INSTA = (
    '<svg class="ico-insta" viewBox="0 0 24 24" width="13" height="13" '
    'fill="currentColor" aria-hidden="true" focusable="false"><path d="M12 2.16c3.2 0 3.58.01 4.85.07 '
    '1.17.05 1.8.25 2.23.41.56.22.96.48 1.38.9.42.42.68.82.9 1.38.16.43.36 1.06.41 2.23.06 1.27.07 '
    '1.65.07 4.85s-.01 3.58-.07 4.85c-.05 1.17-.25 1.8-.41 2.23-.22.56-.48.96-.9 1.38-.42.42-.82.68-1.38.9-.43.16-'
    '1.06.36-2.23.41-1.27.06-1.65.07-4.85.07s-3.58-.01-4.85-.07c-1.17-.05-1.8-.25-2.23-.41-.56-.22-.96-.48-1.38-.9-'
    '.42-.42-.68-.82-.9-1.38-.16-.43-.36-1.06-.41-2.23C2.17 15.58 2.16 15.2 2.16 12s.01-3.58.07-4.85c.05-1.17.25-1.8'
    '.41-2.23.22-.56.48-.96.9-1.38.42-.42.82-.68 1.38-.9.43-.16 1.06-.36 2.23-.41C8.42 2.17 8.8 2.16 12 2.16M12 0C8.74 0 '
    '8.33.01 7.05.07 5.78.13 4.9.33 4.14.63c-.79.3-1.46.72-2.13 1.38C1.35 2.68.94 3.35.63 4.14.33 4.9.13 5.78.07 7.05.01 '
    '8.33 0 8.74 0 12s.01 3.67.07 4.95c.06 1.27.26 2.15.56 2.91.31.79.72 1.46 1.38 2.13.67.67 1.34 1.08 2.13 '
    '1.38.76.3 1.64.5 2.91.56C8.33 23.99 8.74 24 12 24s3.67-.01 4.95-.07c1.27-.06 2.15-.26 2.91-.56.79-.3 1.46-.72 '
    '2.13-1.38.67-.67 1.08-1.34 1.38-2.13.3-.76.5-1.64.56-2.91.06-1.28.07-1.69.07-4.95s-.01-3.67-.07-4.95c-.06-1.27-.26-'
    '2.15-.56-2.91-.3-.79-.72-1.46-1.38-2.13-.67-.67-1.34-1.08-2.13-1.38-.76-.3-1.64-.5-2.91-.56C15.67.01 15.26 0 12 '
    '0z"/><path d="M12 5.84a6.16 6.16 0 1 0 0 12.32 6.16 6.16 0 0 0 0-12.32zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 '
    '8z"/><circle cx="18.41" cy="5.59" r="1.44"/></svg>'
)

ICONE = {'blog': '📄', 'video': '▶', 'insta': SVG_INSTA}


def links_html(nome):
    itens = list(MATERIAL.get(nome) or [])
    perfil = INSTAGRAM.get(nome)
    if perfil:
        rotulo, conta = perfil
        itens.append(('insta', rotulo, f'https://www.instagram.com/{conta}/'))
    if not itens:
        return ''
    chips = ''.join(
        f'<a class="opt-link {tipo}" href="{B.esc(url)}" target="_blank" rel="noopener" '
        f'title="{B.esc(rotulo)}">{ICONE[tipo]} {B.esc(rotulo)}</a>'
        for tipo, rotulo, url in itens)
    return f'<div class="opt-links">{chips}</div>'


def capa_html(slug, foto, nome):
    """Foto do lugar, ou o cabeçalho gráfico de quem ainda não tem uma."""
    if foto:
        autor, lic, pagina = FOTOS.get(foto, ('', '', ''))
        credito = (f'<a class="opt-foto-cred" href="{B.esc(pagina)}" target="_blank" rel="noopener" '
                   f'title="{B.esc(autor)} · {B.esc(lic)} · Wikimedia Commons">📷</a>') if pagina else ''
        return (f'<div class="opt-foto">'
                f'<img src="{IMG_DIR}/{foto}.jpg" alt="{B.esc(nome)}" loading="lazy" '
                f'width="800" height="533">{credito}</div>')
    return '<div class="opt-foto sem-foto" aria-hidden="true"></div>'


def card(op):
    emoji, rotulo, cls = SELOS[op['status']]
    r_emoji, r_rotulo, r_cls = REC[op['rec']]
    tipo = 'Principal' if op['tipo'] == 'principal' else 'Leve'
    material = links_html(op['nome'])
    slug, foto = ficha(op['nome'])
    return (
        f'<article id="{slug}" class="opt-card fade-in {cls}" data-rec="{op["rec"]}" '
        f'data-status="{op["status"]}" data-material="{"sim" if material else "nao"}">'
        f'{capa_html(slug, foto, op["nome"])}'
        f'<div class="opt-corpo">'
        f'<div class="opt-top"><span class="opt-rec {r_cls}">{r_emoji} {B.esc(r_rotulo)}</span>'
        f'<span class="opt-tipo">{tipo}</span></div>'
        f'<h3 class="opt-nome">{B.esc(op["nome"])}</h3>'
        f'<p class="opt-onde">{B.esc(op["onde"])} · <span class="opt-selo">{emoji} {B.esc(rotulo)}</span></p>'
        f'<p class="opt-nota">{op["desc"]}</p>'
        f'{material}'
        f'</div>'
        f'</article>'
    )


def bloco_dia(d):
    ordenadas = sorted(d['opcoes'], key=lambda o: (o['rec'], o['nome']))
    cards = ''.join(card(o) for o in ordenadas)
    return (
        f'<div class="dia-bloco" data-dia="{d["id"]}">'
        f'<div class="dia-cab"><h2 class="dia-tit"><span class="dia-chip">{d["rotulo"]}</span>{B.esc(d["titulo"])}</h2>'
        f'<p class="dia-ancora">⚓ {B.esc(d["ancora"])}</p></div>'
        f'<div class="opt-grid">{cards}</div>'
        f'<p class="dia-vazio">Nenhum lugar deste dia passa no filtro atual.</p>'
        f'</div>'
    )


todas = [o for d in DIAS for o in d['opcoes']]
total = len(todas)
imperdiveis = sum(1 for o in todas if o['rec'] == 1)
escolhidas = sum(1 for o in todas if o['status'] == 'escolhida')

legenda = ''.join(
    f'<span class="leg-item"><b>{e}</b> {B.esc(r)}</span>' for e, r, _ in REC.values()
)

com_material = sum(1 for o in todas if MATERIAL.get(o['nome']))
por_rec = {n: sum(1 for o in todas if o['rec'] == n) for n in REC}

filtros_dia = ''.join(
    f'<button class="filtro-btn" data-dia="{d["id"]}">{d["rotulo"]}</button>' for d in DIAS
)

filtros_rec = ''.join(
    f'<button class="filtro-btn rec-btn {cls}" data-rec="{n}">{emoji} {B.esc(rot)} '
    f'<span class="filtro-n">{por_rec[n]}</span></button>'
    for n, (emoji, rot, cls) in REC.items()
)

filtros_extra = (
    f'<button class="filtro-btn" data-extra="escolhida">✅ Só o que está no roteiro '
    f'<span class="filtro-n">{escolhidas}</span></button>'
    f'<button class="filtro-btn" data-extra="decidir">❓ Precisa de decisão</button>'
    f'<button class="filtro-btn" data-extra="material">🔗 Com blog ou vídeo '
    f'<span class="filtro-n">{com_material}</span></button>'
)

barra_filtros = (
    '<div class="filtro-grupo"><span class="filtro-rot">Recomendação</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-rec="todos">Todas</button>'
    f'{filtros_rec}</div></div>'
    '<div class="filtro-grupo"><span class="filtro-rot">Dia</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-dia="todos">Todos</button>'
    f'{filtros_dia}</div></div>'
    '<div class="filtro-grupo"><span class="filtro-rot">Atalhos</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-extra="todos">Tudo</button>'
    f'{filtros_extra}</div></div>'
    '<p class="filtro-saida"><span id="filtro-conta"></span>'
    '<button class="filtro-limpa" type="button">limpar filtros</button></p>'
)

rest_html = ''.join(
    '<div class="info-card fade-in"><h3>' + B.esc(cidade) + '</h3><ul class="rest-lista">'
    + ''.join(f'<li>{B.esc(r)}</li>' for r in lista) + '</ul></div>'
    for cidade, lista in RESTAURANTES
)

fontes_html = ''.join(
    f'<div class="kv"><span class="k"><a href="{B.esc(u)}" target="_blank" rel="noopener">{B.esc(n)}</a></span>'
    f'<span class="v">{B.esc(o)}</span></div>'
    for n, u, o in FONTES_CURADORIA
)

creditos_cabecalhos = ''.join(
    f'<div class="kv"><span class="k">{B.esc(onde)}</span>'
    f'<span class="v">{B.esc(autor)} · <a href="{B.esc(url)}" target="_blank" rel="noopener">'
    f'{B.esc(lic)}</a></span></div>'
    for onde, autor, lic, url in CREDITOS
)

# nome legível da atração que usa cada foto, na ordem em que aparecem na página
usa_foto = {}
for _d in DIAS:
    for _o in _d['opcoes']:
        _s, _f = ficha(_o['nome'])
        if _f and _f not in usa_foto:
            usa_foto[_f] = _o['nome']

creditos_atracoes = ''.join(
    f'<div class="kv"><span class="k">{B.esc(usa_foto[f])}</span>'
    f'<span class="v">{B.esc(FOTOS[f][0])} · <a href="{B.esc(FOTOS[f][2])}" target="_blank" '
    f'rel="noopener">{B.esc(FOTOS[f][1])}</a></span></div>'
    for f in usa_foto if f in FOTOS
)

creditos_html = creditos_cabecalhos + creditos_atracoes
com_foto = len(usa_foto)

corpo = (
    B.page_header(
        trip, 'Os lugares da viagem',
        'Atrações',
        f'{total} lugares nos sete dias do roteiro, com foto, resumo e as leituras que sustentam '
        f'a nota. {imperdiveis} imperdíveis, {escolhidas} já no roteiro.',
        PAGE)
    + B.nav_html(trip, PAGES, PAGE)
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Como ler</span>'
      '<h2 class="section-title">O roteiro está fechado; o resto é plano B</h2>'
      '<p class="section-desc">A âncora é o deslocamento que não se move. O resto cabe naquele dia — '
      'geograficamente e no relógio. A regra do ritmo tranquilo é <strong>no máximo uma principal e uma leve por dia</strong>. '
      'A recomendação combina o consenso de blogs, guias e vídeos com o perfil do grupo: esforço de médio a baixo, '
      'ritmo tranquilo e outubro no fim da seca. O ✅ marca o que entrou no roteiro; '
      'o resto é plano B ou o que cabe se sobrar tempo. Nada aqui está reservado.</p>'
      '<p class="section-desc">Os filtros abaixo se combinam: dá para pedir, por exemplo, '
      '<em>só as imperdíveis da quarta-feira</em>. Cada card traz os links de blog (📄) e de vídeo (▶) '
      'que sustentam a nota, e o ' + SVG_INSTA + ' do perfil de quem opera o lugar — abrir dois ou três antes de decidir vale mais do que qualquer resumo. '
      'O 📷 no canto da foto leva à página da imagem no Wikimedia Commons.</p>'
      '<p class="section-desc">No roteiro, o link <strong>ℹ️ Sobre o lugar</strong> de cada bloco '
      'traz direto para o card daqui.</p>'
      f'<div class="legenda">{legenda}</div>'
      '</div>'
      f'<div class="filtro-barra">{barra_filtros}</div>'
    + ''.join(bloco_dia(d) for d in DIAS)
    + '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Comida</span>'
      '<h2 class="section-title">Onde comer, por trecho</h2>'
      '<p class="section-desc">Levantamento gastronômico acumulado, por trecho do roteiro.</p>'
      '</div>'
      f'<div class="info-grid">{rest_html}</div>'
      '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Procedência</span>'
      '<h2 class="section-title">De onde vem a curadoria</h2>'
      '<p class="section-desc">Blogs de viagem, guias regionais e vídeos consultados em 23/08/2026 e 22/09/2026. '
      'Onde as fontes divergiram, a nota do card diz o que foi considerado.</p>'
      '</div>'
      f'<div class="info-card fade-in">{fontes_html}</div>'
      '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Fotos</span>'
      '<h2 class="section-title">Créditos das imagens</h2>'
      f'<p class="section-desc">As fotos dos cabeçalhos e dos {com_foto} cards com imagem vêm do '
      'Wikimedia Commons, sob licença Creative Commons ou em domínio público, e estão baixadas no '
      'projeto — o site não depende de servidor de terceiros para exibi-las, e continua inteiro '
      'na versão offline. As licenças CC BY e CC BY-SA exigem o crédito que segue.</p>'
      '</div>'
      f'<div class="info-card fade-in">{creditos_html}</div>'
      '</section>'
    + B.footer_html(trip, PAGES)
)

SCRIPT = """
(function () {
  // Tres eixos independentes que se combinam por E: recomendacao, dia e atalho.
  var estado = { rec: 'todos', dia: 'todos', extra: 'todos' };
  var blocos = document.querySelectorAll('.dia-bloco');
  var conta = document.getElementById('filtro-conta');
  var total = document.querySelectorAll('.opt-card').length;

  function passaExtra(card) {
    if (estado.extra === 'todos') return true;
    if (estado.extra === 'material') return card.getAttribute('data-material') === 'sim';
    if (estado.extra === 'decidir') {
      var s = card.getAttribute('data-status');
      return s === 'ambigua' || s === 'conflito';
    }
    return card.getAttribute('data-status') === estado.extra;
  }

  function aplicar() {
    var visiveis = 0;
    blocos.forEach(function (bl) {
      var diaOk = estado.dia === 'todos' || bl.getAttribute('data-dia') === estado.dia;
      var nesteBloco = 0;
      bl.querySelectorAll('.opt-card').forEach(function (card) {
        var ok = diaOk
          && (estado.rec === 'todos' || card.getAttribute('data-rec') === estado.rec)
          && passaExtra(card);
        card.style.display = ok ? '' : 'none';
        if (ok) { nesteBloco++; visiveis++; if (window.revelar) window.revelar(card); }
      });
      bl.style.display = diaOk ? '' : 'none';
      bl.classList.toggle('sem-resultado', diaOk && nesteBloco === 0);
      if (diaOk && window.revelar) {
        bl.querySelectorAll('.dia-cab .fade-in').forEach(function (el) { window.revelar(el); });
      }
    });
    if (conta) {
      var limpo = estado.rec === 'todos' && estado.dia === 'todos' && estado.extra === 'todos';
      conta.textContent = limpo
        ? total + ' lugares catalogados'
        : visiveis + ' de ' + total + ' lugares';
    }
    var botao = document.querySelector('.filtro-limpa');
    if (botao) {
      botao.style.visibility =
        (estado.rec === 'todos' && estado.dia === 'todos' && estado.extra === 'todos')
          ? 'hidden' : 'visible';
    }
  }

  document.querySelectorAll('.filtro-btn').forEach(function (b) {
    var eixo = b.hasAttribute('data-rec') ? 'rec'
             : b.hasAttribute('data-dia') ? 'dia' : 'extra';
    b.addEventListener('click', function () {
      estado[eixo] = b.getAttribute('data-' + eixo);
      document.querySelectorAll('.filtro-btn[data-' + eixo + ']').forEach(function (o) {
        o.classList.toggle('ativo', o === b);
      });
      aplicar();
    });
  });

  var limpa = document.querySelector('.filtro-limpa');
  if (limpa) {
    limpa.addEventListener('click', function () {
      estado = { rec: 'todos', dia: 'todos', extra: 'todos' };
      document.querySelectorAll('.filtro-btn').forEach(function (o) {
        o.classList.toggle('ativo', o.getAttribute('data-rec') === 'todos'
          || o.getAttribute('data-dia') === 'todos'
          || o.getAttribute('data-extra') === 'todos');
      });
      aplicar();
    });
  }

  aplicar();
})();
"""

faltando = [f'{ROOT}/{IMG_DIR}/{f}.jpg' for f in usa_foto
            if not os.path.exists(os.path.join(ROOT, IMG_DIR, f + '.jpg'))]
for f in faltando:
    print(f'⚠️  foto ausente: {f}')

B.write(os.path.join(ROOT, PAGE),
        B.shell(trip, 'Atrações', corpo, PAGE, PAGES, scripts=SCRIPT))
print(f'✅ {PAGE} — {total} atrações · {com_foto} com foto · '
      f'{imperdiveis} imperdíveis · {escolhidas} no roteiro')
