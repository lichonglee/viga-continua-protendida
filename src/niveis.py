"""Niveis de protensao NBR 6118 (Tab. 13.4): 3 completa, 2 limitada, 1 parcial."""
import numpy as np
from scipy.optimize import brentq
from analysis import *

Es = 210000.0
def lvl_checks(d, r):
    """margens (MPa; >=0 ok) para cada nivel, ao longo de todas as estacoes"""
    ck = r['ck']; W = d['W']; ext = r['ext']; rf = r['res']['inf']
    Mg = ext['Mg']
    Mq_p = Mg + d['psi2'] * ext['Mq_max']; Mq_n = Mg + d['psi2'] * ext['Mq_min']
    Mf_p = Mg + d['psi1'] * ext['Mq_max']; Mf_n = Mg + d['psi1'] * ext['Mq_min']
    Mr_p = Mg + ext['Mq_max']; Mr_n = Mg + ext['Mq_min']
    s = lambda M, sgn, key: rf[key] + sgn * M / W / 1e3
    ft = d['ft_els']
    out = {}
    # nivel 3: ELS-D freq <= 0 ; ELS-F rara <= ft
    out['N3 ELS-D (CF)'] = min((-s(Mf_p, 1, 's1p')).min(), (-s(Mf_n, -1, 's2p')).min())
    out['N3 ELS-F (CR)'] = min((ft - s(Mr_p, 1, 's1p')).min(), (ft - s(Mr_n, -1, 's2p')).min())
    # nivel 2: ELS-D quase-perm <= 0 ; ELS-F freq <= ft
    out['N2 ELS-D (CQP)'] = min((-s(Mq_p, 1, 's1p')).min(), (-s(Mq_n, -1, 's2p')).min())
    out['N2 ELS-F (CF)'] = min((ft - s(Mf_p, 1, 's1p')).min(), (ft - s(Mf_n, -1, 's2p')).min())
    # tensao maxima de tracao em cada combinacao
    out['_max_cf'] = max(s(Mf_p, 1, 's1p').max(), s(Mf_n, -1, 's2p').max())
    out['_max_cqp'] = max(s(Mq_p, 1, 's1p').max(), s(Mq_n, -1, 's2p').max())
    out['_max_cr'] = max(s(Mr_p, 1, 's1p').max(), s(Mr_n, -1, 's2p').max())
    return out

def cracked_sigma_s(d, M, N, As_cm2, ds):
    """secao retangular fissurada, N compressao (kN) no CG, M (kNm) tracao embaixo (>0). retorna sigma_s (MPa), x"""
    b, h = d['bw'], d['h']; Ec = d['Ecs'] * 1e3; E_s = Es * 1e3; As = As_cm2 * 1e-4
    def eps_c(x):
        den = 0.5 * Ec * b * x - E_s * As * (ds - x) / x
        return N / den, den
    def Mcalc(x):
        ec, den = eps_c(x)
        Cc = 0.5 * Ec * ec * b * x; Ts = E_s * As * ec * (ds - x) / x
        return Cc * (h / 2 - x / 3) + Ts * (ds - h / 2)
    # x minimo em que den>0
    a_ = 0.5 * Ec * b; b_ = E_s * As; c_ = -E_s * As * ds
    xmin = (-b_ + np.sqrt(b_ ** 2 - 4 * a_ * c_)) / (2 * a_)
    xs = np.linspace(xmin * 1.0005, h * 0.999, 4000)
    f = np.array([Mcalc(x) - M for x in xs])
    idx = np.where(np.sign(f[:-1]) != np.sign(f[1:]))[0]
    if len(idx) == 0:
        return None, None
    x = brentq(lambda t: Mcalc(t) - M, xs[idx[0]], xs[idx[0] + 1])
    ec, _ = eps_c(x)
    return E_s * ec * (ds - x) / x / 1e3, x

def wk_calc(d, sig_s, As_cm2, phi_mm, cover=0.05):
    fctm = d['fctm']; eta1 = 2.25
    Acri = d['bw'] * (cover + 7.5 * phi_mm / 1000)
    rho = As_cm2 * 1e-4 / Acri
    f = phi_mm / (12.5 * eta1) * sig_s / Es
    w1 = f * 3 * sig_s / fctm
    w2 = f * (4 / rho + 45)
    return min(w1, w2), w1, w2, rho, Acri

def sec_actions(d, r, i, hog):
    ext = r['ext']; rf = r['res']['inf']
    Mext = ext['Mg'][i] + d['psi1'] * (ext['Mq_min'][i] if hog else ext['Mq_max'][i])
    M = Mext + rf['MP'][i]               # sag +
    N = rf['N'][i]
    return Mext, rf['MP'][i], M, N

def elu_need(d, r, i, hog, bar, nbar_max=14):
    """Msd(ELU) e As passiva tracionada minima (cm2) para MRd>=Msd com x/d<=0.45"""
    res = elu(d, r)
    xi, Mpos, Mneg, mh = res[i]
    Msd = abs(Mneg) if hog else Mpos
    Ls = r['Ls']; e = r['e'][i]
    Pinf = Ls['Pinf'][i]; sinf = Ls['sig_inf'][i]
    de_n = Pinf / (d['Ac'] * d['Ecs'] * 1e3) * (1 + e ** 2 * d['Ac'] / d['Ic'])
    eps0 = sinf / d['Ep'] + de_n
    # hogging: comprimida embaixo, cabo a dp=h/2-e da base ; sag: dp=h/2+e
    dp = d['h'] / 2 - e if hog else d['h'] / 2 + e
    ds = d['h'] - 0.06
    for n in range(0, nbar_max + 1):
        As = n * BAR_AREA[bar] * 1e-4
        m = mrd_section(d, dp, d['Ap'], eps0, As=As, ds=ds)
        if m['Mrd'] >= Msd and m['xd'] <= 0.45:
            return dict(n=n, As=n * BAR_AREA[bar], Mrd=m['Mrd'], Msd=Msd, xd=m['x'] / dp, ok=True, eps0=eps0, dp=dp)
    return dict(n=nbar_max, As=nbar_max * BAR_AREA[bar], Mrd=m['Mrd'], Msd=Msd, xd=m['xd'], ok=False)

def run(ncord, phi=16.0, verbose=True):
    d = final_design(n_cord=ncord)
    r = evaluate(d)
    L = lvl_checks(d, r)
    out = dict(ncord=ncord, Ap=d['Ap'] * 1e4, Pj=r['Ls']['Pj'], Pinf=(r['Ls']['Pinf'].min(), r['Ls']['Pinf'].max()), L=L, d=d, r=r)
    # ato
    Aato = as_ato(d, r)
    out['As_ato'] = Aato.max()
    return out

if __name__ == '__main__':
    for nc in (3, 4, 5, 6):
        o = run(nc)
        L = o['L']
        print('ncord', nc, 'Ap %.2f' % o['Ap'], 'Pj %.0f' % o['Pj'], 'Pinf %.0f-%.0f' % o['Pinf'], 'As_ato %.1f' % o['As_ato'])
        for k, v in L.items(): print('   ', k, round(float(v), 2))
