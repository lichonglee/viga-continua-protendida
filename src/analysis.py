"""Analises adicionais: fuso, ELU, cisalhamento, flecha, CA."""
import numpy as np
from scipy.optimize import brentq
from engine import *

FINAL = dict(n_cab=2, n_cord=5, e_span=0.28, lam=1.0, d_bain=0.061, e_sup=0.28)

def final_design(**kw):
    D2 = dict(D); D2.update(FINAL); D2.update(kw)
    return derived(D2)

# ------------------------------------------------------------------ fuso limite
def fuso(d, r):
    x = r['x']; W, A, k = d['W'], d['Ac'], d['k']
    Ls = r['Ls']; ext = r['ext']
    cosa = r['cosa']
    Ni = Ls['Pi'] * cosa; Nf = Ls['Pinf'] * cosa
    ftA, fcjA = d['ft_ato'] * 1e3, 0.7 * d['fcj'] * 1e3
    ftS, fcS = d['ft_els'] * 1e3, 0.7 * d['fck'] * 1e3
    Mg0, Mg = ext['Mg0'], ext['Mg']
    Mcfq_max = Mg + d['psi1'] * ext['Mq_max']; Mcfq_min = Mg + d['psi1'] * ext['Mq_min']
    Mcr_max = Mg + ext['Mq_max']; Mcr_min = Mg + ext['Mq_min']
    lows = {
        'ato: tração fibra inf.': (Mg0 - ftA * W) / Ni - k,
        'ato: compr. fibra sup.': (Mg0 - fcjA * W) / Ni + k,
        'ELS-D fibra inf. (CFQ)': Mcfq_max / Nf - k,
        'ELS-F fibra inf. (CR)': (Mcr_max - ftS * W) / Nf - k,
        'ELS-CE fibra sup. (CR)': (Mcr_max - fcS * W) / Nf + k,
    }
    ups = {
        'ato: compr. fibra inf.': (Mg0 + fcjA * W) / Ni - k,
        'ato: tração fibra sup.': (Mg0 + ftA * W) / Ni + k,
        'ELS-D fibra sup. (CFQ)': Mcfq_min / Nf + k,
        'ELS-F fibra sup. (CR)': (ftS * W + Mcr_min) / Nf + k,
        'ELS-CE fibra inf. (CR)': (Mcr_min + fcS * W) / Nf - k,
    }
    lo = np.max(np.array(list(lows.values())), axis=0)
    up = np.min(np.array(list(ups.values())), axis=0)
    return dict(lows=lows, ups=ups, lo=lo, up=up)

# --------------------------------------------------------------- ELU flexao
def sigma_p(d, eps):
    Ep = d['Ep']; epy = d['fpyd'] / Ep
    return np.where(eps <= epy, Ep * eps, d['fpyd'])

def mrd_section(d, dp, Ap, eps_p0, As=0.0, ds=None, Es=210000.0, Asc=0.0, dsc=0.05):
    """Mrd (kNm) secao retangular b x h, face comprimida: dp,ds medidos da fibra comprimida. m, m2"""
    b = d['bw']; fcd = d['fcd'] * 1e3; fyd = 500 / 1.15 * 1e3
    eps_cu = 3.5e-3
    def forces(x):
        ep = eps_p0 + eps_cu * (dp - x) / x
        sp = float(sigma_p(d, ep)) * 1e3
        Tp = Ap * sp
        Ts = 0.0
        if As > 0:
            es = eps_cu * (ds - x) / x
            ss = np.clip(Es * 1e3 * es, -fyd, fyd)
            Ts = As * ss
        return Tp, Ts, ep
    def Cs(x):
        if Asc <= 0: return 0.0
        es = eps_cu * (x - dsc) / x
        return Asc * float(np.clip(Es * 1e3 * es, -fyd, fyd))
    f = lambda x: 0.85 * fcd * b * 0.8 * x + Cs(x) - sum(forces(x)[:2])
    x = brentq(f, 1e-4, dp * 0.999)
    Tp, Ts, ep = forces(x)
    M = Tp * (dp - 0.4 * x) + (Ts * (ds - 0.4 * x) if As > 0 else 0) - (Cs(x) * (dsc - 0.4 * x) if Asc > 0 else 0)
    return dict(x=x, Mrd=M, Tp=Tp, Ts=Ts, Cs=Cs(x), eps_p=ep, sig_p=Tp / Ap / 1e3, xd=x / dp)

