import sys; sys.path.insert(0,'.')
from analysis import *
import numpy as np
d=final_design(); r,m,Aato,AscB,Ascs=evaluate_design(d); fu=fuso(d,r)
S=50.0                      # escala de plotagem 1:50 (1 unid. = 1 mm real)
SEC=5.0                     # ampliação das seções (1:50 -> 1:10)
out=[]; 
def w(code,val): out.append(f'{code}\n{val}')
def ent(kind,layer,*pairs,color=None):
    w(0,kind); w(8,layer)
    if color is not None: w(62,color)
    for c,v in pairs: w(c,v)
def line(layer,x1,y1,x2,y2,color=None): ent('LINE',layer,(10,x1),(20,y1),(30,0),(11,x2),(21,y2),(31,0),color=color)
def poly(layer,pts,closed=False,color=None):
    w(0,'POLYLINE'); w(8,layer); w(66,1); w(70,1 if closed else 0)
    if color is not None: w(62,color)
    for (x,y) in pts: w(0,'VERTEX'); w(8,layer); w(10,x); w(20,y); w(30,0)
    w(0,'SEQEND'); w(8,layer)
def circle(layer,x,y,rad,color=None): ent('CIRCLE',layer,(10,x),(20,y),(30,0),(40,rad),color=color)
import unicodedata
def asc(s):
    s=s.replace('Ø','%%c').replace('∞','inf').replace('–','-').replace('×','x').replace('µ','u').replace('²','2').replace('≥','>=').replace('≤','<=').replace('°','%%d').replace('±','%%p').replace('’',"'").replace("'",'`' if False else "'")
    s=''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn')
    return s.encode('ascii','replace').decode().replace('\n',' ')
def text(layer,x,y,h,s,rot=0,align='L',color=None):
    s=asc(s)
    pairs=[(10,x),(20,y),(30,0),(40,h),(1,s),(50,rot)]
    if align!='L':
        pairs+= [(72,{'C':1,'R':2}[align]),(11,x),(21,y),(31,0)]
    ent('TEXT',layer,*pairs,color=color)
def rect(layer,x1,y1,x2,y2,color=None): poly(layer,[(x1,y1),(x2,y1),(x2,y2),(x1,y2)],True,color)
def tri(layer,x,y,s):  poly(layer,[(x,y),(x-s/2,y-s),(x+s/2,y-s)],True)
T1,T2,T3,T4=2.0*S,2.5*S,3.5*S,7.0*S   # alturas de texto (mm no papel x escala)

# ---------------- geometria base
L=d['L']*1000; H=d['h']*1000; BW=d['bw']*1000; CG=H/2
X0,Y0=2800.0, 16300.0   # origem da elevação (extremo esq., face inferior), mm
fx=lambda x: X0+x*1000
fy=lambda e: Y0+CG-e*1000     # e positivo abaixo do CG

# ---------------- moldura A1 (841x594) em escala 1:50
SW,SH=594*S,420*S   # A2 paisagem
rect('MOLDURA',0,0,SW,SH); rect('MOLDURA',10*S,10*S,SW-10*S,SH-10*S)
# ---------------- ELEVAÇÃO
text('TEXTO',X0,Y0+H+2300,T3,'ELEVAÇÃO – VIGA CONTÍNUA PROTENDIDA 2 x 10,00 m          ESC. 1:50')
rect('CONTORNO',X0,Y0,X0+2*L,Y0+H)
line('EIXO',X0-500,Y0+CG,X0+2*L+500,Y0+CG)
for xs in (0,L,2*L):
    tri('APOIO',X0+xs,Y0,450); line('APOIO',X0+xs-350,Y0-450,X0+xs+350,Y0-450)
    line('EIXO',X0+xs,Y0-700,X0+xs,Y0+H+900)
