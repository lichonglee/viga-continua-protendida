import sys, os; sys.path.insert(0, '.')
import io, textwrap
from PIL import Image, ImageDraw, ImageFont
from cues import CUES
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
from scipy.interpolate import PchipInterpolator
from analysis import *
from engine import cable, profile_params

FPS = 24
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 34)
TOTAL = 78.0
NF = int(TOTAL * FPS)
OUT = 'vid_frames'

d = final_design(); r, m, A, B, C = evaluate_design(d)
fu = fuso(d, r)
L = d['L']; h = d['h']; emax = d['e_max']; em = d['e_span']
pp = profile_params(d)
x41 = r['x']
Mh = r['res']['inf']['Mhip']; N = r['res']['inf']['N']
elp41 = r['e'] - Mh / N
xs = np.linspace(0, 2 * L, 801)
ecab, _ = cable(d, xs)
ip = lambda y: PchipInterpolator(x41, y)(xs)
lows = {k: ip(v) for k, v in fu['lows'].items()}
ups = {k: ip(v) for k, v in fu['ups'].items()}
lo = ip(fu['lo']); up = ip(fu['up']); elp = ip(elp41)
YL = 0.70

NAVY = '#1F3864'; RED = '#C0392B'; TEAL = '#1B7F79'; ORG = '#D9822B'; GRAY = '#6B7280'
LCOL = ['#1B7F79', '#2A9D8F', '#3BAA9E', '#5FBFB0', '#86D0C3']
UCOL = ['#B45F06', '#D9822B', '#E39A4F', '#EDB278', '#F3C79D']
LLAB = ['ato: tração na fibra inferior', 'ato: compressão na fibra superior',
        'ELS-D fibra inferior (CF)', 'ELS-F fibra inferior (CR)', 'ELS-CE fibra superior (CR)']
ULAB = ['ato: compressão na fibra inferior', 'ato: tração na fibra superior',
        'ELS-D fibra superior (CF)', 'ELS-F fibra superior (CR)', 'ELS-CE fibra inferior (CR)']

# agenda (s)
T = dict(title_end=3.6, beam=3.6, supports=6.0, emax=8.0, lows=11.0, lo_env=19.8, ups=22.2, up_env=30.8,
         fill=33.0, cab_a=35.8, cab_b=46.0, cab_c=51.0, elp=56.0, check=59.5, end=70.0)
STEP = 1.6


def sm(t, a, b):
    if b <= a: return 1.0 if t >= a else 0.0
    u = np.clip((t - a) / (b - a), 0, 1)
    return u * u * (3 - 2 * u)


def prog_line(ax, x, y, p, **kw):
    n = max(2, int(len(x) * p))
    if p <= 0: return
    yy = np.where(np.abs(y[:n]) > 0.58, np.nan, y[:n]); ax.plot(x[:n], -yy, **kw)


