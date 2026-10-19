import openpyxl,subprocess,glob,os
from openpyxl.worksheet.properties import PageSetupProperties
from PIL import Image,ImageChops
src='../out/Planilha_Apoio_Viga_Continua_CP.xlsx'
specs=[('Dados','A1:E46','portrait','Dados_1'),('Dados','A47:E91','portrait','Dados_2'),
('Esforcos','A1:N26','landscape',None),
('Tracado_Perdas','A1:O26','landscape','Tracado_1'),('Tracado_Perdas','P1:AD26','landscape','Tracado_2'),
('Hiperestatico','A1:J26','landscape',None),
('Tensoes','A1:L26','landscape','Tensoes_1'),('Tensoes','M1:W26','landscape','Tensoes_2'),
('Fuso','A1:Q26','landscape',None),
('Cortante','A1:O26','landscape','Cortante_1'),('Cortante','P1:AB26','landscape','Cortante_2'),
('ELU','A1:D30','portrait',None),('Alongamento','A1:C13','portrait',None),
('Flecha_PC','A1:R26','landscape',None),('CA','A1:D27','portrait',None),
('CA_Flecha','A1:K26','landscape',None),('Niveis','A1:L26','landscape',None),
('Niveis_Comparativo','A1:E33','portrait',None)]
for i,(n,rng,ori,tag) in enumerate(specs):
    wb=openpyxl.load_workbook(src)
    for ws in wb:
        if ws.title!=n: ws.sheet_state='hidden'
    ws=wb[n]; wb.active=wb.sheetnames.index(n)
    ws.print_area=rng
    ws.page_setup.orientation=ori; ws.page_setup.paperSize=8
    ws.sheet_properties.pageSetUpPr=PageSetupProperties(fitToPage=True)
    ws.page_setup.fitToWidth=1; ws.page_setup.fitToHeight=1
    ws.print_options.gridLines=True; ws.print_options.headings=True
    ws.page_margins.left=ws.page_margins.right=ws.page_margins.top=ws.page_margins.bottom=0.2
    ws.oddHeader.center.text='';ws.oddFooter.center.text=''
    ws.print_title_rows=None
    wb.save(f'x_{i:02d}.xlsx')
subprocess.run('soffice --headless --convert-to pdf x_*.xlsx >/dev/null 2>&1',shell=True)
for i,(n,rng,ori,tag) in enumerate(specs):
    subprocess.run(f'pdftoppm -r 150 -png -f 1 -l 1 x_{i:02d}.pdf x_{i:02d}',shell=True)
    im=Image.open(f'x_{i:02d}-1.png').convert('RGB')
    b=ImageChops.difference(im,Image.new('RGB',im.size,'white')).getbbox()
    im.crop((max(b[0]-10,0),max(b[1]-10,0),b[2]+10,b[3]+10)).save(f'tela_{i:02d}.png'); print(i,n,rng,Image.open(f'tela_{i:02d}.png').size)
