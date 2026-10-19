import sys; sys.path.insert(0,'.')
from analysis import *
import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=final_design(); r,m,Aato,AscB,Ascs=evaluate_design(d)
x=r['x']; e=r['e']; fu=fuso(d,r); ext=r['ext']; ck=r['ck']; lim=r['lim']
h=d['h']; L=d['L']
plt.rcParams.update({'font.size':9,'axes.grid':True,'grid.alpha':.3})
# 1 traçado + fuso
fig,ax=plt.subplots(figsize=(8,3.6))
ax.fill_between(x,fu['lo'],fu['up'],color='#DCE6F1',label='Fuso limite')
ax.plot(x,fu['lo'],'#1F3864',lw=.8); ax.plot(x,fu['up'],'#1F3864',lw=.8)
ax.plot(x,e,'r',lw=2,label='Cabo resultante e(x)')
ax.axhline(d['e_max'],color='g',ls='--',lw=.8,label="e_max (cobrimento)"); ax.axhline(-d['e_max'],color='g',ls='--',lw=.8)
ax.invert_yaxis(); ax.set_xlabel('x (m)'); ax.set_ylabel('e (m)  (+ abaixo do CG)'); ax.legend(ncol=3,fontsize=7,loc='lower center')
ax.set_title('Traçado do cabo e fuso limite'); fig.tight_layout(); fig.savefig('fig/fuso.png',dpi=170); plt.close()
# 2 momentos
fig,ax=plt.subplots(figsize=(8,3.4))
ax.plot(x,ext['Mg'],label='Mg'); ax.plot(x,ext['Mg']+ext['Mq_max'],label='Mg+Mq máx'); ax.plot(x,ext['Mg']+ext['Mq_min'],label='Mg+Mq mín')
ax.invert_yaxis(); ax.set_xlabel('x (m)'); ax.set_ylabel('M (kN·m)'); ax.legend(fontsize=7); ax.set_title('Momentos externos (tração embaixo positiva; eixo invertido)')
fig.tight_layout(); fig.savefig('fig/momentos.png',dpi=170); plt.close()
# 3 tensões
fig,axs=plt.subplots(1,2,figsize=(9,3.6))
for a,(k1,k2,t) in zip(axs,[('cfq_s1','cfq_s2','CFQ (ELS-D)'),('cr_s1','cr_s2','CR (ELS-F)')]):
    a.plot(x,ck[k1],label='σ1 inferior'); a.plot(x,ck[k2],label='σ2 superior'); a.axhline(0,color='k',lw=.6)
    a.set_title(t); a.set_xlabel('x (m)'); a.set_ylabel('σ (MPa)'); a.legend(fontsize=7)
axs[1].axhline(lim['ft'] if np.isscalar(lim['ft']) else 2.43,color='r',ls='--',lw=.8)
fig.tight_layout(); fig.savefig('fig/tensoes.png',dpi=170); plt.close()
# 4 flechas
dp=deflection_pc(d,r)
fig,ax=plt.subplots(figsize=(8,3.2))
for k,lab in (('qp_net','quase-permanente (t=0)'),('qp_inf','quase-permanente (t∞)')):
    ax.plot(x,np.asarray(dp[k])*1000,label=lab)
ax.invert_yaxis(); ax.axhline(0,color='k',lw=.6); ax.set_xlabel('x (m)'); ax.set_ylabel('δ (mm), + para baixo'); ax.legend(fontsize=7); ax.set_title('Flecha da viga protendida')
fig.tight_layout(); fig.savefig('fig/flecha.png',dpi=170); plt.close()
print(lim, np.asarray(dp['qp_inf']).min()*1000, np.asarray(dp['qp_inf']).max()*1000, np.asarray(dp['qp_net']).max()*1000)