def frame(i):
    t = i / FPS
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0.045, 0.29, 0.925, 0.57])
    ax.set_xlim(-0.8, 20.8); ax.set_ylim(-YL, YL); ax.axis('off')

    # cabeçalho
    fig.text(0.045, 0.935, 'Traçado do cabo e fuso limite', fontsize=36, weight='bold', color=NAVY)
    fig.text(0.045, 0.885, 'Viga contínua 2 × 10 m · seção 30 × 90 cm · C30 · CP 190 RB Ø12,7 · pós-tração aderente',
             fontsize=20, color=GRAY)
    fig.text(0.97, 0.935, 'UnB · Concreto Protendido', fontsize=18, color=GRAY, ha='right')

    # --- viga
    pb = sm(t, T['beam'], T['beam'] + 2.2)
    if pb > 0:
        xe = -0.0 + 2 * L * pb
        ax.add_patch(Polygon([[0, h / 2], [xe, h / 2], [xe, -h / 2], [0, -h / 2]], closed=True,
                             fc='#EEF2F8', ec=NAVY, lw=2.5, zorder=1))
        ax.plot([0, xe], [0, 0], color=GRAY, lw=1.5, ls=(0, (8, 5)), zorder=2)
        ax.text(20.7, 0, 'CG', color=GRAY, fontsize=16, va='center')
    ps = sm(t, T['supports'], T['supports'] + 1.0)
    if ps > 0:
        for xp, nm in ((0, 'A'), (L, 'B'), (2 * L, 'C')):
            w = 0.38
            ax.add_patch(Polygon([[xp, -h / 2], [xp - w, -h / 2 - 0.16], [xp + w, -h / 2 - 0.16]], closed=True,
                                 fc=NAVY, alpha=ps, zorder=3))
            ax.text(xp, -h / 2 - 0.27, nm, ha='center', va='top', fontsize=22, weight='bold', color=NAVY, alpha=ps)
        ax.annotate('', (0, -0.585), (L, -0.585), arrowprops=dict(arrowstyle='<->', color=GRAY, lw=1.6, alpha=ps))
        ax.annotate('', (L, -0.585), (2 * L, -0.585), arrowprops=dict(arrowstyle='<->', color=GRAY, lw=1.6, alpha=ps))
        ax.text(L / 2, -0.60, 'L = 10 m', ha='center', va='top', fontsize=17, color=GRAY, alpha=ps)
        ax.text(1.5 * L, -0.60, 'L = 10 m', ha='center', va='top', fontsize=17, color=GRAY, alpha=ps)
        ax.text(-0.7, h / 2 + 0.02, 'h = 90 cm', ha='left', va='bottom', fontsize=17, color=GRAY, alpha=ps)

    # --- e_max
    pe = sm(t, T['emax'], T['emax'] + 1.6)
    if pe > 0:
        for s in (1, -1):
            ax.plot([0, 2 * L * pe], [s * emax] * 2, color='#2E7D32', lw=2, ls=(0, (6, 4)), zorder=2)
        if pe > 0.9:
            ax.text(20.35, -emax, 'e_max', color='#2E7D32', fontsize=17, va='center', ha='left')
            ax.text(20.35, emax, '−e_max', color='#2E7D32', fontsize=17, va='center', ha='left')
        ax.text(15.6, emax + 0.025, 'e_max = h/2 − d′ = 37,5 cm', ha='center',
                fontsize=17, color='#2E7D32', alpha=pe)

    # --- fuso: limites inferiores de e (mais perto do topo)
    legend = []
    for k in range(5):
        a = T['lows'] + k * STEP
        p = sm(t, a, a + 1.3)
        if p > 0:
            fade = 1 - 0.65 * sm(t, T['lo_env'], T['lo_env'] + 1.5)
            prog_line(ax, xs, list(lows.values())[k], p, color=LCOL[k], lw=2.4, alpha=fade, zorder=4)
            legend.append((LLAB[k], LCOL[k], fade))
    p = sm(t, T['lo_env'], T['lo_env'] + 2.0)
    if p > 0:
        prog_line(ax, xs, lo, p, color=TEAL, lw=5, zorder=6)
    for k in range(5):
        a = T['ups'] + k * STEP
        p = sm(t, a, a + 1.3)
        if p > 0:
            fade = 1 - 0.65 * sm(t, T['up_env'], T['up_env'] + 1.5)
            prog_line(ax, xs, list(ups.values())[k], p, color=UCOL[k], lw=2.4, alpha=fade, zorder=4)
            legend.append((ULAB[k], UCOL[k], fade))
    p = sm(t, T['up_env'], T['up_env'] + 2.0)
    if p > 0:
        prog_line(ax, xs, up, p, color=ORG, lw=5, zorder=6)
    pf = sm(t, T['fill'], T['fill'] + 2.0)
    if pf > 0:
        ok = up >= lo
        ax.fill_between(xs, -np.clip(up, -YL, YL), -np.clip(lo, -YL, YL), where=ok, color='#6FA8DC', alpha=0.38 * pf,
                        zorder=2, interpolate=True, lw=0)
        if pf > .9:
            ax.text(L / 2 + 0.2, 0.455 if False else -0.12 + 0.0, '', fontsize=1)

    # legenda de limites (canto superior esquerdo do eixo, sobre a viga fica poluído -> faixa inferior)
    if legend:
        lows_l = [l for l in legend if l[0] in LLAB]
        ups_l = [l for l in legend if l[0] in ULAB]
        def chips(items, x0, ttl):
            if not items: return
            fig.text(x0, 0.225, ttl, fontsize=15, color=GRAY, weight='bold')
            for j, (lab, col, fd) in enumerate(items):
                yy = 0.198 - j * 0.027
                fig.patches.append(Rectangle((x0, yy - 0.004), 0.016, 0.014, transform=fig.transFigure, fc=col,
                                             alpha=max(fd, .35)))
                fig.text(x0 + 0.022, yy, lab, fontsize=15, color='#222', va='center', alpha=max(fd, .45))
        chips(lows_l, 0.045, 'LIMITES DE e MÍNIMO')
        chips(ups_l, 0.285, 'LIMITES DE e MÁXIMO')
        env = []
        if t > T['lo_env']: env.append(('e mín = máx. dos 5 limites', TEAL))
        if t > T['up_env']: env.append(('e máx = mín. dos 5 limites', ORG))
        if t > T['fill']: env.append(('fuso limite', '#6FA8DC'))
        if t > T['cab_a']: env.append(('cabo e(x)', RED))
        if t > T['elp']: env.append(('linha de pressões e_lp', '#4B2E83'))
        if env:
            fig.text(0.53, 0.225, 'LEGENDA', fontsize=15, color=GRAY, weight='bold')
            for j, (lab, col) in enumerate(env):
                yy = 0.198 - j * 0.027
                fig.patches.append(Rectangle((0.53, yy - 0.004), 0.016, 0.014, transform=fig.transFigure, fc=col))
                fig.text(0.552, yy, lab, fontsize=15, color='#222', va='center')

    # --- cabo
    def ec_at(xq): return float(np.interp(xq, xs, ecab))
    x0 = pp['x0']; xi = pp['xi']
    segs = [(0, xi, T['cab_a'] + 2.5, T['cab_b'], RED), (xi, L, T['cab_b'], T['cab_c'], '#8E1B1B'),
            (L, 2 * L, T['cab_c'], T['elp'] - 0.4, RED)]
    # trecho A (0 -> xi)
    tipx = None
    for (xa, xb, ta, tb, col) in segs:
        p = sm(t, ta, tb)
        if p > 0:
            xe = xa + (xb - xa) * p
            msk = (xs >= xa) & (xs <= xe)
            ax.plot(xs[msk], -ecab[msk], color=col, lw=5, zorder=8, solid_capstyle='round')
            tipx = xe
    # ancoragem
    pa = sm(t, T['cab_a'], T['cab_a'] + 1.2)
    if pa > 0:
        ax.plot([0], [0], 'o', color=RED, ms=14, zorder=9, alpha=pa)
        ax.annotate('ancoragem: e = 0\n(cabo no CG)', (0, 0), (0.6, 0.30 if False else 0.20), fontsize=16, color=RED,
                    alpha=pa, arrowprops=dict(arrowstyle='-', color=RED, alpha=pa), va='bottom')
    if tipx is not None and t < T['elp'] - 0.4:
        ax.plot([tipx], [-ec_at(tipx)], 'o', color='white', mec=RED, mew=3.5, ms=15, zorder=10)
    # marcos
    if t > T['cab_a'] + 6.0:
        ax.plot([x0], [-em], 's', color=RED, ms=11, zorder=9)
        ax.annotate('vértice da parábola A\nx = %.2f m  ·  e = +%.0f cm' % (x0, em * 100), (x0, -em), (x0 + 0.4, -0.57),
                    fontsize=16, color=RED, ha='left', arrowprops=dict(arrowstyle='-', color=RED))
    if t > T['cab_b'] + 1.6:
        ax.plot([L], [em], 's', color='#8E1B1B', ms=11, zorder=9)
        ax.annotate('apoio B: e = −%.0f cm\n(cabo no topo, parábola reversa λ = 1 m)' % (em * 100), (L, em),
                    (L - 0.8, 0.53), fontsize=16, color='#8E1B1B', ha='right',
                    arrowprops=dict(arrowstyle='-', color='#8E1B1B'))
    if t > T['cab_c'] + 3.5:
        ax.text(15.0, -0.49 if False else 0.0, '', fontsize=1)

    # painel de leitura
    if T['cab_a'] + 1.2 < t < T['elp'] + 0.5 and tipx is not None:
        fig.text(0.97, 0.865, 'x = %5.2f m   e(x) = %+6.1f cm' % (tipx, ec_at(tipx) * 100),
                 fontsize=22, family='monospace', color=RED, ha='right', va='center')

    # --- linha de pressões e_lp = e − M_hip/N
    pl = sm(t, T['elp'], T['elp'] + 3.2)
    if pl > 0:
        n = max(2, int(len(xs) * pl))
        ax.plot(xs[:n], -elp[:n], color='#4B2E83', lw=3.2, ls=(0, (7, 3)), zorder=9)
        if pl > .98:
            ax.text(14.2, -0.50, 'e_lp = e − M_hip/N', color='#4B2E83',
                    fontsize=18, weight='bold', ha='left', va='top')

    # --- verificação
    pc = sm(t, T['check'], T['check'] + 1.2)
    if pc > 0:
        okmask = (elp >= lo - 1e-6) & (elp <= up + 1e-6)
        bad = ~okmask
        ax.plot(xs[bad], -elp[bad], color='#D62828', lw=7, zorder=11, alpha=pc)
        ax.annotate('apoio B: tração no ato excede o limite\n→ armadura passiva As,ato = 4,9 cm²',
                    (L, -elp[400]), (L + 1.0, 0.53), fontsize=16, color='#D62828', alpha=pc, ha='left',
                    arrowprops=dict(arrowstyle='->', color='#D62828', lw=2, alpha=pc))
        fig.text(0.045, 0.03, 'Nas demais seções a linha de pressões fica dentro do fuso: o traçado do cabo está compatível com as tensões-limite.',
                 fontsize=19, color=NAVY, weight='bold', alpha=pc)

    # cartão de título
    pt = 1 - sm(t, T['title_end'] - .6, T['title_end'])
    if pt > 0:
        fig.patches.append(Rectangle((0, 0), 1, 1, transform=fig.transFigure, fc='white', alpha=pt, zorder=50))
        fig.text(0.5, 0.56, 'Traçado do cabo e fuso limite', fontsize=58, weight='bold', color=NAVY, ha='center',
                 alpha=pt, zorder=51)
        fig.text(0.5, 0.47, 'Viga contínua protendida 2 × 10 m · item b)', fontsize=28, color=GRAY, ha='center',
                 alpha=pt, zorder=51)
        fig.text(0.5, 0.38, 'Prof. Li Chong Lee Bacelar de Castro · UnB', fontsize=22, color=GRAY, ha='center',
                 alpha=pt, zorder=51)

    # fecho
    pe2 = sm(t, T['end'], T['end'] + 1.0)
    if pe2 > 0:
        fig.patches.append(Rectangle((0, 0), 1, 1, transform=fig.transFigure, fc='white', alpha=pe2, zorder=50))
        lines = ['Resumo do traçado', '',
                 'e = 0 na ancoragem · e = +28 cm no meio do vão (x = 3,93 m) · e = −28 cm sobre o apoio B',
                 'parábola A (0 → 9 m) + parábola reversa (9 → 10 m), simétrica no 2º vão',
                 'comprimento do cabo 20,09 m · Σα = 1,013 rad · e_max = 37,5 cm',
                 'fuso = máx. de 5 limites inferiores e mín. de 5 limites superiores de e',
                 'M_hip,B(∞) = +68,9 kN·m desloca a linha de pressões: e_lp = e − M_hip/N']
        for j, s in enumerate(lines):
            fig.text(0.5, 0.68 - j * 0.07, s, fontsize=36 if j == 0 else 24, weight='bold' if j == 0 else 'normal',
                     color=NAVY if j == 0 else '#222', ha='center', alpha=pe2, zorder=51)

    # barra de progresso
    fig.patches.append(Rectangle((0, 0), t / TOTAL, 0.008, transform=fig.transFigure, fc=NAVY, zorder=60))
    os.makedirs(OUT, exist_ok=True)
    buf = io.BytesIO(); fig.savefig(buf, format='png'); plt.close(fig); buf.seek(0)
    base = Image.open(buf).convert('RGB')
    canvas = Image.new('RGB', (1920, 1200), (16, 33, 63)); canvas.paste(base, (0, 0))
    dr = ImageDraw.Draw(canvas)
    for (a, b, txt) in CUES:
        if a <= t <= b:
            lines = textwrap.wrap(txt, 78)
            y0 = 1080 + (120 - 44 * len(lines)) // 2
            for k, ln in enumerate(lines):
                w = dr.textlength(ln, font=FONT)
                dr.text(((1920 - w) / 2, y0 + 44 * k), ln, font=FONT, fill=(255, 255, 255))
    canvas.save('%s/f%04d.png' % (OUT, i))


if __name__ == '__main__':
    a = int(sys.argv[1]); b = int(sys.argv[2]); st = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    for i in range(a, b, st):
        frame(i)
