from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
wb = Workbook()
NAVY='1F3864'; hf=Font(bold=True,color='FFFFFF'); hfill=PatternFill('solid',fgColor=NAVY)
yel=PatternFill('solid',fgColor='FFF2CC'); grn=PatternFill('solid',fgColor='E2EFDA'); sec=PatternFill('solid',fgColor='DCE6F1')
thin=Side(style='thin',color='BFBFBF'); box=Border(left=thin,right=thin,top=thin,bottom=thin)
ctr=Alignment(horizontal='center',vertical='center',wrap_text=True)

# ---- Parametros
p = wb.active; p.title='Parametros'
p['A1']='Parâmetros comuns (viga contínua 2 × 10 m, 30×90, C30, CAA II)'; p['A1'].font=Font(bold=True,size=13,color=NAVY)
par=[('L','Vão de cada tramo','m',10),('f','Flecha do cabo f = e_vão + e_sup/2','m',0.42),('pbal','Carga a equilibrar g + ψ2·q','kN/m',27.5),
     ('fptk','fptk (CP190 RB)','MPa',1900),('Ap1','Área de 1 cordoalha Ø12,7','cm²',0.987),('sj','σp,j / fptk','',0.74),
     ('Lcab','Comprimento do cabo','m',20.09),('mlin','Massa linear de 1 cordoalha','kg/m',0.793),('ft','Limite de tração 1,2·fctk,inf','MPa',2.43),('wlim','Abertura-limite (CAA II)','mm',0.2)]
for i,h in enumerate(['Símbolo','Descrição','Unid.','Valor']): 
    c=p.cell(3,i+1,h); c.font=hf; c.fill=hfill; c.alignment=ctr
for r,(k,d,u,v) in enumerate(par,start=4):
    p.cell(r,1,k); p.cell(r,2,d); p.cell(r,3,u); c=p.cell(r,4,v); c.fill=yel; c.border=box
p.column_dimensions['A'].width=10; p.column_dimensions['B'].width=44; p.column_dimensions['C'].width=8; p.column_dimensions['D'].width=12
P={k:f'Parametros!$D${r}' for r,(k,*_) in enumerate(par,start=4)}

# ---- Criterios
c=wb.create_sheet('Criterios')
c['A1']='Níveis de protensão - NBR 6118, Tab. 13.4 (pós-tração, CAA II)'; c['A1'].font=Font(bold=True,size=13,color=NAVY)
rows=[['Nível','Protensão','ELS-D (descompressão)','ELS-F (formação de fissuras)','ELS-W (abertura de fissuras)'],
['3','Completa','Comb. frequente: σ ≤ 0','Comb. rara: σ ≤ 1,2·fctk,inf','não exigido'],
['2','Limitada','Comb. quase permanente: σ ≤ 0','Comb. frequente: σ ≤ 1,2·fctk,inf','não exigido'],
['1','Parcial','não exigido','não exigido','Comb. frequente: wk ≤ 0,2 mm']]
for i,row in enumerate(rows):
    for j,v in enumerate(row):
        cell=c.cell(3+i,j+1,v); cell.border=box; cell.alignment=ctr
        if i==0: cell.font=hf; cell.fill=hfill
c['A8']='Nível 2 é o mínimo indicado para pós-tração em CAA II. CF = combinação frequente (CFQ nas aulas), CQP = quase permanente, CR = rara.'; c['A8'].font=Font(italic=True,size=9)
for col,w in zip('ABCDE',(8,12,34,34,34)): c.column_dimensions[col].width=w

# ---- Comparativo
s = wb.create_sheet('Comparativo',0)
s['A1']='Comparativo dos níveis de protensão - mesma seção, traçado e = 28 cm'; s['A1'].font=Font(bold=True,size=13,color=NAVY)
s['A2']='Amarelo = entrada; verde = calculado por fórmula ou vindo do motor de cálculo (valores fixos, mesma metodologia da planilha de apoio).'; s['A2'].font=Font(italic=True,size=9)
for j,h in enumerate(['Item','Unid.','Nível 3 - completa','Nível 2 - limitada','Nível 1 - parcial'],start=1):
    x=s.cell(4,j,h); x.font=hf; x.fill=hfill; x.alignment=ctr
