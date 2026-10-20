"""Capta as telas do painel (app/viga_continua_protendida.html) para o manual, com Playwright + Chromium.
Uso: py src/shots_painel.py   (a partir da raiz do repositório). Ajuste CHROME se o Chromium estiver em outro lugar."""
import os, sys, threading, http.server, functools, json, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, 'app')
OUT = os.path.join(ROOT, 'src', 'manual_painel', 'img')
CHROME = os.path.expanduser(r'~\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe')
os.makedirs(OUT, exist_ok=True)

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=APP)
handler.log_message = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
URL = 'http://127.0.0.1:8765/viga_continua_protendida.html'

TABS = ['resumo', 'tracado', 'perdas', 'esforcos', 'tensoes', 'elu', 'flecha', 'niveis', 'ca', 'memorial']
# quantos cartões de cada aba entram no manual (os primeiros)
NCARDS = {'resumo': 4, 'tracado': 2, 'perdas': 2, 'esforcos': 3, 'tensoes': 2, 'elu': 3, 'flecha': 2, 'niveis': 3, 'ca': 2}

def shot(loc, name, **kw):
    p = os.path.join(OUT, name + '.png')
    for tent in range(4):   # o painel redesenha os cartões ao rolar/redimensionar; tenta de novo se o elemento sumir
        try:
            loc.page.wait_for_timeout(350); loc.screenshot(path=p, **kw); print('ok', name); return p
        except Exception as e:
            if tent == 3: raise
            print('retry', name, str(e)[:60])

def novo(browser, tema='light', w=1480, h=1000):
    ctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1.5, locale='pt-BR')
    pg = ctx.new_page(); pg.add_init_script("try{localStorage.clear();localStorage.setItem('viga-cp-tema','%s')}catch(e){}" % tema)
    pg.goto(URL); pg.wait_for_selector('#panel .card')
    pg.add_style_tag(content='.tabs{position:static !important;box-shadow:none !important}')   # a barra de abas fixa cobriria o topo das fotos dos cartões
    pg.wait_for_timeout(600); return ctx, pg

def tipo(pg, tp):
    pg.click('#tipos button[data-tp="%s"]' % tp); pg.wait_for_timeout(700)

def aba(pg, t):
    pg.click('#tab_' + t); pg.wait_for_timeout(1800 if t == 'memorial' else 600)