# fuso limite (tracejado)
xs=np.asarray(r['x'])*1000
poly('FUSO',[(X0+a,Y0+CG-b*1000) for a,b in zip(xs,fu['lo'])])
poly('FUSO',[(X0+a,Y0+CG-b*1000) for a,b in zip(xs,fu['up'])])
# cabo resultante (parábolas, passo 100 mm)
xx=np.arange(0,2*L+1,100.0); ee,_=cable(d,xx/1000)
poly('CABO',[(X0+a,Y0+CG-b*1000) for a,b in zip(xx,ee)])
# limite de cobrimento
for s_ in (1,-1):
    line('COBRIM',X0,Y0+CG-s_*d['e_max']*1000,X0+2*L,Y0+CG-s_*d['e_max']*1000)
# ancoragens ativas (extremos)
for xs_ in (0,2*L):
    rect('CABO',X0+xs_-(0 if xs_==0 else 250),Y0+CG-150,X0+xs_+(250 if xs_==0 else 0),Y0+CG+150)
# estribos Ø8 c/25
for i in range(0,int(2*L/250)+1):
    xe=X0+i*250; line('ESTRIBO',xe,Y0+35,xe,Y0+H-35)
# armaduras passivas sobre B
bw_=7500; 
line('ARMAD',X0+L-2500,Y0+50,X0+L+2500,Y0+50,color=1)
text('TEXTO',X0+L-2400,Y0-190,T1,"4 Ø12,5 C/ 500 na face inferior (As,ato = 4,91 cm²; A' no ELU)")
# cotas
def dim(x1,x2,y,s,off=250):
    line('COTAS',x1,y,x2,y)
    for xx_ in (x1,x2): line('COTAS',xx_,y-off,xx_,y+off)
    text('COTAS',(x1+x2)/2,y+80,T1,s,align='C')
dim(X0,X0+L,Y0-1100,'1000'); 
text('COTAS',X0+L/2,Y0-1020,T1,'1000 cm',align='C')
dim(X0+L,X0+2*L,Y0-1100,''); text('COTAS',X0+1.5*L,Y0-1020,T1,'1000 cm',align='C')
dim(X0,X0+2*L,Y0-1700,''); text('COTAS',X0+L,Y0-1620,T1,'2000 cm',align='C')
# cotas de excentricidade
for xs_,lab in ((4000,'e = 28,0 cm (abaixo CG)'),(L,'e = 28,0 cm (acima CG)')):
    x_=X0+xs_; yv=float(cable(d,np.array([xs_/1000]))[0][0])*1000
    line('COTAS',x_+300,Y0+CG,x_+300,Y0+CG-yv); text('COTAS',x_+360,Y0+CG-yv/2,T1,lab)
text('TEXTO',X0+500,Y0+H+450,T1,'Traçado do cabo resultante (2 cabos 5 Ø12,5/12,7 – CP190 RB), linha tracejada = fuso limite, tracejado fino = e_max (cobrimento)')
text('TEXTO',X0+L,Y0+H+1100,T1,'Estribos Ø8 c/ 25 (2 ramos) em toda a viga',align='C')
# ---------------- TABELA de ordenadas do cabo (a cada 1 m)
TX,TY=X0,Y0-3200
text('TEXTO',TX-500,TY,T3,'ORDENADAS DO CABO RESULTANTE (cm) – y medido da face inferior; e + abaixo do CG')
cw=1000; rh=290
rows=[('x (m)',[i for i in range(0,21)]),]
xs_t=np.arange(0,21.0,1.0); e_t,_=cable(d,xs_t)
for j,(xv,ev) in enumerate(zip(xs_t,e_t)):
    cx=TX+j*cw-cw/2
    rect('TABELA',cx,TY-2*rh-rh-120,cx+cw,TY-120)
    line('TABELA',cx,TY-120-rh,cx+cw,TY-120-rh); line('TABELA',cx,TY-120-2*rh,cx+cw,TY-120-2*rh)
    text('TEXTO',cx+cw/2,TY-120-0.7*rh,T1,f'{xv:.0f}',align='C')
    text('TEXTO',cx+cw/2,TY-120-1.7*rh,T1,f'{ev*100:.1f}',align='C')
    text('TEXTO',cx+cw/2,TY-120-2.7*rh,T1,f'{45-ev*100:.1f}',align='C')
