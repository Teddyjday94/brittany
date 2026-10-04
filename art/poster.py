import math, random
from PIL import Image, ImageDraw, ImageFont
F="/root/.claude/skills/synced/f92399da-8174-40a2-a9d7-c58560b9068e_d2b7f5bd-daf3-4f6c-b34c-4915dbfa094f/canvas-design/canvas-fonts/"
S=3; W,H=1200,1600
VIOLET=(91,31,224); GOLD=(255,194,26); PINK=(255,46,147); TEAL=(25,211,192); INK=(36,8,46); CREAM=(255,244,226); TANG=(255,122,26)
im=Image.new("RGB",(W*S,H*S),VIOLET); d=ImageDraw.Draw(im)
def C(x,y,r,fill=None,outline=None,w=0):
    d.ellipse([(x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S],fill=fill,outline=outline,width=int(w*S))
def L(x1,y1,x2,y2,col,w): d.line([x1*S,y1*S,x2*S,y2*S],fill=col,width=max(1,int(w*S)))
def font(n,sz): return ImageFont.truetype(F+n,int(sz*S))
random.seed(519)

M=84
# --- ruler ticks, left & bottom ---
for i,y in enumerate(range(M,H-M+1,16)):
    long=(y-M)%160==0
    L(40,y,40+(18 if long else 8),y,CREAM if long else (205,190,250),1.2 if long else .8)
for x in range(M,W-M+1,16):
    long=(x-M)%160==0
    L(x,H-40,x,H-40-(18 if long else 8),CREAM if long else (205,190,250),1.2 if long else .8)

cx,cy,R=600,536,318
# --- broadcast arcs (pink), measured intervals, two flanks ---
for k in range(7):
    r=R+46+k*26
    w=2.2 if k%3==0 else 1.1
    for a0,a1 in [(202,232),(308,338)]:
        d.arc([(cx-r)*S,(cy-r)*S,(cx+r)*S,(cy+r)*S],a0,a1,fill=PINK,width=int(w*S))

# --- seal ---
C(cx,cy,R+14,fill=INK)
C(cx,cy,R,fill=GOLD)
# hairline inner ring
C(cx,cy,R-22,outline=INK,w=1.4)
# packed bubbles, larger at bottom, rising and shrinking
inner=R-36
pts=[]; grid={}; cell=30
def ok(x,y,r):
    gx,gy=int(x//cell),int(y//cell)
    for i in range(gx-1,gx+2):
        for j in range(gy-1,gy+2):
            for (px,py,pr) in grid.get((i,j),[]):
                if (px-x)**2+(py-y)**2 < (pr+r+2.2)**2: return False
    return True
for t in range(90000):
    a=random.random()*2*math.pi; rr=inner*math.sqrt(random.random())
    x=cx+rr*math.cos(a); y=cy+rr*math.sin(a)
    f=(y-(cy-inner))/(2*inner)       # 0 top .. 1 bottom
    rmax=2.2+f**1.6*13.5
    r=rmax*(0.55+0.45*random.random())
    if math.hypot(x-cx,y-cy)+r>inner: continue
    if f<0.18 and random.random()<0.55: continue   # thinning at the surface
    if ok(x,y,r):
        pts.append((x,y,r)); grid.setdefault((int(x//cell),int(y//cell)),[]).append((x,y,r))
pal=[TANG]*7+[CREAM]*2+[PINK]
for (x,y,r) in pts:
    col=random.choice(pal)
    C(x,y,r,fill=col)
    if r>7: C(x-r*.33,y-r*.33,r*.22,fill=CREAM if col!=CREAM else GOLD)

# --- crown of rising columns ---
base_y=1128; heights=[150,100,206,100,150]; xs=[396,498,600,702,804]
for x,h in zip(xs,heights):
    y=base_y-12; r=15.0
    while y-2*r>base_y-h:
        C(x,y-r,r,fill=GOLD); y-=2*r+5; r=max(3.4,r*0.83)
    C(x,y-10,9,fill=TEAL,outline=INK,w=1.6)
# band
d.rounded_rectangle([352*S,base_y*S,848*S,(base_y+26)*S],radius=13*S,fill=GOLD,outline=INK,width=int(2*S))
for x in range(372,840,22): C(x+4,base_y+13,3.2,fill=INK)

# --- type ---
big=font("BigShoulders-Bold.ttf",156)
b1,b2=1346,1488
d.text((M*S,b1*S),"FIRST",font=big,fill=CREAM,anchor="ls")
d.text((M*S,b2*S),"SIP.",font=big,fill=GOLD,anchor="ls")
mono=font("DMMono-Regular.ttf",13); monob=font("DMMono-Regular.ttf",15)
d.text((M*S,M*S),"MINISTRY OF EFFERVESCENCE",font=monob,fill=CREAM)
d.text((M*S,(M+24)*S),"PLATE VIII  ·  MMXIX",font=mono,fill=(205,190,250))
tr="No. 0519"; tw=d.textlength(tr,font=monob); d.text(((W-M)*S-tw,M*S),tr,font=monob,fill=GOLD)
lab=["FIG. 01","RISE OBSERVED","FROM A SINGLE SIP","n = 1,997"]
yy=1488-3*24
for i,t in enumerate(lab):
    f=monob if i==0 else mono
    d.text(((W-M)*S,yy*S),t,font=f,fill=GOLD if i==0 else CREAM,anchor="rs"); yy+=24
# small figure marker beside seal
L(cx+R+20,cy,cx+R+60,cy,CREAM,1)
d.text(((cx+R+66)*S,(cy-9)*S),"A",font=monob,fill=CREAM)
L(cx-R-60,cy+140,cx-R-14,cy+140,CREAM,1)
tw=d.textlength("B",font=monob); d.text(((cx-R-66)*S-tw,(cy+131)*S),"B",font=monob,fill=CREAM)

im=im.resize((W,H),Image.LANCZOS)
im.save("/home/claude/art/first-sip-poster.png",optimize=True)
print(len(pts))