def elu(d, r):
    x = r['x']; ext = r['ext']; Ls = r['Ls']; e = r['e']
    Mhip = r['res']['inf']['Mhip']
    out = {}
    Ap = d['Ap']
    for name, i in (('B', int(round(10 / 0.5))), ('vao', None)):
        pass
    res = []
    for i in range(0, 21):                 # secoes 0..10 (vao 1)
        xi = x[i]
        Mmax = 1.4 * (ext['Mg'][i] + ext['Mq_max'][i]); Mmin = 1.4 * (ext['Mg'][i] + ext['Mq_min'][i])
        mh = Mhip[i]
        # hiperestatico: favoravel 0,9 / desfavoravel 1,2
        Msd_pos = Mmax + (0.9 if mh < 0 else 1.2) * mh
        Msd_neg = Mmin + (0.9 if mh > 0 else 1.2) * mh
        res.append((xi, Msd_pos, Msd_neg, mh))
    return res

def mrd_at(d, r, i, hogging, Asc=0.0):
    """Mrd na estacao i. hogging=True -> face comprimida embaixo"""
    Ls = r['Ls']; e = r['e'][i]
    Pinf = Ls['Pinf'][i]; sinf = Ls['sig_inf'][i]
    de_n = Pinf / (d['Ac'] * d['Ecs'] * 1e3) * (1 + e ** 2 * d['Ac'] / d['Ic'])
    eps0 = sinf / d['Ep'] + de_n
    # posicao do cabo a partir da face comprimida
    if hogging:      # comprimida embaixo; cabo a (h/2 - e) ... e>0 abaixo do CG -> distancia da base = h/2 - e
        dp = d['h'] - (d['h'] / 2 + e) * 0 - ( d['h'] / 2 - e) if False else (d['h'] / 2 + e)
        # cabo esta a (h/2 - e) da base?  e positivo abaixo do CG => dist. da base = h/2 - e ; da face tracionada(topo) = h/2 + e
        # face comprimida = base; profundidade do cabo = distancia da base ate o cabo
        dp = d['h'] / 2 - e
    else:            # comprimida em cima; profundidade do cabo = h/2 + e
        dp = d['h'] / 2 + e
    out = mrd_section(d, dp, d['Ap'], eps0, Asc=Asc * 1e-4)
    out.update(dp=dp, eps0=eps0)
    return out


