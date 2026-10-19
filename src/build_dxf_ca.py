import sys; sys.path.insert(0,'.')
from analysis import *
import numpy as np
d=final_design(); r,m,Aato,AscB,Ascs=evaluate_design(d)
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
    s=s.replace('Ø','%%c').replace('∞','inf').replace('–','-').replace('×','x').replace('µ','u').replace('²','2').replace('≥','>=').replace('≤','<=').replace('°','%%d').replace('±','%%p').replace('·','.').replace('≈','~').replace('’',"'").replace("'",'`' if False else "'")
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

# ================= DESENHO DE CONCRETO ARMADO =================
ext=r['ext']; xg=np.asarray(r['x'])*1000          # estações (mm), 0..20000 a cada 500
dd=0.82; fyd=500/1.15*1e3; fcd=d['fcd']*1e3; bw=d['bw']
Mneg=1.4*(ext['Mg']+ext['Mq_min']); Mpos=1.4*(ext['Mg']+ext['Mq_max'])
def MRd(n,phi=20):
    As=n*np.pi*(phi/20)**2*3.1416e-4*(phi/20)**0; As=n*(np.pi*(phi/1000)**2/4)
    xx=As*fyd/(0.68*fcd*bw); return As*fyd*(dd-0.4*xx)
M4=MRd(4); M6=MRd(6); M8=MRd(8)
fbd=2.25*1.0*1.0*d['fctd']*1e3/1e3       # MPa
lb=20/4*(500/1.15)/ (2.25*d['fctd'])/1000.0   # m  (phi/4 * fyd/fbd)
# pontos de corte (x em m)
def cross(xs,ys,level,start,end):
    for i in range(start,end):
        a,b=ys[i]-level,ys[i+1]-level
        if a*b<=0 and a!=b: return xs[i]+(xs[i+1]-xs[i])*(-a)/(b-a)
x_m=xg/1000
x_neg0=cross(x_m,Mneg,0.0,10,20)                    # Mneg = 0 no 1º vão (perto de 6 m)
x_neg4=cross(x_m,-Mneg,M4,12,20)                    # |Mneg| = MRd(4Ø20)
x_pos4a=cross(x_m,Mpos,M4,0,8); x_pos4b=cross(x_m,Mpos,M4,8,20)
al=dd
lbn_full=lb; lbn_min=max(0.3*lb,0.2,0.1)
c1=10-x_neg0+al+lbn_min          # N1: distância de B até a ponta (m)
c2=10-x_neg4+al+lb               # N2
a4=x_pos4a-al-lb; b4=x_pos4b+al+lb   # N4 início e fim (m), 1º vão
c1=np.ceil(c1*20)/20; c2=np.ceil(c2*20)/20; a4=np.floor(a4*20)/20; b4=np.ceil(b4*20)/20
print('lb',lb,'x_neg0',x_neg0,'x_neg4',x_neg4,'x_pos4',x_pos4a,x_pos4b,'N1',c1,'N2',c2,'N4',a4,b4,'M4,M6,M8',M4,M6,M8)
# 1ª camada y=53 mm; 2ª camada y=98 mm (c=35 + Ø8 + Ø20/2; 2ª camada com 25 mm livres)
Y1,Y2=53.0,98.0
# ---------------- moldura A2
SW,SH=594*S,420*S
rect('MOLDURA',0,0,SW,SH); rect('MOLDURA',10*S,10*S,SW-10*S,SH-10*S)
# ---------------- elevação
text('TEXTO',X0,Y0+H+2300,T3,'ELEVAÇÃO – VIGA CONTÍNUA EM CONCRETO ARMADO 2 x 10,00 m          ESC. 1:50')
rect('CONTORNO',X0,Y0,X0+2*L,Y0+H)
line('EIXO',X0-500,Y0+CG,X0+2*L+500,Y0+CG)
for xs in (0,L,2*L):
    tri('APOIO',X0+xs,Y0,450); line('APOIO',X0+xs-350,Y0-450,X0+xs+350,Y0-450)
    line('EIXO',X0+xs,Y0-700,X0+xs,Y0+H+900)
