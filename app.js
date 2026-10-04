/* The Broski Bulletin: shared behavior. Each feature runs only on pages that contain its markup. */
(function(){
  var $=function(id){return document.getElementById(id)};
  var reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function each(sel,fn){Array.prototype.forEach.call(document.querySelectorAll(sel),fn)}
  function press(group,btn){each(group,function(x){x.setAttribute('aria-pressed',String(x===btn))})}
  function json(id){var n=$(id);try{return n?JSON.parse(n.textContent):null}catch(e){return null}}
  function scrollTo(el){el.scrollIntoView({behavior:reduce?'auto':'smooth',block:'center'})}
  function copy(text,ok,fail){try{navigator.clipboard.writeText(text).then(ok,fail)}catch(e){fail()}}
  function yt(q){return 'https://www.youtube.com/results?search_query='+encodeURIComponent(q).replace(/%20/g,'+')}
  function shuffled(a){a=a.slice();for(var i=a.length-1;i>0;i--){var k=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[k];a[k]=t}return a}

  /* ---------- Back to top (every page) ---------- */
  var top=document.createElement('button');top.type='button';top.className='to-top';top.hidden=true;top.textContent='↑';top.setAttribute('aria-label','Back to top');
  document.body.appendChild(top);
  top.addEventListener('click',function(){window.scrollTo({top:0,behavior:reduce?'auto':'smooth'});var h=document.querySelector('.seal');if(h)h.focus({preventScroll:true})});
  var topTick=false;addEventListener('scroll',function(){if(topTick)return;topTick=true;requestAnimationFrame(function(){topTick=false;top.hidden=window.scrollY<700})},{passive:true});

  /* ---------- Carbonated Ascent: generative fizz (home hero) ---------- */
  if($('fizz') && typeof p5!=='undefined'){
    new p5(function(p){
      var host,parts=[],rings=[];
      var pal=[[255,194,26],[255,46,147],[25,211,192],[255,122,26],[255,244,226]],wts=[3,3,2,2,1];
      function pick(){var t=p.random(11),a=0;for(var i=0;i<wts.length;i++){a+=wts[i];if(t<a)return pal[i]}return pal[0]}
      function spawn(any){var r=p.random()<.14?p.random(6,10):p.random(2,5.5);return{x:p.random(p.width),y:any?p.random(p.height):p.height+r+p.random(60),r:r,v:.22+r*.085,c:pick(),s:p.random(1000)}}
      function count(){return Math.max(60,Math.min(170,Math.floor(p.width*p.height/9000)))}
      p.setup=function(){host=$('fizz');p.pixelDensity(Math.min(2,window.devicePixelRatio||1));p.createCanvas(host.clientWidth,host.clientHeight).parent(host);p.randomSeed(519);p.noiseSeed(519);for(var i=0;i<count();i++)parts.push(spawn(true));if(reduce)p.noLoop()};
      p.windowResized=function(){p.resizeCanvas(host.clientWidth,host.clientHeight);if(reduce)p.redraw()};
      p.draw=function(){
        p.clear();p.noStroke();var t=p.frameCount*.004,mx=p.mouseX,my=p.mouseY;
        for(var i=0;i<parts.length;i++){
          var b=parts[i];
          if(!reduce){
            var n=p.noise(b.s,b.y*.004,t)-.5+(p.noise(b.s+50,b.y*.012,t*2)-.5)*.4;
            b.x+=n*1.7*(1+b.r*.08);b.y-=b.v;
            var dx=b.x-mx,dy=b.y-my,d2=dx*dx+dy*dy;
            if(d2<8100&&d2>1){var d=Math.sqrt(d2),f=(90-d)/90*2.4;b.x+=dx/d*f;b.y+=dy/d*f}
            if(b.y<-b.r){rings.push({x:b.x,y:Math.max(4,b.r),r:b.r,a:200});parts[i]=spawn(false);continue}
          }
          p.fill(b.c[0],b.c[1],b.c[2]);p.circle(b.x,b.y,b.r*2);
          if(b.r>3.5){var hc=b.c===pal[4]?pal[0]:pal[4];p.fill(hc[0],hc[1],hc[2]);p.circle(b.x-b.r*.32,b.y-b.r*.32,b.r*.5)}
        }
        p.noFill();
        for(var j=rings.length-1;j>=0;j--){var g=rings[j];p.stroke(255,46,147,g.a);p.strokeWeight(1.5);p.circle(g.x,g.y,g.r*2);g.r+=.9;g.a-=9;if(g.a<=0)rings.splice(j,1)}
      };
    });
  }

  /* ---------- Click-to-play YouTube (hosted build only) ---------- */
  /* YouTube refuses embeds from pages opened as local files (error 153: no referrer).
     On file:// we open the video on YouTube instead and explain why. */
  var localFile=location.protocol==='file:';
  if(localFile) each('button.yt[data-id],button.yt[data-list]',function(b){
    var note=document.createElement('p');note.className='pl-note local-note';
    note.textContent='You opened this page as a file, so YouTube plays it in a new tab. Videos play right here once the site is on a web address.';
    var host=b.closest('.playlist')||b.closest('.vid');if(host&&!host.querySelector('.local-note'))host.appendChild(note)});
  each('button.yt[data-id],button.yt[data-list]',function(b){b.addEventListener('click',function(){
    if(localFile){window.open(b.dataset.id?'https://www.youtube.com/watch?v='+b.dataset.id:'https://www.youtube.com/playlist?list='+b.dataset.list,'_blank','noopener');return}
    var f=document.createElement('iframe');
    f.src=b.dataset.id?'https://www.youtube-nocookie.com/embed/'+b.dataset.id+'?autoplay=1&rel=0'
                      :'https://www.youtube-nocookie.com/embed/videoseries?list='+b.dataset.list+'&autoplay=1&rel=0';
    f.title=b.getAttribute('aria-label')||'YouTube video';
    f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.referrerPolicy='strict-origin-when-cross-origin';f.allowFullscreen=true;
    var w=document.createElement('div');w.className=b.className;w.appendChild(f);b.replaceWith(w);f.focus()})});

  /* ---------- Emergency broadcast TV ---------- */
  var tvEps=json('tv-data');
  if(tvEps && $('tv-next')){
    var cur=58, order=[], hist=[], typing=null, scan=null;
    var refill=function(){order=shuffled(tvEps.map(function(_,i){return i}).filter(function(i){return i!==cur}))};
    var tvShow=function(i){var e=tvEps[i];cur=i;
      $('tv-ch').textContent='CH '+String(e.n).padStart(3,'0');$('tv-date').textContent=e.d;$('tv-tag').textContent='Season '+e.s+' · '+e.g;
      $('tv-find').href=yt('Broski Report '+e.t);$('tv-ep').href='report.html#ep-'+String(e.n).padStart(3,'0');
      $('tv-prev').disabled=!hist.length;
      var h=$('tv-headline');clearInterval(typing);
      if(reduce){h.textContent=e.t;return}
      var scr=$('tv-screen');scr.classList.remove('tuning');void scr.offsetWidth;scr.classList.add('tuning');
      var n=0;h.textContent='';typing=setInterval(function(){n++;h.textContent=e.t.slice(0,n);if(n>=e.t.length)clearInterval(typing)},28)};
    var next=function(){if(!order.length)refill();hist.push(cur);if(hist.length>50)hist.shift();tvShow(order.pop())};
    var stopScan=function(){clearInterval(scan);scan=null;$('tv-scan').setAttribute('aria-pressed','false');$('tv-scan').textContent='Scan'};
    $('tv-next').addEventListener('click',function(){stopScan();next()});
    $('tv-prev').addEventListener('click',function(){stopScan();if(hist.length)tvShow(hist.pop())});
    $('tv-scan').addEventListener('click',function(){
      if(scan){stopScan();return}
      next();scan=setInterval(next,4200);this.setAttribute('aria-pressed','true');this.textContent='Stop scan'});
    $('tv-screen').addEventListener('click',function(){stopScan();next()});
    $('tv-screen').style.cursor='pointer';$('tv-screen').title='Click to change the channel';
    document.addEventListener('visibilitychange',function(){if(document.hidden)stopScan()});
  }

  /* ---------- Fact of the day ---------- */
  var facts=json('facts-data');
  if(facts && $('fotd-next')){
    var day=Math.floor(Date.now()/864e5), idx=day%facts.length;
    var showFact=function(i){var f=facts[i];$('fotd-text').textContent=f.t;$('fotd-src').textContent=f.s;$('fotd-src').href=f.u};
    showFact(idx);
    $('fotd-next').addEventListener('click',function(){var n=idx;while(n===idx)n=Math.floor(Math.random()*facts.length);idx=n;showFact(idx)});
  }

  /* ---------- Citizenship papers ---------- */
  if($('citForm')){
    var posts=["Bureau of Kombucha Affairs","Department of Hozier Studies","Ministry of Unhinged Lore","Office of Medieval Times Diplomacy","Royal Court Dragon Keeper","Broski Nation Space Program","Bureau of Harry Styles Intelligence","Council of Green Screen Operations","Broski Nation Special Ops","Royal Ballet School Faculty","Irishman Recon Unit","Santa Investigation Task Force"];
    var clears=["Hozier Level","Throne Room Access","Kombucha Tolerant","Top Secret Second Account","Fur Cloak Certified","Council Seat Pending","Goblet Clearance"];
    var duties=["Listen every Tuesday. No exceptions.","Defend Beyoncé at all costs.","Report all dragon sightings to the Court.","Never trust a first sip.","Keep the propaganda broadcasts flowing.","Flirt with the knights responsibly.","Learn one history fact per week, minimum.","Stream the singles. Twice.","Keep an eye on Santa."];
    var hash=function(s){var h=2166136261;for(var i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0};
    var current=null;
    $('citForm').addEventListener('submit',function(e){e.preventDefault();var n=$('citName').value.trim();
      if(!n){$('citStatus').textContent='Enter a name so the Ministry knows who to file.';return}
      var h=hash(n.toLowerCase());
      current={name:n,post:posts[h%posts.length],clear:clears[(h>>>4)%clears.length],duty:duties[(h>>>9)%duties.length],no:String(h%9999999).padStart(7,'0')};
      $('cName').textContent=current.name;$('cPost').textContent=current.post;$('cClear').textContent=current.clear;$('cDuty').textContent=current.duty;$('cNo').textContent='CITIZEN NO. '+current.no;
      $('citStatus').textContent='Papers issued. Welcome to Broski Nation, '+n+'.'});
    $('copyCard').addEventListener('click',function(){
      var c=current||{name:'Loyal Subject',post:$('cPost').textContent,clear:$('cClear').textContent,duty:$('cDuty').textContent,no:'0000519'};
      var txt='BROSKI NATION CITIZENSHIP PAPERS\n'+c.name+'\nAssigned to: '+c.post+'\nClearance: '+c.clear+'\nDuty: '+c.duty+'\nCitizen No. '+c.no+' (unofficial fan card)';
      var fail=function(){$('citStatus').textContent='Copy was blocked here. Select the card text and copy it manually.'};
      try{navigator.clipboard.writeText(txt).then(function(){$('citStatus').textContent='Copied. Go share your papers.'},fail)}catch(err){fail()}});
  }

  /* ---------- Episode archive ---------- */
  if($('archive-list')){
    var list=$('archive-list');
    var rows=[].slice.call(list.querySelectorAll('.ep')),season='all',tag='all',q='',all=false,LIMIT=24,newest=false;
    var apply=function(){
      var match=rows.filter(function(r){return(season==='all'||r.dataset.s===season)&&(tag==='all'||r.dataset.g===tag)&&(!q||r.dataset.t.indexOf(q)>-1)});
      if(newest)match.reverse();
      var filtering=season!=='all'||tag!=='all'||q;
      rows.forEach(function(r){r.hidden=true;r.classList.remove('picked')});
      match.forEach(function(r,i){r.hidden=!(all||filtering||i<LIMIT)});
      var shown=match.filter(function(r){return!r.hidden}).length;
      $('ep-count').textContent='Showing '+shown+' of '+match.length+(filtering?' matches':'');
      $('ep-empty').hidden=match.length>0;
      $('ep-more').hidden=all||filtering||match.length<=LIMIT;
      return match};
    var resetFilters=function(){season='all';tag='all';q='';$('ep-search').value='';
      press('[data-season]',document.querySelector('[data-season="all"]'));press('[data-tag]',document.querySelector('[data-tag="all"]'))};
    var deb=null;
    $('ep-search').addEventListener('input',function(){var v=this.value;clearTimeout(deb);deb=setTimeout(function(){q=v.trim().toLowerCase();apply()},120)});
    $('ep-search').addEventListener('keydown',function(e){if(e.key==='Escape'){this.value='';q='';apply()}});
    each('[data-season]',function(b){b.addEventListener('click',function(){season=b.dataset.season;press('[data-season]',b);apply()})});
    each('[data-tag]',function(b){b.addEventListener('click',function(){tag=b.dataset.tag;press('[data-tag]',b);apply()})});
    $('ep-more').addEventListener('click',function(){all=true;apply()});
    $('ep-sort').addEventListener('click',function(){newest=!newest;this.setAttribute('aria-pressed',String(newest));this.textContent=newest?'Oldest first':'Newest first';
      var ordered=rows.slice();if(newest)ordered.reverse();ordered.forEach(function(r){list.appendChild(r)});apply()});
    $('ep-random').addEventListener('click',function(){var m=apply();if(!m.length)return;var r=m[Math.floor(Math.random()*m.length)];r.hidden=false;r.classList.add('picked');scrollTo(r)});
    var goHash=function(){var m=/^#ep-(\d{3})$/.exec(location.hash);if(!m)return;var r=$('ep-'+m[1]);if(!r)return;
      resetFilters();all=true;apply();r.classList.add('picked');setTimeout(function(){scrollTo(r)},60)};
    addEventListener('hashchange',goHash);
    apply();goHash();
  }

  /* ---------- Royal Court roll ---------- */
  if($('roll-list')){
    var gs=[].slice.call(document.querySelectorAll('#roll-list .guest')),cs='all',gq='';
    var gapply=function(){var m=gs.filter(function(g){return(cs==='all'||g.dataset.s===cs)&&(!gq||g.dataset.n.indexOf(gq)>-1)});
      gs.forEach(function(g){g.hidden=m.indexOf(g)<0;g.classList.remove('picked')});
      $('g-count').textContent=m.length+(m.length===1?' knight':' knights');$('g-empty').hidden=m.length>0;return m};
    $('g-search').addEventListener('input',function(){gq=this.value.trim().toLowerCase();gapply()});
    each('[data-cs]',function(b){b.addEventListener('click',function(){cs=b.dataset.cs;press('[data-cs]',b);gapply()})});
    $('g-random').addEventListener('click',function(){var m=gapply();if(!m.length)return;var g=m[Math.floor(Math.random()*m.length)];g.classList.add('picked');scrollTo(g);g.focus({preventScroll:true})});
    $('g-search').addEventListener('keydown',function(e){if(e.key==='Escape'){this.value='';gq='';gapply()}});
  }

  /* ---------- Coat of arms builder ---------- */
  var icons=json('icon-data');
  if(icons && $('shield')){
    var state=[{i:'crown',c:'#FF2E93'},{i:'bottle',c:'#FFC21A'},{i:'mic',c:'#19D3C0'},{i:'dragon',c:'#5B1FE0'}];
    var light={'#FFC21A':1,'#19D3C0':1,'#FF7A1A':1};
    var path='M20 20 H220 V140 C220 205 170 245 120 265 C70 245 20 205 20 140 Z';
    var cells=[[20,20],[120,20],[20,140],[120,140]];
    var draw=function(){
      var s='<defs><clipPath id="sh"><path d="'+path+'"/></clipPath></defs><g clip-path="url(#sh)">';
      cells.forEach(function(xy,k){var st=state[k],ink=light[st.c]?'#24082E':'#FFF4E2';
        s+='<rect x="'+xy[0]+'" y="'+xy[1]+'" width="100" height="'+(k<2?120:130)+'" fill="'+st.c+'"/>';
        s+='<svg x="'+(xy[0]+22)+'" y="'+(xy[1]+(k<2?32:22))+'" width="56" height="56" viewBox="0 0 24 24" style="color:'+ink+'">'+icons[st.i]+'</svg>'});
      s+='</g><path d="M120 20V265M20 140H220" stroke="#24082E" stroke-width="5"/><path d="'+path+'" fill="none" stroke="#24082E" stroke-width="8"/>';
      s+='<path d="M95 10 L105 0 L120 8 L135 0 L145 10 Z" fill="#FFC21A" stroke="#24082E" stroke-width="3"/>';
      $('shield').innerHTML=s;
      $('motto-out').textContent=$('motto').value.trim()||'Long live the Supreme Leader'};
    each('.icon-btn',function(b){b.addEventListener('click',function(){var k=+b.dataset.q;state[k].i=b.dataset.icon;press('.icon-btn[data-q="'+k+'"]',b);draw()})});
    each('.swatch',function(b){b.addEventListener('click',function(){var k=+b.dataset.q;state[k].c=b.dataset.color;press('.swatch[data-q="'+k+'"]',b);draw()})});
    $('motto').addEventListener('input',draw);
    $('arms-random').addEventListener('click',function(){
      var names=Object.keys(icons),cols=['#FF2E93','#FFC21A','#5B1FE0','#19D3C0','#FF7A1A','#33105F'];
      state.forEach(function(st,k){st.i=names[Math.floor(Math.random()*names.length)];st.c=cols[Math.floor(Math.random()*cols.length)];
        each('.icon-btn[data-q="'+k+'"]',function(x){x.setAttribute('aria-pressed',String(x.dataset.icon===st.i))});
        each('.swatch[data-q="'+k+'"]',function(x){x.setAttribute('aria-pressed',String(x.dataset.color===st.c))})});
      draw()});
    var NAMES={'#FF2E93':'pink','#FFC21A':'gold','#5B1FE0':'violet','#19D3C0':'turquoise','#FF7A1A':'tangerine','#33105F':'royal plum'};
    var QN=['upper left','upper right','lower left','lower right'];
    var blazon=function(){return 'My Royal Court coat of arms: '+state.map(function(st,k){return QN[k]+', a '+st.i+' on '+NAMES[st.c]}).join('; ')+'. Motto: "'+$('motto-out').textContent+'"'};
    $('arms-copy').addEventListener('click',function(){copy(blazon(),function(){$('arms-status').textContent='Blazon copied. Present it to the court.'},function(){$('arms-status').textContent='Copy was blocked here. '+blazon()})});
    if($('arms-dl'))$('arms-dl').addEventListener('click',function(){
      var svg=$('shield').cloneNode(true);svg.setAttribute('xmlns','http://www.w3.org/2000/svg');svg.setAttribute('width','720');svg.setAttribute('height','840');
      var url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'}));
      var img=new Image();img.onload=function(){var c=document.createElement('canvas');c.width=800;c.height=1000;var x=c.getContext('2d');
        x.fillStyle='#FFF4E2';x.fillRect(0,0,800,1000);x.drawImage(img,40,30,720,840);
        x.fillStyle='#33105F';x.font='44px "UnifrakturMaguntia", Georgia, serif';x.textAlign='center';x.fillText($('motto-out').textContent,400,940,740);
        URL.revokeObjectURL(url);c.toBlob(function(b){var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='my-coat-of-arms.png';document.body.appendChild(a);a.click();a.remove();
          $('arms-status').textContent='Saved my-coat-of-arms.png.'})};
      img.onerror=function(){$('arms-status').textContent='Download failed in this browser. Try a screenshot instead.'};img.src=url});
    draw();
  }

  /* ---------- Fact files ---------- */
  if($('fact-list')){
    var fcs=[].slice.call(document.querySelectorAll('#fact-list .fact')),fcat='all',fq='';
    var fapply=function(){var m=fcs.filter(function(f){return(fcat==='all'||f.dataset.c===fcat)&&(!fq||f.textContent.toLowerCase().indexOf(fq)>-1)});
      fcs.forEach(function(f){f.hidden=m.indexOf(f)<0;f.classList.remove('picked')});
      $('f-count').textContent=m.length+(m.length===1?' fact':' facts');$('f-empty').hidden=m.length>0;return m};
    each('[data-fc]',function(b){b.addEventListener('click',function(){fcat=b.dataset.fc;press('[data-fc]',b);fapply()})});
    $('f-search').addEventListener('input',function(){fq=this.value.trim().toLowerCase();fapply()});
    $('f-search').addEventListener('keydown',function(e){if(e.key==='Escape'){this.value='';fq='';fapply()}});
    $('f-random').addEventListener('click',function(){var m=fapply();if(!m.length)return;var f=m[Math.floor(Math.random()*m.length)];f.classList.add('picked');scrollTo(f)});
    each('.copy-fact',function(b){b.addEventListener('click',function(){var card=b.closest('.fact');
      var txt=card.querySelector('p').textContent+' (via The Broski Bulletin, source: '+card.querySelector('.src').textContent.replace(' ↗','')+')';
      copy(txt,function(){b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1600)},function(){b.textContent='Blocked';setTimeout(function(){b.textContent='Copy'},1600)})})});
  }

  /* ---------- Citizenship exam ---------- */
  var Q0=json('quiz-data');
  if(Q0 && $('quiz-box')){
    var Q,qi,score,missed,answered;
    var RANKS=[[0,"Tourist","You wandered in for the kombucha meme. Stay a while and read the fact files."],[5,"Loyal Subject","Solid. You listen on Tuesdays, mostly."],[8,"Royal Council Member","Knighted. You could pass the coat of arms round."],[11,"Supreme Leader's Right Hand","Terrifying. Stanley should be worried about his job."]];
    var start=function(){
      Q=shuffled(Q0).map(function(item){var idx=shuffled(item[1].map(function(_,i){return i}));
        return [item[0],idx.map(function(i){return item[1][i]}),idx.indexOf(item[2]),item[3]]});
      qi=0;score=0;missed=[];$('q-stage').hidden=false;$('q-result').hidden=true;renderQ()};
    var renderQ=function(){var item=Q[qi];answered=false;
      $('q-num').textContent='Question '+(qi+1)+' of '+Q.length+' · Score '+score;$('q-bar').style.width=(qi/Q.length*100)+'%';
      $('q-text').textContent=item[0];$('q-explain').textContent='';$('q-next').hidden=true;
      var box=$('q-answers');box.innerHTML='';
      item[1].forEach(function(a,k){var b=document.createElement('button');b.type='button';b.className='answer';
        var kb=document.createElement('kbd');kb.textContent=String(k+1);b.appendChild(kb);b.appendChild(document.createTextNode(a));
        b.addEventListener('click',function(){pick(k)});box.appendChild(b)})};
    var pick=function(k){if(answered)return;answered=true;var item=Q[qi],box=$('q-answers');
      [].forEach.call(box.children,function(x,j){x.disabled=true;if(j===item[2])x.classList.add('right')});
      if(k===item[2]){score++;$('q-explain').textContent='Correct. '+item[3]}
      else{box.children[k].classList.add('wrong');$('q-explain').textContent='Not quite. '+item[3];missed.push([item[0],item[1][item[2]]])}
      $('q-num').textContent='Question '+(qi+1)+' of '+Q.length+' · Score '+score;
      $('q-next').textContent=qi===Q.length-1?'See my rank':'Next question';$('q-next').hidden=false;$('q-next').focus({preventScroll:true})};
    var finish=function(){
      $('q-stage').hidden=true;$('q-result').hidden=false;$('q-bar').style.width='100%';$('q-num').textContent='Exam complete';
      var r=RANKS[0];RANKS.forEach(function(x){if(score>=x[0])r=x});
      $('q-score').textContent=score+'/'+Q.length;$('q-rank').textContent=r[1];$('q-blurb').textContent=r[2];
      var rv=$('q-review');rv.innerHTML='';
      if(missed.length){var h=document.createElement('p');h.className='eyebrow';h.textContent='Study these before your next exam';rv.appendChild(h);
        missed.forEach(function(m){var d=document.createElement('div');var b=document.createElement('b');b.textContent=m[0]+' ';d.appendChild(b);d.appendChild(document.createTextNode('Answer: '+m[1]));rv.appendChild(d)})}
      $('q-share').dataset.text='I scored '+score+'/'+Q.length+' on the Broski Nation citizenship exam. Rank: '+r[1]+'.';
      $('q-again').focus({preventScroll:true})};
    $('q-next').addEventListener('click',function(){qi++;if(qi<Q.length)renderQ();else finish()});
    $('q-again').addEventListener('click',start);
    $('q-share').addEventListener('click',function(){var b=this;copy(b.dataset.text,function(){b.textContent='Copied'},function(){b.textContent='Copy blocked'});setTimeout(function(){b.textContent='Copy my result'},1800)});
    $('quiz-box').addEventListener('keydown',function(e){
      if($('q-stage').hidden)return;var n=parseInt(e.key,10);
      if(n>=1&&n<=Q[qi][1].length){e.preventDefault();pick(n-1)}
      else if(e.key==='Enter'&&answered&&document.activeElement!==$('q-next')){e.preventDefault();$('q-next').click()}});
    start();
  }
})();