# ---------------------------------------------------------------- cisalhamento
def shear(d, r):
    x = r['x']; Ls = r['Ls']; ext = r['ext']
    L = d['L']
    Pinf = Ls['Pinf']; N = r['res']['inf']['N']
    alpha = Ls['alpha']
    RB = r['res']['inf']['RB']
    Vp_iso = -Pinf * np.sin(alpha)
    Vhip = np.where(x <= L, -RB / 2, RB / 2)
    Vp = Vp_iso + Vhip
    Vg, Vqm, Vqn = ext['Vg'], ext['Vq_max'], ext['Vq_min']
    Mhip = r['res']['inf']['Mhip']; e = r['e']; k = d['k']
    MP = r['res']['inf']['MP']
    M0_sag = 0.9 * (N * k - MP)           # fibra inferior tracionada
    M0_hog = 0.9 * (N * k + MP)           # fibra superior tracionada
    Msag = 1.4 * (ext['Mg'] + ext['Mq_max']); Mhog = 1.4 * (ext['Mg'] + ext['Mq_min'])
    use_sag = np.abs(Msag) >= np.abs(Mhog)
    Msd = np.where(use_sag, np.abs(Msag), np.abs(Mhog))
    M0 = np.where(use_sag, M0_sag, M0_hog)
    # Msd = maior valor entre secoes adjacentes (criterio da aula)
    Msd_adj = Msd.copy()
    Msd_adj[:-1] = np.maximum(Msd[:-1], Msd[1:])
    Msd_adj[1:] = np.maximum(Msd_adj[1:], Msd[:-1])
    beta = np.minimum(1 + M0 / np.maximum(Msd_adj, 1e-6), 2.0)
    tauc = 0.6 * d['fctd']
    tau_cor = beta * tauc
    cases = []
    for gp, gg in ((0.9, 1.4), (1.2, 1.0)):
        for vq in (np.zeros_like(Vg), Vqm, Vqn):
            cases.append(gp * Vp + gg * Vg + 1.4 * vq)
    cases = np.array(cases)
    Vsd = np.max(np.abs(cases), axis=0)
    # combinacoes nomeadas (padrao da aula)
    c1 = 0.9 * Vp + 1.4 * Vg
    c2 = 0.9 * Vp + 1.4 * Vg + 1.4 * Vqm
    c2b = 0.9 * Vp + 1.4 * Vg + 1.4 * Vqn
    c3 = 1.2 * Vp + 1.0 * Vg
    c4 = 1.2 * Vp + 1.0 * Vg + 1.4 * Vqn
    c4b = 1.2 * Vp + 1.0 * Vg + 1.4 * Vqm
    bw = d['bw']; dd = 0.9 * d['h']
    dbain = d['d_bain']; nduct = d['n_cab']
    red = (dbain > bw / 8)
    bwred = bw - 0.5 * nduct * dbain * (1 if red else 0)
    tau_u = 0.27 * (1 - d['fck'] / 250) * (d['fcd'])
    Vu = tau_u * 1e3 * bwred * dd
    twd = Vsd / (bwred * dd) / 1e3          # MPa
    td = (twd - tau_cor) / 0.9
    fywd = 500 / 1.15
    asw_n = np.maximum(td, 0) / fywd * bwred * 100 / 2 * 100 / 100   # cm2/m por ramo : td[MPa]/fywd * bwred[m] -> m2/m*... ajustar
    # unidades: td/fywd (adim) * bwred (m) = m2/m ; *1e4 cm2/m ; /2 ramos
    asw_n = np.maximum(td, 0) / fywd * bwred * 1e4 / 2
    rho_min = 0.2 * d['fctm'] / 500
    asw_min_n = np.full_like(Vg, rho_min * bw * 1e4 / 2)
    asw_calc = np.maximum(asw_n, asw_min_n)
    return dict(Vp=Vp, Vp_iso=Vp_iso, Vhip=Vhip, Vg=Vg, Vqm=Vqm, Vqn=Vqn, c1=c1, c2=np.where(np.abs(c2)>=np.abs(c2b),c2,c2b), c3=c3, c4=np.where(np.abs(c4)>=np.abs(c4b),c4,c4b),
                Vsd=Vsd, M0=M0, Msd=Msd_adj, beta=beta, tau_cor=tau_cor, tauc=tauc, tau_u=tau_u, bwred=bwred, Vu=Vu,
                twd=twd, td=td, asw_n=asw_n, asw_min_n=asw_min_n, asw_calc=asw_calc, dd=dd, rho_min=rho_min, use_sag=use_sag)

# ---------------------------------------------------------------- flecha
def integrate_defl(x, kappa, L):
    """y'' = -M/EI  ->  retorna y (positivo para baixo)  com y(0)=0,y(L)=0"""
    dx = np.diff(x)
    slope = np.concatenate([[0], np.cumsum(0.5 * (kappa[1:] + kappa[:-1]) * dx)])
    y = np.concatenate([[0], np.cumsum(0.5 * (slope[1:] + slope[:-1]) * dx)])
    iL = int(round(L / (x[1] - x[0])))
    yc = y - y[iL] * x / L
    # em x=L,  y(L)=0 ; se y(2L) != 0 refina com apoio em 2L
    return yc

def deflection_pc(d, r):
    x = r['x']; L = d['L']
    EI = d['Ecs'] * 1e3 * d['Ic']
    ext = ext_actions(d, x)
    (Mg_, _), = two_span_moment_shear([(d['g'], d['g'])], L, x)
    (Mpsi, _), = two_span_moment_shear([(d['psi2'] * d['q'],) * 2], L, x)
    (Mq_, _), = two_span_moment_shear([(d['q'], d['q'])], L, x)
    (Mg0_, _), = two_span_moment_shear([(d['g_pp'], d['g_pp'])], L, x)
    MP = r['res']['inf']['MP']
    out = {}
    def y_of(M):
        # com y(0)=0 e y(L)=0 ; assume simetria
        y = integrate_defl(x, -M / EI, L)
        return y
    out['g'] = y_of(Mg_); out['qp_live'] = y_of(Mpsi); out['P'] = y_of(MP)
    out['qp_net'] = y_of(Mg_ + Mpsi + MP)
    out['q_full'] = y_of(Mq_)
    phi = d['phi_cr']
    out['qp_inf'] = out['qp_net'] * (1 + phi)
    # carga frequente adicional
    (Mfreq, _), = two_span_moment_shear([(d['psi1'] * d['q'],) * 2], L, x)
    out['cfq_net'] = y_of(Mg_ + Mfreq + MP)
    # frequencia fundamental (modo antissimetrico = biapoiado)
    m = (d['g']) / 9.81 * 1000   # kg/m
    EIn = d['Ecs'] * 1e6 * d['Ic']
    out['f1'] = np.pi / (2 * L ** 2) * np.sqrt(EIn / m)
    return out


