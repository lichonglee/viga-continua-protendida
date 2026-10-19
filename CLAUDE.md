# Projeto: viga contínua protendida, 2 vãos (UnB · Concreto Protendido)

Responsável: Prof. Li Chong Lee Bacelar de Castro (UnB). Tratar no masculino. Idioma: português do Brasil.

## O problema
Viga contínua de 2 vãos de 10 m, seção 30 × 90 cm, C30, CAA II, pós-tração aderente, CP190 RB Ø12,7 (Ap1 = 0,987 cm²),
2 cabos × 5 cordoalhas (nível 3), bainha Ø61 mm, cnom 3,5 cm, estribo Ø10, protensão simultânea pelas duas extremidades.
Ações: g adicional 13,25 kN/m e q = 25 kN/m (adotadas, provisórias), ψ1 = 0,4, ψ2 = 0,3 (passarela). NBR 6118.

## Convenções (não mudar sem avisar)
- kN, m, MPa; tração positiva, compressão negativa; momento positivo = tração embaixo; e positivo abaixo do CG; σ1 = fibra inferior, σ2 = superior.
- Estações a cada 0,5 m (x = 0 a 20 m, 41 linhas; B = x 10 m). Dois lados protendidos: calcular 0 a 10 m e espelhar.
- Hiperestático por método das forças com integral em trapézio na planilha (R_B = −13,78 kN; M_hip,B = +68,9 kN·m); Simpson dá −13,80.
- Cortante: β = 1 + M0/Msd com Msd = 1,4(Mg+Mq) sem hiperestático. Mq,máx em B = 0.
- As,ato fica na face inferior de B (σ1 = +3,90 MPa; limite 2,70). No ELU as mesmas barras valem como A′.

## Valores de referência (conferir após qualquer mudança)
Ap 9,87 cm²; p_bal 27,5 kN/m; e_max 37,45 cm; Pj 1388 kN; xa 9,23 m; Σα 1,013 rad; cabo 20,09 m; P∞ 941,7 kN (x=4) e 975,7 kN (B);
R_B −13,78 kN; M_hip,B +68,9 kN·m; σ1 ato 3,90 MPa; As,ato 4,9 cm²; CFQ máx −0,45; CR máx 1,83 (limite 2,43); Vsd 388 / VRd2 986 kN;
MRd/Msd 1,26 (B) e 1,60 (vão); alongamento 67,4 mm por ponta (líquido 61,4); flecha qp,∞ −2,8 mm; CA: As 25,2/16,1 cm², wk 0,10 mm, flecha total +7,4 mm.
Níveis: N3 = 5 cord./cabo; N2 = 4 (frequente −0,70, QP −1,04 MPa, As,ato 3,15 cm², flecha −0,2 mm); N1 = 2 (frequente +3,94, QP +3,17, flecha +5,4 mm, wk 0,03 mm).

## Estrutura
- src/engine.py, py_ref.py, analysis.py: motor de cálculo em Python (referência independente da planilha).
- src/build_xlsx.py: gera a planilha de apoio (14 abas, fórmulas vivas, openpyxl). Recalcular com `soffice --headless --convert-to xlsx`.
- src/build_niveis.py: planilha Niveis_de_Protensao. src/memorial.py: memorial .docx. src/build_dxf*.py: desenhos DXF (CP, níveis 1/2, CA).
- src/content.py, build_manual.py, shots.py: manual da planilha com telas (LibreOffice + python-docx).
- rot/: roteiros (viga.txt, plan.txt = texto dos Claude Docs) e build.py que gera o Word UnB.
- app/viga_continua_protendida.html: app interativo (HTML único, motor em JS). Artefato publicado no claude.ai.
- deck/: slides HTML (project/slides, deck.json), imagens (blob/) e render_slides.py (Playwright → PNG).
- entregas/: últimas versões dos arquivos gerados (xlsx, docx, pdf, dxf, legendas).

## Atenção
- Os scripts foram escritos numa sessão em nuvem e têm caminhos absolutos (/tmp/claude-0/.../scratchpad). Ajuste os caminhos antes de rodar.
- Os roteiros vivos estão em Claude Docs (viga e planilhas); aqui só há cópia de texto. Os slides e o app vivem como artefatos no claude.ai.
- Pendências conhecidas: vídeo "Traço e Fuso Limite" não foi regerado; flecha CA instantânea difere da do aluno (7,18 vs 3,19 mm): comparar Mr, As por estação e Ie em x = 4 m.
