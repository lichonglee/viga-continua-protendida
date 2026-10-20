# -*- coding: utf-8 -*-
"""Conteúdo do manual do painel (viga protendida de 1 vão e de 2 vãos). Usado por build_manual_painel.py (Word e PDF).
Blocos: ('h1', t) ('h2', t) ('p', t) ('bul', [t]) ('num', [t]) ('img', [(arquivo, legenda)], maxh_cm)
        ('side', arquivo, legenda, maxh_cm, [texto]) ('tab', linhas, larguras_cm) ('call', tipo, rótulo, texto) ('pb',)
Marcação em texto: **negrito**. Tipos de caixa: info, warn, ok."""

VERSAO = 'v2.8.0'

def blocos():
    B = []
    A = B.append

    # ------------------------------------------------------------------ 1
    A(('h1', '1. Para que serve o painel'))
    A(('p', 'O painel é um aplicativo de uma única página que **recalcula, a cada alteração dos dados**, o projeto de uma viga protendida de seção retangular, em pós-tração aderente, pela NBR 6118. Ele segue a mesma lógica da planilha de apoio (14 abas) e do memorial, e serve para estudar variantes de vão, carga, traçado e quantidade de aço sem refazer a planilha.'))
    A(('p', 'Este manual cobre dois casos: a **viga de 1 vão** (isostática) e a **viga de 2 vãos**, iguais (o projeto de referência da disciplina) ou diferentes. O painel aceita até 6 vãos, mas o passo a passo aqui trata dos dois primeiros casos.'))
    A(('tab', [['O painel calcula', 'Como aparece'],
               ['Traçado do cabo e fuso limite', 'Aba "Traçado e fuso" e cartão de cortes na seção'],
               ['Perdas de protensão e alongamento', 'Aba "Perdas e alongamento"'],
               ['Esforços externos e hiperestático', 'Aba "Esforços e hiperestático"'],
               ['Tensões no ato e em serviço (ELS-D, ELS-F, ELS-CE)', 'Abas "Resumo", "Tensões" e "Níveis de protensão"'],
               ['Ruptura à flexão (ELU), cortante e estribos', 'Aba "Ruptura e cortante"'],
               ['Flecha e frequência fundamental', 'Aba "Flecha"'],
               ['Comparação com concreto armado', 'Aba "Comparação com CA"'],
               ['Memorial de cálculo passo a passo, com fórmulas e telas', 'Aba "Memorial de cálculo" (exporta HTML, Word e PDF)']], [13.5, 12.2]))
    A(('call', 'info', 'Escopo.', 'Seção retangular constante; um cabo contínuo ao longo da viga, com o mesmo traçado para todos os cabos; protensão simultânea pelas duas extremidades; cargas uniformemente distribuídas (permanente e sobrecarga). Os resultados são os do motor do painel; confira sempre as grandezas de referência dos capítulos 4 e 5.'))

    # ------------------------------------------------------------------ 2
    A(('h1', '2. Abrindo o painel e conhecendo a tela'))
    A(('p', 'Abra o endereço do painel no navegador (computador, tablet ou celular). Não há instalação, e os dados ficam só no seu navegador, até você salvá-los em arquivo.'))
    A(('p', '**https://lichonglee.github.io/viga-continua-protendida/app/viga_continua_protendida.html**'))
    A(('img', [('g01_tela_inicial', 'Tela inicial: barra superior, situação do projeto, dados à esquerda e abas à direita')], 15.5))
    A(('h2', 'Barra superior e situação do projeto'))
    A(('img', [('g02_barra_topo', 'Barra superior com logotipo da UnB e as ferramentas'), ('g02b_cabecalho', 'Título, versão e faixa de situação')], 3.2))
    A(('tab', [['Elemento', 'Função'],
               ['Tema', 'Alterna entre automático (segue o sistema), claro e escuro.'],
               ['Salvar dados', 'Baixa um arquivo .json com todos os dados de entrada, para abrir em outra oportunidade.'],
               ['Carregar dados', 'Abre um arquivo .json salvo antes; esses passam a ser os "dados carregados".'],
               ['Limpar tudo', 'Apaga os dados guardados no navegador e volta ao projeto padrão (pede confirmação).'],
               ['Faixa de chips', 'Tipo de viga, nível de protensão atingido (com a cor do nível), situação das verificações, aviso de passiva e forças Pj e P∞.']], [5, 20.7]))
    A(('h2', 'Dados à esquerda e abas à direita'))
    A(('side', 'g04_dados_topo', 'Topo da barra de dados: dados carregados, níveis e tipos de viga', 11.5, [
        '**Dados carregados**: volta ao que foi carregado (arquivo, último estado do navegador ou projeto padrão).',
        '**Nível 3, Nível 2, Nível 1**: calculam, para a viga que está na tela, o menor número de cordoalhas por cabo que atinge cada nível (e a passiva do ELU nos níveis 2 e 1). Ficam desativados se o nível não for atingido com até 12 cordoalhas.',
        '**Tipo de viga**: 1 vão, 2 vãos iguais, 2 vãos diferentes (8 m + 12 m) e 3 vãos iguais. Só mudam a estrutura; os demais dados ficam como estão.',
        'Abaixo ficam os grupos de campos (nível alvo, vãos, seção, ações, traçado, armadura ativa, perdas, passivas e comparações). Os grupos fechados abrem com um clique no título.']))
    A(('img', [('g03_abas', 'Abas e controles de exibição: limites por nível e tabelas do 1º vão ou de todos os vãos')], 2.8))
    A(('bul', ['As **abas** seguem a ordem da planilha: Resumo, Traçado e fuso, Perdas e alongamento, Esforços e hiperestático, Tensões, Ruptura e cortante, Flecha, Níveis de protensão, Comparação com CA e Memorial de cálculo.',
               'A barra de abas **fica fixa** ao rolar a página.',
               '**Limites** escolhe entre mostrar só os limites do nível de protensão escolhido ou os dos três níveis.',
               '**Tabelas e flecha** escolhe entre o 1º vão e todos os vãos (aparece quando há mais de um vão).']))

    # ------------------------------------------------------------------ 3
    A(('h1', '3. Convenções e dados de entrada'))
    A(('tab', [['Convenção', 'Valor'],
               ['Unidades', 'kN, m e MPa (momentos em kN·m; áreas de aço em cm²).'],
               ['Sinais', 'Tração positiva e compressão negativa; momento positivo traciona a fibra inferior.'],
               ['Excentricidade e', 'Positiva abaixo do centro de gravidade (CG); sobre o apoio interno o cabo fica acima (e negativo).'],
               ['Fibras', 'σ1 = fibra inferior; σ2 = fibra superior.'],
               ['Estações de cálculo', '20 divisões por vão (a cada 0,5 m para vão de 10 m); há uma estação em cada apoio.'],
               ['Peso próprio', 'Já está incluído: g0 = 25·bw·h. O campo "g adicional" vale além dele; com g adicional = 0 atua só o peso próprio.']], [6, 19.7]))
    A(('h2', 'Dados do projeto de referência'))
    A(('p', 'Os valores abaixo são o padrão do painel e o projeto de referência da disciplina. Os campos de apoio (e_sup, λ, As e A′ nos apoios) só aparecem quando há mais de um vão.'))
    A(('tab', [['Grupo', 'Campo (símbolo)', 'Valor', 'Observação'],
               ['Vãos', 'Número de vãos (n) e vão (L)', '2 vãos de 10 m', '1 vão: n = 1, L = 10 m'],
               ['Seção e materiais', 'bw × h; fck; γc; t0', '0,30 × 0,90 m; 30 MPa; 1,4; 7 dias', 'CAA II, cnom 3,5 cm, estribo Ø10'],
               ['Ações', 'g adicional; q; ψ1; ψ2', '13,25 kN/m; 25 kN/m; 0,4; 0,3', 'g e q adotadas (provisórias); passarela'],
               ['Traçado do cabo', 'e_ancoragem; e_vão; e_sup; λ', '0; 0,28 m; 0,28 m; 1,0 m', 'e_max = 37,45 cm (h/2 − d′, com d′ = 7,55 cm)'],
               ['Armadura ativa', 'Cabos × cordoalhas; Ap1; fptk; Ep; σpj/fptk', '2 × 5; 0,987 cm²; 1900 MPa; 200000 MPa; 0,74', 'CP190 RB Ø12,7; bainha Ø61 mm'],
               ['Perdas', 'μ; k; cravação; φ; εcs', '0,20; 0,002 1/m; 6 mm; 2,9; −0,23 ‰', 'Ou perda total estipulada em %'],
               ['Passivas (apoio / vão)', 'A′ comprimida', '4,91 cm² / 2,45 cm²', 'As,ato fica na face inferior do apoio B']], [4.2, 7.6, 7.2, 6.7]))

    # ------------------------------------------------------------------ 4
    A(('h1', '4. Passo a passo: viga de 1 vão'))
    A(('p', 'A viga de 1 vão é isostática: não há apoio interno, portanto **não há hiperestático** (M_hip = 0 e M_P = M_iso), e o ELU e a flecha são verificados no vão. O cabo ancora com e = e_ancoragem nas duas pontas e desce até e_vão no meio.'))
    A(('num', ['No topo da barra de dados, clique em **1 vão** (isostática, 10 m). Os campos de apoio desaparecem e o título passa a "Viga protendida, 1 vão".',
               'Confira os dados da seção, das ações e da armadura (capítulo 3). Para este caso, use os mesmos dados do projeto de referência.',
               'Percorra as abas na ordem, como nas telas a seguir, comparando com a tabela de conferência.']))
    A(('h2', '4.1 Resumo'))
    A(('img', [('v1_resumo_1', 'Resumo: traçado do cabo e fuso limite (1 vão)'), ('v1_resumo_2', 'Resumo: verificações do projeto')], 14))
    A(('p', 'O traçado deve ficar **dentro da faixa cinza** (fuso). A linha de pressões coincide com o cabo, porque sem hiperestático e_lp = e. O cartão "Verificações" lista cada limite com valor e situação; o nível alvo é o escolhido em "Nível de protensão alvo".'))
    A(('call', 'warn', 'Resultado esperado com os dados de referência.', 'A protensão dimensionada para 2 vãos fica **sobrando em um vão só**: a viga de 1 vão atinge o **nível 2** e reprova o ELS-F do nível 3 (margem −0,30 MPa). Use o botão **Nível 3** na barra de dados: para esta viga ele sugere 6 cordoalhas por cabo (4 para o nível 2 e 2 para o nível 1).'))
    A(('side', 'v1_resumo_3', 'Cortes na seção para a viga de 1 vão', 15.5, [
        'O cartão mostra a seção ao longo da viga: ancoragem, vão, vértice da parábola e ancoragem de novo. Os círculos azuis são as cordoalhas; os roxos, a armadura passiva (A′, As,ato e As do ELU).',
        'A linha tracejada verde é o estribo. Na região de ancoragem (menos de 1 m das pontas) não se desenha passiva.',
        'O controle **Corte em x** percorre a viga; os botões **Salvar seção** gravam o corte escolhido ou todos os cortes em SVG ou PNG.']))
    A(('h2', '4.2 Traçado e fuso'))
    A(('img', [('v1_tracado_1', 'Traçado e fuso: marque "Mostrar os 10 limites" para ver cada condição de tensão')], 10.5))
    A(('p', 'Cada limite do fuso vem de uma condição de tensão: tração e compressão no ato, descompressão, formação de fissuras e compressão excessiva em serviço. O fuso é o maior dos cinco limites inferiores e o menor dos cinco superiores. O cartão "Parábolas de cada vão" traz x0, a e λ.'))
    A(('h2', '4.3 Perdas e alongamento'))
    A(('img', [('v1_perdas_1', 'Tensão no aço ao longo do cabo'), ('v1_perdas_2', 'Forças, perdas e alongamento')], 14.5))
    A(('bul', ['A tensão cai pelo **atrito** (curvas azuis, da extremidade esquerda e da direita), a **cravação** devolve tensão perto das ancoragens, e o encurtamento elástico e as perdas progressivas completam o quadro.',
               'Com 1 vão, a cravação **não é absorvida** ao longo do vão: o alcance x_a vale L/2 = 5,00 m (limite no cruzamento das curvas de atrito). Os dois lados têm o mesmo alongamento: 34,7 mm por ponta (líquido 28,7 mm).']))
    A(('h2', '4.4 Esforços e hiperestático'))
    A(('img', [('v1_esforcos_1', 'Momentos externos: Mg, Mg + Mq,máx e Mg + Mq,mín'), ('v1_esforcos_2', 'Momentos da protensão: só isostático')], 14))
    A(('p', 'Os momentos externos valem g·L²/8 no meio do vão (Mg = 250,0 kN·m com g = 20 kN/m) e a sobrecarga q dá Mq,máx = 312,5 kN·m. No segundo cartão, a curva de M_hip é nula: a protensão não gera esforços hiperestáticos.'))
    A(('h2', '4.5 Tensões'))
    A(('img', [('v1_tensoes_1', 'Tensões nas fibras (escolha o estado no seletor)'), ('v1_tensoes_2', 'Margens e limites adotados')], 14))
    A(('p', 'O seletor **Estado** alterna entre ato, quase permanente, frequente (ELS-D), rara (ELS-F e ELS-CE) e "todos os estados". As margens do cartão ao lado são positivas quando há folga. As linhas laranja são limites do nível 3 (capítulo 6).'))
    A(('h2', '4.6 Ruptura e cortante'))
    A(('side', 'v1_elu_1', 'Flexão no ELU: seção crítica no vão', 16.5, [
        'Cada coluna é uma seção crítica; com 1 vão há **uma só coluna**, a do vão.',
        'Leia as linhas em ordem: pré-alongamento εp0, forças Tp, Ts e Cs, linha neutra x, deformação do aço, MRd, Msd e a razão MRd/|Msd|.',
        'Com os dados de referência: MRd/|Msd| = **1,14** e x/dp = 0,43 (limite 0,45).',
        'O cortante máximo é Vsd = **206 kN** (limite VRd2 = 986 kN), no apoio, e os estribos ficam no mínimo (1,74 cm²/m por ramo).']))
    A(('img', [('v1_elu_2', 'Cortante Vsd e VRd2'), ('v1_elu_3', 'Seções do vão: Vp, Vsd, β e estribos')], 10))
    A(('h2', '4.7 Flecha'))
    A(('img', [('v1_flecha_1', 'Deslocamentos verticais'), ('v1_flecha_2', 'Resultados e limite L/250')], 12))
    A(('p', 'A flecha quase permanente × (1 + φ) é **4,0 mm** (limite L/250 = 40 mm). A frequência fundamental, estimada com o vão biapoiado, é 7,7 Hz.'))
    A(('h2', '4.8 Níveis de protensão e comparação com CA'))
    A(('img', [('v1_niveis_1', 'Níveis de protensão da NBR 6118'), ('v1_niveis_2', 'Tração máxima por combinação')], 11))
    A(('img', [('v1_ca_1', 'Concreto protendido × concreto armado'), ('v1_ca_2', 'Flecha imediata do concreto armado')], 11))
    A(('p', 'Na aba Níveis, as linhas laranja, azul e roxa são os níveis 3, 2 e 1. Na comparação com CA, a viga de 1 vão pede As = 25,2 cm² no vão em concreto armado, contra a protensão de 9,87 cm² mais as passivas.'))
    A(('h2', '4.9 Valores de conferência: 1 vão'))
    A(('tab', [['Grandeza', 'Valor esperado', 'Grandeza', 'Valor esperado'],
               ['Ap (2 × 5 cord.)', '9,87 cm²', 'Pj', '1388 kN'],
               ['Carga a equilibrar g + ψ2·q', '27,5 kN/m', 'e_max', '37,45 cm'],
               ['Mg (meio do vão)', '250,0 kN·m', 'Mq,máx (meio do vão)', '312,5 kN·m'],
               ['Alcance da cravação x_a', '5,00 m (limitado a L/2)', 'Σα · comprimento do cabo', '0,223 rad · 10,02 m'],
               ['Alongamento por ponta', '34,7 mm (líquido 28,7)', 'P∞ (mín. a máx.)', '1049,6 a 1090,5 kN'],
               ['Nível atingido', '2 (ELS-F do nível 3: −0,30 MPa)', 'Margens do nível 2 (D / F)', '+2,67 / +4,33 MPa'],
               ['MRd/|Msd| e x/dp no vão', '1,14 e 0,43', 'Vsd / VRd2', '206 / 986 kN'],
               ['Flecha qp,∞', '4,0 mm (limite 40)', 'Frequência f1', '7,7 Hz'],
               ['CA: As no vão', '25,2 cm²', 'CA: flecha total', '34,8 mm']], [7, 5.8, 6.7, 6.2]))

    # ------------------------------------------------------------------ 5
    A(('h1', '5. Passo a passo: viga de 2 vãos iguais'))
    A(('p', 'É o projeto de referência: 2 vãos de 10 m, seção 30 × 90 cm, C30, 2 cabos × 5 cordoalhas, g adicional 13,25 kN/m e q = 25 kN/m. O apoio central impede a deformação da protensão e gera a **reação hiperestática R_B**.'))
    A(('num', ['Clique em **2 vãos iguais** (projeto atual) ou em **Restaurar**, que volta ao projeto padrão.',
               'Percorra as abas e compare com a tabela de conferência do item 5.8.']))
    A(('h2', '5.1 Resumo'))
    A(('img', [('v2_resumo_1', 'Resumo: traçado e fuso (2 vãos)'), ('v2_resumo_2', 'Resumo: verificações')], 14.5))
    A(('p', 'Com os dados de referência todas as verificações do nível 3 atendem, e a faixa de chips mostra **"1 ponto pede passiva"**: no ato, a tração em B (σ1 = 3,90 MPa) passa do limite de 2,70 MPa, e a armadura As,ato = 4,9 cm² a absorve. Essa mesma armadura vale como A′ no ELU.'))
    A(('side', 'v2_resumo_3', 'Cortes na seção para a viga de 2 vãos', 15.5, [
        'Mostra seis seções: ancoragem, vão, vértice, a 0,7 L, junto ao apoio e o apoio B.',
        'Sobre o apoio B o cabo passa **acima do CG** (e negativo) e a armadura passiva aparece nas faces superior e inferior.',
        'O cartão "Valores principais" resume Pj, P∞, x_a, alongamento, R_B e M_hip no apoio B.']))
    A(('h2', '5.2 Traçado e fuso'))
    A(('img', [('v2_tracado_1', 'Traçado em dois vãos, com a parábola reversa junto ao apoio B')], 10.5))
    A(('p', 'No vão, a parábola principal desce até e_vão; junto ao apoio, a **parábola reversa** (comprimento λ) leva o cabo para cima de B, com inclinação contínua. O quadro "Parábolas de cada vão" traz x0, a, λ esquerdo e λ direito de cada vão.'))
    A(('h2', '5.3 Perdas e alongamento'))
    A(('img', [('v2_perdas_1', 'Tensão no aço ao longo do cabo (2 vãos)'), ('v2_perdas_2', 'Forças, perdas e alongamento')], 14.5))
    A(('p', 'O alcance da cravação é x_a = **9,23 m** e o alongamento vale 67,4 mm por ponta (líquido 61,4 mm). As curvas de atrito das duas extremidades se cruzam no apoio B; cada extremidade comanda o seu lado.'))
    A(('h2', '5.4 Esforços e hiperestático'))
    A(('img', [('v2_esforcos_1', 'Momentos externos'), ('v2_esforcos_2', 'Momentos da protensão: isostático, hiperestático e total')], 14))
    A(('p', 'Os momentos externos usam a equação dos três momentos, com a sobrecarga alternada por vão. No apoio B: Mg = −250,0 kN·m e Mq,mín = −312,5 kN·m. O hiperestático é **R_B = −13,78 kN** e **M_hip,B = +68,9 kN·m**.'))
    A(('h2', '5.5 Tensões, ruptura e cortante'))
    A(('img', [('v2_tensoes_1', 'Tensões nas fibras'), ('v2_elu_2', 'Cortante Vsd e VRd2')], 12.5))
    A(('p', 'Resultados do nível 3: ELS-D (frequente) com tração máxima de −0,45 MPa (atende), ELS-F (rara) com 1,83 MPa (limite 2,43) e ELS-CE com −9,06 MPa (limite −21,00). Na ruptura: MRd/|Msd| = **1,26** em B e **1,60** nos vãos; Vsd = **388 kN** (limite VRd2 = 986 kN).'))
    A(('h2', '5.6 Flecha, níveis e comparação com CA'))
    A(('img', [('v2_flecha_1', 'Flecha dos dois vãos'), ('v2_niveis_1', 'Níveis de protensão')], 12.5))
    A(('img', [('v2_niveis_2', 'Tração máxima por combinação'), ('v2_ca_1', 'Protendido × concreto armado')], 12.5))
    A(('p', 'A flecha quase permanente × (1 + φ) fica em −2,8 mm (contraflecha). Em concreto armado a mesma viga pede As = 25,2 cm² em B e 16,1 cm² no vão, com wk = 0,10 mm e flecha total de +7,4 mm.'))
    A(('h2', '5.7 Memorial de cálculo'))
    A(('img', [('v2_memorial_topo', 'Memorial: capa, sumário, dados e primeira etapa')], 14))
    A(('p', 'O memorial reúne, etapa a etapa, **fórmula, substituição com os valores e resultado**, seguidos das telas correspondentes (gráficos, tabelas e cortes). Os botões **Baixar HTML**, **Baixar Word (.doc)** e **Imprimir / salvar em PDF** exportam o mesmo conteúdo, sempre em tema claro. A caixa "Incluir as telas" liga e desliga as figuras.'))
    A(('h2', '5.8 Valores de conferência: 2 vãos iguais'))
    A(('tab', [['Grandeza', 'Valor esperado', 'Grandeza', 'Valor esperado'],
               ['Ap · Pj', '9,87 cm² · 1388 kN', 'p_bal · e_max', '27,5 kN/m · 37,45 cm'],
               ['Alcance da cravação x_a', '9,23 m', 'Σα · comprimento do cabo', '1,013 rad · 20,09 m'],
               ['P∞ em x = 4 m · em B', '941,7 kN · 975,7 kN', 'Alongamento por ponta', '67,4 mm (líquido 61,4)'],
               ['R_B', '−13,78 kN', 'M_hip no apoio B', '+68,9 kN·m'],
               ['σ1 no ato em B', '3,90 MPa (limite 2,70)', 'As,ato', '4,9 cm²'],
               ['ELS-D (frequente) · ELS-F (rara)', '−0,45 · 1,83 MPa (limite 2,43)', 'Vsd / VRd2', '388 / 986 kN'],
               ['MRd/|Msd| em B · no vão', '1,26 · 1,60', 'Flecha qp,∞', '−2,8 mm'],
               ['Níveis (cordoalhas por cabo)', 'N3 = 5; N2 = 4; N1 = 2', 'CA: As · wk · flecha total', '25,2 / 16,1 cm² · 0,10 mm · +7,4 mm']], [7, 5.8, 6.7, 6.2]))
    A(('call', 'ok', 'Como conferir.', 'Se algum valor do quadro não bater, volte ao capítulo 3 e confira os dados de entrada, principalmente a seção, as ações, e_vão, e_sup, λ e a armadura ativa; depois use "Restaurar" e refaça o caminho.'))

    A(('h2', '5.9 Variante: 2 vãos diferentes (8 m + 12 m)'))
    A(('p', 'Clique em **2 vãos diferentes**. O campo "Comprimentos dos vãos" passa a "diferentes" e aparecem L1 e L2. Cargas e traçado podem ser iguais em todos os vãos ou definidos por vão e por apoio (campos "Cargas g e q" e "Traçado do cabo").'))
    A(('img', [('v2d_resumo_2', 'Verificações para 8 m + 12 m'), ('v2d_esforcos_1', 'Momentos externos assimétricos')], 14))
    A(('img', [('v2d_tracado_1', 'Traçado do cabo em vãos diferentes')], 10))
    A(('tab', [['Grandeza (8 m + 12 m, dados de referência)', 'Valor'],
               ['M_B permanente · Mq,mín em B', '−280,0 kN·m · −350,0 kN·m'],
               ['Mg máximo no vão 1 · no vão 2', '47,6 kN·m · 233,6 kN·m'],
               ['R_B · M_hip,B', '−14,32 kN · +68,7 kN·m'],
               ['Alcance da cravação (esquerda) · alongamentos esq. / dir.', '7,48 m · 51,1 mm / 83,6 mm'],
               ['P∞ (mín. a máx.)', '899,2 a 1066,3 kN'],
               ['MRd/|Msd| no apoio · nos vãos 1 e 2', '1,12 · 2,87 e 1,10'],
               ['Flecha ×(1+φ) vão 1 · vão 2 (limites L/250)', '8,8 mm (32) · 10,1 mm (48)'],
               ['Situação do nível', 'N2: ELS-D −2,09 e ELS-F +0,03 MPa; N3 também não atende']], [15, 10.7]))
    A(('call', 'warn', 'Atenção.', 'Com vãos diferentes a protensão de referência já não satisfaz os níveis 2 e 3 (o vão maior pede mais protensão). Use os botões de nível e ajuste e_vão, e_sup e λ por vão. Os alongamentos das duas pontas diferem: informe os dois valores ao operador.'))

    # ------------------------------------------------------------------ 6 (recursos)
    A(('h1', '6. Recursos do painel'))
    A(('h2', '6.1 Níveis de protensão e cores'))
    A(('p', 'O painel identifica o nível pela NBR 6118 (pós-tração em CAA II exige no mínimo o nível 2). Os itens que só valem para um nível têm cor: **laranja = nível 3**, **azul = nível 2** e **roxo = nível 1**, com a etiqueta N3, N2 ou N1. As cores aparecem nas verificações, na aba Níveis, nas margens da aba Tensões, nos botões de nível e no chip de situação.'))
    A(('h2', '6.2 Limites: só do nível escolhido ou todos'))
    A(('img', [('f01_verificacoes_todos_limites', 'Em "Todos", os limites de outros níveis aparecem esmaecidos, só para consulta'), ('f02_limites_e_vaos', 'Controle de limites e de vãos na barra de abas')], 14))
    A(('p', 'O padrão é **Só do nível N**, que mostra os limites do nível escolhido mais os comuns (ato, ELS-CE, ELU, cortante e flecha). Em **Todos**, aparecem também os dos outros níveis; eles **não entram** na contagem de "verificações não atendem". O memorial sempre sai com todos os limites.'))
    A(('h2', '6.3 Cartões recolhíveis'))
    A(('img', [('f03_cartao_recolhido', 'Cartão recolhido vira um botão tracejado; os demais ocupam a largura toda')], 10))
    A(('p', 'O botão **–** no título recolhe o cartão. Os recolhidos viram botões na barra "Recolhidos" e voltam com um clique; **Recolher todos** e **Mostrar todos** atuam na aba inteira. Os cartões que ficam se reorganizam e ocupam toda a largura. A escolha fica guardada no navegador.'))
    A(('h2', '6.4 Escala dos eixos e efeitos de cada gráfico'))
    A(('img', [('f04_escala_eixos', 'Escala dos eixos: x e y mínimo e máximo, Aproximar, Afastar e Automática')], 10.5))
    A(('img', [('f05_efeitos_grupo', 'Mostrar: agrupamentos de efeitos'), ('f09_perdas_estipulada', 'Mesmo gráfico com a perda total estipulada')], 12))
    A(('bul', ['**Escala dos eixos**: digite os limites de x e y (campos em branco ficam automáticos), ou use **Aproximar**, **Afastar** e **Automática**. O memorial ignora a escala personalizada.',
               '**Mostrar:** liga um agrupamento de efeitos (por exemplo "Perdas imediatas"); a legenda também liga e desliga cada curva.']))
    A(('h2', '6.5 Salvar a seção'))
    A(('img', [('f06_cortes_salvar_secao', 'Cartão de cortes com os botões Salvar seção (SVG e PNG)')], 12.5))
    A(('p', 'No cartão de cortes, **Salvar seção** grava o corte escolhido ou todos os cortes em SVG ou PNG, em cores claras, com cotas em cm e legenda (posição x, excentricidade, distância dos cabos à base e armaduras passivas).'))
    A(('h2', '6.6 Perda total estipulada e cabo resultante'))
    A(('img', [('f07_perda_estipulada', 'Perda total estipulada (%)'), ('f08_cabo_resultante', 'Cabo resultante: número de cabos e Pj')], 6.5))
    A(('bul', ['**Perda total estipulada**: em "Perdas de protensão", escolha "estipulada (%)" e informe a perda. A tensão final fica σp,∞ = σp,j·(1 − Δ), igual em todo o cabo. As perdas imediatas continuam calculadas; se o total estipulado for menor que elas, a tensão final iguala a do ato e um aviso amarelo aparece na aba Perdas.',
               '**Cabo resultante**: em "Armadura ativa", escolha "cabo resultante (Pj)" e informe o número de cabos e a força no macaco total. A área sai de Ap = Pj/σpj, e a nota abaixo mostra o equivalente em cordoalhas por cabo.']))
    A(('h2', '6.7 Salvar e carregar dados, limpar tudo e tema'))
    A(('img', [('f11_salvar_dados_aviso', 'Aviso após salvar os dados'), ('f10_tema_escuro', 'Tema escuro')], 8.5))
    A(('bul', ['**Salvar dados** gera o arquivo `Viga_dados_<n>vaos_<data>.json` com todos os campos (inclusive número e comprimento dos vãos, cargas, traçado, passivas e perdas).',
               '**Carregar dados** valida e preenche tudo; campos ausentes usam o padrão e arquivos inválidos não alteram nada.',
               '**Limpar tudo** apaga o que o painel guardou no navegador e volta ao projeto padrão, depois de confirmar.',
               '**Tema** alterna automático, claro e escuro; o memorial é sempre claro por dentro.']))

    # ------------------------------------------------------------------ 7
    A(('h1', '7. Roteiro de conferência e dúvidas frequentes'))
    A(('tab', [['Dúvida ou sintoma', 'O que fazer'],
               ['O título ou os chips não mostram o tipo de viga esperado', 'Confira "Número de vãos" e "Comprimentos dos vãos"; clique no tipo de viga desejado.'],
               ['Os botões de nível estão desativados ou em branco', 'O nível não é atingido com até 12 cordoalhas por cabo, ou o painel ainda não calculou. Ajuste e_vão, e_sup, λ ou a seção.'],
               ['"1 ponto pede passiva"', 'A tração no ato passou do limite; informe As,ato (ou A′) em "Armaduras passivas" no apoio e confira o ELU.'],
               ['ELU com x/d acima de 0,45', 'Aumente A′ comprimida; o cartão da aba Ruptura mostra o A′ mínimo.'],
               ['Perda estipulada menor que as perdas imediatas', 'Aumente o percentual; o aviso da aba Perdas mostra quantas seções foram limitadas.'],
               ['Gráfico com a escala estranha', 'Abra "Escala dos eixos" e clique em Automática.'],
               ['Quero repetir uma análise outro dia', 'Use Salvar dados; depois Carregar dados em qualquer computador.']], [10, 15.7]))
    A(('call', 'info', 'Limites do cálculo.', 'A frequência fundamental é uma estimativa (maior vão biapoiado). Cada vão tem 20 divisões. O motor não verifica se as cordoalhas cabem na bainha informada. As armaduras passivas informadas valem para todos os apoios internos e para todos os vãos. Para 2 vãos iguais o motor reproduz o anterior (conferido em 5 casos), e o hiperestático segue o método das forças.'))
    return B