def cards_da_aba(pg, prefix, t, n):
    aba(pg, t)
    cards = pg.locator('#panel > .card')
    for i in range(min(n, cards.count())):
        c = cards.nth(i)
        if c.is_visible(): shot(c, '%s_%s_%d' % (prefix, t, i + 1))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    # ---- visão geral e barra superior (2 vãos iguais, projeto padrão)
    ctx, pg = novo(b)
    pg.screenshot(path=os.path.join(OUT, 'g01_tela_inicial.png'), clip={'x': 0, 'y': 0, 'width': 1480, 'height': 880}); print('ok g01')
    shot(pg.locator('.unbbar'), 'g02_barra_topo')
    shot(pg.locator('header.top'), 'g02b_cabecalho')
    shot(pg.locator('#tabs'), 'g03_abas')
    # presets e tipos de viga (topo da barra lateral)
    box = pg.locator('#dados').bounding_box()
    pg.screenshot(path=os.path.join(OUT, 'g04_dados_topo.png'), clip={'x': box['x'], 'y': box['y'], 'width': box['width'], 'height': 430}); print('ok g04')
    ctx.close()
    # ---- barra lateral completa (janela alta)
    ctx, pg = novo(b, h=2900)
    for d in pg.locator('details.grp').all(): d.evaluate('e => e.open = true')
    pg.wait_for_timeout(300); shot(pg.locator('#dados'), 'g05_dados_completo')
    ctx.close()
    # ---- caso 1 vão e caso 2 vãos iguais: uma série de telas por aba
    for tp, pref in (('1', 'v1'), ('2e', 'v2')):
        ctx, pg = novo(b); tipo(pg, tp)
        for t in TABS[:-1]: cards_da_aba(pg, pref, t, NCARDS[t])
        aba(pg, 'memorial')
        pg.screenshot(path=os.path.join(OUT, pref + '_memorial_topo.png'), clip={'x': 0, 'y': 0, 'width': 1480, 'height': 1000}); print('ok', pref, 'memorial')
        ctx.close()
    # ---- 2 vãos diferentes (8 + 12 m)
    ctx, pg = novo(b); tipo(pg, '2d')
    for t in ('resumo', 'tracado', 'esforcos', 'flecha'): cards_da_aba(pg, 'v2d', t, 2)
    ctx.close()
    # ---- recursos (sobre 2 vãos iguais)
    ctx, pg = novo(b)
    # níveis com cores e limites "todos"
    aba(pg, 'resumo'); pg.click('.limsw button[data-l="all"]'); pg.wait_for_timeout(500)
    shot(pg.locator('#panel > .card').nth(1), 'f01_verificacoes_todos_limites')
    shot(pg.locator('.tabs'), 'f02_limites_e_vaos')
    pg.click('.limsw button[data-l="nivel"]'); pg.wait_for_timeout(300)
    # recolher cartão
    pg.locator('#panel > .card').nth(1).locator('.cbtn').click(); pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(OUT, 'f03_cartao_recolhido.png'), clip={'x': 330, 'y': 150, 'width': 1150, 'height': 700}); print('ok f03')
    pg.click('#recbar button:has-text("Mostrar todos")'); pg.wait_for_timeout(500)
    # escala dos eixos
    aba(pg, 'tracado'); card = pg.locator('#panel > .card').first
    card.locator('details.scl summary').click(); pg.wait_for_timeout(300)
    card.locator('.sclrow input').nth(0).fill('2'); card.locator('.sclrow input').nth(1).fill('8'); card.locator('.sclrow input').nth(1).press('Enter'); pg.wait_for_timeout(500)
    shot(pg.locator('#panel > .card').first, 'f04_escala_eixos')
    # efeitos por agrupamento
    aba(pg, 'perdas'); pg.locator('#panel > .card').first.locator('.lgctl button:has-text("Perdas imediatas")').click(); pg.wait_for_timeout(500)
    shot(pg.locator('#panel > .card').first, 'f05_efeitos_grupo')
    # cortes + salvar seção
    aba(pg, 'resumo'); shot(pg.locator('#cutsCard'), 'f06_cortes_salvar_secao')
    for d in pg.locator('details.grp').all(): d.evaluate('e => e.open = true')
    pg.select_option('#in_perdaMode', '1'); pg.select_option('#in_cabMode', '1'); pg.wait_for_timeout(700)
    aba(pg, 'perdas'); shot(pg.locator('#panel > .card').first, 'f09_perdas_estipulada')
    ctx.close()
    # perda estipulada e cabo resultante (barra lateral, janela alta para não rolar)
    ctx, pg = novo(b, h=2900)
    for d in pg.locator('details.grp').all(): d.evaluate('e => e.open = true')
    pg.select_option('#in_perdaMode', '1'); pg.select_option('#in_cabMode', '1'); pg.wait_for_timeout(800)
    for d in pg.locator('details.grp').all(): d.evaluate('e => e.open = true')
    pg.wait_for_timeout(300)
    shot(pg.locator('details.grp:has(summary:has-text("Perdas de protensão"))'), 'f07_perda_estipulada')
    shot(pg.locator('details.grp:has(summary:has-text("Armadura ativa"))'), 'f08_cabo_resultante')
    ctx.close()
    # ação do tema escuro e toast
    ctx, pg = novo(b, tema='dark')
    pg.screenshot(path=os.path.join(OUT, 'f10_tema_escuro.png'), clip={'x': 0, 'y': 0, 'width': 1480, 'height': 880}); print('ok f10')
    ctx.close()
    # salvar dados (aviso)
    ctx, pg = novo(b)
    pg.click('#savedata'); pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(OUT, 'f11_salvar_dados_aviso.png'), clip={'x': 0, 'y': 0, 'width': 1480, 'height': 1000}); print('ok f11')
    ctx.close(); b.close()
srv.shutdown()
print('pronto', len(os.listdir(OUT)), 'imagens')
