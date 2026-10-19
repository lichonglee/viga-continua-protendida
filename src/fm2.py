import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, json
from PIL import Image
F={
'u1':r'\mathrm{N3:}\ \ \sigma_{CF}\leq 0,\quad \sigma_{CR}\leq 1{,}2\,f_{ctk,inf}',
'u2':r'\mathrm{N2:}\ \ \sigma_{CQP}\leq 0,\quad \sigma_{CF}\leq 1{,}2\,f_{ctk,inf}',
'u3':r'\mathrm{N1:}\ \ w_k\,(CF)\leq 0{,}2\ \mathrm{mm}\quad(CAA\ II)',
'u4':r'N_\infty = C_c - T_s,\qquad M = M_{ext} + M_P',
'u5':r'w_k = \min\left\{\frac{\phi}{12{,}5\,\eta_1}\frac{\sigma_s}{E_s}\frac{3\sigma_s}{f_{ct,m}},\ \frac{\phi}{12{,}5\,\eta_1}\frac{\sigma_s}{E_s}\left(\frac{4}{\rho_{ri}}+45\right)\right\}',
}
plt.rcParams['mathtext.fontset']='stix'
sz=json.load(open('fm/sizes.json'))
for k,t in F.items():
    fig=plt.figure(figsize=(0.1,0.1)); fig.text(0,0,'$'+t+'$',fontsize=40,color='#163F70')
    fig.savefig(f'fm/{k}.png',dpi=200,transparent=True,bbox_inches='tight',pad_inches=0.04); plt.close(fig)
    sz[k]=Image.open(f'fm/{k}.png').size
json.dump(sz,open('fm/sizes.json','w')); print({k:(round(sz[k][0]*.3),round(sz[k][1]*.3)) for k in F})

# figura dos niveis
import numpy as np
from niveis import *
fig,axs=plt.subplots(1,3,figsize=(16.64,4.8),dpi=100,sharey=True)
cases=[(5,'Nível 3 – completa (10 cord.)',('CF','CR'),'#163F70'),(4,'Nível 2 – limitada (8 cord.)',('CQP','CF'),'#8E2F6A'),(2,'Nível 1 – parcial (4 cord.)',('CF',),'#2A7F62')]
for ax,(nc,tit,cmb,col) in zip(axs,cases):
    o=run(nc); d,r=o['d'],o['r']; W=d['W']; ext=r['ext']; rf=r['res']['inf']; x=r['x']
    Mg=ext['Mg']
    M={'CQP':(Mg+d['psi2']*ext['Mq_max'],Mg+d['psi2']*ext['Mq_min']),'CF':(Mg+d['psi1']*ext['Mq_max'],Mg+d['psi1']*ext['Mq_min']),'CR':(Mg+ext['Mq_max'],Mg+ext['Mq_min'])}
    def sig(c):
        a=rf['s1p']+M[c][0]/W/1e3; b=rf['s2p']-M[c][1]/W/1e3
        return np.maximum(a,b)
    ls={'CQP':'-','CF':'--','CR':':'}
    for c in cmb:
        ax.plot(x,sig(c),ls[c],color=col,lw=2.2,label='tração máx. '+c)
    ax.axhline(0,color='#444',lw=1)
    ax.axhline(d['ft_els'],color='#C0392B',lw=1.4); ax.text(0.3,d['ft_els']+0.12,'1,2·fctk,inf = %.2f MPa'%d['ft_els'],color='#C0392B',fontsize=11)
    ax.set_title(tit,fontsize=15,color='#163F70',fontweight='bold'); ax.set_xlabel('x (m)',fontsize=12); ax.grid(alpha=.3); ax.legend(fontsize=11,loc='lower right')
    ax.set_xlim(0,20); ax.tick_params(labelsize=11)
axs[0].set_ylabel('σ de tração máxima nas fibras (MPa)',fontsize=12)
plt.tight_layout(); plt.savefig('fig/niveis.png'); print('fig ok')