# ---------------------------------------------------------------- concreto armado (comparacao)
BAR_AREA = {8: 0.503, 10: 0.785, 12.5: 1.227, 16: 2.011, 20: 3.142, 25: 4.909}

def rc_flexure(d, Md, dd, bw=None):
    """Md kNm (positivo), dd (m). retorna x, As (cm2), xd"""
    bw = bw or d['bw']; fcd = d['fcd'] * 1e3; fyd = 500 / 1.15 * 1e3
    Kmd = Md / (bw * dd ** 2 * fcd)
    disc = 1 - 2 * Kmd / 0.85
    xd = 1.25 * (1 - np.sqrt(disc))
    x = xd * dd
    As = Md / (fyd * (dd - 0.4 * x)) * 1e4
    return dict(Kmd=Kmd, xd=xd, x=x, As=As)

def rc_design(d, r):
    x = r['x']; ext = r['ext']; L = d['L']
    dd = 0.82
    i_sup = 20
    Md_neg = 1.4 * abs(ext['Mg'][i_sup] + ext['Mq_min'][i_sup])
    ipos = np.argmax((ext['Mg'] + ext['Mq_max'])[:21])
    Md_pos = 1.4 * (ext['Mg'][ipos] + ext['Mq_max'][ipos])
    neg = rc_flexure(d, Md_neg, dd); pos = rc_flexure(d, Md_pos, dd)
    out = dict(dd=dd, Md_neg=Md_neg, Md_pos=Md_pos, x_pos=x[ipos], neg=neg, pos=pos)
    # armaduras adotadas
    out['bars_neg'] = (8, 20)    # 8 phi20 = 25.13
    out['bars_pos'] = (6, 20)    # 6 phi20 = 18.85
    out['As_neg'] = 8 * BAR_AREA[20]; out['As_pos'] = 6 * BAR_AREA[20]
    As_min = max(0.0015 * d['bw'] * d['h'] * 1e4, 0)
    out['As_min'] = As_min
    # ELS-W / ELS-F
    Es = 210000.0; ae = Es / d['Ecs']
    fctm = d['fctm']
    Ic, h, bw = d['Ic'], d['h'], d['bw']
    Mr = 1.5 * fctm * 1e3 * Ic / (h / 2)
    out['Mr'] = Mr
    def stage2(As, dd_, Asc=0.0, dc=0.05):
        # x2 : b x^2/2 + (ae-1)As' (x-d') = ae As (d-x)
        b = bw; As_ = As * 1e-4; Asc_ = Asc * 1e-4
        a = b / 2; bb = ae * As_ + (ae - 1) * Asc_; c = -(ae * As_ * dd_ + (ae - 1) * Asc_ * dc)
        x2 = (-bb + np.sqrt(bb ** 2 - 4 * a * c)) / (2 * a)
        I2 = b * x2 ** 3 / 3 + ae * As_ * (dd_ - x2) ** 2 + (ae - 1) * Asc_ * (x2 - dc) ** 2
        return x2, I2
    res = {}
    for tag, As, Asc, i in (('neg', out['As_neg'], 0.0, 20), ('pos', out['As_pos'], 0.0, ipos)):
        Mfreq = abs(ext['Mg'][i] + d['psi1'] * (ext['Mq_min'][i] if tag == 'neg' else ext['Mq_max'][i]))
        # para a envoltoria usa-se q em padrao desfavoravel
        x2, I2 = stage2(As, dd, Asc)
        sig_s = ae * Mfreq * (dd - x2) / I2 / 1e3          # MPa
        phi_l = 20.0
        eta1 = 2.25
        cg = 0.0755
        Acri = d['bw'] * (cg + 7.5 * phi_l / 1000)
        rho_ri = As * 1e-4 / Acri
        w1 = phi_l / (12.5 * eta1) * sig_s / Es * 3 * sig_s / fctm
        w2 = phi_l / (12.5 * eta1) * sig_s / Es * (4 / rho_ri + 45)
        res[tag] = dict(Mfreq=Mfreq, x2=x2, I2=I2, sig_s=sig_s, rho_ri=rho_ri, w1=w1, w2=w2, wk=min(w1, w2), Acri=Acri)
    out['els'] = res
    # flecha (Branson) - integracao com rigidez variavel
    Ecs = d['Ecs'] * 1e3
    (Mg_, _), = two_span_moment_shear([(d['g'], d['g'])], L, x)
    (Mpsi, _), = two_span_moment_shear([(d['psi2'] * d['q'],) * 2], L, x)
    Mqp = Mg_ + Mpsi
    EIx = np.zeros_like(x)
    for j, xx in enumerate(x):
        M = Mqp[j]
        As = out['As_pos'] if M >= 0 else out['As_neg']
        x2, I2 = stage2(As, dd)
        Ma = abs(M)
        if Ma <= Mr:
            Ie = Ic
        else:
            Ie = min((Mr / Ma) ** 3 * Ic + (1 - (Mr / Ma) ** 3) * I2, Ic)
        EIx[j] = Ecs * Ie
    kappa = -Mqp / EIx
    yi = integrate_defl(x, kappa, L)
    af = (2 - 0.68 * 0.996) / (1 + 50 * 0.0)  # rho'=0 conservador
    out['defl_inst'] = float(np.max(yi[:21])); out['alpha_f'] = af
    out['defl_tot'] = out['defl_inst'] * (1 + af)
    out['defl_qp_x'] = x[int(np.argmax(yi[:21]))]
    out['EIx'] = EIx
    # cortante
    Vsd_B = 1.4 * abs(ext['Vg'][20] + ext['Vq_min'][20])
    Vsd_A = 1.4 * (ext['Vg'][0] + ext['Vq_max'][0])
    fywd = 500 / 1.15
    Vc = 0.6 * d['fctd'] * 1e3 * d['bw'] * dd
    def asw(V):
        Vsw = max(V - Vc, 0)
        return Vsw / (0.9 * dd * fywd * 1e3) * 1e4
    out['Vsd_B'] = Vsd_B; out['Vsd_A'] = Vsd_A; out['Vc'] = Vc
    out['asw_B'] = asw(Vsd_B); out['asw_A'] = asw(Vsd_A)       # total (2 ramos) cm2/m
    out['asw_min'] = 0.2 * d['fctm'] / 500 * d['bw'] * 1e4
    return out


