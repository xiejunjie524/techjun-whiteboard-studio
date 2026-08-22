from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "examples/gigabit-300mbps/rendered"
W, H = 1920, 1080
BG = (245, 235, 215)
INK = (45, 50, 55)
BLUE = (82, 151, 190)
ORANGE = (221, 125, 65)
GREEN = (99, 159, 112)

def base():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.line((70, 930, 1850, 930), fill=(190, 176, 150), width=5)
    return im, d

def router(d, x=760, y=410, scale=1.0, color=BLUE):
    w, h = int(390*scale), int(170*scale)
    d.rounded_rectangle((x, y, x+w, y+h), radius=int(28*scale), outline=INK, width=10, fill=(235, 227, 209))
    for i in range(4):
        d.ellipse((x+55+i*62, y+55, x+78+i*62, y+78), fill=color, outline=INK, width=3)
    d.line((x+w//2-35, y, x+w//2-70, y-140*scale), fill=INK, width=9)
    d.line((x+w//2+35, y, x+w//2+70, y-140*scale), fill=INK, width=9)

def laptop(d, x=1070, y=520, scale=1.0):
    w, h = int(440*scale), int(270*scale)
    d.rounded_rectangle((x, y, x+w, y+h), radius=18, outline=INK, width=10, fill=(226, 235, 235))
    d.rectangle((x+35, y+35, x+w-35, y+h-55), outline=INK, width=6, fill=(205, 227, 231))
    d.line((x-35, y+h, x+w+35, y+h), fill=INK, width=14)
    d.line((x+105, y+140, x+210, y+95), fill=ORANGE, width=13)
    d.line((x+210, y+95, x+315, y+120), fill=ORANGE, width=13)

def phone(d, x, y, label_color=BLUE):
    d.rounded_rectangle((x, y, x+185, y+360), radius=28, outline=INK, width=10, fill=(234, 238, 231))
    d.rectangle((x+23, y+55, x+162, y+280), outline=INK, width=6, fill=(208, 229, 232))
    d.ellipse((x+80, y+315, x+105, y+340), fill=label_color)

def cable(d, x1, y1, x2, y2, color=ORANGE):
    d.arc((min(x1,x2), min(y1,y2)-120, max(x1,x2), max(y1,y2)+120), 0, 180, fill=color, width=14)

def make(i):
    im, d = base()
    if i == 1:
        router(d, 450, 450); laptop(d); cable(d, 830, 530, 1100, 650); d.ellipse((1450, 350, 1650, 550), outline=ORANGE, width=13); d.line((1490,450,1610,450), fill=ORANGE, width=13)
    elif i == 2:
        phone(d, 520, 350); router(d, 1050, 500); d.arc((700,300,1100,700), 200, 340, fill=ORANGE, width=15); d.arc((760,250,1200,750), 200, 340, fill=BLUE, width=15)
    elif i == 3:
        phone(d, 380, 330); laptop(d, 1050, 500, .9); d.line((700,540,1020,650), fill=GREEN, width=12); d.ellipse((760,500,800,540), fill=GREEN)
    elif i == 4:
        router(d, 480, 430); d.rectangle((1080,470,1320,650), outline=INK, width=10, fill=(235,227,209)); cable(d, 850,520,1080,550, BLUE); d.line((1370,560,1650,560), fill=ORANGE, width=13); d.line((1370,610,1650,610), fill=ORANGE, width=13)
    elif i == 5:
        d.rectangle((420, 450, 740, 700), outline=INK, width=12, fill=(230,225,212)); d.rectangle((1120, 430, 1480, 680), outline=INK, width=12, fill=(232,235,229)); d.line((830,560,1080,560), fill=ORANGE, width=18); d.line((900,520,900,600), fill=ORANGE, width=12)
    elif i == 6:
        d.rectangle((270, 370, 610, 760), outline=INK, width=12, fill=(215, 218, 210)); router(d, 1180, 460); d.line((610,560,1160,560), fill=BLUE, width=14); d.line((720,420,720,700), fill=ORANGE, width=12); d.line((900,420,900,700), fill=ORANGE, width=12)
    elif i == 7:
        laptop(d, 400, 500, .8); phone(d, 1170, 380); d.arc((820,300,1220,760), 90, 270, fill=GREEN, width=16); d.ellipse((820,490,850,520), fill=GREEN); d.ellipse((1150,760,1180,790), fill=ORANGE)
    else:
        router(d, 360, 470); laptop(d, 1090, 500, .9); d.line((800,560,1050,560), fill=GREEN, width=16); d.ellipse((830,490,910,570), outline=GREEN, width=12); d.line((860,530,880,550), fill=GREEN, width=10); d.line((880,550,920,500), fill=GREEN, width=10)
    path = OUT / f"scene-{i:02d}" / f"scene-{i:02d}.png"
    path.parent.mkdir(parents=True, exist_ok=True); im.save(path)

for n in range(1, 9): make(n)
print(f"created {OUT}")
