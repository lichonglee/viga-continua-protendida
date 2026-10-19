from PIL import Image, ImageDraw, ImageFont
T='/tmp/claude-0/-home-claude/714531a0-74fd-5a12-b94f-74c52a8d18b7/scratchpad/unbt/ppt/media/'
im1=Image.open(T+'image1.png').convert('RGB'); print(im1.size, im1.getpixel((500,1020)))
im2=Image.open(T+'image2.png').convert('RGB'); print(im2.size)
W,H=im2.size
bh=int(W/2.1)            # banner 21 x 10 cm
ban=im2.crop((0,H-bh,W,H)).copy()
d=ImageDraw.Draw(ban)
fb=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf',int(W*0.036))
fr=ImageFont.truetype('/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf',int(W*0.026))
x=int(W*0.075)
d.text((x,int(bh*0.12)),'UNIVERSIDADE DE BRASÍLIA',font=fb,fill=(255,255,255))
d.text((x,int(bh*0.12)+int(W*0.050)),'Concreto Armado e Protendido',font=fr,fill=(255,255,255))
d.rectangle((x,int(bh*0.12)+int(W*0.092),x+int(W*0.09),int(bh*0.12)+int(W*0.097)),fill=(243,147,37))
ban.save('banner.png'); print(ban.size)
