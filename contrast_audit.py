"""Contrast audit: flags text whose color vs. its solid background is below WCAG AA."""
import os, sys
from playwright.sync_api import sync_playwright
BASE="file://"+os.path.dirname(os.path.abspath(__file__))+"/"
JS=r"""
() => {
 const lum=c=>{const v=c.map(x=>{x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4)});return .2126*v[0]+.7152*v[1]+.0722*v[2]};
 const parse=s=>{const m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(',').map(Number);return {c:p.slice(0,3),a:p.length>3?p[3]:1}};
 const bgOf=el=>{let layers=[];for(let e=el;e;e=e.parentElement){const cs=getComputedStyle(e);const b=parse(cs.backgroundColor);if(b&&b.a>0){layers.push(b);if(b.a>=1)break}}
   let c=[255,255,255];for(const l of layers.reverse()){c=c.map((x,i)=>x*(1-l.a)+l.c[i]*l.a)}return c};
 const out=[];const seen=new Set();
 document.querySelectorAll('body *').forEach(el=>{
   if(!el.offsetParent&&getComputedStyle(el).position!=='fixed')return;
   const own=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim().length>1);if(!own)return;
   if(el.closest('svg,.ticker,.cur-ring,.wipe,[aria-hidden="true"]'))return;
   const cs=getComputedStyle(el);if(cs.visibility==='hidden'||+cs.opacity===0)return;
   const fg=parse(cs.color);if(!fg)return;let op=1;for(let e=el;e;e=e.parentElement){op*=+getComputedStyle(e).opacity}
   const bg=bgOf(el);const f=fg.c.map((x,i)=>x*fg.a*op+bg[i]*(1-fg.a*op));
   const L1=lum(f),L2=lum(bg);const r=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
   const size=parseFloat(cs.fontSize),w=+cs.fontWeight;const large=size>=24||(size>=18.66&&w>=700);
   const need=large?3:4.5;
   if(r<need){const key=el.className+'|'+el.tagName+'|'+cs.color+'|'+bg;if(seen.has(key))return;seen.add(key);
     out.push({r:+r.toFixed(2),need,tag:el.tagName.toLowerCase()+(el.className&&typeof el.className==='string'?'.'+el.className.split(' ').join('.'):''),text:el.textContent.trim().slice(0,40),size,w,fg:cs.color,bg:'rgb('+bg.map(Math.round).join(',')+')'})}
 });return out}
"""
with sync_playwright() as p:
    b=p.chromium.launch()
    total=0
    for width in (1280,390):
        pg=b.new_page(viewport={"width":width,"height":900},reduced_motion="reduce")
        for name in ["index.html","report.html","court.html","music.html","lore.html"]:
            pg.goto(BASE+name); pg.wait_for_timeout(300)
            pg.evaluate("document.querySelectorAll('[hidden]').forEach(e=>{if(e.closest('#archive-list,#roll-list,#fact-list'))e.hidden=false})")
            res=pg.evaluate(JS)
            for r in res:
                total+=1; print(f"[{width}] {name}: {r['r']} < {r['need']}  {r['tag']}  '{r['text']}'  {r['fg']} on {r['bg']} ({r['size']}px/{r['w']})")
        pg.close()
    b.close()
print("issues:",total)
