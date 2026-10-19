import json,re,os,glob
from playwright.sync_api import sync_playwright
S='../deck/project/'
order=json.load(open(S+'deck.json'))['order']
ext={os.path.splitext(f)[0]:f for f in os.listdir('blob')}
os.makedirs('png',exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium') if False else p.chromium.launch()
    pg=b.new_page(viewport={'width':1920,'height':1080})
    for n,i in enumerate(order,1):
        h=open(S+'slides/%s.html'%i,encoding='utf8').read()
        h=re.sub(r'/_blob/([0-9a-f]{32})',lambda m:'file://'+os.path.abspath('blob/'+ext[m.group(1)]),h)
        h=re.sub(r'<aside>.*?</aside>','',h,flags=re.S)
        open('s.html','w',encoding='utf8').write('<!doctype html><meta charset=utf8><style>html,body{margin:0}section{isolation:isolate;position:relative;width:1920px;height:1080px;overflow:hidden;box-sizing:border-box}section>img[style*="position:absolute"]{z-index:-1}</style>'+h)
        pg.goto('file://'+os.path.abspath('s.html')); pg.wait_for_timeout(200)
        pg.evaluate('''()=>{const s=document.querySelector('section');
        const kids=[...s.children].filter(e=>e.tagName!='IMG'&&e.tagName!='ASIDE'&&getComputedStyle(e).position!='absolute');
        const bot=()=>{let m=0;for(const e of s.querySelectorAll('*')){if(e.tagName=='IMG'&&getComputedStyle(e).position=='absolute')continue;if(getComputedStyle(e).position=='absolute')continue;m=Math.max(m,e.getBoundingClientRect().bottom)}return m};
        let z=1;for(let k=0;k<12&&bot()>935&&z>0.5;k++){const t=kids[0]?kids[0].getBoundingClientRect().top:64;z*=Math.max(0.6,(935-t)/(bot()-t));kids.forEach(e=>e.style.zoom=z)}}''')
        pg.wait_for_timeout(100)
        pg.screenshot(path='png/%02d.png'%n)
    b.close()