text('TEXTO',TX-600,TY-120-0.7*rh,T1,'x (m)',align='R'); text('TEXTO',TX-600,TY-120-1.7*rh,T1,'e (cm)',align='R'); text('TEXTO',TX-600,TY-120-2.7*rh,T1,'y (cm)',align='R')

# ---------------- SEÇÕES (ampliadas SEC x no modelo => 1:10 quando plotadas em 1:50)
def section(cx,cy,etas,title,ebar_bot=None,top_bars=0,bot_bars=0):
    s=SEC
    rect('CONTORNO',cx,cy,cx+BW*s,cy+H*s)
    rect('ESTRIBO',cx+35*s,cy+35*s,cx+(BW-35)*s,cy+(H-35)*s)
    ydp=cy+(CG-etas*1000)*s
    for dxx in (-45,45):
        circle('CABO',cx+(BW/2+dxx)*s,ydp,30.5*s)
        for k in range(5):
            ang=2*np.pi*k/5+0.3
            circle('CABO',cx+(BW/2+dxx)*s+11*s*np.cos(ang),ydp+11*s*np.sin(ang),6.35*s,color=1)
    for n,yb in ((top_bars,H-55),(bot_bars,55)):
        for k in range(n):
            xb=cx+(55+k*(BW-110)/max(n-1,1))*s
            circle('ARMAD',xb,cy+yb*s,6.25*s,color=3)
    text('TEXTO',cx+BW*s/2,cy+H*s+400,T2,title,align='C')
    text('TEXTO',cx+BW*s/2,cy-800,T1,f'y = {(CG-etas*1000)/10:.1f} cm da base',align='C')
    # cotas
    line('COTAS',cx,cy-300,cx+BW*s,cy-300); text('COTAS',cx+BW*s/2,cy-560,T1,'30',align='C')
    line('COTAS',cx+BW*s+250,cy,cx+BW*s+250,cy+H*s); text('COTAS',cx+BW*s+330,cy+H*s/2,T1,'90')
sy=4400.0
sx=X0
text('TEXTO',sx,sy+H*SEC+1700,T3,'SEÇÕES TRANSVERSAIS – ESC. 1:10 (desenhadas ampliadas 5x no modelo; cotas em cm)')
section(sx,sy,0.0,'S1 – ANCORAGEM (x = 0)')
section(sx+4200,sy,0.28,'S2 – VÃO (x = 4,0 m)',top_bars=2)
section(sx+8400,sy,-0.28,'S3 – APOIO CENTRAL (x = 10,0 m)',top_bars=0,bot_bars=4)
# ---------------- Quadro de dados
nx=15200.0
txt=['DADOS DO PROJETO',
 'Concreto C30 (fck = 30 MPa) – CAA II – cobrimento 3,5 cm',
 'Seção 30 x 90 cm; vãos 2 x 10,00 m',
 'Aço ativo: CP190 RB Ø12,7 – 2 cabos x 5 cordoalhas (Ap = 9,87 cm²)',
 'Pj = 1388 kN (0,74 fptk); P∞ = 942 kN (x = 4 m) / 976 kN (apoio central)',
 'Protensão simultânea pelas duas extremidades, pós-tração aderente',
 'Bainhas Ø61 mm (metálicas); atrito µ = 0,20; k = 0,002/m; cravação 6 mm',
 'Alongamento teórico por extremidade: 67,4 mm (total 134,8 mm, tol. ±5 %)',
 'Aço passivo CA-50: estribos Ø8 c/ 25; 4 Ø12,5 inf. sobre o apoio central (As,ato e A′ do ELU)',
 'Cargas: g = 20,0 kN/m (ADOTADA), q = 25,0 kN/m (ADOTADA) – confirmar',
 'Unidades: cotas em cm, exceto indicação. Desenho em mm no modelo, plotar em 1:50 (A2)']
