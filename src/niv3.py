from niveis import *
import numpy as np
for nc, tag in ((5,'N3'),(4,'N2'),(2,'N1a'),(3,'N1b')):
    o = run(nc); d, r = o['d'], o['r']
    df = deflection_pc(d, r)
    print(tag, 'ncord', nc, 'flecha qp_net(max) %.1f mm  qp_inf %.1f mm  cfq %.1f' % (df['qp_net'].max()*1e3, df['qp_inf'].max()*1e3, df['cfq_net'].max()*1e3), 'min', df['qp_net'].min()*1e3, df['qp_inf'].min()*1e3)
    # losses
    Ls = r['Ls']; print('   perda total max %.1f%%' % (100*(1-Ls['sig_inf']/Ls['sig_i'].max()).max()), 'Pj %.0f'%Ls['Pj'])
d = final_design(n_cord=2); r = evaluate(d)
for name,i,hog,n,bar in (('B',20,True,4,20),('vao',8,False,2,20)):
    Mext,MP,M,N = sec_actions(d,r,i,hog)
    As = n*BAR_AREA[bar]
    sig,x = cracked_sigma_s(d,abs(M),N,As,d['h']-0.06)
    print(name, 'As',As,'sig',sig,'x',x, wk_calc(d,sig,As,bar) if sig else None)
# nivel 2: B com 2phi16
d = final_design(n_cord=4); r=evaluate(d)
for As,bar in ((4.02,16),):
    i=20; dp=d['h']/2-r['e'][i]
    Ls=r['Ls']; Pinf=Ls['Pinf'][i]; e=r['e'][i]
    de_n=Pinf/(d['Ac']*d['Ecs']*1e3)*(1+e**2*d['Ac']/d['Ic']); eps0=Ls['sig_inf'][i]/d['Ep']+de_n
    m=mrd_section(d,dp,d['Ap'],eps0,As=As*1e-4,ds=d['h']-0.06); print('N2 B 2phi16', m['Mrd'], m['x']/dp)
