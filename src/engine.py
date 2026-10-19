"""Motor de calculo - viga continua protendida 2 vaos (kN, m, MPa)."""
import numpy as np
from scipy.optimize import brentq

# ----------------------------------------------------------------- dados
D = dict(
    L=10.0, bw=0.30, h=0.90,
    fck=30.0, gc=1.4, gs=1.15,
    g_pp=None, g_add=13.25, q=25.0,          # kN/m (g_pp = 25*Ac)
    psi1=0.4, psi2=0.3,
    cnom=0.035, phi_t=0.010, d_bain=0.066,    # cobrimento, estribo, bainha ext.
    e_end=0.0,                                # excentricidade na ancoragem
    lam=1.0,                                  # comprimento da parabola reversa junto ao apoio (m)
    e_span=0.25, e_sup=None,
    n_cab=2, n_cord=5, Ap1=0.987e-4,          # cabos, cordoalhas/cabo, area cordoalha (m2)
    fptk=1900.0, Ep=200000.0,
    sig_j_ratio=0.74,
    mu=0.20, kk=0.002, slip=0.006,
    t0=7, UR=75,
    phi_cr=2.9, eps_cs=-0.23e-3,
)

def derived(D):
    d = dict(D)
    d['Ac'] = d['bw'] * d['h']
    d['Ic'] = d['bw'] * d['h'] ** 3 / 12
    d['W'] = d['Ic'] / (d['h'] / 2)
    d['k'] = d['W'] / d['Ac']
    d['g_pp'] = 25 * d['Ac']
    d['g'] = d['g_pp'] + d['g_add']
    d['dpp'] = d['cnom'] + d['phi_t'] + d['d_bain'] / 2          # d' do cabo
    d['e_max'] = d['h'] / 2 - d['dpp']
    if d['e_sup'] is None:
        d['e_sup'] = d['e_max']
    fck = d['fck']
    d['fcd'] = fck / d['gc']
    d['fctm'] = 0.3 * fck ** (2 / 3)
    d['fctkinf'] = 0.7 * d['fctm']
    d['fctksup'] = 1.3 * d['fctm']
    d['fctd'] = d['fctkinf'] / d['gc']
    d['Eci'] = 5600 * fck ** 0.5
    d['alpha_i'] = min(0.8 + 0.2 * fck / 80, 1.0)
    d['Ecs'] = d['alpha_i'] * d['Eci']
    d['fcj'] = np.exp(0.38 * (1 - np.sqrt(28 / d['t0']))) * fck
    d['Eci_j'] = 5600 * d['fcj'] ** 0.5
    d['fctmj'] = 0.3 * d['fcj'] ** (2 / 3)
    d['ft_els'] = 1.2 * d['fctkinf']                              # ELS-F (CR)
    d['ft_ato'] = 1.2 * d['fctmj']
    d['Ap'] = d['n_cab'] * d['n_cord'] * d['Ap1']
    d['fpyk'] = 0.9 * d['fptk']
    d['fpyd'] = d['fpyk'] / d['gs']
    d['fptd'] = d['fptk'] / d['gs']
    d['sig_j'] = d['sig_j_ratio'] * d['fptk']
    return d

# ------------------------------------------------------------ geometria do cabo
def profile_params(d):
    L, lam, em, es, ee = d['L'], d['lam'], d['e_span'], d['e_sup'], d['e_end']
    xi = L - lam
    # parabola A: e = em - aA (x-x0)^2 ; e(0)=ee ; parabola B: e = -es + aB (L-x)^2
    # continuidade em xi (valor e inclinacao)  ->  equacao do 2o grau em x0
    # (em-ee)... generalizado:  aA = (em-ee)/x0^2
    # (em+es) x0^2 = (em-ee)(xi-x0)(L-x0)
    c = em - ee
    A = (em + es) - c
    B = c * (xi + L)
    C = -c * xi * L
    x0 = (-B + np.sqrt(B * B - 4 * A * C)) / (2 * A)
    aA = c / x0 ** 2
    aB = aA * (xi - x0) / lam
    return dict(x0=x0, aA=aA, aB=aB, xi=xi)

