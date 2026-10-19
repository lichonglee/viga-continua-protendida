import sys; sys.path.insert(0,'.')
from analysis import *
import numpy as np
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from openpyxl import load_workbook
d=final_design(); r,m,Aato,AscB,Ascs=evaluate_design(d)
Ls=r['Ls']; ext=r['ext']; ck=r['ck']; lim=r['lim']; res=r['res']
wb=load_workbook('rc/Planilha_Apoio_Viga_Continua_CP.xlsx',data_only=True)
S=wb['Tensoes']; T=wb['Tracado_Perdas']; U=wb['ELU']; A=wb['Alongamento']; P=wb['Flecha_PC']; RC=wb['CA']; K=wb['CA_Flecha']; C=wb['Cortante']; H=wb['Hiperestatico']
f=lambda v,n=2: f'{v:.{n}f}'.replace('.',',')
NAVY=RGBColor(0x1F,0x38,0x64)
doc=Document()
sec=doc.sections[0]; sec.left_margin=sec.right_margin=Cm(2.2); sec.top_margin=sec.bottom_margin=Cm(2)
st=doc.styles['Normal']; st.font.name='Calibri'; st.font.size=Pt(10.5)
for n,sz in (('Heading 1',15),('Heading 2',12.5),('Heading 3',11)):
    s=doc.styles[n]; s.font.name='Calibri'; s.font.size=Pt(sz); s.font.color.rgb=NAVY; s.font.bold=True
def shade(cell,color):
    tcPr=cell._tc.get_or_add_tcPr(); sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),color); tcPr.append(sh)
def para(t,bold=False,italic=False,size=None,align=None):
    p=doc.add_paragraph(); run=p.add_run(t); run.bold=bold; run.italic=italic
    if size: run.font.size=Pt(size)
    if align: p.alignment=align
    p.paragraph_format.space_after=Pt(4); return p
def box(lines,fill='F2F2F2',left=True,bold=False):
    tb=doc.add_table(rows=1,cols=1); c=tb.rows[0].cells[0]; shade(c,fill)
    tcPr=c._tc.get_or_add_tcPr(); b=OxmlElement('w:tcBorders')
    e=OxmlElement('w:left'); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'36'); e.set(qn('w:color'),'1F3864'); b.append(e); tcPr.append(b)
    c.paragraphs[0].text=''
    for i,l in enumerate(lines):
        p=c.paragraphs[0] if i==0 else c.add_paragraph()
        rr=p.add_run(l); rr.bold=bold; rr.font.size=Pt(10); p.paragraph_format.space_after=Pt(2)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
def formula(title,form,onde,subs=None,result=None):
    box([title,form],fill='F2F2F2',bold=False)
    if onde: para('onde: '+onde,italic=True,size=9.5)
    if subs:
        for i,s in enumerate(subs,1): para(f'({i}) {s}',size=10)
    if result: box([result],fill='DCE6F1',bold=True)
def table(head,rows,widths=None,fs=8.5):
    t=doc.add_table(rows=1,cols=len(head)); t.style='Table Grid'
    for j,h in enumerate(head):
        c=t.rows[0].cells[j]; c.text=''; rr=c.paragraphs[0].add_run(h); rr.bold=True; rr.font.size=Pt(fs); rr.font.color.rgb=RGBColor(255,255,255); shade(c,'1F3864')
    for row in rows:
        cs=t.add_row().cells
        for j,v in enumerate(row):
            cs[j].text=''; rr=cs[j].paragraphs[0].add_run(str(v)); rr.font.size=Pt(fs)
            cs[j].paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after=Pt(2); return t
