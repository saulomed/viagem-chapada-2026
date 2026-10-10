#!/usr/bin/env python3
"""Gera restaurantes.html — a curadoria gastronômica da viagem.

Cada lugar tem a base onde fica, o tipo de cozinha, em que refeições encaixa,
a faixa de preço e uma nota curta. Os filtros se combinam (base + refeição +
cozinha + preço + atalhos + busca por texto), para decidir onde comer na hora,
já estando na cidade.

Fonte: blogs de viagem e guias regionais consultados em 02/10/2026 (Rota 1976,
Melhores Destinos, Guia Chapada Diamantina, CNN Viagem & Gastronomia, Portal
Vale do Capão, Fazenda Pratinha e as listas do TripAdvisor por cidade). Preço e
horário de restaurante mudam: a faixa é orientação, não tabela.

Rode SEMPRE depois do build.py:

    python3 ~/.claude/skills/agente-viagem/scripts/build.py site
    python3 scripts/gera-restaurantes.py
    python3 ~/.claude/skills/agente-viagem/scripts/build.py site   # offline
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.expanduser('~/.claude/skills/agente-viagem/scripts'))
import build as B  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site')
trip = json.load(open(os.path.join(ROOT, 'trip.json'), encoding='utf-8'))

PAGE = 'restaurantes.html'

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
# Eixos dos filtros
# ─────────────────────────────────────────────────────────────────────────────

# base -> (rótulo, emoji, linha de contexto no cabeçalho do bloco)
CIDADES = [
    ('lencois', 'Lençóis', '🏛️',
     'Dias 2 e 6 · o maior polo de comida da viagem, tudo a pé no centro histórico.'),
    ('capao', 'Vale do Capão (Caeté-Açu)', '🥾',
     'Dias 1 e 2 · jantar na noite de chegada e almoço depois da Fumaça, a 3 km da portaria. A vila janta cedo e só aceita espécie.'),
    ('poco-azul', 'Poço Azul / Nova Redenção', '💧',
     'Dia 3 · almoço na chegada, entre a flutuação e a estrada para Mucugê.'),
    ('mucuge', 'Mucugê', '⛏️',
     'Dias 3 e 4 · a melhor gastronomia do eixo sul, dentro do conjunto tombado.'),
    ('ibicoara', 'Ibicoara', '🏞️',
     'Dia 5 · almoço na volta do Buracão e jantar na vila depois do Sítio Canjerana.'),
    ('iraquara', 'Iraquara / Pratinha', '🕳️',
     'Dia 6 · almoço na Fazenda Pratinha ou no caminho das grutas.'),
    ('estrada', 'Estrada · Morro do Chapéu, Jacobina e Senhor do Bonfim', '🚗',
     'Dia 7 (e almoço da ida, no dia 1) · as paradas de estrada.'),
    ('juazeiro', 'Juazeiro / Petrolina', '🏠',
     'Chegada na sexta à noite e o fim de semana em casa.'),
]

# tipo de cozinha -> (rótulo, emoji)
TIPOS = [
    ('regional', 'Regional baiana', '🍲'),
    ('contemporanea', 'Contemporânea / autoral', '✨'),
    ('italiana', 'Italiana / massas', '🍝'),
    ('pizza', 'Pizzaria', '🍕'),
    ('mar', 'Frutos do mar', '🦐'),
    ('carne', 'Carnes / steakhouse', '🥩'),
    ('japonesa', 'Japonesa', '🍣'),
    ('vegetariana', 'Vegetariana / saudável', '🥗'),
    ('cafe', 'Café / padaria / doces', '☕'),
    ('lanche', 'Lanches / hambúrguer', '🍔'),
    ('selfservice', 'Self-service / a quilo', '🍽️'),
    ('caseira', 'Comida caseira', '🏡'),
]

REFEICOES = [
    ('cafe', 'Café da manhã', '☕'),
    ('almoco', 'Almoço', '🌤️'),
    ('jantar', 'Jantar', '🌙'),
    ('petisco', 'Petisco / bar', '🍺'),
]

FAIXAS = {
    1: ('$', 'até ~R$ 40 por pessoa'),
    2: ('$$', '~R$ 40 a 90 por pessoa'),
    3: ('$$$', 'acima de ~R$ 90 por pessoa'),
}

# atalhos: data-<chave>="sim" no card
EXTRAS = [
    ('top', '⭐ Escolha da curadoria'),
    ('no-roteiro', '✅ Já citado no roteiro'),
    ('vegetariano', '🥗 Opções vegetarianas'),
    ('musica', '🎶 Música ao vivo'),
    ('vista', '🌅 Vista ou ao ar livre'),
    ('delivery', '🛵 Delivery'),
]

TIPO_LABEL = dict((k, r) for k, r, _ in TIPOS)
CIDADE_LABEL = dict((k, r) for k, r, _, _ in CIDADES)
REFEICAO_LABEL = dict((k, r) for k, r, _ in REFEICOES)


def R(nome, cidade, tipo, refeicoes, faixa, desc, local=None, dias=None,
      tags=(), insta=None, fonte=None, top=False, no_roteiro=False,
      vegetariano=False, musica=False, vista=False, delivery=False):
    return {
        'nome': nome, 'cidade': cidade, 'tipo': tipo, 'refeicoes': refeicoes,
        'faixa': faixa, 'desc': desc, 'local': local, 'dias': dias,
        'tags': list(tags), 'insta': insta, 'fonte': fonte, 'top': top,
        'no_roteiro': no_roteiro, 'vegetariano': vegetariano, 'musica': musica,
        'vista': vista, 'delivery': delivery,
    }


# ─────────────────────────────────────────────────────────────────────────────
# A curadoria
# ─────────────────────────────────────────────────────────────────────────────
RESTAURANTES = [

    # ── Lençóis ──────────────────────────────────────────────────────────────
    R('Cozinha Aberta Slow Food', 'lencois', 'contemporanea', ['jantar'], 3,
      'Alta gastronomia regional em pátio aberto e arborizado, com a proposta de '
      '"refeição com calma" — o ritmo tranquilo do grupo combina exatamente. Selo '
      'TripAdvisor de Slow Food, produtos regionais e orgânicos e atendimento em '
      'vários idiomas. É o jantar mais autoral de Lençóis.',
      local='Centro histórico', tags=['🌸 Pátio arborizado', 'Reserva recomendada'],
      insta='cozinhaaberta', top=True, no_roteiro=True, vegetariano=True),

    R('Quilombola', 'lencois', 'regional', ['almoco', 'jantar'], 2,
      'Cozinha baiana de raiz servida por gente de comunidades quilombolas: o '
      '<strong>godó de banana verde</strong> (herança do garimpo), o cortado de '
      'palma, a moqueca de camarão com banana da terra e um acarajé muito elogiado. '
      'Tem som ao vivo na calçada e chope artesanal.',
      local='Centro histórico', dias='Todos os dias, 16h30–23h30',
      tags=['🎶 Música ao vivo', 'Prato típico', 'Reserva recomendada'],
      insta='restaurantequilombola', top=True, no_roteiro=True, vegetariano=True),

    R('Lampião Culinária Nordestina', 'lencois', 'regional', ['almoco', 'jantar'], 2,
      'Clássico nordestino de releituras bem-feitas, com o bobó de camarão e o '
      'filé mignon de sol entre as melhores pedidas. Ambiente descontraído no '
      'centro, boa entrada para a cozinha da região na primeira noite.',
      local='Centro histórico', tags=['Cozinha regional', 'Reserva recomendada'],
      top=True, no_roteiro=True),

    R('Garimpo Gourmet', 'lencois', 'mar', ['almoco', 'jantar'], 2,
      'Especialista em frutos do mar com sabor regional e porções generosas: '
      'picanha, moqueca e bobó de camarão, arroz de polvo. Fica na esquina da rua '
      'de acesso ao centrinho, com salão grande — bom para um grupo de quatro.',
      local='Centro histórico', dias='11h–22h, almoço e jantar',
      tags=['Porções generosas'], insta='gourmet_garimpo', no_roteiro=True),

    R('Bistrô do Mato', 'lencois', 'contemporanea', ['jantar'], 2,
      'A casa dos crepes: camarão, filé mignon, carne de sol e palmito de jaca, '
      'além de risotos e escondidinhos. O café é selecionado na Serra e vem com '
      'demonstração de preparo na mesa. Tem terraço reservado, bom para o grupo. '
      'Fecha às terças.',
      local='Centro histórico', dias='16h–23h, fecha terça',
      tags=['☕ Café especial', 'Opções vegetarianas'],
      insta='bistrodomatolencois', no_roteiro=True, vegetariano=True),

    R('Quarar Resto & Café', 'lencois', 'contemporanea', ['almoco', 'jantar'], 2,
      'Casa da primeira barista de Lençóis, que funciona como restaurante e café '
      'ao mesmo tempo. Os campeões são a lasanha e o escondidinho de camarão, e a '
      'sobremesa mais pedida é a "Doce Infância". Fecha às segundas.',
      local='Centro histórico', dias='16h–23h, terça a domingo',
      tags=['☕ Café', 'Opções vegetarianas'], insta='quarar_restoecafe',
      vegetariano=True),

    R('Cozinha Italiana da Marisa', 'lencois', 'italiana', ['jantar'], 2,
      'Massas artesanais e molhos de família, com o fettuccine de camarão como '
      'carro-chefe e pizza de fermentação natural assada na pedra. Dona Marisa '
      'trouxe a receita de Nápoles e mantém mesa na calçada da Rua das Pedras.',
      local='Rua das Pedras', dias='17h–23h, todos os dias',
      tags=['Massa artesanal', 'Pizza na pedra'], insta='cozinhaitalianalencois'),

    R('Cascalho', 'lencois', 'italiana', ['jantar'], 2,
      'Pizzas artesanais de oito fatias, massas, filé à parmegiana e um bacalhau '
      'à moda da casa que virou assinatura. Comandado pessoalmente pela '
      'proprietária. Fecha às terças.',
      local='Centro histórico', dias='16h–23h30, fecha terça',
      tags=['Bacalhau', 'Opções vegetarianas'], insta='cascalhorestaurante',
      vegetariano=True),

    R('Colors', 'lencois', 'contemporanea', ['jantar', 'petisco'], 2,
      'Cozinha mediterrânea com pegada argentina, produtos orgânicos e do sítio '
      'da casa: filé ao Cabernet com fettuccine ao gorgonzola, tapas, ceviche e '
      'saladas. Fica na esquina da Rua da Baderna, o point da noite, com a rua '
      'das sombrinhas coloridas.',
      local='Rua da Baderna', tags=['🌅 Mesas na rua', 'Drinques'],
      insta='colors.restobar', vista=True),

    R('Santo Chico Sushi Bar', 'lencois', 'japonesa', ['jantar'], 2,
      'Sushi no meio da Chapada: sashimi, niguiri, poke, temaki e combinados, com '
      'a dupla de Sofia (camarão empanado com lâmina de salmão maçaricado) entre '
      'os especiais. Boa saída quando o grupo quiser variar da comida baiana.',
      local='Centro histórico', tags=['Sushi', 'Drinques'],
      insta='santochicosushibar'),

    R('Azul Restaurante — Canto das Águas', 'lencois', 'contemporanea', ['almoco', 'jantar'], 3,
      'Restaurante do hotel à beira do rio, com menu que vai da cozinha regional '
      'à internacional e arte em cada detalhe do ambiente. O jantar mais '
      'estruturado da cidade, para uma noite de despedida caprichada.',
      local='Hotel Canto das Águas', tags=['À beira-rio', 'Reserva recomendada'],
      vista=True, top=True),

    R("Roda d'Água — Hotel de Lençóis", 'lencois', 'contemporanea', ['almoco', 'jantar'], 3,
      'Cozinha de estudo sobre costumes e práticas gastronômicas locais, da '
      'entrada à sobremesa, com adega climatizada. Requeinte sem sair do centro '
      'tombado.',
      local='Hotel de Lençóis', tags=['Adega', 'Reserva recomendada']),

    R('Sabor da Serra', 'lencois', 'contemporanea', ['jantar'], 2,
      'Risoto baiano de carne de sol reduzida na cachaça, filé mignon na manteiga '
      'noisette, moquecas e pratos vegetarianos como o fettuccine de cacau ao '
      'shimeji. Sobremesa de sorvete de tapioca com licuri da região.',
      local='Centro histórico', dias='16h–23h, segunda a sábado',
      tags=['Opções vegetarianas', 'Ingredientes da região'],
      insta='sabordaserralencois', vegetariano=True),

    R('A Doce Vida', 'lencois', 'italiana', ['jantar'], 2,
      'Casa acolhedora de 16 anos, com o nhoque nordestino (banana, carne seca e '
      'queijo coalho) como carro-chefe, além de camarão ao curry, filé ao vinho '
      'e massas. Mesas ao ar livre em frente ao salão.',
      local='Centro histórico', tags=['Massa artesanal'], insta='adocevidarestaurante',
      vista=True),

    R('Restaurante da Bete', 'lencois', 'caseira', ['jantar'], 1,
      'Comida caseira farta na Rua da Baderna, do tipo que repõe a energia depois '
      'da trilha: carne de sol com fritas e feijão tropeiro, moqueca de peixe, '
      'massas e crepes. Preço justo e porções individuais ou para dois.',
      local='Rua da Baderna', dias='17h–23h, todos os dias',
      tags=['Preço justo'], insta='restaurantedabete8'),

    R('Aquarela Culinária Gourmet', 'lencois', 'selfservice', ['almoco', 'jantar'], 1,
      'Self-service e à la carte o dia todo, com risotos, filé com massa e molho '
      'gorgonzola e o risoto de camarão com brie entre os campeões. Churrasco de '
      'sexta a domingo e música ao vivo nas sextas.',
      local='Centro histórico', tags=['🎶 Música ao vivo', 'Vegetariano'],
      insta='aquarelaculinariagourmet', musica=True, vegetariano=True),

    R('O Bode', 'lencois', 'selfservice', ['almoco'], 1,
      'Self-service caprichado de comida regional, a opção prática para o almoço '
      'entre um passeio e outro, sem abrir mão do tempero baiano.',
      local='Centro histórico', tags=['Self-service', 'Almoço rápido']),

    R('Café do Mato', 'lencois', 'cafe', ['cafe', 'petisco'], 1,
      'Crepe de borda de parmesão torradinho e café 100% arábica torrado na '
      'região, coado na hora. Bom para o café da manhã reforçado ou uma pausa à '
      'tarde no centro.',
      local='Centro histórico', tags=['☕ Café da região', 'Crepes']),

    R('Bavarois', 'lencois', 'lanche', ['petisco'], 1,
      'Hambúrgueres, confeitaria e sorvetes artesanais. Resolve o lanche da tarde '
      'ou a sobremesa depois do jantar.',
      local='Centro histórico', tags=['Sobremesa']),

    R('Do Vale Delivery', 'lencois', 'italiana', ['jantar'], 2,
      'Pizzas, lasanhas, rondelli e massas artesanais entregues na pousada, das '
      '18h à meia-noite. A saída para a noite em que ninguém quer sair depois de '
      'um dia de trilha.',
      local='Entrega na pousada', dias='18h–0h, quarta a segunda',
      tags=['Delivery'], insta='dovaledelivery', delivery=True),

    # ── Vale do Capão ────────────────────────────────────────────────────────
    R('Pizzaria Capão Grande', 'capao', 'pizza', ['almoco', 'jantar'], 2,
      'A pizza integral de forno a lenha que virou lenda no Capão, com apenas '
      'dois sabores: cenoura com queijo e banana com mel e queijo. Dá para pedir '
      'metade de cada e ver a pizza sair do forno direto para a mesa. Ótima '
      'depois de um dia de trilha.',
      local='Vila do Capão', tags=['Forno a lenha', 'Vegetariano'], top=True,
      vegetariano=True),

    R('Bistrô Orquídea Negra', 'capao', 'contemporanea', ['jantar'], 3,
      'Cozinha criativa da chef Jakie Lessa, misturando Itália, França, Brasil, '
      'Espanha e África, com carta de vinhos. O jantar mais elaborado do vale, '
      'para quem quiser comemorar o dia da Fumaça.',
      local='Vila do Capão', tags=['Carta de vinhos', 'Reserva recomendada'],
      top=True),

    R('Ôxe! Restô', 'capao', 'regional', ['almoco', 'jantar'], 2,
      'O sabor do nordeste no Capão, em pratos generosos que agradam quem acabou '
      'de subir a Fumaça e quer comida de verdade.',
      local='Vila do Capão', tags=['Cozinha nordestina']),

    R('Gatto Sete Bistrô', 'capao', 'contemporanea', ['jantar'], 2,
      'Bistrô concorrido da vila, com pratos bem executados e ambiente '
      'aconchegante. Entra bem como jantar leve antes da volta para Lençóis.',
      local='Vila do Capão', tags=['Bistrô'], top=True),

    R('Charrúa Restaurante', 'capao', 'carne', ['almoco', 'jantar'], 2,
      'Parrilla uruguaia no meio da Chapada, a mais bem avaliada do vale. Para '
      'quem quiser um corte no almoço do dia da Fumaça.',
      local='Vila do Capão', tags=['Parrilla']),

    R('Herbívoras Bistrô', 'capao', 'vegetariana', ['almoco', 'jantar'], 2,
      'Cozinha vegetariana e vegana criativa, uma das razões de o Capão ser '
      'conhecido pela comida saudável. Resolve o almoço de quem não come carne.',
      local='Vila do Capão', tags=['Vegetariano', 'Vegano'],
      vegetariano=True),

    R('Natural Bistrô', 'capao', 'vegetariana', ['almoco'], 2,
      'Refeições leves e naturais, com ingredientes frescos da região. Alternativa '
      'tranquila na vila, a poucos minutos da portaria da Fumaça.',
      local='Vila do Capão', tags=['Saudável', 'Vegetariano'],
      vegetariano=True),

    R('Comida Caseira da Dona Beli', 'capao', 'caseira', ['almoco'], 1,
      'Comida caseira de fogão simples, no esquema que fez a fama do Capão: '
      'prato do dia barato e bem servido.',
      local='Vila do Capão', tags=['Preço justo'], vegetariano=True),

    R('Pastel de palmito de jaca', 'capao', 'lanche', ['petisco'], 1,
      'O quitute-símbolo do Capão, vendido nas lanchonetes aos pés da trilha da '
      'Fumaça. Melhor deixar para a volta, quando bate o cansaço — também tem '
      'queijo, carne e açaí.',
      local='Início da trilha da Fumaça', tags=['Típico da região'],
      vegetariano=True),

    R('Terroá Cafés Especiais', 'capao', 'cafe', ['cafe', 'petisco'], 1,
      'Cafés especiais da região para começar o dia antes da trilha ou fechar a '
      'tarde na vila.',
      local='Vila do Capão', tags=['☕ Café especial']),

    # ── Poço Azul / Nova Redenção ────────────────────────────────────────────
    R('APA Restaurante & Cia', 'poco-azul', 'caseira', ['almoco', 'jantar'], 1,
      'A 200 metros do Poço Azul, é o almoço natural do dia da flutuação. Comida '
      'caseira da região — palma, godó e mamão verde — feita por gente de Nova '
      'Redenção. Funciona de sábado à noite até sexta às 17h.',
      local='A 200 m do Poço Azul', dias='Sáb a sex; fecha sexta às 17h',
      tags=['Ao lado do Poço Azul', 'Preço justo'],
      insta='restaurante_apa_reserva', no_roteiro=True, top=True,
      vegetariano=True),

    # ── Mucugê ───────────────────────────────────────────────────────────────
    R('Paraguassu', 'mucuge', 'contemporanea', ['almoco', 'jantar'], 3,
      'O jantar mais elaborado do eixo sul, do chef André Chequer, dentro do '
      'hotel Refúgio na Serra e da área tombada. Cozinha contemporânea com '
      'toque regional, adega convidativa e carta de drinques. Almoço das 12h às '
      '15h e jantar das 19h às 23h; o <strong>menu degustação é tradicional aos '
      'sábados</strong> — e o grupo não passa sábado em Mucugê.',
      local='Rua Caetité, 40B — centro histórico', dias='12h–15h e 19h–23h, todos os dias',
      tags=['Reserva recomendada', 'Menu degustação sábado'],
      insta='restaurante_paraguassu', top=True, no_roteiro=True),

    R('Beco da Bateia', 'mucuge', 'pizza', ['jantar', 'petisco'], 2,
      'Um beco cultural no centro tombado que reúne a <strong>Pizza da Garagem</strong>, '
      'famosa pela pizza e pelas massas, e o Matuto, conhecido pelos coquetéis e '
      'petiscos. Ambiente muito bem decorado, com playlist de pop e rock. Aberto '
      'das 18h30 às 22h.',
      local='Centro histórico', dias='18h30–22h',
      tags=['Pizza', 'Coquetéis', 'Clima cultural'],
      insta='becodabateia', top=True),

    R('Restaurante e Pizzaria Point da Chapada', 'mucuge', 'pizza', ['almoco', 'jantar'], 2,
      'O restaurante mais avaliado de Mucugê: pizzas de forno a lenha, o famoso '
      'filé à parmegiana e refeições completas. Resolve almoço e jantar no mesmo '
      'lugar, no centro.',
      local='Centro da cidade', tags=['Pizza', 'Parmegiana']),

    R('Pizzaria d\'Enrico', 'mucuge', 'pizza', ['jantar'], 2,
      'Pizzaria entre as mais bem avaliadas da cidade, uma alternativa simples '
      'para a noite depois de um dia de cachoeira.',
      local='Centro da cidade', tags=['Pizza']),

    R('Restaurante Sabor da Picanha', 'mucuge', 'carne', ['almoco', 'jantar'], 2,
      'Indicação do próprio chef André Chequer entre os lugares de Mucugê. '
      'Carnes na brasa para quem quiser um jantar mais substancioso.',
      local='Centro da cidade', tags=['Carne na brasa']),

    R('Mizu Mucugê Sushi Bar', 'mucuge', 'japonesa', ['jantar'], 2,
      'Sushi no meio do garimpo, também na lista do chef André Chequer. Boa '
      'válvula de escape quando a comida baiana pesar dois dias seguidos.',
      local='Centro da cidade', tags=['Sushi']),

    R('Bia Maria Café', 'mucuge', 'cafe', ['cafe', 'almoco'], 1,
      'Café e comida leve, citado pelos chefs locais. Começa o dia da visita ao '
      'Parque Municipal sem pressa.',
      local='Centro da cidade', tags=['☕ Café'], vegetariano=True),

    R('Comida Caseira da Dona Nena', 'mucuge', 'caseira', ['almoco'], 1,
      'A comida é servida no próprio fogão a lenha da Dona Nena, com mesas na '
      'cozinha e no quintal. Simples, limpinho e o almoço mais afetivo da cidade.',
      local='Centro da cidade', tags=['Fogão a lenha', 'Preço justo'],
      top=True, vegetariano=True),

    R('Sertãozinho', 'mucuge', 'lanche', ['jantar', 'petisco'], 1,
      'Hambúrgueres artesanais para recarregar depois do Parque Municipal, numa '
      'noite sem cerimônia.',
      local='Centro da cidade', tags=['Hambúrguer artesanal']),

    R('Capim Rosa Chá', 'mucuge', 'italiana', ['jantar'], 2,
      'A pizza de chapati — massa mais leve — para quem quer algo menos pesado à '
      'noite. Fica na hospedagem de mesmo nome.',
      local='Centro da cidade', tags=['Massa leve', 'Vegetariano'],
      vegetariano=True),

    R('Bistrô Café.Com', 'mucuge', 'contemporanea', ['jantar'], 2,
      'Ambiente tranquilo e romântico para a noite, com cozinha de bistrô no '
      'centro histórico.',
      local='Centro histórico', tags=['Clima tranquilo'], vista=True),

    # ── Ibicoara ─────────────────────────────────────────────────────────────
    R('Espaço Gourmet Fazenda Produtiva', 'ibicoara', 'contemporanea', ['almoco', 'jantar'], 3,
      'A melhor avaliação de Ibicoara: culinária tratada como arte, com '
      'ingredientes de qualidade, entradas servidas com flores comestíveis e '
      'molhos da casa. <strong>Exige reserva</strong> — é o jantar especial da '
      'noite na vila.',
      local='Zona rural de Ibicoara', tags=['Reserva obrigatória', 'Experiência autoral'],
      insta='fazendaprodutiva', top=True),

    R('Restaurante Mandioca — Sítio Monte Alegre', 'ibicoara', 'caseira', ['almoco'], 2,
      'Cozinha caseira do sítio, entre as mais bem avaliadas da cidade. Prato '
      'farto e ingredientes da roça, boa parada na volta do Buracão.',
      local='Sítio Monte Alegre', tags=['Comida da roça', 'Opções vegetarianas'],
      vegetariano=True, top=True),

    R('Restaurante Quintal Licuri', 'ibicoara', 'regional', ['almoco', 'jantar', 'cafe'], 1,
      'Na estrada das cachoeiras do Buracão, Licuri e Fumacinha, a partir de '
      'R$ 35 por pessoa. Carne de sol na manteiga e frango perfumado entre os '
      'pratos, além de café da manhã e lanche para trilha. Almoço forte nos '
      'fins de semana.',
      local='Campo Redondo, estrada das cachoeiras',
      tags=['Preço justo', 'Lanche para trilha'],
      insta='quintal_licuri', vegetariano=True),

    R('Point dos Amigos', 'ibicoara', 'caseira', ['almoco', 'jantar'], 1,
      'Ponto concorrido da cidade, com comida bem avaliada e preço amigável. '
      'Boa alternativa central quando a Fazenda Produtiva estiver cheia.',
      local='Centro de Ibicoara', tags=['Preço justo']),

    R('Restaurante Raízes', 'ibicoara', 'regional', ['almoco', 'jantar'], 1,
      'Aberto das 8h às 22h (domingo até o meio-dia), é o tipo de lugar que '
      'resolve café, almoço e jantar sem deslocamento. Comida regional do dia a '
      'dia.',
      local='Centro de Ibicoara', dias='8h–22h',
      tags=['Abre cedo'], vegetariano=True),

    R("Trilheiru's Restaurante e Pizzaria", 'ibicoara', 'pizza', ['jantar', 'petisco'], 1,
      'Pizzas, drinks e petiscos à noite, o point descontraído da vila depois do '
      'Sítio Canjerana.',
      local='Centro de Ibicoara', tags=['Pizza', 'Drinks', 'Petiscos']),

    R('Restaurante & Gastrobar Mudra', 'ibicoara', 'contemporanea', ['jantar'], 2,
      'Gastrobar com pratos mais elaborados e drinks, uma das novidades da '
      'gastronomia de Ibicoara.',
      local='Centro de Ibicoara', tags=['Drinks', 'Clima jovem']),

    R('Cheiro Verde Restaurante e Pizzaria', 'ibicoara', 'pizza', ['almoco', 'jantar'], 1,
      'Restaurante e pizzaria de bairro, opção simples para o jantar na vila sem '
      'reserva.',
      local='Centro de Ibicoara', tags=['Pizza', 'Preço justo']),

    R('Restaurante Vitão', 'ibicoara', 'regional', ['almoco', 'jantar'], 1,
      'Uma das casas mais recentes do centro, com comida regional e ambiente '
      'novo.',
      local='Centro de Ibicoara', tags=['Comida regional']),

    # ── Iraquara / Pratinha ──────────────────────────────────────────────────
    R('Restaurante Gruta Azul — Fazenda Pratinha', 'iraquara', 'caseira', ['almoco'], 2,
      'Dentro da Fazenda Pratinha, no caminho da Gruta Azul: pratos à la carte e '
      'porções, com a galinha caipira como destaque e opções vegetarianas. É o '
      'almoço que encaixa na tarde da Pratinha sem precisar sair da fazenda.',
      local='Fazenda Pratinha', tags=['Na fazenda', 'Galinha caipira', 'Vegetariano'],
      insta='restaurantegrutazul', no_roteiro=True, top=True, vegetariano=True),

    R('Restaurante João de Barro — Fazenda Pratinha', 'iraquara', 'caseira', ['almoco'], 2,
      'Segunda opção dentro da Fazenda Pratinha, no interior da propriedade. '
      'Resolve o almoço do dia das grutas sem deslocamento.',
      local='Fazenda Pratinha', tags=['Na fazenda'],
      insta='restaurantegrutazul', no_roteiro=True),

    R('Restaurante da Lapa Doce', 'iraquara', 'selfservice', ['almoco'], 1,
      'No complexo da Gruta da Lapa Doce, funciona no esquema de buffet — prático '
      'e barato para quem emendar a gruta com a Pratinha. Só faz sentido se a '
      'Lapa Doce entrar no dia 22.',
      local='Complexo da Lapa Doce', tags=['Buffet', 'Só se a Lapa Doce entrar'],
      vegetariano=True),

    R('Restaurante Paulistano', 'iraquara', 'regional', ['almoco', 'jantar'], 1,
      'Entre os mais bem avaliados de Iraquara, boa parada de estrada se a fome '
      'chegar antes ou depois das grutas.',
      local='Centro de Iraquara', tags=['Comida regional', 'Na estrada']),

    # ── Estrada ──────────────────────────────────────────────────────────────
    R('Eusépio Pizzaria e Restaurante', 'estrada', 'italiana', ['almoco', 'jantar'], 2,
      'Um cantinho da Itália em Morro do Chapéu desde 1962, fundado por Eusébio '
      'Garofani, da região de Perugia. Pizza e massa com história — o almoço ou '
      'jantar da parada na cidade na volta.',
      local='Morro do Chapéu', tags=['Desde 1962', 'Cozinha italiana'],
      top=True),

    R('Casarão', 'estrada', 'regional', ['almoco', 'jantar'], 2,
      'Comida da Bahia com identidade e sabor afetivo, um dos poucos restaurantes '
      'da Chapada em que os relatos destacam a cozinha local de raiz.',
      local='Morro do Chapéu', tags=['Cozinha baiana']),

    R('Restaurante Colonial', 'estrada', 'regional', ['almoco', 'jantar'], 2,
      'Cozinha representativa da Chapada Diamantina, montada para lembrar a '
      'infância e os sabores da região.',
      local='Morro do Chapéu', tags=['Cozinha afetiva'], vegetariano=True),

    R('Varanda Bistrô', 'estrada', 'pizza', ['jantar'], 2,
      'Pizza no forno a lenha, aberta de terça a domingo a partir das 18h. Boa '
      'para a noite em Morro do Chapéu.',
      local='Morro do Chapéu', dias='Ter a dom, a partir das 18h',
      tags=['Forno a lenha'], insta='varandabistromdc'),

    R('Rancho Catarinense', 'estrada', 'selfservice', ['almoco'], 1,
      'Buffet a quilo e à la carte, um dos almoços mais bem avaliados de '
      'Jacobina. É o encaixe natural de horário na metade do caminho de volta — '
      'cerca de 4h30 depois da saída de Lençóis.',
      local='Jacobina', tags=['Buffet a quilo', 'Metade do caminho'],
      no_roteiro=True, top=True, vegetariano=True),

    R('Deck Steakhouse', 'estrada', 'carne', ['almoco', 'jantar'], 2,
      'Steakhouse muito bem avaliada em Jacobina, para um almoço mais reforçado '
      'na estrada.',
      local='Jacobina', tags=['Carnes']),

    R('Casa do Mar', 'estrada', 'mar', ['almoco', 'jantar'], 2,
      'Frutos do mar com boa avaliação em Jacobina, surpresa agradável na rota '
      'de volta.',
      local='Jacobina', tags=['Frutos do mar']),

    R('Cucina Artezanalle', 'estrada', 'italiana', ['almoco', 'jantar'], 2,
      'Cozinha italiana artesanal em Jacobina, alternativa à buffet na parada do '
      'almoço.',
      local='Jacobina', tags=['Massa artesanal']),

    R('O Cuscuz', 'estrada', 'regional', ['cafe', 'almoco'], 1,
      'Cuscuz e café sertanejo, parada leve na saída de Juazeiro ou na volta. '
      'Senhor do Bonfim, cerca de 1h depois de Jacobina, tem estrutura parecida '
      'para quem preferir esticar.',
      local='Jacobina / Senhor do Bonfim', tags=['Café sertanejo', 'Preço justo'],
      vegetariano=True),

    # ── Juazeiro / Petrolina ────────────────────────────────────────────────
    R('777 Sushi Bistrô', 'juazeiro', 'japonesa', ['jantar'], 2,
      'Sushi em Juazeiro para o jantar da chegada, na sexta à noite — o roteiro '
      'já prevê sushi no primeiro dia em casa.',
      local='Juazeiro', tags=['Jantar da chegada'], top=True),

    R('Restaurante Macaxeira', 'juazeiro', 'selfservice', ['almoco'], 1,
      'Self-service por quilo com comida regional, opção prática do dia a dia em '
      'Juazeiro.',
      local='Juazeiro', tags=['Self-service', 'Regional'],
      vegetariano=True),

    R('Cantinho da Dani', 'juazeiro', 'cafe', ['cafe'], 1,
      'Café da manhã servido das 7h às 15h, na Rua Argentina. Bom para a manhã '
      'antes de pegar a estrada de volta à Chapada.',
      local='Juazeiro', dias='7h–15h', tags=['☕ Café da manhã'], vegetariano=True),

    R('Flor de Mandacaru', 'juazeiro', 'regional', ['almoco', 'jantar'], 2,
      'Culinária típica do Vale do São Francisco, há quase 10 anos entre as '
      'primeiras da lista de quem vive ou visita Petrolina.',
      local='Petrolina', tags=['Cozinha típica'], vegetariano=True),

    R('Bar do Gaúcho', 'juazeiro', 'carne', ['jantar'], 2,
      'Carnes e churrasco muito bem avaliados em Petrolina, para uma noite do fim '
      'de semana em casa.',
      local='Petrolina', tags=['Churrasco']),

    R('Nossa Casa', 'juazeiro', 'contemporanea', ['almoco', 'jantar'], 2,
      'Restaurante de pratos variados em Juazeiro, opção para o almoço ou jantar '
      'do fim de semana.',
      local='Juazeiro', tags=['Pratos variados'], vegetariano=True),
]

# ─────────────────────────────────────────────────────────────────────────────
# Fontes
# ─────────────────────────────────────────────────────────────────────────────

FONTES = [
    ('Rota 1976 — Tour gastrô: onde comer bem em Lençóis',
     'https://rota1976.com/tour-gastro-onde-comer-bem-em-lencois-na-chapada-diamantina-ba/',
     'casa por casa em Lençóis: pratos, horários e faixa de preço'),
    ('Melhores Destinos — Onde comer na Chapada Diamantina',
     'https://guia.melhoresdestinos.com.br/onde-comer-na-chapada-diamantina-221-2879-p.html',
     'panorama de Lençóis, Capão, Mucugê e dos restaurantes dentro dos atrativos'),
    ('Guia Chapada Diamantina — 8 restaurantes elegantes',
     'https://www.guiachapadadiamantina.com.br/10-restaurantes-elegantes-chapada-diamantina-2/',
     'Cozinha Aberta, Orquídea Negra, Paraguassu e Roda d’Água'),
    ('CNN Viagem & Gastronomia — Onde os chefs comem: André Chequer',
     'https://www.cnnbrasil.com.br/viagemegastronomia/gastronomia/onde-os-chefs-comem-com-andre-chequer-na-chapada-diamantina/',
     'as indicações do chef do Paraguassu para Mucugê'),
    ('Portal Vale do Capão — Bares e restaurantes',
     'https://portalvaledocapao.com.br/guia-comercial/bares-restaurantes/',
     'guia comercial da vila, com os tipos de cozinha'),
    ('Fazenda Pratinha — Restaurantes',
     'https://www.fazendapratinha.com.br/restaurantes/',
     'Restaurante Gruta Azul e João de Barro, dentro da fazenda'),
    ('TripAdvisor — listas por cidade',
     'https://www.tripadvisor.com.br/Restaurants-g635725-Lencois_State_of_Bahia.html',
     'ranking e avaliações de Lençóis, Mucugê, Ibicoara, Capão, Morro do Chapéu e Jacobina'),
    ('Instagram dos estabelecimentos', None,
     'cardápio, horário e disponibilidade do dia — cada card tem o perfil quando existe'),
]


def cidade_info(cid):
    return next(c for c in CIDADES if c[0] == cid)


def tipo_label(t):
    return TIPO_LABEL.get(t, t)


def refeicao_labels(refeicoes):
    return ' · '.join(REFEICAO_LABEL[r] for r in refeicoes if r in REFEICAO_LABEL)


def faixa_simbolo(n):
    return FAIXAS[n][0]


def data_busca(r):
    partes = [r['nome'], r.get('local') or '', cidade_info(r['cidade'])[1],
              tipo_label(r['tipo']), refeicao_labels(r['refeicoes']),
              ' '.join(r['tags']), re.sub(r'<[^>]+>', ' ', r['desc'])]
    return B.esc(' '.join(partes).lower())


def links_html(r):
    itens = []
    if r.get('insta'):
        itens.append(f'<a class="opt-link insta" href="https://www.instagram.com/{B.esc(r["insta"])}/" '
                     f'target="_blank" rel="noopener" title="@{B.esc(r["insta"])}">📷 @{B.esc(r["insta"])}</a>')
    if r.get('fonte'):
        rotulo, url = r['fonte']
        itens.append(f'<a class="opt-link" href="{B.esc(url)}" target="_blank" rel="noopener">{B.esc(rotulo)}</a>')
    if not itens:
        return ''
    return '<div class="opt-links">' + ''.join(itens) + '</div>'


def card(r):
    _, cidade_emoji, _, _ = cidade_info(r['cidade'])
    tipo_emoji = dict((k, e) for k, _, e in TIPOS).get(r['tipo'], '🍽️')
    faixa, faixa_desc = FAIXAS[r['faixa']]
    refeicoes = refeicao_labels(r['refeicoes'])

    extras = {
        'top': r['top'], 'no-roteiro': r['no_roteiro'], 'vegetariano': r['vegetariano'],
        'musica': r['musica'], 'vista': r['vista'], 'delivery': r['delivery'],
    }
    attrs = ''.join(f' data-{k}="{"sim" if v else "nao"}"' for k, v in extras.items())

    tags = ''
    if r['tags']:
        tags = '<div class="rest-tags">' + ''.join(
            f'<span class="rest-tag">{B.esc(t)}</span>' for t in r['tags']) + '</div>'

    local = f'<span class="rest-local">{B.esc(r["local"])}</span>' if r.get('local') else ''
    dias = f'<div class="rest-dias">🕒 {B.esc(r["dias"])}</div>' if r.get('dias') else ''

    return (
        f'<article class="opt-card rest-card fade-in"'
        f' data-cidade="{r["cidade"]}" data-cozinha="{r["tipo"]}" data-faixa="{r["faixa"]}"'
        f' data-refeicoes="{" ".join(r["refeicoes"])}" data-busca="{data_busca(r)}"{attrs}>'
        f'<div class="opt-corpo">'
        f'<div class="opt-top"><span class="rest-faixa" title="{B.esc(faixa_desc)}">{faixa}</span>'
        f'<span class="opt-tipo">{tipo_emoji} {B.esc(tipo_label(r["tipo"]))}</span></div>'
        f'<h3 class="opt-nome">{B.esc(r["nome"])}</h3>'
        f'<p class="opt-onde">{cidade_emoji} {B.esc(cidade_info(r["cidade"])[1])}'
        + (f' · {local}' if local else '') + f'</p>'
        f'<p class="rest-refeicoes">🍴 {B.esc(refeicoes)}</p>'
        f'<p class="opt-nota">{r["desc"]}</p>'
        f'{dias}{tags}{links_html(r)}'
        f'</div></article>'
    )


def bloco(c):
    cid, rotulo, emoji, ancora = c
    cards = [r for r in RESTAURANTES if r['cidade'] == cid]
    if not cards:
        return ''
    cards_html = ''.join(card(r) for r in cards)
    return (
        f'<div class="rest-bloco dia-bloco" data-cidade="{cid}">'
        f'<div class="rest-cab dia-cab"><h2 class="dia-tit"><span class="dia-chip">{emoji} {B.esc(rotulo)}</span>'
        f'<span class="rest-conta-bloco">{len(cards)} lugares</span></h2>'
        f'<p class="dia-ancora">{B.esc(ancora)}</p></div>'
        f'<div class="opt-grid rest-grid">{cards_html}</div>'
        f'<p class="dia-vazio">Nenhum restaurante desta base passa no filtro atual.</p>'
        f'</div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Barra de filtros
# ─────────────────────────────────────────────────────────────────────────────

def contar(pred):
    return sum(1 for r in RESTAURANTES if pred(r))


filtros_cidade = ''.join(
    f'<button class="filtro-btn" data-eixo="cidade" data-valor="{cid}">'
    f'{emoji} {B.esc(rotulo.split(" · ")[0])} '
    f'<span class="filtro-n">{contar(lambda r, c=cid: r["cidade"] == c)}</span></button>'
    for cid, rotulo, emoji, _ in CIDADES)

filtros_refeicao = ''.join(
    f'<button class="filtro-btn" data-eixo="refeicao" data-valor="{k}">'
    f'{emoji} {B.esc(rot)} '
    f'<span class="filtro-n">{contar(lambda r, k=k: k in r["refeicoes"])}</span></button>'
    for k, rot, emoji in REFEICOES)

filtros_cozinha = ''.join(
    f'<button class="filtro-btn" data-eixo="cozinha" data-valor="{k}">'
    f'{emoji} {B.esc(rot)} '
    f'<span class="filtro-n">{contar(lambda r, k=k: r["tipo"] == k)}</span></button>'
    for k, rot, emoji in TIPOS)

filtros_faixa = ''.join(
    f'<button class="filtro-btn" data-eixo="faixa" data-valor="{n}" title="{B.esc(desc)}">'
    f'{simbolo} '
    f'<span class="filtro-n">{contar(lambda r, n=n: r["faixa"] == n)}</span></button>'
    for n, (simbolo, desc) in FAIXAS.items())

filtros_extra = ''.join(
    f'<button class="filtro-btn" data-eixo="extra" data-valor="{k}">{B.esc(rot)} '
    f'<span class="filtro-n">{contar(lambda r, k=k: r[k.replace("-", "_")])}</span></button>'
    for k, rot in EXTRAS)

barra_filtros = (
    '<div class="filtro-busca">'
    '<label class="filtro-busca-rot" for="rest-busca">🔎 Buscar</label>'
    '<input id="rest-busca" type="search" autocomplete="off" '
    'placeholder="nome, prato, bairro ou tipo de cozinha…">'
    '</div>'
    '<div class="filtro-grupo"><span class="filtro-rot">Base</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-eixo="cidade" data-valor="todas">Todas</button>'
    f'{filtros_cidade}</div></div>'
    '<div class="filtro-grupo"><span class="filtro-rot">Refeição</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-eixo="refeicao" data-valor="todas">Todas</button>'
    f'{filtros_refeicao}</div></div>'
    '<div class="filtro-grupo"><span class="filtro-rot">Cozinha</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-eixo="cozinha" data-valor="todas">Todas</button>'
    f'{filtros_cozinha}</div></div>'
    '<div class="filtro-grupo"><span class="filtro-rot">Preço</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-eixo="faixa" data-valor="todas">Todos</button>'
    f'{filtros_faixa}</div></div>'
    '<div class="filtro-grupo"><span class="filtro-rot">Atalhos</span>'
    '<div class="filtros"><button class="filtro-btn ativo" data-eixo="extra" data-valor="todos">Tudo</button>'
    f'{filtros_extra}</div></div>'
    '<p class="filtro-saida"><span id="rest-conta"></span>'
    '<button class="filtro-limpa" type="button">limpar filtros</button></p>'
)

fontes_html = ''.join(
    f'<div class="kv"><span class="k">'
    + (f'<a href="{B.esc(url)}" target="_blank" rel="noopener">{B.esc(nome)} ↗</a>' if url else B.esc(nome))
    + f'</span><span class="v">{B.esc(nota)}</span></div>'
    for nome, url, nota in FONTES)

total = len(RESTAURANTES)
n_cidades = len(set(r['cidade'] for r in RESTAURANTES))

corpo = (
    B.page_header(
        trip, 'Onde comer na estrada',
        'Restaurantes',
        f'{total} lugares em {n_cidades} bases, com filtros para escolher na hora. '
        'A curadoria junta blogs de viagem, guias regionais e as listas de avaliação de '
        '02/10/2026. Faixa de preço e horário mudam: confirme antes de contar com eles.',
        PAGE)
    + B.nav_html(trip, PAGES, PAGE)
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Como usar</span>'
      '<h2 class="section-title">Escolher o jantar estando já na cidade</h2>'
      '<p class="section-desc">Os filtros se combinam: dá para pedir, por exemplo, '
      '<em>só os regionais de Mucugê que servem jantar</em>, ou <em>um almoço barato '
      'no Vale do Capão</em>. A busca por texto procura no nome, no prato, no bairro e no '
      'tipo de cozinha. As bases seguem a ordem do roteiro, para bater com o dia em que '
      'vocês estão lá.</p>'
      '<p class="section-desc">Cada card traz onde fica, em que refeições encaixa, a '
      'faixa de preço e os atalhos de quem tem opção vegetariana, música ao vivo, vista, '
      'delivery ou já está citado no roteiro. O <strong>⭐</strong> marca a escolha da '
      'curadoria dentro da base — não é obrigação, é por onde começar a decidir.</p>'
      '<div class="legenda rest-legenda">'
      + ''.join(f'<span class="leg-item"><b>{simbolo}</b> {B.esc(desc)}</span>'
                for simbolo, desc in FAIXAS.values())
      + '</div>'
      '</div>'
      f'<div class="filtro-barra rest-filtro-barra">{barra_filtros}</div>'
    + ''.join(bloco(c) for c in CIDADES)
    + '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Prático</span>'
      '<h2 class="section-title">Três coisas que valem saber</h2>'
      '</div>'
      '<div class="info-grid">'
      '<div class="info-card fade-in"><h3>⏰ Horário de restaurante escorrega</h3>'
      '<ul class="rest-lista">'
      '<li>Várias casas só abrem para o jantar, a partir das 16h30–18h, e algumas só '
      'fecham bem tarde. O 💡 está no card quando encontramos o horário publicado.</li>'
      '<li>Segunda e terça são as folgas mais comuns na Chapada. Lençóis tem poucas '
      'fechadas nesses dias; nas cidades menores, vale confirmar antes de sair.</li>'
      '<li>O jantar de domingo 18 em Lençóis é o mais apertado: o carro sai às 6h15 '
      'para a Fumaça, então jantem cedo e perto da pousada.</li>'
      '</ul></div>'
      '<div class="info-card fade-in"><h3>💳 Dinheiro e reserva</h3>'
      '<ul class="rest-lista">'
      '<li>Os restaurantes mais concorridos (Cozinha Aberta, Paraguassu, Espaço Gourmet '
      'Fazenda Produtiva) pedem reserva — vale ligar ou chamar no Instagram na véspera.</li>'
      '<li>Em vilas pequenas, como o Capão e Ibicoara, alguns estabelecimentos só '
      'aceitam dinheiro. Reforce o caixa antes de subir a serra.</li>'
      '<li>O almoço dentro dos atrativos (Poço Azul, Pratinha, Lapa Doce) resolve o '
      'dia sem deslocamento — está listado nas bases de cada trecho.</li>'
      '</ul></div>'
      '<div class="info-card fade-in"><h3>🍽️ Para todos os gostos</h3>'
      '<ul class="rest-lista">'
      '<li>Quem não come carne tem opção fácil em quase toda base — os cards marcados '
      'com 🥗 reúnem as casas com pratos vegetarianos confirmados.</li>'
      '<li>Palmito de jaca, godó de banana verde e cortado de palma são quitutes da '
      'região que quase não se acham fora daqui. Vale provar ao menos uma vez.</li>'
      '<li>O eixo sul fecha cedo; Lençóis e o Capão são os lugares de esticar a noite '
      'com música ao vivo.</li>'
      '</ul></div>'
      '</div>'
      '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Procedência</span>'
      '<h2 class="section-title">De onde vem a curadoria</h2>'
      '<p class="section-desc">Blogs de viagem, guias regionais e listas de avaliação '
      'consultados em 02/10/2026. Onde as fontes divergiram, prevaleceu o que tinha '
      'fonte mais recente ou mais de um relato concordando.</p>'
      '</div>'
      f'<div class="info-card fade-in">{fontes_html}</div>'
      '</section>'
    + '<section class="section">'
      '<div class="section-header fade-in">'
      '<span class="section-tag">Fotos</span>'
      '<h2 class="section-title">Crédito do cabeçalho</h2>'
      '<p class="section-desc">A foto do topo é do centro histórico de Lençóis, do '
      'Wikimedia Commons, já baixada no projeto.</p>'
      '</div>'
      '<div class="info-card fade-in"><div class="kv">'
      '<span class="k">Centro histórico de Lençóis — Rua das Pedras</span>'
      '<span class="v">Diego Carrion Serrano · '
      '<a href="https://commons.wikimedia.org/wiki/File:Luar_sobre_a_cidade_de_Len%C3%A7ois.JPG" '
      'target="_blank" rel="noopener">CC BY-SA 3.0</a></span>'
      '</div></div>'
      '</section>'
    + B.footer_html(trip, PAGES)
)

SCRIPT = """
(function () {
  // Seis eixos que se combinam por E: base, refeicao, cozinha, preco, atalho e busca.
  var estado = { cidade: 'todas', refeicao: 'todas', cozinha: 'todas', faixa: 'todas', extra: 'todos', busca: '' };
  var blocos = document.querySelectorAll('.rest-bloco');
  var conta = document.getElementById('rest-conta');
  var total = document.querySelectorAll('.rest-card').length;
  var input = document.getElementById('rest-busca');

  function normaliza(s) {
    return (s || '').toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
  }

  function limpo() {
    return estado.cidade === 'todas' && estado.refeicao === 'todas'
      && estado.cozinha === 'todas' && estado.faixa === 'todas'
      && estado.extra === 'todos' && !estado.busca;
  }

  function passaExtra(card) {
    if (estado.extra === 'todos') return true;
    return card.getAttribute('data-' + estado.extra) === 'sim';
  }

  function passaBusca(card) {
    if (!estado.busca) return true;
    return normaliza(card.getAttribute('data-busca')).indexOf(normaliza(estado.busca)) !== -1;
  }

  function aplicar() {
    var visiveis = 0;
    blocos.forEach(function (bl) {
      var baseOk = estado.cidade === 'todas' || bl.getAttribute('data-cidade') === estado.cidade;
      var nesteBloco = 0;
      bl.querySelectorAll('.rest-card').forEach(function (card) {
        var ok = baseOk
          && (estado.refeicao === 'todas' || (card.getAttribute('data-refeicoes') || '').split(' ').indexOf(estado.refeicao) !== -1)
          && (estado.cozinha === 'todas' || card.getAttribute('data-cozinha') === estado.cozinha)
          && (estado.faixa === 'todas' || card.getAttribute('data-faixa') === estado.faixa)
          && passaExtra(card) && passaBusca(card);
        card.style.display = ok ? '' : 'none';
        if (ok) { nesteBloco++; visiveis++; if (window.revelar) window.revelar(card); }
      });
      bl.style.display = baseOk ? '' : 'none';
      bl.classList.toggle('sem-resultado', baseOk && nesteBloco === 0);
      if (baseOk && window.revelar) {
        bl.querySelectorAll('.rest-cab .fade-in, .rest-cab').forEach(function (el) { window.revelar(el); });
      }
    });
    if (conta) {
      conta.textContent = limpo()
        ? total + ' restaurantes catalogados'
        : visiveis + ' de ' + total + ' restaurantes';
    }
    var botao = document.querySelector('.filtro-limpa');
    if (botao) botao.style.visibility = limpo() ? 'hidden' : 'visible';
  }

  document.querySelectorAll('.filtro-btn').forEach(function (b) {
    var eixo = b.getAttribute('data-eixo');
    if (!eixo) return;
    b.addEventListener('click', function () {
      estado[eixo] = b.getAttribute('data-valor');
      document.querySelectorAll('.filtro-btn[data-eixo="' + eixo + '"]').forEach(function (o) {
        o.classList.toggle('ativo', o === b);
      });
      aplicar();
    });
  });

  if (input) input.addEventListener('input', function () { estado.busca = input.value; aplicar(); });

  var limpa = document.querySelector('.filtro-limpa');
  if (limpa) {
    limpa.addEventListener('click', function () {
      estado = { cidade: 'todas', refeicao: 'todas', cozinha: 'todas', faixa: 'todas', extra: 'todos', busca: '' };
      if (input) input.value = '';
      document.querySelectorAll('.filtro-btn').forEach(function (o) {
        var v = o.getAttribute('data-valor');
        o.classList.toggle('ativo', v === 'todas' || v === 'todos');
      });
      aplicar();
    });
  }

  aplicar();
})();
"""

B.write(os.path.join(ROOT, PAGE),
        B.shell(trip, 'Restaurantes', corpo, PAGE, PAGES,
                scripts='<script>' + SCRIPT + '</script>'))
print(f'✅ {PAGE} — {total} restaurantes em {n_cidades} bases')
