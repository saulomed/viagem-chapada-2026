#!/usr/bin/env python3
"""Gera opcoes.html — o cardápio de opções da viagem, com curadoria.

Cada opção tem descrição própria e nível de recomendação (1 a 4), apurados
em blogs de viagem, guias e vídeos em 23/08/2026. Dentro de cada dia as
opções saem ordenadas da mais recomendada para a menos.

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
    'escolhida': ('✅', 'Escolha da Michele', 'sel-ok'),
    'ambigua': ('❓', 'Precisa de decisão', 'sel-duv'),
    'conflito': ('⚠️', 'Conflita com o horário', 'sel-conf'),
    'disponivel': ('○', 'Na mesa', 'sel-livre'),
}

DIAS = [
    {
        'id': 'd1', 'rotulo': 'Sáb 17', 'titulo': 'A estrada',
        'ancora': 'Juazeiro → Lençóis, 489 km · ~7h10. Não cabe passeio.',
        'opcoes': [
            {'nome': 'Jantar no Quilombola', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Centro de Lençóis',
             'desc': 'Godó de banana verde e cortado de palma — pratos da cozinha baiana de raiz que praticamente não se encontram fora da região. É comida como programa, não só como refeição, e resolve a primeira noite sem exigir nada de ninguém depois de sete horas de estrada.'},
            {'nome': 'Volta pelo centro histórico iluminado', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'A pé',
             'desc': 'O casario colonial de Lençóis ganha outra cara à noite, e a Rua das Pedras concentra mesas na calçada e música ao vivo. Custo zero, esforço zero, e nenhum quilômetro a mais no carro — o encerramento certo para o dia da estrada.'},
            {'nome': 'Paraguassu — menu degustação', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Centro de Lençóis',
             'desc': 'O menu degustação é tradicional aos sábados, e este é o único sábado da viagem. É alternativa ao Quilombola, não soma: quem escolher um abre mão do outro.'},
            {'nome': 'Direto para a pousada', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': '—',
             'desc': 'Escolha perfeitamente legítima depois de sete horas ao volante. O dia seguinte é o mais cheio da viagem.'},
        ],
    },
    {
        'id': 'd2', 'rotulo': 'Dom 18', 'titulo': 'Grutas e mirante',
        'ancora': 'Nenhuma. Base em Lençóis, tudo a até 1h30 de carro.',
        'opcoes': [
            {'nome': 'Morro do Pai Inácio', 'rec': 1, 'tipo': 'leve', 'status': 'conflito',
             'onde': '26 km · ~30–40 min',
             'desc': 'O cartão-postal da Chapada, e o ponto em que todas as fontes concordam sem ressalva. São 500 m de subida em 20 a 30 minutos — íngreme em trechos, mas classificada como fácil — até uma vista de 360° com o Morro do Camelo e o Dois Irmãos. Fica na beira da BR-242, no caminho de volta das grutas, sem quilômetro extra. <strong>O pôr do sol é unanimidade entre os relatos, mas joga a volta a Lençóis para as 18h45, no escuro.</strong> Subindo por volta das 16h, a luz já está baixa e a volta é clara.'},
            {'nome': 'Gruta da Lapa Doce', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '68 km · ~1h30',
             'desc': 'Caminhada guiada de cerca de 1h30 por um salão de formações que os relatos descrevem como o mais impressionante do circuito de Iraquara. Guia obrigatório, contratado na portaria. Terreno plano, sem exigência física — só escuro, então lanterna e calçado fechado.'},
            {'nome': 'Fazenda Pratinha e Gruta Azul', 'rec': 2, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '73 km, ao lado da Lapa Doce',
             'desc': 'Complementa a Lapa Doce no mesmo dia. Na Pratinha dá para fazer snorkel no rio de água transparente, e há tirolesa sobre o lago; a estrutura resolve o almoço. <strong>Detalhe de horário que vale planejar:</strong> na Gruta Azul o feixe de sol entra pela abertura superior entre 14h e 15h — chegar nessa janela muda o passeio.'},
            {'nome': 'Ribeirão do Meio', 'rec': 2, 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Trilha de 3,5 km, do centro',
             'desc': 'Escorregador natural de pedra que termina num poço grande e fundo — o programa mais divertido da viagem em relação ao esforço. A trilha é classificada como fácil, mas são 3,5 km saindo do centro, mais do que "uma caminhada curta". Não cabe no mesmo dia das grutas.'},
            {'nome': 'Poço do Diabo', 'rec': 3, 'tipo': 'principal', 'status': 'disponivel',
             'onde': '19,6 km · ~25 min',
             'desc': 'Queda de 22 m formando uma piscina natural, com trilha de uns 20 minutos à beira do rio. Sugestão da Michele em 09/08. Costuma ser vendido em conjunto com a Cachoeira do Mosquito, mas funciona sozinho e fica bem mais perto.'},
            {'nome': 'Casa de Cultura Afrânio Peixoto + Mercado Cultural', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'A pé',
             'desc': 'Acervo do escritor lençoense da Academia Brasileira de Letras, e artesanato local no mercado. Cerca de 2h, tudo a pé — o encaixe natural para uma manhã de chuva ou para quem não quiser entrar na água.'},
            {'nome': 'Nada. Pousada, rede, livro', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': '—',
             'desc': 'Ritmo tranquilo é isso. O roteiro tem seis dias e nenhum deles é obrigatório.'},
            {'nome': 'Cachoeira do Mosquito + Fazenda Santo Antônio', 'rec': 4, 'tipo': 'principal', 'status': 'disponivel',
             'onde': '40 km, sendo 20 de terra',
             'desc': 'O almoço no fogão a lenha com redário é ótimo e combina com o lado gastronômico da viagem, mas o acesso pesa: 40 km de Lençóis, metade em estrada de terra. Fica atrás do Ribeirão do Meio e do Rio Serrano em custo-benefício, e num dia que já tem as grutas não cabe de jeito nenhum.'},
        ],
    },
    {
        'id': 'd3', 'rotulo': 'Seg 19', 'titulo': 'Descida para o sul',
        'ancora': 'Mudança de base: Lençóis → Mucugê. Se o Poço Azul entrar, ele manda no dia — 12h30 às 14h.',
        'opcoes': [
            {'nome': 'Poço Azul — flutuação na caverna alagada', 'rec': 1, 'tipo': 'principal', 'status': 'ambigua',
             'onde': '~95 km · ~1h40',
             'desc': 'Flutuação sobre uma caverna alagada de 20 m de profundidade e água transparente, com o feixe de sol atravessando a água entre 12h30 e 14h. A taxa de R$ 30 inclui colete e máscara, e exige banho antes de entrar para tirar o protetor solar. <strong>A permanência é curta — 20 a 30 minutos por grupo</strong> —, então o passeio é mais um momento do que um programa de meio período. A janela do fenômeno fecha em 20/10 e o dia 20 virou o Buracão: ou entra aqui, ou sai da viagem.'},
            {'nome': 'Vila de Igatu e as ruínas', 'rec': 1, 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Igatu, a pé',
             'desc': 'Chamada de "Machu Picchu baiana" pelos relatos: ruínas de casas de pedra encaixada sem argamassa, do auge do ciclo do diamante, hoje sítio histórico do garimpo. Tudo se visita a pé e o acesso é livre. É o ponto de maior densidade cultural da viagem com o menor esforço físico.'},
            {'nome': 'Gruna do Brejo', 'rec': 2, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Igatu',
             'desc': 'Não é uma gruta natural: é uma mina de diamante do século XIX escavada à mão, percorrida no escuro com lanterna pelas galerias abertas pelos garimpeiros. Na entrada há um poço grande e fundo para banho depois da visita. Singular — não existe equivalente no resto do roteiro.'},
            {'nome': 'Galeria Arte e Memória', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu',
             'desc': 'Museu a céu aberto com peças do garimpo e exposição de arte contemporânea, com café anexo. Ter a dom, 10h às 18h.'},
            {'nome': 'Rampa do Caim', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu',
             'desc': 'Mirante sobre o vale a partir de Igatu, citado nos relatos como a melhor vista da vila. Entra na conta se a tarde em Igatu for inteira.'},
            {'nome': 'Casa de Lindaura', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu',
             'desc': 'Histórias de família do garimpo contadas em casa, com bolinho de chuva e café. O tipo de parada de 30 minutos que não entra em roteiro de agência.'},
            {'nome': 'Casa de Amarildo dos Santos', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu',
             'desc': 'Livros feitos à mão sobre a vila, pelo próprio autor.'},
            {'nome': 'Igreja de São Sebastião', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Igatu',
             'desc': 'Erguida em pedra em 1844. Ponto de partida da trilha histórica Igatu–Andaraí, que não está no nosso perfil, mas a igreja em si custa 15 minutos.'},
            {'nome': 'Marimbus — canoa no "pantanal baiano"', 'rec': 3, 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Sai de Andaraí',
             'desc': 'Passeio de canoa por área alagada, com esforço zero e ritmo lento. É a alternativa natural se o Poço Azul cair do roteiro — mas consome meio período, o que este dia não tem de sobra.'},
        ],
    },
    {
        'id': 'd4', 'rotulo': 'Ter 20', 'titulo': 'O Buracão',
        'ancora': 'Ibicoara. 118 km · ~2h30 por trecho — o dia é dedicado.',
        'opcoes': [
            {'nome': 'Cachoeira do Buracão', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '118 km · ~2h30',
             'desc': 'O consenso das fontes é raro nesse grau: está entre os visuais mais impressionantes de toda a Chapada. São 3 km de trilha ao longo do Rio Espalhado, com poucas subidas e terreno quase todo plano — dificuldade leve a moderada, cerca de 1h de caminhada. No trecho final, ou se entra nadando por um cânion de 3 m de largura e 90 m de altura até a queda de 85 m se revelar, ou se fica no mirante. Cada um escolhe, e não precisa ser unânime. Guia obrigatório.'},
            {'nome': 'Cachoeira do Licuri', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mesmo complexo',
             'desc': 'Sai no mesmo passeio do Buracão, sem custo de deslocamento extra. Vale perguntar ao guia se cabe no dia.'},
            {'nome': 'Projeto Sempre-Viva e Cachoeira do Tiburtino', 'rec': 3, 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Mucugê',
             'desc': 'A alternativa leve para quem não quiser encarar as 5h de carro do Buracão: 25 minutos de caminhada dentro do único projeto de preservação ambiental da Chapada até uma queda de 30 m, com poço raso de um lado e fundo do outro. Fica em Mucugê, então o grupo pode se dividir sem logística nenhuma.'},
            {'nome': 'Cachoeira Véu de Noiva', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'No caminho',
             'desc': 'Queda alta com mirante, na estrada para Ibicoara. Parada rápida, se o guia topar.'},
        ],
    },
    {
        'id': 'd5', 'rotulo': 'Qua 21', 'titulo': 'Mucugê e volta ao norte',
        'ancora': 'Mucugê → Lençóis, 114 km · ~2h20. Cabe uma coisa em Mucugê antes de sair.',
        'opcoes': [
            {'nome': 'Rio Serrano e Salão de Areias Coloridas', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': 'Lençóis, a pé',
             'desc': 'Caldeirões e piscinas naturais escavados na pedra pelo Rio Lençóis, com o Salão de Areias Coloridas — grutas e túneis de arenito em decomposição, de cores diferentes — na mesma caminhada. Está dentro do perímetro urbano: chega-se de Mucugê e vai a pé da pousada. É o encaixe mais confortável do roteiro inteiro.'},
            {'nome': 'Cemitério Santa Isabel ("Bizantino")', 'rec': 2, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mucugê',
             'desc': 'Mausoléus brancos em estilo bizantino, com torres e cruzes em miniatura, encravados na encosta contra o azul do céu — construído entre 1850 e 1886, é apontado como único das Américas nesse estilo. Os relatos o descrevem como o ponto mais singular de Mucugê, acima do próprio centro histórico.'},
            {'nome': 'Centro histórico de Mucugê', 'rec': 2, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mucugê, a pé',
             'desc': 'Conjunto tombado pelo IPHAN em 1980: cerca de 300 casas térreas e 10 sobrados do século XIX em três ruas planas. Uma volta antes do café resolve, e o centro é plano o bastante para fazer tudo a pé em 10 a 15 minutos.'},
            {'nome': 'Igatu, o que faltou da segunda', 'rec': 2, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'No caminho',
             'desc': 'A rota Mucugê → Lençóis passa por Andaraí e Igatu. É a segunda chance da vila, e a saída mais limpa para a sobrecarga da segunda-feira: o Poço Azul fica no dia 19 e Igatu ganha a manhã de quarta.'},
            {'nome': 'Ribeirão do Meio', 'rec': 2, 'tipo': 'principal', 'status': 'disponivel',
             'onde': 'Lençóis',
             'desc': 'Se não tiver acontecido no domingo, ainda cabe nesta tarde — mas escolhendo entre ele e o Rio Serrano, não os dois.'},
            {'nome': 'Igreja Matriz de Santa Isabel', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Mucugê',
             'desc': 'Meados do século XIX, ao lado do centro. Custa 20 minutos.'},
        ],
    },
    {
        'id': 'd6', 'rotulo': 'Qui 22', 'titulo': 'Volta para casa',
        'ancora': 'Lençóis → Juazeiro, 489 km · ~7h10. Saindo às 8h, chega-se por volta das 16h.',
        'opcoes': [
            {'nome': 'Sair às 8h direto para casa', 'rec': 1, 'tipo': 'principal', 'status': 'escolhida',
             'onde': '—',
             'desc': 'Chegada por volta das 16h com o almoço incluído, ainda com sol — e a quinta à noite já em casa. É o que faz a volta antecipada valer a pena.'},
            {'nome': 'Sushi à noite em Juazeiro', 'rec': 1, 'tipo': 'leve', 'status': 'escolhida',
             'onde': 'Juazeiro',
             'desc': 'O fim de semana em casa começa na quinta à noite. O resto do cardápio — rio, ilhas, jetski, churrasco — está no arquivo do fim de semana.'},
            {'nome': 'Almoço em Jacobina', 'rec': 2, 'tipo': 'leve', 'status': 'ambigua',
             'onde': '~4h30 depois da saída',
             'desc': 'O encaixe natural de horário e a melhor estrutura da rota, com metade do caminho já feita. <strong>Falta escolher o restaurante</strong> — é a pergunta em aberto da Michele.'},
            {'nome': 'Senhor do Bonfim, almoço mais tarde', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': '~1h depois de Jacobina',
             'desc': 'Alternativa a Jacobina para quem preferir esticar mais antes de parar.'},
            {'nome': 'Buraco do Possidônio', 'rec': 3, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Morro do Chapéu',
             'desc': 'Cratera com mata nativa no fundo. Parada rápida, se já estiver parando em Morro do Chapéu.'},
            {'nome': 'Cachoeira do Ferro Doido', 'rec': 4, 'tipo': 'leve', 'status': 'disponivel',
             'onde': 'Morro do Chapéu, 18 km do centro',
             'desc': 'Cânion de mais de 100 m com quedas em degraus, a 650 m de caminhada do estacionamento — dez minutos, esforço leve. Voltou a ser possível porque Morro do Chapéu está na estrada de casa. <strong>Mas a curadoria derrubou a recomendação:</strong> os relatos são consistentes em dizer que só vale na estação chuvosa, porque fora dela é raro ter água — e outubro fecha a estação seca. Some-se a isso a falta de sinalização e de estrutura de segurança no local. Vale como aposta de 40 minutos, não como programa contado.'},
        ],
    },
]

FORA = [
    ('Poço Encantado (Itaetê)', 'Fora da janela dos raios em outubro. Descartado pelo grupo em 08/08.'),
    ('Cachoeira da Fumaça', '12 km ida e volta, 2 km iniciais de subida íngreme, guia obrigatório. Fora do perfil por larga margem.'),
    ('Vale do Capão', 'Caiu junto com a Fumaça. Sobrava o Riachinho, que não justifica 2h de carro e 20 km de terra.'),
    ('Cachoeira do Sossego', '14 km ida e volta sobre leito de rio.'),
    ('Rio de Contas', 'O centro histórico mais rico dos três, mas a 128 km de Mucugê — mais de 2h por trecho.'),
    ('Trilha histórica Igatu–Andaraí', 'Sai da Igreja de São Sebastião, mas é trilha longa em terreno de pedra.'),
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
                    'Fazenda Pratinha — estrutura no dia das grutas',
                    'Fazenda Santo Antônio — fogão a lenha e redário, ligada à Cachoeira do Mosquito']),
    ('Mucugê', ['Jantar no centro — melhor gastronomia do eixo sul']),
    ('Volta', ['Jacobina — a definir', 'Senhor do Bonfim — alternativa mais tarde']),
]

FONTES_CURADORIA = [
    ('Guia Chapada Diamantina', 'https://www.guiachapadadiamantina.com.br/', 'acessos, horários e taxas dos atrativos'),
    ('Um Viajante', 'https://www.umviajante.com.br/bahia/', 'relatos de Lapa Doce, Pratinha, Buracão, Ribeirão do Meio, Mosquito e Poço do Diabo'),
    ('Conecta Chapada', 'https://conectachapada.com.br/trilha-da-cachoeira-do-buracao/', 'trilha do Buracão e pôr do sol do Pai Inácio'),
    ('Vem Pra Bahia', 'https://vemprabahia.com.br/cemiterio-bizantino-de-mucuge-saiba-a-historia-e-como-visitar/', 'Cemitério Bizantino e Projeto Sempre-Viva'),
    ('Como Viajei', 'https://comoviajeiblog.wordpress.com/2022/10/04/a-gruna-do-brejo-as-ruinas-de-igatu-a-cidade-de-pedra-e-o-mirante-do-cruzeiro/', 'Gruna do Brejo, ruínas de Igatu e Rampa do Caim'),
    ('TripAdvisor — Ferro Doido', 'https://www.tripadvisor.com.br/Attraction_Review-g2347287-d7182501-Reviews-Cachoeira_Ferro_Doido-Morro_Do_Chapeu_State_of_Bahia.html', 'avaliações que apontam a falta de água fora da estação chuvosa'),
    ('YouTube — Trilha da Cachoeira do Buracão', 'https://www.youtube.com/watch?v=lAvhDwxt8F4', 'vídeo da trilha inteira, útil para calibrar o esforço'),
    ('YouTube — Roteiro de 6 dias saindo de Lençóis', 'https://www.youtube.com/watch?v=UgOb0fI3CgE', 'encadeamento de passeios num roteiro de duração parecida'),
    ('YouTube — Morro do Chapéu e o Ferro Doido', 'https://www.youtube.com/watch?v=oEiFHZ_AfHE', 'estado da cachoeira e do mirante'),
]


def card(op):
    emoji, rotulo, cls = SELOS[op['status']]
    r_emoji, r_rotulo, r_cls = REC[op['rec']]
    tipo = 'Principal' if op['tipo'] == 'principal' else 'Leve'
    return (
        f'<article class="opt-card fade-in {cls}" data-rec="{op["rec"]}">'
        f'<div class="opt-top"><span class="opt-rec {r_cls}">{r_emoji} {B.esc(r_rotulo)}</span>'
        f'<span class="opt-tipo">{tipo}</span></div>'
        f'<h3 class="opt-nome">{B.esc(op["nome"])}</h3>'
        f'<p class="opt-onde">{B.esc(op["onde"])} · <span class="opt-selo">{emoji} {B.esc(rotulo)}</span></p>'
        f'<p class="opt-nota">{op["desc"]}</p>'
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
        f'</div>'
    )


todas = [o for d in DIAS for o in d['opcoes']]
total = len(todas)
imperdiveis = sum(1 for o in todas if o['rec'] == 1)
escolhidas = sum(1 for o in todas if o['status'] == 'escolhida')

legenda = ''.join(
    f'<span class="leg-item"><b>{e}</b> {B.esc(r)}</span>' for e, r, _ in REC.values()
)

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

fontes_html = ''.join(
    f'<div class="kv"><span class="k"><a href="{B.esc(u)}" target="_blank" rel="noopener">{B.esc(n)}</a></span>'
    f'<span class="v">{B.esc(o)}</span></div>'
    for n, u, o in FONTES_CURADORIA
)

corpo = (
    B.page_header(
        trip, 'Tudo o que está sobre a mesa',
        'Cardápio de opções',
        f'{total} opções levantadas e avaliadas em 23/08/2026, filtradas por dia e ordenadas '
        f'da mais recomendada para a menos. {imperdiveis} imperdíveis, {escolhidas} já escolhidas pela Michele.',
        PAGE)
    + B.nav_html(trip, PAGES, PAGE)
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Como ler</span>'
      '<h2 class="section-title">Uma âncora por dia, o resto é escolha</h2>'
      '<p class="section-desc">A âncora é o deslocamento que não se move. O resto cabe naquele dia — '
      'geograficamente e no relógio. A regra do ritmo tranquilo é <strong>no máximo uma principal e uma leve por dia</strong>. '
      'A recomendação combina o consenso de blogs, guias e vídeos com o perfil do grupo: esforço de médio a baixo, '
      'ritmo tranquilo e outubro no fim da seca. Nada aqui está reservado.</p>'
      f'<div class="legenda">{legenda}</div>'
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
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Procedência</span>'
      '<h2 class="section-title">De onde vem a curadoria</h2>'
      '<p class="section-desc">Blogs de viagem, guias regionais e vídeos consultados em 23/08/2026. '
      'Onde as fontes divergiram, a nota do card diz o que foi considerado.</p>'
      '</div>'
      f'<div class="info-card fade-in">{fontes_html}</div>'
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
print(f'✅ {PAGE} — {total} opções · {imperdiveis} imperdíveis · {escolhidas} escolhidas')