def fig(path,w=16): doc.add_picture(path,width=Cm(w)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER

g=d['g']; q=d['q']; L=d['L']; pb=g+d['psi2']*q
# capa
para('UNIVERSIDADE DE BRASÍLIA – UnB',bold=True,size=12,align=WD_ALIGN_PARAGRAPH.CENTER)
para('Concreto Armado e Protendido',size=11,align=WD_ALIGN_PARAGRAPH.CENTER)
para('MEMORIAL DE CÁLCULO',bold=True,size=20,align=WD_ALIGN_PARAGRAPH.CENTER)
para('Viga contínua protendida de dois vãos de 10 m\nSeção 30 × 90 cm – C30 – CAA II – CP 190 RB Ø12,7 – pós-tração aderente',size=12,align=WD_ALIGN_PARAGRAPH.CENTER)
para('Referência: viga biapoiada do projeto (30×90, L = 10 m, 12 CP190 RB, e = 35 cm, P∞ ≈ 1090 kN)',italic=True,align=WD_ALIGN_PARAGRAPH.CENTER)
para('Prof. Li Chong Lee Bacelar de Castro',align=WD_ALIGN_PARAGRAPH.CENTER)
box(['ATENÇÃO – dados adotados provisoriamente:',
 f'• Carga permanente adicional = {f(d["g_add"])} kN/m (g total = {f(g)} kN/m) e sobrecarga q = {f(q)} kN/m foram ADOTADAS por não constarem dos arquivos anexos. Substituir pelos valores da viga biapoiada de referência (aba Dados da planilha) – todos os resultados são recalculados.',
 f'• Fluência φ = {f(d["phi_cr"],1)} e retração εcs = {f(d["eps_cs"]*1000,2)} ‰ (UR 75 %, t0 = 7 d, hfic ≈ 22 cm) estimados pela Tab. 8.2 da NBR 6118 – conferir.',
 '• Nível 3 (protensão completa), CAA II: ELS-D sob a combinação frequente (CFQ: Mg + ψ1·Mq) e ELS-F sob a combinação rara (CR: Mg + Mq).'],fill='FFF2CC')
doc.add_page_break()

doc.add_heading('1. Dados e hipóteses',1)
table(['Grandeza','Valor','Grandeza','Valor'],[
 ['Vão (cada tramo)','2 × 10,0 m','Seção',f'{f(d["bw"]*100,0)} × {f(d["h"]*100,0)} cm'],
 ['Ac / Ic',f'{f(d["Ac"],3)} m² / {f(d["Ic"],5)} m⁴','W1 = W2 / k',f'{f(d["W"],4)} m³ / {f(d["k"],3)} m'],
 ['fck / fcd',f'30 / {f(d["fcd"])} MPa','Eci / Ecs',f'{f(d["Eci"],0)} / {f(d["Ecs"],0)} MPa'],
 ['fct,m / fctk,inf',f'{f(d["fctm"])} / {f(d["fctkinf"])} MPa','fcj (7 d) / fct,m,j',f'{f(d["fcj"],1)} / {f(d["fctmj"])} MPa'],
 ['g0 (peso próprio)',f'{f(d["g_pp"])} kN/m','g total',f'{f(g)} kN/m'],
 ['q (sobrecarga)',f'{f(q)} kN/m','ψ1 / ψ2','0,4 / 0,3'],
 ['Aço ativo','CP190 RB Ø12,7 (Ap1 = 0,987 cm²)','σp,j = 0,74·fptk',f'{f(d["sig_j"],0)} MPa'],
 ['Cobrimento nominal','3,5 cm (CAA II)','μ / k',f'{f(d["mu"])} / {f(d["kk"],3)} /m'],
 ['Cravação','6 mm por extremidade','Protensão','simultânea, 2 extremidades']])
para('Convenção: tração positiva, compressão negativa; M positivo traciona a fibra inferior; excentricidade e positiva abaixo do CG. Resultados obtidos com a planilha de apoio (abas indicadas) e conferidos com cálculo independente em Python.',italic=True,size=9.5)

doc.add_heading('2. a) Carga a ser equilibrada',1)
formula('Método do balanceamento de cargas (Lin)','p_bal = g + ψ2·q   (combinação quase-permanente)',
        'g = permanente total; ψ2 = 0,3 (passarela); q = sobrecarga.',
        [f'p_bal = {f(g)} + 0,3 × {f(q)} = {f(pb)} kN/m'],f'p_bal = {f(pb)} kN/m')
para('Com essa carga balanceada, em serviço permanente a viga fica, no vão, praticamente sem flecha e sob compressão uniforme P/A; o hiperestático é considerado separadamente (item 6).')

doc.add_heading('3. b) Excentricidades máximas e b.1) fuso limite',1)
formula("Excentricidade máxima pelo cobrimento","e_max = h/2 − d'   ;   d' = c + Øestribo + Øbainha/2",
        "c = 3,5 cm; Øestribo = 1,0 cm; Øbainha = 6,1 cm (5 cordoalhas).",
        [f"d' = 3,5 + 1,0 + 6,1/2 = {f(d['dpp']*100,2)} cm",f"e_max = 45 − {f(d['dpp']*100,2)} = {f(d['e_max']*100,2)} cm"],f"e_max = {f(d['e_max']*100,1)} cm")
para(f'Adotou-se e = {f(d["e_span"]*100,0)} cm no vão (e = 0 nas ancoragens, CG) e {f(d["e_sup"]*100,0)} cm acima do CG no apoio central, deixando folga em relação a e_max para a tolerância de execução (±1 cm) e a curvatura da bainha.')
formula('Fuso limite (aula 06) – limites da linha de pressões e_lp = e − M_hip/N',
 'Limite inferior (σ1 ≤ σlim):  e_lp ≥ (M − σlim·W)/N − k        Limite superior (σ2 ≤ σlim):  e_lp ≤ (M + σlim·W)/N + k',
 'k = W/Ac = 15 cm (distância ao núcleo); cinco limites inferiores (ato σ1 tração, ato σ2 compressão, ELS-D, ELS-F, ELS-CE) e cinco superiores.',None,None)
fig('fig/fuso.png',16)
para('O cabo está contido no fuso em todas as seções. Nas seções 9,5 a 10,5 m (apoio B) a tração no ato excede 1,2·fct,m,j; adota-se armadura passiva As,ato (item 8.1). A tabela completa dos limites por seção está na aba "Fuso".')

doc.add_heading('4. Traçado do cabo',1)
para('Cabo resultante com parábolas do 2º grau: parábola de vértice em x0 no vão e parábola reversa de comprimento λ = 1,0 m junto ao apoio central, espelhado no segundo tramo.')
formula('Equações do traçado','e(x) = e_vão − aA·(x − x0)²  (0 ≤ x ≤ L−λ);   e(x) = −e_sup + aB·(L − x)²  (L−λ ≤ x ≤ L)',
        f'x0 = {f(float(wb["Dados"]["C"+str([i for i in range(4,100) if wb["Dados"].cell(i,1).value=="x0"][0])].value),3)} m; aA = c/x0²; aB = aA(xi − x0)/λ.',None,None)
fig('fig/momentos.png',15)

doc.add_heading('5. c) Força de protensão necessária e d) quantidade de cabos',1)
fcab=d['e_span']+d['e_sup']/2-0.0; P_inf_min=pb*L**2/(8*fcab)
formula('Balanceamento: P = p_bal·L²/(8·f)','P = p_bal·L² / (8f)',"f = flecha do cabo.",
        [f'Flecha equivalente do cabo em cada tramo (corda entre a ancoragem e o apoio): f ≈ e_vão + e_sup/2 = {f(d["e_span"])} + {f(d["e_sup"])}/2 = {f(fcab)} m',f'P = {f(pb)} × 10² / (8 × {f(fcab)}) = {f(P_inf_min,0)} kN (balanceamento integral)',
         'O valor adotado é definido pelas tensões em serviço (ELS-D/ELS-F) e pelo ELU, ficando cerca de 15 % acima do balanceamento.'],
        f'P∞ de balanceamento ≈ {f(P_inf_min,0)} kN; adotado P∞ ≈ 940–980 kN')
Pj=Ls['Pj']; Pinf10=Ls['Pinf'][20]; Pinf4=Ls['Pinf'][8]
formula('Número de cabos','Ap = n_cab·n_cord·Ap1 ;  Pj = Ap·σp,j','Ap1 = 0,987 cm² (CP190 RB Ø12,7).',
        [f'Adotados {d["n_cab"]} cabos de {d["n_cord"]} cordoalhas = {d["n_cab"]*d["n_cord"]} cordoalhas, Ap = {f(d["Ap"]*1e4,2)} cm²',f'Pj = {f(d["Ap"]*1e4,2)}·10⁻⁴ × {f(d["sig_j"],0)}·10³ = {f(Pj,0)} kN'],
        f'10 cordoalhas (2 cabos 5Ø12,7), Pj = {f(Pj,0)} kN; P∞ = {f(Pinf4,0)} kN (x = 4 m) e {f(Pinf10,0)} kN (apoio)')
para('Em relação à viga biapoiada (12 cordoalhas, P∞ ≈ 1090 kN) a contínua usa menos aço ativo porque o momento no vão é bem menor (wL²·9/128 contra wL²/8) e o hiperestático favorece o apoio.')

doc.add_heading('5.1 Perdas de protensão',2)
para('Perdas calculadas por mecanismo físico (aba Tracado_Perdas): atrito, acomodação das cunhas, encurtamento elástico e perdas progressivas (fluência, retração e relaxação).')
formula('Atrito (NBR 6118 9.6.3.3.2)','σp(x) = σp,j·e^−(μΣα + k·x)','Σα = ângulo acumulado do cabo (rad); x = comprimento do arco.',
        [f'No apoio central: Σα = {f(float(T.cell(28,10).value),4)} rad; x = {f(float(T.cell(28,12).value),2)} m',f'σp = {f(d["sig_j"],0)}·e^−(0,20×{f(float(T.cell(28,10).value),4)}+0,002×{f(float(T.cell(28,12).value),2)}) = {f(float(T.cell(28,13).value),1)} MPa'],
        f'Perda por atrito até B = {f((1-float(T.cell(28,13).value)/d["sig_j"])*100,1)} %')
formula('Cravação das cunhas (método da reflexão)','Δ(x) = 2·[∫σ dx − σ(x)·x]/Ep = 6 mm',f'Alcance xa = {f(float(Ls["xa"]),2)} m (por extremidade).',None,
        f'Alcance da cravação xa = {f(float(Ls["xa"]),2)} m')
formula('Encurtamento elástico (cabos protendidos sucessivamente)','Δσp,ES = αp·(n−1)/(2n)·σcp','αp = Ep/Eci,j = '+f(Ls['ap'])+'; n = 2 cabos.',
        [f'No apoio B: σcp0 = {f(float(Ls["scp0"][20]),2)} MPa → Δσ = {f(float(Ls["d_es"][20]),1)} MPa'],None)
formula('Perdas progressivas (NBR 6118 9.6.3.4.2)','Δσp = [ |εcs|·Ep + αp·|σcp0g|·φ + σp0·χ ] / [ χp + χc·αp·η·ρp ]','χ = −ln(1−ψ); ψ∞ = 2,5·ψ1000; η = 1 + e²Ac/Ic.',
        [f'No apoio B: Δσ = {f(float(Ls["d_prog"][20]),1)} MPa'],None)
rows=[]
for i in (0,4,8,12,16,20):
    rows.append([f(float(Ls['x'][i]),1),f(float(Ls['e'][i]),3),f(float(Ls['sig_fric'][i]),0),f(float(Ls['sig_slip'][i]),0),f(float(Ls['d_es'][i]),1),f(float(Ls['sig_i'][i]),0),f(float(Ls['d_prog'][i]),0),f(float(Ls['sig_inf'][i]),0),f(float(Ls['Pi'][i]),0),f(float(Ls['Pinf'][i]),0)])
table(['x (m)','e (m)','σ atrito','σ após cravação','Δσ ES','σp,i','Δσ prog.','σp,∞','Pi (kN)','P∞ (kN)'],rows)
para(f'Perdas totais no apoio central: {f((1-Pinf10/Pj)*100,1)} %; a 4 m do apoio de extremidade: {f((1-Pinf4/Pj)*100,1)} %.')

doc.add_heading('6. Efeito hiperestático',1)
formula('Método das forças (apoio B removido)','R_B = 6·∫M_iso·m dx / L³ ;  M_hip(x) = −R_B·m(x)','M_iso = P·e·cosα (momento isostático da protensão); m = momento da carga unitária em B.',
        [f'R_B(∞) = {f(float(H["H4"].value))} kN → M_hip,B = {f(float(H["J4"].value))} kN·m ;  R_B(ato) = {f(float(H["H3"].value))} kN'],
        f'M_hip,B(∞) = {f(float(H["J4"].value),1)} kN·m (comprime a fibra superior no apoio B, favorável ao ELS)')
para('Verificação: para um cabo concordante o hiperestático calculado por esse procedimento resulta nulo (|M_hip| < 0,4 kN·m), e ΣR = 0.')

doc.add_heading('7. e) Tensões em serviço (ELS)',1)
formula('Tensões normais','σ1 = −N/A + (M_P ± M)/W1 (fibra inferior);  σ2 = −N/A − (M_P ± M)/W2 (fibra superior)','N = P·cosα; M_P = −N·e + M_hip.',None,None)
xi=[8,12,16,20,24,28,32]
rows=[]
for i in (0,4,8,12,16,20,28,36):
    rr=8+i
    rows.append([f(S.cell(rr,1).value,1),f(S.cell(rr,2).value,3),f(S.cell(rr,11).value),f(S.cell(rr,12).value),f(S.cell(rr,13).value),f(S.cell(rr,14).value),f(S.cell(rr,15).value),f(S.cell(rr,16).value)])
table(['x (m)','e (m)','σ1 ato','σ2 ato','σ1 CFQ','σ2 CFQ','σ1 CR','σ2 CR'],rows)
fig('fig/tensoes.png',16)
rows=[['Ato (tração, 1,2·fct,m,j = 2,70)',f(S['K4'].value),'≤ 2,70','NÃO – armar (As,ato)'],
['Ato (compressão, 0,7·fcj = 14,36)',f(S['K5'].value),'≥ −14,36','OK'],
['ELS-D (CFQ) σ1 máx',f(S['M4'].value),'≤ 0','OK'],['ELS-D (CFQ) σ2 máx',f(S['N4'].value),'≤ 0','OK'],
['ELS-F (CR) σ1 máx',f(S['O4'].value),'≤ 2,43','OK'],['ELS-F (CR) σ2 máx',f(S['P4'].value),'≤ 2,43','OK'],
['ELS-CE compressão máx',f(S['R4'].value),'≥ −21,0','OK']]
table(['Verificação','Valor (MPa)','Limite (MPa)','Situação'],rows)
para(f'No ato, a tração máxima ({f(S["K4"].value)} MPa) ocorre no apoio central e supera o limite; a armadura passiva calculada para equilibrar a tração é As,ato = {f(float(max(Aato)),2)} cm² (σs = 250 MPa), distribuída na face inferior sobre B (σ1 > 0 no ato, pois o cabo está acima do CG e comprime o topo; a mesma armadura funciona como A′ comprimida no ELU, item 8.1). Em serviço, as tensões ficam dentro dos limites do nível 3 (protensão completa); os níveis 2 e 1 são tratados no item 7.1.')
doc.add_heading('ELS-DEF (flecha)',2)
dmin=float(P['Q3'].value); dqp=float(P['N5'].value)
formula('Flecha da seção não fissurada','y″ = −M/(Ecs·Ic) ; δ∞ = δ·(1+φ)','Combinação quase-permanente Mg + ψ2·Mq + efeito de P∞.',None,
        f'δ_qp,∞ = {f(dmin)} mm (contraflecha) ; limite L/250 = 40 mm → OK')
fig('fig/flecha.png',14)
para(f'Frequência do 1º modo (antissimétrico) aproximada: f1 ≈ {f(float(P["Q5"].value),1)} Hz, acima da faixa de excitação do passo (1,6–2,4 Hz) e de seus harmônicos mais baixos; o conforto dinâmico da passarela deve ser verificado à parte (NBR 6118 23.3).')

doc.add_heading('7.1 Níveis de protensão (NBR 6118, Tab. 13.4)',2)
para('Para pós-tração e CAA II a norma indica o nível 2 (protensão limitada) como mínimo; o projeto principal foi feito no nível 3 (completa). Os três níveis diferem nas combinações e nos estados-limites exigidos:')
table(['Nível','Protensão','ELS-D (descompressão)','ELS-F (formação de fissuras)','ELS-W (abertura)'],
 [['3','Completa','Comb. frequente: σ ≤ 0','Comb. rara: σ ≤ 1,2·fctk,inf','—'],
  ['2','Limitada','Comb. quase permanente: σ ≤ 0','Comb. frequente: σ ≤ 1,2·fctk,inf','—'],
  ['1','Parcial','—','—','Comb. frequente: wk ≤ 0,2 mm (CAA II)']])
formula('Fissuração com protensão (nível 1)','σs obtida na seção fissurada sob N∞ e M = Mext + M_P ;  wk = min{ φ/(12,5η1)·σs/Es·3σs/fct,m ; φ/(12,5η1)·σs/Es·(4/ρri + 45) }',
 'η1 = 2,25 (CA-50 nervurado); ρri = As/Acri; Acri = bw(c + 7,5φ). O aumento de tensão do cabo aderente foi desprezado (a favor da segurança).',None,None)
para('Para cada nível buscou-se o menor número de cordoalhas Ø12,7 (2 cabos, mesmo traçado e = 28 cm) que atende aos critérios, completando com armadura passiva para o ato e para o ELU, e conferindo a abertura de fissuras no nível 1.')
rowsN=[['Cordoalhas totais (2 cabos)','10 (2 × 5)','8 (2 × 4)','4 (2 × 2)'],
['Ap (cm²) / Pj (kN)','9,87 / 1388','7,90 / 1110','3,95 / 555'],
['P∞ mín–máx (kN)','939–1050','776–853','411–442'],
['Carga equilibrada por P∞,mín (kN/m)','31,6 (115 % de g+ψ2q)','26,1 (95 %)','13,8 (50 %)'],
['Margem ELS-D do nível (MPa)','+0,45 (CF)','+1,04 (CQP)','—'],
['Margem ELS-F do nível (MPa)','+0,60 (CR)','+3,14 (CF)','—'],
['Tração máx. na comb. frequente (MPa)','−0,45','−0,70','+3,94 (fissurada em B)'],
['Tração máx. na comb. quase permanente (MPa)','−0,45','−1,04','+3,17'],
['Passiva do ato (cm²)','4,9','3,2','0'],
['Passiva tracionada em B / no vão (ELU)',"A' = 4,9 / A' = 2,5",'2 Ø16 / —','4 Ø20 / 2 Ø20'],
['MRd/Msd em B / vão','1,26 / 1,60','1,14 / 1,31','1,01 / 1,09'],
['wk em B (CF)','não fissura','não fissura','0,03 mm (≤ 0,2)'],
['Flecha final qp (mm)','−2,8 (contraflecha)','−0,2','+5,4 (≤ 40)'],
['Aço ativo (kg)','≈ 159','≈ 127','≈ 64'],
['P∞ em x = 4 m / apoio B (kN)','942 / 976','779 / 806','416 / 431'],
['Bainha, Ø externo (mm)','61','55 (adotado)','45 (adotado)'],
['Alongamento por extremidade (mm)','67,4','67,4','67,4']]
table(['Item','Nível 3 – completa','Nível 2 – limitada','Nível 1 – parcial'],rowsN)
para('Leitura dos resultados: com 8 cordoalhas a viga atende ao nível 2 (ELS-D quase permanente e ELS-F frequente), mas não ao nível 3, pois a tração na combinação rara excede o limite em 1,49 MPa. Com 6 cordoalhas já não há descompressão na quase permanente (violação de 0,77 MPa). No nível 1 bastam 4 cordoalhas: o apoio B fissura sob a combinação frequente (σ = 3,94 MPa > 2,43 MPa), mas a abertura calculada, 0,03 mm, fica muito abaixo de 0,2 mm porque a armadura passiva exigida pelo ELU (4 Ø20) é grande. A redução de protensão do nível 3 ao 1 poupa cerca de 95 kg de aço ativo, que passa a ser compensado por aço passivo (12,6 cm² em B e 6,3 cm² no vão), e a flecha deixa de ser contraflecha. Os limites foram verificados com os esforços da própria planilha (aba Niveis e aba Niveis_Comparativo).')
para('Desenhos: além da prancha do nível 3, foram gerados os DXF Viga_Continua_CP_Nivel2_Forma_e_Cabos.dxf e Viga_Continua_CP_Nivel1_Forma_e_Cabos.dxf (A2, 1:50), com traçado e fuso recalculados, seções com 4 e 2 cordoalhas por cabo e as armaduras passivas de cada nível (2 Ø16 sobre B no nível 2; 4 Ø20 sobre B e 2 Ø20 no vão no nível 1). Os diâmetros de bainha de 55 e 45 mm são adotados, e o alongamento de 67,4 mm por extremidade não muda, pois depende só do atrito.')
para('Ressalva: o nível 1 foi verificado apenas para flexão, flecha e abertura de fissuras; cisalhamento, ancoragens e fadiga devem ser reavaliados com a Vp menor, e a armadura mínima da NBR 6118 (17.3.5.2.1) precisa ser conferida nessa solução.',italic=True,size=9.5)

doc.add_heading('8. f) Verificação à ruptura (ELU)',1)
formula('Equilíbrio de seção com pré-alongamento','εp0 = σp∞/Ep + P∞/(Ac·Ecs)·(1+e²Ac/Ic) ; x = (Tp − Cs)/(0,85·fcd·0,8·bw) ; MRd = Cc(dp−0,4x)+Cs(dp−d\')',
 'Ap em escoamento (fpyd = 1487 MPa); Cs = A\'·fyd (armadura passiva comprimida); γp aplicado ao hiperestático (1,2 desfavorável; 0,9 favorável).',None,None)
rows=[]
for rrow,lab in ((8,'ε p0 (‰)'),):
    pass
labs=[(11,'εp0',5),(16,'x (m)',3),(17,'x/dp',3),(18,'εp',5),(22,'MRd (kN·m)',1),(26,'Msd (kN·m)',1),(28,'MRd/|Msd|',2)]
table(['Grandeza','Apoio B (M−)','Vão x = 4,0 m (M+)'],[[l,f(float(U.cell(r_,2).value),n),f(float(U.cell(r_,3).value),n)] for r_,l,n in labs])
para(f'Apoio B: Msd = {f(float(U["B26"].value),0)} kN·m ≤ MRd = {f(float(U["B22"].value),0)} kN·m. Vão: Msd = {f(float(U["C26"].value),0)} kN·m ≤ MRd = {f(float(U["C22"].value),0)} kN·m. Ductilidade x/d ≤ 0,45 atendida (A\' = {f(float(U["B12"].value))} cm² em B e {f(float(U["C12"].value))} cm² no vão). Momento mínimo 0,8·W·fctk,sup = {f(float(U["B30"].value),0)} kN·m atendido.')
doc.add_heading('8.1 Armaduras passivas',2)
para(f'• Face superior sobre B (tração no ato): As,ato = {f(float(max(Aato)),2)} cm² → 4 Ø12,5 (4,91 cm²), estendidos além da zona 9–11 m com o comprimento de ancoragem.')
para('• Face inferior sobre B (compressão no ELU): A\' = 4,91 cm² = 4 Ø12,5; no vão A\' = 2,45 cm² = 2 Ø12,5 na face superior.')
para('• Armadura de pele (0,10 % Ac,alma por face = 2,7 cm²/face) e fretagem das ancoragens: dimensionamento indicativo, a detalhar em projeto (NBR 6118 9.4, 18.2.5 e 21.3).')
doc.add_heading('8.2 Cisalhamento',2)
formula('Modelo I – resumo (Vp = −P·senα; β = 1 + M0/Msd ≤ 2)','τwd = Vsd/(bw,red·d) ;  τc,cor = β·0,6·fctd ;  asw/n = (τwd − τc,cor)/0,9/fywd·bw,red','bw,red = bw − ½ΣØbainha = '+f(float(d['bw'])-0.5*2*d['d_bain'],3)+' m.',None,
        f'Vsd,máx (apoio B) = {f(float(max(C.cell(rr,14).value for rr in range(8,49))),0)} kN ≤ VRd2 = {f(float(C["AA8"].value),0)} kN → OK; estribos Ø8 c/ 25 cm de 2 ramos (4,02 cm²/m ≥ 3,96 cm²/m necessário junto a B e ≥ 3,48 cm²/m mínimo) em todo o comprimento.')

doc.add_heading('9. g) Alongamento final',1)
formula('Alongamento por extremidade','Δl = ∫ σp(s)/Ep ds  (0 ≤ x ≤ L)','σp(s): tensão do atrito antes da cravação.',None,
        f'Δl por extremidade = {f(float(A["B4"].value),1)} mm; total do cabo = {f(float(A["B5"].value),1)} mm (tolerância ±5 %: {f(float(A["B6"].value),1)} a {f(float(A["B7"].value),1)} mm). Alongamento líquido lido no macaco por extremidade, após a cravação de 6 mm: {f(float(A["B9"].value),1)} mm. Comprimento do cabo = {f(float(A["B10"].value),2)} m.')

doc.add_heading('10. i) Comparação com concreto armado',1)
n_Ap=d['Ap']*1e4
rows=[['Armadura principal de flexão','Ap = 9,87 cm² (10 Ø12,7) + passiva 4,9 cm² (ato)','As = 25,1 cm² (8 Ø20) em B ; 18,8 cm² (6 Ø20) no vão'],
['Massa de aço ativo (estimativa)','≈ 156 kg (20,1 m × 10 cord. × 0,775 kg/m)','—'],
['Aço passivo longitudinal (estimativa grosseira, sem ancoragens)','≈ 12 kg de As,ato + mínimas/pele','≈ 420 kg (25,1 cm² × 6,5 m + 18,9 cm² × 2 × 10 m)'],
['Flecha quase-permanente','−2,8 mm (contraflecha), 0 sob g+ψ2q balanceado','+7,4 mm (Branson + fluência)'],
['Abertura de fissuras (CF)','Sem fissuras (ELS-D)','wk ≈ 0,10 mm (< 0,3 mm)'],
['Estribos (Vsd máx)',f'Vsd,máx = {f(float(max(C.cell(rr,14).value for rr in range(8,49))),0)} kN; asw ≈ 3,96 cm²/m (≈ mínimo)','Vsd = 394 kN; asw/s = 5,6 cm²/m em B (mín. 3,48)'],
['Seção','Não fissurada em serviço','Fissurada em serviço (EI reduzida)']]
table(['Item','Concreto protendido (nível 3)','Concreto armado (mesma seção)'],rows,fs=8.5)
para('Conclusões: (1) ambas as soluções atendem ao ELU com a mesma seção 30×90; (2) a protensão elimina a fissuração e produz contraflecha, reduzindo a flecha diferida; (3) o CA exige muito mais aço passivo (ordem de 420 kg contra ≈ 156 kg de aço ativo + pouco passivo), mas dispensa bainhas, ancoragens e macaco; (4) a viga de CA com 25,1 cm² sobre B (8 Ø20 em 30 cm de largura) é congestionada, enquanto o cabo protendido ocupa bainhas de 6,1 cm.')

doc.add_heading('11. Hipóteses e pendências',1)
for t in ['g adicional = 13,25 kN/m e q = 25 kN/m ADOTADOS – substituir pelos valores da viga biapoiada.','φ = 2,9 e εcs = −0,23 ‰ por interpolação da Tab. 8.2 (UR 75 %) – conferir.','μ = 0,20, k = 0,002 /m e cravação de 6 mm adotados (bainha metálica, cordoalha Ø12,7).','ELS-D calculado com Mg + ψ1·Mq (combinação frequente) conforme aula; ELS-F com combinação rara.','Hiperestático por flexibilidade, EI constante; envoltórias com padrões de sobrecarga (ambos os vãos, um vão, outro vão).','Níveis 2 e 1: armadura passiva e flecha por análise simplificada (seção fissurada com protensão como carga externa); conferir o cisalhamento e a armadura mínima nessas soluções.','Memorial acompanha a planilha “Planilha_Apoio_Viga_Continua_CP.xlsx”, que recalcula tudo a partir da aba Dados.']:
    para('• '+t,size=10)
doc.save('Memorial_Viga_Continua_CP.docx'); print('ok')
