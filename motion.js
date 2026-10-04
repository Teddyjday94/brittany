/* The Broski Bulletin: motion layer.
   Scroll progress, reveals, parallax, fizz cursor, magnetic buttons, card tilt, sticky header, page wipes.
   Everything is skipped for reduced-motion visitors; cursor effects run only on fine pointers. */
(function(){
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine=window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var root=document.documentElement;
  if(reduce) return;
  root.classList.add('motion');

  /* ---------- scroll progress + sticky header + parallax (one rAF loop) ---------- */
  var bar=document.createElement('div');bar.className='scroll-progress';bar.setAttribute('aria-hidden','true');document.body.appendChild(bar);
  var header=document.querySelector('.top');
  var heroLines=[].slice.call(document.querySelectorAll('.hero h1 .l1,.hero h1 .l2,.hero h1 .l3,.page-hero h1'));
  var drift=[].slice.call(document.querySelectorAll('.sec-head h2'));
  var plates=[].slice.call(document.querySelectorAll('.plate-art'));
  var burst=document.querySelector('.burst');
  var ticking=false,lastY=-1;
  function frame(){
    ticking=false;
    var y=window.scrollY,h=document.documentElement.scrollHeight-innerHeight;
    if(y===lastY)return;lastY=y;
    bar.style.transform='scaleX('+(h>0?Math.min(1,y/h):0)+')';
    if(header)header.classList.toggle('scrolled',y>60);
    heroLines.forEach(function(el,i){el.style.transform='translate3d('+(i%2?-1:1)*y*.06+'px,'+y*(.12+i*.07)+'px,0)'});
    drift.forEach(function(el){var r=el.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;
      var p=(r.top+r.height/2)/innerHeight-.5;el.style.transform='translate3d('+(p*-36)+'px,0,0)'});
    plates.forEach(function(el,i){var r=el.getBoundingClientRect();if(r.bottom<0||r.top>innerHeight)return;
      var p=(r.top+r.height/2)/innerHeight-.5;el.style.setProperty('--rot',((i?2:-1.5)+p*-5).toFixed(2)+'deg')});
    if(burst)burst.style.setProperty('--spin',(y*.25)+'deg');
  }
  function onScroll(){if(!ticking){ticking=true;requestAnimationFrame(frame)}}
  addEventListener('scroll',onScroll,{passive:true});addEventListener('resize',onScroll);frame();

  /* ---------- reveal on scroll (elements stay visible at rest; they animate as they enter) ---------- */
  var groups=['.sec-head','.stat','.door','.vid','.fotd','.plate-art','.plate-text','.card','.follow a','.ep','.guest','.fact','.lore article','.act','.disc','.t','.decree','.chart','.influences span','.quiz','.shield-wrap','.hero-stats div','.tools'];
  var targets=document.querySelectorAll(groups.join(','));
  var seen=new WeakSet();
  var io=new IntersectionObserver(function(entries){
    var batch=entries.filter(function(e){return e.isIntersecting&&!seen.has(e.target)});
    batch.forEach(function(e,k){var el=e.target;seen.add(el);
      el.style.setProperty('--d',Math.min(k,8)*70+'ms');
      el.classList.remove('reveal');void el.offsetWidth;el.classList.add('reveal');
      io.unobserve(el)});
  },{rootMargin:'0px 0px -6% 0px',threshold:0});
  [].forEach.call(targets,function(el){
    var r=el.getBoundingClientRect();
    if(r.top<innerHeight*.94){seen.add(el);return} /* already in view on load: leave it alone */
    io.observe(el)});

  /* ---------- page wipe between pages ---------- */
  var wipe=document.createElement('div');wipe.className='wipe';wipe.setAttribute('aria-hidden','true');
  wipe.innerHTML='<span>Broadcasting</span>';document.body.appendChild(wipe);
  var arriving=false;try{arriving=sessionStorage.getItem('bb-wipe')==='1';sessionStorage.removeItem('bb-wipe')}catch(e){}
  if(arriving){wipe.classList.add('cover');requestAnimationFrame(function(){requestAnimationFrame(function(){wipe.classList.add('out')})})}
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;
    var href=a.getAttribute('href');
    if(!/^[a-z]+\.html(#.*)?$/.test(href)||a.target==='_blank'||e.metaKey||e.ctrlKey||e.shiftKey||e.button!==0)return;
    if(href.split('#')[0]===location.pathname.split('/').pop()&&href.indexOf('#')>-1)return;
    e.preventDefault();try{sessionStorage.setItem('bb-wipe','1')}catch(err){}
    wipe.classList.remove('out');wipe.classList.add('cover','in');
    setTimeout(function(){location.href=href},420)});
  addEventListener('pageshow',function(ev){if(ev.persisted){wipe.classList.remove('cover','in','out')}});

  if(!fine) return;

  /* ---------- fizz cursor ---------- */
  root.classList.add('fizz-cursor');
  var ring=document.createElement('div');ring.className='cur-ring';
  var dot=document.createElement('div');dot.className='cur-dot';
  ring.setAttribute('aria-hidden','true');dot.setAttribute('aria-hidden','true');
  document.body.appendChild(ring);document.body.appendChild(dot);
  var mx=innerWidth/2,my=innerHeight/2,rx=mx,ry=my,lastBubble=0,visible=false;
  var COLORS=['#FFC21A','#FF2E93','#19D3C0','#FF7A1A','#FFF4E2'];
  addEventListener('mousemove',function(e){mx=e.clientX;my=e.clientY;
    if(!visible){visible=true;ring.style.opacity=dot.style.opacity='1';rx=mx;ry=my}
    dot.style.transform='translate3d('+mx+'px,'+my+'px,0)';
    var now=performance.now();
    if(now-lastBubble>45){lastBubble=now;var b=document.createElement('span');b.className='cur-bubble';
      var s=4+Math.random()*7;b.style.cssText='left:'+mx+'px;top:'+my+'px;width:'+s+'px;height:'+s+'px;background:'+COLORS[Math.floor(Math.random()*COLORS.length)]+';--dx:'+(Math.random()*24-12)+'px';
      document.body.appendChild(b);setTimeout(function(){b.remove()},900)}
  },{passive:true});
  document.addEventListener('mouseleave',function(){visible=false;ring.style.opacity=dot.style.opacity='0'});
  (function loop(){rx+=(mx-rx)*.18;ry+=(my-ry)*.18;ring.style.transform='translate3d('+rx+'px,'+ry+'px,0)';requestAnimationFrame(loop)})();
  var HOT='a,button,input,select,label,[role="button"]';
  document.addEventListener('mouseover',function(e){if(e.target.closest(HOT))ring.classList.add('hot')});
  document.addEventListener('mouseout',function(e){if(e.target.closest(HOT)&&!(e.relatedTarget&&e.relatedTarget.closest&&e.relatedTarget.closest(HOT)))ring.classList.remove('hot')});
  document.addEventListener('mousedown',function(){ring.classList.add('press')});
  document.addEventListener('mouseup',function(){ring.classList.remove('press')});

  /* ---------- magnetic buttons ---------- */
  [].forEach.call(document.querySelectorAll('.btn,.nav a,.chip'),function(el){
    el.addEventListener('mousemove',function(e){var r=el.getBoundingClientRect();
      var x=(e.clientX-r.left-r.width/2)*.22,y=(e.clientY-r.top-r.height/2)*.3;
      el.style.translate=x.toFixed(1)+'px '+y.toFixed(1)+'px'});
    el.addEventListener('mouseleave',function(){el.style.translate=''})});

  /* ---------- 3D tilt cards ---------- */
  [].forEach.call(document.querySelectorAll('.door,.vid,.stat,.card,.tv,.disc,.act,.fotd,.shield-wrap'),function(el){
    el.classList.add('tilt');
    el.addEventListener('mousemove',function(e){var r=el.getBoundingClientRect();
      var px=(e.clientX-r.left)/r.width-.5,py=(e.clientY-r.top)/r.height-.5;
      el.style.setProperty('--tx',(py*-7).toFixed(2)+'deg');el.style.setProperty('--ty',(px*9).toFixed(2)+'deg');
      el.style.setProperty('--gx',(px*100+50).toFixed(1)+'%');el.style.setProperty('--gy',(py*100+50).toFixed(1)+'%')});
    el.addEventListener('mouseleave',function(){el.style.setProperty('--tx','0deg');el.style.setProperty('--ty','0deg')})});
})();