def as_ato(d, r):
    """armadura passiva p/ resultante de tracao no ato (sigma_s=250 MPa). retorna max As (cm2) e estacao."""
    ck = r['ck']; h, b = d['h'], d['bw']
    out = []
    for key, sign in (('ato_s1', 1), ('ato_s2', 1)):
        pass
    s1, s2 = ck['ato_s1'], ck['ato_s2']
    As = np.zeros_like(s1)
    for i in range(len(s1)):
        for st, sc in ((s1[i], s2[i]), (s2[i], s1[i])):
            if st > d['ft_ato']:
                xt = h * st / (st - min(sc, 0) if sc < 0 else st - sc if st - sc != 0 else 1e-9)
                # tensao varia linearmente: x_t = h*st/(st - sc)
                xt = h * st / (st - sc)
                Rst = 0.5 * st * 1e3 * b * xt
                As[i] = max(As[i], Rst / 250e3 * 1e4)
    return As

def asc_needed(d, r, i, hogging):
    for Asc in np.arange(0, 40.1, 0.5):
        m = mrd_at(d, r, i, hogging, Asc)
        if m['xd'] <= 0.45:
            return Asc, m
    return None, m

def evaluate_design(d):
    r = evaluate(d)
    m = margins(r)
    Aato = as_ato(d, r)
    iB = 20
    # secao de maior momento positivo (fina) ~ x=4.0 estacao 8
    isp = 8
    Asc_B, mB = asc_needed(d, r, iB, True)
    Asc_s, ms = asc_needed(d, r, isp, False)
    return r, m, Aato, Asc_B, Asc_s
