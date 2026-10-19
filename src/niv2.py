from niveis import *
import json
out = {}
for nc in (2, 3, 4, 5):
    o = run(nc); d, r = o['d'], o['r']
    print('--- ncord', nc, 'Ap %.2f' % o['Ap'], 'Pj %.0f' % o['Pj'], 'Pinf', ['%.0f' % v for v in o['Pinf']], 'As_ato %.1f' % o['As_ato'])
    for name, i, hog in (('B', 20, True), ('vao', 8, False)):
        Mext, MP, M, N = sec_actions(d, r, i, hog)
        sg = 1 if not hog else -1
        # tensao na fibra tracionada na comb. frequente
        W = d['W']
        sten = -N / d['Ac'] / 1e3 + abs(M) / W / 1e3
        for bar in (16.0, 20.0):
            bn = {16.0: 16, 20.0: 20}[bar]
            ELU = elu_need(d, r, i, hog, bn)
            # menor n de barras para wk <= 0.2
            sol = None
            for n in range(0, 15):
                As = n * BAR_AREA[bn]
                if sten <= d['ft_els']:           # nao fissurado
                    sol = (n, As, 0.0, 0.0, 'nao fissurada'); break
                if n == 0: continue
                sig, x = cracked_sigma_s(d, abs(M), N, As, d['h'] - 0.06)
                if sig is None: continue
                wk = wk_calc(d, sig, As, bar)[0]
                if wk <= 0.2:
                    sol = (n, As, sig, wk, 'fissurada'); break
            print('  %s Ø%d  M_freq=%.0f (Mext %.0f MP %.0f) N=%.0f sig_t=%.2f  ELU: n=%d As=%.1f MRd=%.0f Msd=%.0f xd=%.2f %s | wk: %s' % (name, bn, abs(M), Mext, MP, N, sten, ELU['n'], ELU['As'], ELU['Mrd'], ELU['Msd'], ELU['xd'], ELU['ok'], sol))