# estribos
cB=170.0; zB=1190.0
pos=[]
k=0
while L-zB-250*k>=300: pos.append(L-zB-250*k); k+=1
pos.append(50.0)
left=sorted(set(pos))
zone=[L+j*cB for j in range(-7,8)]
allp=sorted(set(left+zone+[2*L-p for p in left]))
for p in allp: line('ESTRIBO',X0+p,Y0+35,X0+p,Y0+H-35)
n_estr=len(allp)
# barras longitudinais
cov=35.0
def hbar(x1,x2,y,layer='ARMAD',color=None): line(layer,X0+x1,Y0+y,X0+x2,Y0+y,color=color)
# N1: 4 Ø20 sup., 1ª camada, sobre B
hbar(L-c1*1000,L+c1*1000,H-Y1,'ARMAD')
# N2: 4 Ø20 sup., 2ª camada
hbar(L-c2*1000,L+c2*1000,H-Y2,'ARMAD')
# N3: 4 Ø20 inf. contínuas em cada vão, com gancho 90° nas extremidades e traspasse de 0,70 m sobre B
ov=350.0
hbar(cov,L+ov,Y1,'ARMAD'); line('ARMAD',X0+cov,Y0+Y1,X0+cov,Y0+Y1+160)
hbar(L-ov,2*L-cov,Y1+14,'ARMAD2'); line('ARMAD2',X0+2*L-cov,Y0+Y1+14,X0+2*L-cov,Y0+Y1+174)
# N4: 2 Ø20 inf., 2ª camada, cortadas
hbar(a4*1000,b4*1000,Y2,'ARMAD'); hbar(2*L-b4*1000,2*L-a4*1000,Y2,'ARMAD2')
# N5: 2 Ø12,5 porta-estribos
hbar(cov,2*L-cov,H-49,'ARMAD3')
# rótulos
text('TEXTO',X0+L-c1*1000,Y0+H+450,T1,f'N1  4 Ø20 sup. – {c1*1000/10:.0f} cm de cada lado de B (C = {2*c1*100:.0f} cm)')
text('TEXTO',X0+L-c2*1000,Y0+H+250,T1,f'N2  4 Ø20 sup. (2ª camada) – {c2*1000/10:.0f} cm de cada lado de B (C = {2*c2*100:.0f} cm)')
text('TEXTO',X0+500,Y0-900,T1,f'N3  4 Ø20 inf. por vão, gancho 90° nos apoios extremos e traspasse de 70 cm sobre B')
text('TEXTO',X0+a4*1000,Y0-1250,T1,f'N4  2 Ø20 inf. (2ª camada), de {a4*100:.0f} a {b4*100:.0f} cm de cada extremo')
text('TEXTO',X0+L/2,Y0+H+1100,T1,'N5  2 Ø12,5 porta-estribos (construtivos), em todo o comprimento',align='C')
text('TEXTO',X0+L/2,Y0+H+850,T1,'N6  Ø8 c/ 25 (2 ramos) fora da zona de apoio',align='C')
text('TEXTO',X0+L+1300,Y0+H+850,T1,'N6  Ø8 c/ 17 (2 ramos) a 1,19 m de cada lado de B')
# cotas
def dim(x1,x2,y,s,off=250):
    line('COTAS',x1,y,x2,y)
    for xx_ in (x1,x2): line('COTAS',xx_,y-off,xx_,y+off)
    text('COTAS',(x1+x2)/2,y+80,T1,s,align='C')
