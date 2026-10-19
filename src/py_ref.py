import sys, json; sys.path.insert(0,'.')
from niveis import *
def ref(**kw):
    d = final_design(**kw); r = evaluate(d); fu = fuso(d, r); sh = shear(d, r); df = deflection_pc(d, r)
    Aato = as_ato(d, r); rc = rc_design(d, r); L = lvl_checks(d, r)
    Ls = r['Ls']
    el = sum((Ls['sL'][i]+Ls['sL'][i-1])/2*Ls['darc'][i]/d['Ep']*1000 for i in range(1,21))
    return dict(Pj=Ls['Pj'], Pi_min=Ls['Pi'].min(), Pinf_min=Ls['Pinf'].min(), Pinf_max=Ls['Pinf'].max(), xa=float(Ls['xa']), elong=el,
      theta=float(Ls['theta_tot']), arc=float(Ls['arc_tot']), RB=float(r['res']['inf']['RB']), MhipB=float(r['res']['inf']['Mhip'][20]),
      margins={k: float(v) for k, v in m_.items()} if (m_:=margins(r)) else {},
      lo=fu['lo'].tolist(), up=fu['up'].tolist(), Aato=float(Aato.max()), Vsd=sh['Vsd'].tolist(), asw=sh['asw_calc'].tolist(), Vu=float(sh['Vu']),
      qp_net_min=float(df['qp_net'].min()), qp_net_max=float(df['qp_net'].max()), cfq=float(df['cfq_net'].max()), f1=float(df['f1']),
      rc=dict(As_neg=float(rc['neg']['As']), As_pos=float(rc['pos']['As']), wk_neg=float(rc['els']['neg']['wk']), wk_pos=float(rc['els']['pos']['wk']), defl=float(rc['defl_inst']), tot=float(rc['defl_tot']), Vsd_B=float(rc['Vsd_B']), asw_B=float(rc['asw_B'])),
      lv={k: float(v) for k, v in L.items()}, s1=r['ck']['cr_s1'].tolist(), sig_inf=Ls['sig_inf'].tolist(), sig_i=Ls['sig_i'].tolist())
json.dump({'base': ref(), 'n4': ref(n_cord=4, e_span=0.30, e_sup=0.30)}, open('app/ref.json','w'))
print('ok')