def cable(d, x):
    """e(x) (positivo abaixo do CG), de/dx, para x em [0,2L]"""
    L = d['L']
    pp = profile_params(d)
    x = np.asarray(x, float)
    s = np.where(x <= L, x, 2 * L - x)
    sign = np.where(x <= L, 1.0, -1.0)
    em, es = d['e_span'], d['e_sup']
    eA = em - pp['aA'] * (s - pp['x0']) ** 2
    deA = -2 * pp['aA'] * (s - pp['x0'])
    eB = -es + pp['aB'] * (L - s) ** 2
    deB = -2 * pp['aB'] * (L - s)
    inA = s <= pp['xi']
    e = np.where(inA, eA, eB)
    de = np.where(inA, deA, deB) * sign
    return e, de

# -------------------------------------------------------------- esforcos externos
def two_span_moment_shear(w_patterns, L, x):
    """momento e cortante (sagging +, cortante = soma forcas verticais p/ cima a esquerda)
    para carga w uniforme nos vaos conforme padrao (w1,w2). viga continua 2 vaos iguais."""
    out = []
    for (w1, w2) in w_patterns:
        # momento no apoio B (3 momentos): MB = -(w1+w2) L^2 / 16
        MB = -(w1 + w2) * L ** 2 / 16
        RA = w1 * L / 2 + MB / L          # MB negativo -> reduz RA
        RC = w2 * L / 2 + MB / L
        M = np.zeros_like(x)
        V = np.zeros_like(x)
        m1 = x <= L
        xx = x[m1]
        M[m1] = RA * xx - w1 * xx ** 2 / 2
        V[m1] = RA - w1 * xx
        xr = 2 * L - x[~m1]
        M[~m1] = RC * xr - w2 * xr ** 2 / 2
        V[~m1] = -(RC - w2 * xr)
        out.append((M, V))
    return out

def ext_actions(d, x):
    L = d['L']
    g, q, g0 = d['g'], d['q'], d['g_pp']
    (Mg, Vg), = two_span_moment_shear([(g, g)], L, x)
    (Mg0, Vg0), = two_span_moment_shear([(g0, g0)], L, x)
    pats = [(q, q), (q, 0), (0, q)]
    res = two_span_moment_shear(pats, L, x)
    Mq = np.array([r[0] for r in res]); Vq = np.array([r[1] for r in res])
    return dict(Mg=Mg, Vg=Vg, Mg0=Mg0, Mq_max=np.maximum(Mq.max(0), 0), Mq_min=np.minimum(Mq.min(0), 0),
                Vq_max=np.maximum(Vq.max(0), 0), Vq_min=np.minimum(Vq.min(0), 0),
                Mq_all=Mq, Vq_all=Vq)