dim(X0,X0+L,Y0-1700,'1000 cm'); dim(X0+L,X0+2*L,Y0-1700,'1000 cm'); dim(X0,X0+2*L,Y0-2300,'2000 cm')
dim(X0+L-c1*1000,X0+L+c1*1000,Y0-2900,f'N1 = {2*c1*100:.0f} cm')
dim(X0+L-c2*1000,X0+L+c2*1000,Y0-3300,f'N2 = {2*c2*100:.0f} cm')
dim(X0+a4*1000,X0+b4*1000,Y0-3700,f'N4 = {(b4-a4)*100:.0f} cm')
dim(X0+2*L-b4*1000,X0+2*L-a4*1000,Y0-3700,f'N4 = {(b4-a4)*100:.0f} cm')
# ---------------- diagrama de momentos de cálculo e cortes
by=Y0-5900.0; esc=1.2                      # 1 kN·m = 1,2 mm
text('TEXTO',X0,by+1500,T3,'ENVOLTÓRIA DE MOMENTOS DE CÁLCULO Md = 1,4·(Mg + Mq) E CAPACIDADE DAS BARRAS (kN·m; tração para o lado do traço)')
line('EIXO',X0,by,X0+2*L,by)
poly('MOMENTO',[(X0+a,by-m*esc) for a,m in zip(xg,Mneg)])      # negativo para cima? sinal: Mneg<0 -> abaixo; invertido p/ tração em cima
poly('MOMENTO',[(X0+a,by-m*esc) for a,m in zip(xg,Mpos)])
for lvl,lab in ((M4,'MRd 4 Ø20 = %.0f'%M4),(M6,'MRd 6 Ø20 = %.0f'%M6)):
    line('CAP',X0,by-lvl*esc,X0+2*L,by-lvl*esc); text('TEXTO',X0+2*L+100,by-lvl*esc-40,T1,lab)
for lvl,lab in ((M4,'MRd 4 Ø20 = %.0f'%M4),(M8,'MRd 8 Ø20 = %.0f'%M8)):
    line('CAP',X0,by+lvl*esc,X0+2*L,by+lvl*esc); text('TEXTO',X0+2*L+100,by+lvl*esc-40,T1,lab)
for xs_ in (0,L,2*L): line('EIXO',X0+xs_,by-700,X0+xs_,by+1000)
for xv,mv,lab in ((L,Mneg[20],'Md = %.1f'%Mneg[20]),(4000,Mpos[8],'Md = +%.1f'%Mpos[8])):
    text('TEXTO',X0+xv+80,by-mv*esc+(-130 if mv<0 else 60),T1,lab)
for xv in (x_neg0,x_neg4,x_pos4a,x_pos4b):
    line('COTAS',X0+xv*1000,by-150,X0+xv*1000,by+150)
text('TEXTO',X0+500,by-1000,T1,'Cortes: ponto onde o momento resistente das barras que ficam iguala Md, deslocado de a_l = d = 82 cm e acrescido de lb,nec (decalagem e ancoragem, NBR 6118 item 18.3.2.3).')
text('TEXTO',X0+500,by-1200,T1,f'lb = {lb*100:.0f} cm (Ø20, CA-50, C30, boa aderência, fbd = {2.25*d["fctd"]:.2f} MPa); lb,nec mínimo = 20 cm.')
# ---------------- seções transversais 1:10 (5x no modelo)
s=SEC
def section(cx,cy,title,top20=(),bot20=(),top125=0,stir='Ø8'):
    rect('CONTORNO',cx,cy,cx+BW*s,cy+H*s)
    rect('ESTRIBO',cx+35*s,cy+35*s,cx+(BW-35)*s,cy+(H-35)*s)
    xs4=[53+k*(BW-106)/3 for k in range(4)]
    def put(layer_y,idxs,top):
        for k in idxs:
            yy=(H-layer_y) if top else layer_y
            circle('ARMAD',cx+xs4[k]*s,cy+yy*s,10*s,color=3)
    put(Y1,top20[0] if top20 else [],True); put(Y2,top20[1] if top20 else [],True)
    put(Y1,bot20[0] if bot20 else [],False); put(Y2,bot20[1] if bot20 else [],False)
    for n in range(top125):
        xb=[49.25,BW-49.25][n]; circle('ARMAD',cx+xb*s,cy+(H-49.25)*s,6.25*s,color=3)
    text('TEXTO',cx+BW*s/2,cy+H*s+400,T2,title,align='C')
    line('COTAS',cx,cy-300,cx+BW*s,cy-300); text('COTAS',cx+BW*s/2,cy-560,T1,'30',align='C')
    line('COTAS',cx+BW*s+250,cy,cx+BW*s+250,cy+H*s); text('COTAS',cx+BW*s+330,cy+H*s/2,T1,'90')