for i,t in enumerate(txt):
    text('TEXTO',nx,sy+H*SEC+1700-i*(T2*1.5),T3 if i==0 else T2,t)
# legenda
lx,ly=15200.0,sy+800
leg=[('CABO','Cabo resultante / bainhas'),('FUSO','Fuso limite'),('COBRIM','e_max (cobrimento)'),('ESTRIBO','Estribos'),('ARMAD','Armadura passiva')]
for i,(ly_,t) in enumerate(leg):
    yy=ly-i*350; line(ly_,lx,yy,lx+1200,yy); text('TEXTO',lx+1400,yy-60,T1,t)
# carimbo
cbx,cby=SW-10*S-3800*1.0-10500,10*S
rect('MOLDURA',SW-10*S-11000,10*S,SW-10*S,10*S+3200)
text('TEXTO',SW-10*S-10800,10*S+2500,T3,'UnB – Concreto Armado e Protendido')
text('TEXTO',SW-10*S-10800,10*S+1800,T2,'VIGA CONTÍNUA PROTENDIDA 2 x 10 m – FORMA E TRAÇADO DOS CABOS')
text('TEXTO',SW-10*S-10800,10*S+1100,T2,'Prof. Li Chong Lee Bacelar de Castro')
text('TEXTO',SW-10*S-10800,10*S+450,T2,'Escala 1:50 (seções 1:10)      Data: 02/10/2026      Folha 01/01')

# ---------------- escrita
hdr=['0\nSECTION','2\nHEADER','9\n$ACADVER\n1\nAC1009','9\n$INSUNITS\n70\n4','9\n$LTSCALE\n40\n'+str(S),'9\n$EXTMIN\n10\n0\n20\n0','9\n$EXTMAX\n10\n'+str(SW)+'\n20\n'+str(SH),'0\nENDSEC']
tab=['0\nSECTION','2\nTABLES',
 '0\nTABLE\n2\nLTYPE\n70\n3',
 '0\nLTYPE\n2\nCONTINUOUS\n70\n0\n3\nSolid line\n72\n65\n73\n0\n40\n0.0',
 '0\nLTYPE\n2\nDASHED\n70\n0\n3\nDashed\n72\n65\n73\n2\n40\n18.0\n49\n12.0\n49\n-6.0',
 '0\nLTYPE\n2\nCENTER\n70\n0\n3\nCenter\n72\n65\n73\n4\n40\n40.0\n49\n24.0\n49\n-4.0\n49\n4.0\n49\n-4.0',
 '0\nENDTAB']
layers=[('MOLDURA',7,'CONTINUOUS'),('CONTORNO',7,'CONTINUOUS'),('EIXO',1,'CENTER'),('APOIO',7,'CONTINUOUS'),('FUSO',5,'DASHED'),('CABO',1,'CONTINUOUS'),('COBRIM',3,'DASHED'),('ESTRIBO',4,'CONTINUOUS'),('ARMAD',3,'CONTINUOUS'),('COTAS',2,'CONTINUOUS'),('TEXTO',7,'CONTINUOUS'),('TABELA',7,'CONTINUOUS')]
tab.append(f'0\nTABLE\n2\nLAYER\n70\n{len(layers)}')
for n,c,lt in layers: tab.append(f'0\nLAYER\n2\n{n}\n70\n0\n62\n{c}\n6\n{lt}')
tab+=['0\nENDTAB','0\nTABLE\n2\nSTYLE\n70\n1','0\nSTYLE\n2\nSTANDARD\n70\n0\n40\n0.0\n41\n1.0\n50\n0.0\n71\n0\n42\n2.5\n3\ntxt\n4\n','0\nENDTAB','0\nENDSEC']
body='\n'.join(out)
dxf='\n'.join(hdr+tab)+'\n0\nSECTION\n2\nENTITIES\n'+body+'\n0\nENDSEC\n0\nEOF\n'
open('Viga_Continua_CP_Forma_e_Cabos.dxf','w',encoding='cp1252',errors='replace').write(dxf)
print('ok',len(out))