R=[ # label, unit, n3, n2, n1, kind  (in=entrada, f=formula, v=valor, t=texto)
('Cordoalhas por cabo (2 cabos)','',5,4,2,'in'),
('Cordoalhas totais Ø12,7','','=2*C5','=2*D5','=2*E5','f0'),
('Ap','cm²',f'=C6*{P["Ap1"]}',f'=D6*{P["Ap1"]}',f'=E6*{P["Ap1"]}','f2'),
('Pj = σp,j·Ap','kN',f'={P["sj"]}*{P["fptk"]}*C7/10',f'={P["sj"]}*{P["fptk"]}*D7/10',f'={P["sj"]}*{P["fptk"]}*E7/10','f0'),
('P∞ mínimo ao longo do cabo','kN',939,776,411,'v0'),
('P∞ máximo ao longo do cabo','kN',1050,853,442,'v0'),
('Carga equilibrada 8·f·P∞,mín/L²','kN/m',f'=8*{P["f"]}*C9/{P["L"]}^2',f'=8*{P["f"]}*D9/{P["L"]}^2',f'=8*{P["f"]}*E9/{P["L"]}^2','f1'),
('Fração de g+ψ2·q equilibrada','%',f'=C11/{P["pbal"]}*100',f'=D11/{P["pbal"]}*100',f'=E11/{P["pbal"]}*100','f0'),
('Tração máxima na comb. frequente','MPa',-0.45,-0.70,3.94,'v2'),
('Margem ELS-D do critério do nível','MPa',0.45,1.04,'n/a','v2'),
('Margem ELS-F do critério do nível','MPa',0.60,3.14,'n/a','v2'),
('Seção fissura na comb. frequente?','', '=IF(C13>'+P['ft']+',"sim","não")','=IF(D13>'+P['ft']+',"sim","não")','=IF(E13>'+P['ft']+',"sim (apoio B)","não")','t'),
('Atende ao nível 3?','','sim','não (rara excede 1,49 MPa)','não','t'),
('Atende ao nível 2?','','sim','sim','não (quase permanente)','t'),
('Armadura passiva do ato, face inferior sobre B (σs = 250 MPa)','cm²',4.9,3.2,0,'v1'),
('Passiva no ELU no apoio B','', "A' = 4,9 cm² (compressão)",'2 Ø16 = 4,0 cm²','4 Ø20 = 12,6 cm²','t'),
('Passiva no ELU no vão','', "A' = 2,5 cm² (compressão)",'não necessária','2 Ø20 = 6,3 cm²','t'),
('MRd/Msd no apoio B','',1.26,1.14,1.01,'v2'),
('MRd/Msd no vão','',1.60,1.31,1.09,'v2'),
('wk na comb. frequente (apoio B)','mm','não fissura','não fissura',0.03,'v2'),
('wk ≤ limite?','','—','—',f'=IF(E24<={P["wlim"]},"sim","não")','t'),
('Flecha final quase permanente (+ para baixo)','mm',-2.8,-0.2,5.4,'v1'),
('Massa de aço ativo','kg',f'=C6*{P["Lcab"]}*{P["mlin"]}',f'=D6*{P["Lcab"]}*{P["mlin"]}',f'=E6*{P["Lcab"]}*{P["mlin"]}','f0'),
('P∞ em x = 4 m','kN',942,779,416,'v0'),
('P∞ no apoio central B','kN',976,806,431,'v0'),
('Diâmetro externo da bainha (níveis 2 e 1: adotado)','mm',61,55,45,'v0'),
('Alongamento por extremidade (depende só do atrito)','mm',67.4,67.4,67.4,'v1'),
('Desenho DXF 1:50 (A2)','','Viga_Continua_CP_Forma_e_Cabos.dxf','Viga_Continua_CP_Nivel2_Forma_e_Cabos.dxf','Viga_Continua_CP_Nivel1_Forma_e_Cabos.dxf','t'),
('Tração máxima na comb. quase permanente','MPa',-0.45,-1.04,3.17,'v2'),
]
for k,(lab,un,a,b,d,kind) in enumerate(R):
    r=5+k
    s.cell(r,1,lab).border=box; s.cell(r,2,un).border=box
    for j,v in enumerate((a,b,d),start=3):
        x=s.cell(r,j,v); x.border=box; x.alignment=ctr
        if kind=='in': x.fill=yel
        elif kind!='t': x.fill=grn
        if kind[0] in 'fv' and len(kind)==2: x.number_format='0.'+'0'*int(kind[1]) if int(kind[1])>0 else '0'
s.column_dimensions['A'].width=46; s.column_dimensions['B'].width=8
for col in 'CDE': s.column_dimensions[col].width=26
s.freeze_panes='C5'

# ---- Notas
n=wb.create_sheet('Notas')
notes=['Com 8 cordoalhas a viga atende ao nível 2, mas não ao 3: a tração na combinação rara excede o limite em 1,49 MPa.',
'Com 6 cordoalhas já não há descompressão na quase permanente (violação de 0,77 MPa).',
'Nível 1: o apoio B fissura sob a combinação frequente (3,94 MPa > 2,43 MPa), mas wk = 0,03 mm, abaixo de 0,2 mm, porque a armadura passiva do ELU (4 Ø20) é grande.',
'Fissuração calculada na seção fissurada com a protensão como carga externa; o acréscimo de tensão do cabo aderente foi desprezado.',
'Cisalhamento, ancoragens e armadura mínima não foram reavaliados para as soluções dos níveis 1 e 2.',
'g adicional = 13,25 kN/m e q = 25 kN/m seguem como valores adotados, a confirmar com a viga biapoiada.',
'Diâmetros de bainha dos níveis 2 e 1 (55 e 45 mm) são adotados e devem ser confirmados com o fornecedor.',
'Valores fixos vêm de Planilha_Apoio_Viga_Continua_CP.xlsx (abas Niveis e Niveis_Comparativo).']
n['A1']='Notas e ressalvas'; n['A1'].font=Font(bold=True,size=13,color=NAVY)
for i,t in enumerate(notes,start=3):
    n.cell(i,1,'• '+t).alignment=Alignment(wrap_text=True,vertical='top')
n.column_dimensions['A'].width=120
wb.save('Niveis_de_Protensao.xlsx')