sy=2700.0; sx=X0
text('TEXTO',sx,sy+H*SEC+1700,T3,'SEÇÕES TRANSVERSAIS – ESC. 1:10 (desenhadas ampliadas 5x no modelo; cotas em cm)')
allk=[0,1,2,3]
section(sx,sy,'S1 – x = 0,5 m (junto ao apoio A)',bot20=(allk,[]),top125=2)
section(sx+4200,sy,'S2 – VÃO (x = 4,0 m)',bot20=(allk,[1,2]),top125=2)
section(sx+8400,sy,'S3 – APOIO CENTRAL (x = 10,0 m)',top20=(allk,allk),bot20=(allk,allk))
text('TEXTO',sx,sy-1000,T1,'S1: 4 Ø20 (N3) + 2 Ø12,5 (N5), estribos Ø8 c/ 25.   S2: 6 Ø20 (4 N3 + 2 N4), 2 Ø12,5 (N5).   S3: 8 Ø20 sup. (N1 + N2); inf. 4 Ø20 + 4 Ø20 em traspasse (N3), estribos Ø8 c/ 17.')
# ---------------- quadro de dados
nx=15000.0; ny=sy+H*SEC+1700
txt=['DADOS DO PROJETO',
 'Concreto C30 (fck = 30 MPa) – CAA II – cobrimento nominal 3,5 cm (ao estribo)',
 'Seção 30 x 90 cm; vãos 2 x 10,00 m; d = 82 cm (duas camadas)',
 'Aço CA-50 (fyd = 435 MPa); estribos Ø8 de 2 ramos',
 'Md,B = 787,5 kN·m (As,calc = 25,2 cm²; adotado 8 Ø20 = 25,13 cm²)',
 'Md,vão = 528,5 kN·m (As,calc = 16,1 cm²; adotado 6 Ø20 = 18,85 cm²)',
 'Vsd,B = 394 kN: asw = 5,62 cm²/m (Ø8 c/ 17 = 5,92); mínimo 3,48 cm²/m (Ø8 c/ 25 = 4,02)',
 'Cargas: g = 20,0 kN/m (ADOTADA), q = 25,0 kN/m (ADOTADA) – confirmar',
 'A CONFIRMAR: largura dos apoios (ancoragem dos ganchos),',
 'emendas de traspasse e comprimento comercial das barras.',
 'Unidades: cotas em cm, exceto indicação. Desenho em mm no modelo, plotar em 1:50 (A2)']
for i,t in enumerate(txt):
    text('TEXTO',nx,ny-i*(T2*1.5),T3 if i==0 else T2,t)
# legenda
lx,ly=15000.0,sy+800
for i,(ly_,t) in enumerate([('ARMAD','Armadura longitudinal (vão 1)'),('ARMAD2','Armadura do vão 2'),('ARMAD3','Porta-estribos'),('ESTRIBO','Estribos'),('MOMENTO','Envoltória de Md'),('CAP','Momento resistente das barras')]):
    yy=ly-i*350; line(ly_,lx,yy,lx+1200,yy); text('TEXTO',lx+1400,yy-60,T1,t)
# ---------------- quadro de ferros
lenN1=2*c1; lenN2=2*c2; lenN3=(L+ov-cov)/1000+0.16; lenN4=b4-a4; lenN5=(2*L-2*cov)/1000; lenN6=2*(0.23+0.83)+2*0.07
w20=0.2466*10; w20=2.466; w125=0.963; w8=0.395
rows=[('N1','Ø20',4,lenN1,w20),('N2','Ø20',4,lenN2,w20),('N3','Ø20',8,lenN3,w20),('N4','Ø20',4,lenN4,w20),('N5','Ø12,5',2,lenN5,w125),('N6','Ø8',n_estr,lenN6,w8)]
qx=22300; qy=ny
cols=[0,600,1300,2000,3300,4800]; heads=['Pos.','Ø (mm)','Quant.','C unit. (m)','C total (m)','Peso (kg)']
text('TEXTO',qx,qy+420,T3,'QUADRO DE FERROS (CA-50)')
rh=330; tot=0
def rowdraw(yv,vals,bold=False):
    for cxv,v in zip(cols,vals): text('TEXTO',qx+cxv+60,yv-rh*0.7,T2 if not bold else T2,v)
    line('TABELA',qx,yv-rh,qx+6400,yv-rh)