# ------------------------------------------------------------------- perdas
def relax_psi1000(r):
    pts = [(0.5, 0.0), (0.6, 1.3), (0.7, 2.5), (0.8, 3.5)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return float(np.interp(r, xs, ys)) / 100

def losses(d, dx=0.5):
    """Perdas com esquema discreto (estacoes a cada dx) - replicavel na planilha."""
    L = d['L']
    x = np.arange(0, 2 * L + 1e-9, dx)
    n = len(x)
    e, de = cable(d, x)
    alpha = np.arctan(de)
    dtheta = np.concatenate([[0], np.abs(np.diff(alpha))])
    theta = np.cumsum(dtheta)
    darc = np.concatenate([[0], np.sqrt(dx ** 2 + np.diff(e) ** 2)])
    arc = np.cumsum(darc)
    sj = d['sig_j']; mu, kk, Ep = d['mu'], d['kk'], d['Ep']
    sL = sj * np.exp(-mu * theta - kk * arc)                      # pela extremidade esquerda
    Th, S = theta[-1], arc[-1]
    sR = sj * np.exp(-mu * (Th - theta) - kk * (S - arc))
    sf = np.maximum(sL, sR)
    # ---- acomodacao: Delta_k = 2*(Int_0^xk sL dx - sL(xk)*xk)/Ep  (trapezio)
    cum = np.concatenate([[0], np.cumsum(0.5 * (sL[1:] + sL[:-1]) * np.diff(x))])
    delta_k = 2 * (cum - sL * x) / Ep                              # mm?? -> m (sigma MPa*m/MPa)
    ih = x <= L + 1e-9
    dk = delta_k[ih]
    slip = d['slip']
    k = np.searchsorted(dk, slip)         # primeiro indice com dk>=slip
    if k >= len(dk):
        xa = L; sfa = sL[ih][-1]
    else:
        f = (slip - dk[k - 1]) / (dk[k] - dk[k - 1])
        xa = x[k - 1] + f * (x[k] - x[k - 1])
        sfa = sL[k - 1] + f * (sL[k] - sL[k - 1])
    s_slip_half = np.where(x[ih] <= xa, 2 * sfa - sL[ih], sL[ih])
    sig_after_slip = np.concatenate([s_slip_half, s_slip_half[::-1][1:]])
    # ---- encurtamento elastico
    ext = ext_actions(d, x)
    Mg0 = ext['Mg0']
    ncab = d['n_cab']
    ap = Ep / d['Eci_j']
    Ac, Ic, Ap = d['Ac'], d['Ic'], d['Ap']
    # encurtamento elastico em forma fechada (equivalente a iteracao de ponto fixo)
    cES = ap * (ncab - 1) / (2 * ncab) if ncab > 1 else 0.0
    gfac = Ap * 1e3 * (1 / Ac + e ** 2 / Ic) / 1e3          # (MPa por MPa de sigma)
    des = np.maximum(cES * (gfac * sig_after_slip - Mg0 * e / Ic / 1e3) / (1 + cES * gfac), 0.0)
    sig_i = sig_after_slip - des
    Pi = Ap * sig_i * 1e3
    scp0 = -Pi / Ac / 1e3 - Pi * e ** 2 / Ic / 1e3 + Mg0 * e / Ic / 1e3
    # ---- progressivas
    phi, ecs = d['phi_cr'], d['eps_cs']
    rr = sig_i / d['fptk']
    psi1000 = np.array([relax_psi1000(v) for v in rr])
    psi_t = 2.5 * psi1000
    chi = -np.log(1 - psi_t)
    chi_p = 1 + chi
    chi_c = 1 + 0.5 * phi
    eta = 1 + e ** 2 * Ac / Ic
    ap28 = Ep / d['Ecs']
    rho_p = Ap / Ac
    dsig = (abs(ecs) * Ep + ap28 * np.abs(scp0) * phi + sig_i * chi) / (chi_p + chi_c * ap28 * eta * rho_p)
    sig_inf = sig_i - dsig
    return dict(x=x, e=e, de=de, alpha=alpha, dtheta=dtheta, theta=theta, darc=darc, arc=arc,
                sL=sL, sig_fric=sf, delta_k=delta_k, cum=cum, sig_slip=sig_after_slip, xa=xa, sfa=sfa,
                sig_i=sig_i, sig_inf=sig_inf, Pj=Ap * sj * 1e3, Pi=Pi, Pinf=Ap * sig_inf * 1e3, scp0=scp0,
                d_es=sig_after_slip - sig_i, d_prog=dsig, psi1000=psi1000, psi_t=psi_t, chi=chi, eta=eta,
                theta_tot=Th, arc_tot=S, ap=ap, ap28=ap28)

# ------------------------------------------------------------ hiperestatico
def hyperstatic(d, x, e, P, cosa=None):
    """momento hiperestatico (sagging +) para a viga de 2 vaos; P array (kN) por ponto, e (m)."""
    L, Ec = d['L'], d['Ecs'] * 1e3     # kPa
    EI = Ec * d['Ic']
    if cosa is None:
        cosa = np.cos(np.arctan(np.gradient(e, x)))
    Miso = -P * cosa * e
    m = np.where(x <= L, x / 2, (2 * L - x) / 2)
    delta_down = np.trapz(Miso * m, x) / EI
    fBB = L ** 3 / (6 * EI)
    RB = delta_down / fBB                    # reacao para cima em B
    Mhip = -RB * m
    return Miso, Mhip, RB

def solve_P_support(d):
    pass

np.trapz = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz

# --------------------------------------------------------------- verificacoes
def evaluate(d, xs=None):
    L = d['L']
    Ls = losses(d)
    x = Ls['x']
    e = Ls['e']; de = Ls['de']
    cosa = np.cos(np.arctan(de))
    ext = ext_actions(d, x)
    Ac, W = d['Ac'], d['W']
    res = {}
    for tag, P in (('i', Ls['Pi']), ('inf', Ls['Pinf'])):
        Miso, Mhip, RB = hyperstatic(d, x, e, P, cosa)
        N = P * cosa
        MP = Miso + Mhip
        s1p = -N / Ac / 1e3 + MP / W / 1e3
        s2p = -N / Ac / 1e3 - MP / W / 1e3
        res[tag] = dict(N=N, Miso=Miso, Mhip=Mhip, RB=RB, MP=MP, s1p=s1p, s2p=s2p)
    ri, rf = res['i'], res['inf']
    Mg0, Mg = ext['Mg0'], ext['Mg']
    Mcfq_max = Mg + d['psi1'] * ext['Mq_max']; Mcfq_min = Mg + d['psi1'] * ext['Mq_min']
    Mcr_max = Mg + ext['Mq_max']; Mcr_min = Mg + ext['Mq_min']
    ck = {}
    ck['ato_s1'] = ri['s1p'] + Mg0 / W / 1e3
    ck['ato_s2'] = ri['s2p'] - Mg0 / W / 1e3
    ck['cfq_s1'] = rf['s1p'] + Mcfq_max / W / 1e3          # tracao embaixo -> ELS-D
    ck['cfq_s2'] = rf['s2p'] - Mcfq_min / W / 1e3          # tracao em cima
    ck['cr_s1'] = rf['s1p'] + Mcr_max / W / 1e3            # ELS-F embaixo
    ck['cr_s2'] = rf['s2p'] - Mcr_min / W / 1e3            # ELS-F em cima
    ck['ce_s2'] = rf['s2p'] - Mcr_max / W / 1e3            # compressao topo (max sagging)
    ck['ce_s1'] = rf['s1p'] + Mcr_min / W / 1e3            # compressao fundo (max hogging)
    ck['perm_s1'] = rf['s1p'] + Mg / W / 1e3
    ck['perm_s2'] = rf['s2p'] - Mg / W / 1e3
    lim = dict(ato_c=-0.7 * d['fcj'], ato_t=d['ft_ato'], ce=-0.7 * d['fck'], ft=d['ft_els'])
    fails = []
    def chk(name, arr, lo=None, hi=None):
        v = arr
        worst = 0
        if lo is not None: worst = min(worst, float(np.min(v - lo)))
        if hi is not None: worst = min(worst, float(np.min(hi - v)))
        fails.append((name, worst))
    chk('ato s1 comp', ck['ato_s1'], lo=lim['ato_c']); chk('ato s1 trac', ck['ato_s1'], hi=lim['ato_t'])
    chk('ato s2 comp', ck['ato_s2'], lo=lim['ato_c']); chk('ato s2 trac', ck['ato_s2'], hi=lim['ato_t'])
    chk('ELS-D s1', ck['cfq_s1'], hi=0.0); chk('ELS-D s2', ck['cfq_s2'], hi=0.0)
    chk('ELS-F s1', ck['cr_s1'], hi=lim['ft']); chk('ELS-F s2', ck['cr_s2'], hi=lim['ft'])
    chk('ELS-CE s2', ck['ce_s2'], lo=lim['ce']); chk('ELS-CE s1', ck['ce_s1'], lo=lim['ce'])
    return dict(Ls=Ls, res=res, ext=ext, ck=ck, lim=lim, checks=fails, x=x, e=e, cosa=cosa)

def summary(d):
    r = evaluate(d)
    print('Pj=%.0f Pi_min=%.0f Pinf: min %.0f max %.0f  RBinf=%.1f MhipB=%.1f' % (
        r['Ls']['Pj'], r['Ls']['Pi'].min(), r['Ls']['Pinf'].min(), r['Ls']['Pinf'].max(), r['res']['inf']['RB'],
        r['res']['inf']['Mhip'][np.argmin(abs(r['x'] - 10))]))
    for n, w in r['checks']:
        print('  %-12s %s  margem %.2f' % (n, 'OK ' if w >= -1e-9 else 'FALHA', w))
    return r


def margins(r):
    out = {}
    ck = r['ck']; lim = r['lim']
    out['ato s1 trac'] = (lim['ato_t'] - ck['ato_s1'].max())
    out['ato s2 trac'] = (lim['ato_t'] - ck['ato_s2'].max())
    out['ato comp'] = (min(ck['ato_s1'].min(), ck['ato_s2'].min()) - lim['ato_c'])
    out['D s1'] = -ck['cfq_s1'].max(); out['D s2'] = -ck['cfq_s2'].max()
    out['F s1'] = lim['ft'] - ck['cr_s1'].max(); out['F s2'] = lim['ft'] - ck['cr_s2'].max()
    out['CE'] = min(ck['ce_s1'].min(), ck['ce_s2'].min()) - lim['ce']
    return out