rowdraw(qy,heads,True)
line('TABELA',qx,qy,qx+6400,qy)
yv=qy-rh
for nome,ph,qt,cu,wl in rows:
    ct=qt*cu; pw=ct*wl; tot+=pw
    rowdraw(yv,[nome,ph.replace('Ø',''),str(qt),f'{cu:.2f}'.replace('.',','),f'{ct:.1f}'.replace('.',','),f'{pw:.1f}'.replace('.',',')]); yv-=rh
rowdraw(yv,['Total','','','','',f'{tot:.1f}'.replace('.',',')],True)
rect('TABELA',qx,yv-rh,qx+6400,qy)
for cxv in cols[1:]: line('TABELA',qx+cxv,qy,qx+cxv,yv-rh)
text('TEXTO',qx,yv-rh-250,T1,'N6: ≈ 2,26 m por estribo (ganchos de 7 cm); comprimentos de N3 incluem gancho de 16 cm.')
print('total kg',tot,'n estribos',n_estr)
# ---------------- carimbo
rect('MOLDURA',SW-10*S-11000,10*S,SW-10*S,10*S+3200)
text('TEXTO',SW-10*S-10800,10*S+2500,T3,'UnB – Concreto Armado e Protendido')
text('TEXTO',SW-10*S-10800,10*S+1800,T2,'VIGA CONTÍNUA EM CONCRETO ARMADO 2 x 10 m – ARMAÇÃO')
text('TEXTO',SW-10*S-10800,10*S+1100,T2,'Prof. Li Chong Lee Bacelar de Castro')
text('TEXTO',SW-10*S-10800,10*S+450,T2,'Escala 1:50 (seções 1:10)      Data: 05/10/2026      Folha 01/01')
# ---------------- escrita
hdr=['0\nSECTION','2\nHEADER','9\n$ACADVER\n1\nAC1009','9\n$INSUNITS\n70\n4','9\n$LTSCALE\n40\n'+str(S),'9\n$EXTMIN\n10\n0\n20\n0','9\n$EXTMAX\n10\n'+str(SW)+'\n20\n'+str(SH),'0\nENDSEC']
tab=['0\nSECTION','2\nTABLES',
 '0\nTABLE\n2\nLTYPE\n70\n3',
 '0\nLTYPE\n2\nCONTINUOUS\n70\n0\n3\nSolid line\n72\n65\n73\n0\n40\n0.0',
 '0\nLTYPE\n2\nDASHED\n70\n0\n3\nDashed\n72\n65\n73\n2\n40\n18.0\n49\n12.0\n49\n-6.0',
 '0\nLTYPE\n2\nCENTER\n70\n0\n3\nCenter\n72\n65\n73\n4\n40\n40.0\n49\n24.0\n49\n-4.0\n49\n4.0\n49\n-4.0',
 '0\nENDTAB']
layers=[('MOLDURA',7,'CONTINUOUS'),('CONTORNO',7,'CONTINUOUS'),('EIXO',1,'CENTER'),('APOIO',7,'CONTINUOUS'),('ARMAD',3,'CONTINUOUS'),('ARMAD2',5,'CONTINUOUS'),('ARMAD3',6,'CONTINUOUS'),('ESTRIBO',4,'CONTINUOUS'),('MOMENTO',1,'CONTINUOUS'),('CAP',5,'DASHED'),('COTAS',2,'CONTINUOUS'),('TEXTO',7,'CONTINUOUS'),('TABELA',7,'CONTINUOUS')]
tab.append(f'0\nTABLE\n2\nLAYER\n70\n{len(layers)}')
for n,c,lt in layers: tab.append(f'0\nLAYER\n2\n{n}\n70\n0\n62\n{c}\n6\n{lt}')
tab+=['0\nENDTAB','0\nTABLE\n2\nSTYLE\n70\n1','0\nSTYLE\n2\nSTANDARD\n70\n0\n40\n0.0\n41\n1.0\n50\n0.0\n71\n0\n42\n2.5\n3\ntxt\n4\n','0\nENDTAB','0\nENDSEC']
body='\n'.join(out)
dxf='\n'.join(hdr+tab)+'\n0\nSECTION\n2\nENTITIES\n'+body+'\n0\nENDSEC\n0\nEOF\n'
open('Viga_Continua_CA_Armacao.dxf','w',encoding='cp1252',errors='replace').write(dxf)
print('ok',len(out))
