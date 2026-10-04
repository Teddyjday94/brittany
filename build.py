"""Builds The Broski Bulletin pages from data.py. Run: python3 build.py"""
import json, html, os, re
from urllib.parse import quote_plus
EMBED = os.environ.get("EMBED") == "1"  # 1 = click-to-play YouTube embeds (for a real host like Vercel)
from collections import Counter
from data import SOURCES, FACTS, EPISODES, COURT, QUIZ, tag_for, EPISODE_VIDEO_IDS, COURT_VIDEO_IDS, MUSIC_VIDEO_IDS, REPORT_PLAYLIST, COURT_PLAYLIST

E = html.escape
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def fmt(d):
    y, m, dd = d.split("-")
    return f"{MONTHS[int(m)-1]} {int(dd)}, {y}"

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900&family=Familjen+Grotesk:ital,wght@0,400;0,500;0,700;1,400&family=DM+Mono:wght@400;500&family=UnifrakturMaguntia&family=Shrikhand&display=swap">'

SEAL = '<svg width="46" height="46" viewBox="0 0 44 44" aria-hidden="true"><circle cx="22" cy="22" r="20" fill="#FF2E93" stroke="#24082E" stroke-width="3"/><path d="M22 8 L25.5 18 L36 18.2 L27.8 24.5 L30.8 34.6 L22 28.6 L13.2 34.6 L16.2 24.5 L8 18.2 L18.5 18 Z" fill="#FFC21A" stroke="#24082E" stroke-width="1.5"/></svg>'

NAV = [("index.html","Home"),("report.html","The Report"),("court.html","Royal Court"),("music.html","Music"),("lore.html","Lore & Facts")]

TICK = "★ Public service announcement <b>★</b> New Broski Report episodes every Tuesday <b>★</b> The Royal Court is in session <b>★</b> Loyal subjects remain calm <b>★</b> Hydrate, but maybe not with kombucha <b>★</b> Broski Nation thanks you for your service"

def head(title, standalone):
    top = f"<title>{E(title)}</title>\n{FONTS}\n<link rel=\"stylesheet\" href=\"styles.css\">\n"
    if standalone:
        return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                + top + '</head>\n<body>\n')
    return top

def header(active):
    links = "\n".join(
        f'      <a href="{h}"{" aria-current=\"page\"" if h==active else ""}>{E(t)}</a>' for h,t in NAV)
    return f'''<div class="ticker" aria-hidden="true"><div class="ticker-track"><span>{TICK}</span><span>{TICK}</span></div></div>
<header class="top" id="top">
  <div class="wrap">
    <a class="seal" href="index.html">{SEAL}The Broski Bulletin</a>
    <nav class="nav" aria-label="Pages">
{links}
    </nav>
  </div>
</header>
'''

def footer(keys):
    items = "\n".join(f'        <li><a href="{SOURCES[k][1]}" target="_blank" rel="noopener">{E(SOURCES[k][0])}</a></li>' for k in keys)
    return f'''<footer class="band b-ink">
  <div class="wrap">
    <div>
      <p><strong>An unofficial fan site.</strong> The Broski Bulletin is made by fans and is not affiliated with or endorsed by Brittany Broski, The Broski Report, Royal Court, or Atlantic Records. We made every illustration here. We drew the facts from public interviews, show notes, and published reporting, and some may have changed. We stick to what she has shared on the record about her work and her tastes.</p>
    </div>
    <div>
      <p><strong>Sources for this page</strong></p>
      <ul>
{items}
      </ul>
    </div>
  </div>
</footer>
'''

def page(fname, title, active, body, src, standalone=True):
    out = head(title, standalone) + header(active) + "<main>\n" + body + "</main>\n" + footer(src)
    if fname == "index.html":
        out += '<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js"></script>\n'
    out += '<script src="app.js"></script>\n<script src="motion.js"></script>\n'
    if standalone:
        out += "</body>\n</html>\n"
    open(fname, "w").write(out)

def page_hero(band, kicker, h1, lede, stats):
    s = "".join(f'<div><b>{E(a)}</b><span>{E(b)}</span></div>' for a,b in stats)
    return f'''<section class="band {band} page-hero" aria-labelledby="page-title">
  <div class="wrap">
    <div>
      <span class="kicker">{E(kicker)}</span>
      <h1 id="page-title">{h1}</h1>
      <p class="lede">{lede}</p>
    </div>
    <div class="hero-stats">{s}</div>
  </div>
</section>
'''

def sec_head(h2, p, hid):
    return f'<div class="sec-head"><h2 id="{hid}">{h2}</h2><p>{p}</p></div>'



MIC_SVG = '<svg class="pl-icon" viewBox="0 0 24 24" width="64" height="64" aria-hidden="true"><rect x="8" y="2" width="8" height="13" rx="4" fill="#FFC21A" stroke="#24082E" stroke-width="1.6"/><path d="M8.5 6.5h7M8.5 9.5h7" stroke="#24082E" stroke-width="1.2"/><path d="M5 11a7 7 0 0014 0M12 18v4M8 22h8" fill="none" stroke="#FFC21A" stroke-width="2.2" stroke-linecap="round"/></svg>'
def watch_url(vid, list_id=None):
    return f"https://www.youtube.com/watch?v={vid}" + (f"&list={list_id}" if list_id else "")

def playlist_html(list_id, show, label, icon, variant):
    url = f"https://www.youtube.com/playlist?list={list_id}"
    if EMBED:
        return (f'<div class="playlist stage" data-list="{list_id}" data-variant="{variant}"><button class="yt pl-yt pl-{variant}" type="button" data-list="{list_id}" aria-label="Play the {E(show)} playlist">'
            f'{icon}<span class="play" aria-hidden="true"></span><span class="pl-label">{E(label)}</span></button>'
            f'<p class="pl-now" hidden></p>'
            f'<p class="pl-note">Plays here through YouTube. Pick any episode below to load it into this player. Prefer the app? <a href="{url}" target="_blank" rel="noopener">Open the playlist on YouTube ↗</a></p></div>')
    return (f'<a class="playlist pl-link" href="{url}" target="_blank" rel="noopener"><span class="yt pl-yt pl-{variant}" aria-hidden="true">'
        f'{icon}<span class="play"></span><span class="pl-label">{E(label)}</span></span>'
        f'<span class="pl-note">Opens the official {E(show)} playlist on YouTube ↗</span></a>')

VIDEOS = [
 ("fV70vvbaktk","Royal Court · Ep. 1","Orville Peck joins the court","b-court","hat"),
 ("GQL-T7LR8YU","Royal Court","Bob the Drag Queen joins the court","pink","crown"),
 ("c_afT5Inopg","Music","The Sun (official visualizer)","gold","sun"),
 ("s1zBQ8uGs2k","Music","Adore You (cover)","teal","heart"),
 ("hnI9UcccTIc","Disney Channel","Cartoonified with Phineas and Ferb","tang","rocket"),
]

_ink, _cr, _g, _p, _t = "#24082E", "#FFF4E2", "#FFC21A", "#FF2E93", "#19D3C0"
CARD_ART = {
 # cowboy hat with a fringe mask, for Orville Peck
 "hat": f'<svg class="card-art" viewBox="0 0 160 90"><path d="M22 58 C40 70 120 70 138 58 C130 66 112 74 80 74 C48 74 30 66 22 58Z" fill="{_g}" stroke="{_ink}" stroke-width="3"/><path d="M50 58 C50 30 56 20 66 22 C72 24 76 30 80 30 C84 30 88 24 94 22 C104 20 110 30 110 58Z" fill="{_g}" stroke="{_ink}" stroke-width="3"/><path d="M52 50 H108" stroke="{_p}" stroke-width="5"/><g stroke="{_cr}" stroke-width="2"><path d="M58 74v10M66 75v11M74 76v10M82 76v11M90 76v10M98 75v11M106 74v10"/></g></svg>',
 "crown": f'<svg class="card-art" viewBox="0 0 160 90"><path d="M40 70 L34 26 L60 46 L80 14 L100 46 L126 26 L120 70Z" fill="{_g}" stroke="{_ink}" stroke-width="3.5" stroke-linejoin="round"/><rect x="38" y="68" width="84" height="12" rx="3" fill="{_g}" stroke="{_ink}" stroke-width="3"/><circle cx="34" cy="22" r="6" fill="{_cr}" stroke="{_ink}" stroke-width="2.5"/><circle cx="80" cy="10" r="7" fill="{_cr}" stroke="{_ink}" stroke-width="2.5"/><circle cx="126" cy="22" r="6" fill="{_cr}" stroke="{_ink}" stroke-width="2.5"/></svg>',
 "sun": f'<svg class="card-art" viewBox="0 0 160 90"><g stroke="{_ink}" stroke-width="2.5" stroke-linejoin="round">' + "".join(f'<path d="M80 45 L{80+40*__import__("math").cos((i*30-6)*3.14159/180):.1f} {45+40*__import__("math").sin((i*30-6)*3.14159/180):.1f} L{80+40*__import__("math").cos((i*30+6)*3.14159/180):.1f} {45+40*__import__("math").sin((i*30+6)*3.14159/180):.1f}Z" fill="{_p}"/>' for i in range(12)) + f'</g><circle cx="80" cy="45" r="24" fill="{_cr}" stroke="{_ink}" stroke-width="3"/></svg>',
 "heart": f'<svg class="card-art" viewBox="0 0 160 90"><path d="M80 82 C40 58 30 40 34 26 C38 12 60 8 80 26 C100 8 122 12 126 26 C130 40 120 58 80 82Z" fill="{_p}" stroke="{_ink}" stroke-width="3.5"/><path d="M52 24 C46 28 46 36 50 40" stroke="{_cr}" stroke-width="4" fill="none" stroke-linecap="round"/><g fill="{_cr}" stroke="{_ink}" stroke-width="2"><circle cx="22" cy="20" r="5"/><circle cx="140" cy="64" r="4"/><circle cx="136" cy="16" r="3"/></g></svg>',
 "rocket": f'<svg class="card-art" viewBox="0 0 160 90"><path d="M60 64 C60 30 80 10 100 6 C104 26 96 50 70 72Z" fill="{_cr}" stroke="{_ink}" stroke-width="3" stroke-linejoin="round"/><circle cx="86" cy="32" r="7" fill="{_t}" stroke="{_ink}" stroke-width="2.5"/><path d="M62 52 L46 54 L56 66Z M74 70 L72 86 L84 74Z" fill="{_p}" stroke="{_ink}" stroke-width="2.5" stroke-linejoin="round"/><path d="M60 72 C54 78 50 84 44 86 C46 80 50 76 56 70" fill="{_g}" stroke="{_ink}" stroke-width="2.5"/><g fill="{_cr}"><circle cx="24" cy="18" r="2.5"/><circle cx="130" cy="30" r="3"/><circle cx="140" cy="70" r="2"/><circle cx="30" cy="62" r="2"/></g></svg>',
}
def video_cards():
    out=[]
    for vid,eyebrow,title,col,art in VIDEOS:
        url=f"https://www.youtube.com/watch?v={vid}"
        if EMBED:
            out.append(f'<div class="vid v-{col}"><button class="yt" type="button" data-id="{vid}" aria-label="Play {E(title)}" style="background-image:url(https://i.ytimg.com/vi/{vid}/hqdefault.jpg)"><span class="play" aria-hidden="true"></span></button><div class="vid-text"><span class="eyebrow">{E(eyebrow)}</span><h3>{E(title)}</h3><a href="{url}" target="_blank" rel="noopener">Open on YouTube ↗</a></div></div>')
        else:
            out.append(f'<a class="vid v-{col}" href="{url}" target="_blank" rel="noopener"><span class="yt yt-art" aria-hidden="true">{CARD_ART[art]}<span class="play"></span></span><span class="vid-text"><span class="eyebrow">{E(eyebrow)}</span><h3>{E(title)}</h3><span class="go">Watch on YouTube ↗</span></span></a>')
    return "\n".join(out)


# ---- Emergency broadcast TV (home hero): real episode titles as breaking news
_tv_eps = [{"n":i,"d":fmt(d),"t":t,"s":s,"g":tag_for(t),"v":EPISODE_VIDEO_IDS[i-1]} for i,(s,d,t) in enumerate(EPISODES,1)]
_tv0 = _tv_eps[58]  # #059 Dragons are REAL
TV_HTML = (
 '<div class="tv" aria-labelledby="tv-title">'
 '<div class="tv-head"><h2 id="tv-title">Emergency Broadcast</h2><span class="onair"><i aria-hidden="true"></i>On air</span></div>'
 '<div class="screen" id="tv-screen">'
 '<div class="screen-top"><span>BNEBS</span><span id="tv-ch">CH ' + f"{_tv0['n']:03d}" + '</span></div>'
 '<p class="breaking">Breaking news</p>'
 '<p class="headline" id="tv-headline" aria-live="polite">' + E(_tv0["t"]) + '</p>'
 '<div class="screen-bot"><span id="tv-date">' + E(_tv0["d"]) + '</span><span id="tv-tag">Season ' + str(_tv0["s"]) + ' · ' + E(_tv0["g"]) + '</span></div>'
 '<span class="static" aria-hidden="true"></span>'
 '</div>'
 '<div class="tv-dial">'
 '<button class="btn small" id="tv-prev" type="button" aria-label="Previous channel" disabled>◀ Back</button>'
 '<button class="btn gold" id="tv-next" type="button">Change the channel</button>'
 '<button class="btn small teal" id="tv-scan" type="button" aria-pressed="false">Scan</button>'
 '<a class="btn small" id="tv-find" href="' + watch_url(_tv0["v"]) + '" target="_blank" rel="noopener">Watch it ↗</a>'
 '<a class="btn small" id="tv-ep" href="report.html#ep-' + f"{_tv0['n']:03d}" + '">In the archive</a>'
 '</div>'
 '<small>Every headline is a real Broski Report episode title, ' + EPISODES[0][1][:4] + ' to ' + EPISODES[-1][1][:4] + '. Click through all ' + str(len(_tv_eps)) + ' channels.</small>'
 '<script type="application/json" id="tv-data">' + json.dumps(_tv_eps) + '</script>'
 '</div>'
)

# ---------------------------------------------------------------- HOME
fact_json = json.dumps([{"c":c,"t":t,"s":SOURCES[s][0],"u":SOURCES[s][1]} for c,t,s in FACTS])
f0 = FACTS[16]
home = f'''<section class="band b-violet hero" aria-labelledby="hero-title">
  <div class="fizz" id="fizz" aria-hidden="true"></div>
  <div class="wrap">
    <div>
      <span class="stamp">Attention, loyal subjects</span>
      <h1 id="hero-title"><span class="l1">Long live the</span><span class="l2">Supreme</span><span class="l3">Leader.</span></h1>
      <p class="lede">You found the fan-run news desk of <strong>Broski Nation</strong>. We cover Brittany Broski the comedian, the podcaster, the Royal Court monarch, the singer, and the woman behind the internet's most famous sip of kombucha. Brittany has nothing to do with this site, so blame the fans for everything here.</p>
      <div class="cta-row">
        <a class="btn gold" href="report.html">Browse {len(EPISODES)} episodes</a>
        <a class="btn pink" href="lore.html#quiz">Take the citizenship exam</a>
      </div>
    </div>
    <div>
      <div class="burst" aria-hidden="true">
        <svg viewBox="0 0 200 200"><defs><path id="circ" d="M100,100 m-62,0 a62,62 0 1,1 124,0 a62,62 0 1,1 -124,0"/></defs>
          <polygon fill="#19D3C0" stroke="#24082E" stroke-width="4" points="100,4 117,38 151,20 148,58 188,62 162,92 192,118 152,128 164,166 126,156 112,194 92,160 60,186 56,146 16,150 38,116 6,90 44,76 30,38 68,46 82,10"/>
          <text font-family="DM Mono, monospace" font-size="15" font-weight="500" fill="#24082E" letter-spacing="2"><textPath href="#circ">100% UNOFFICIAL ✦ 100% DEVOTED ✦</textPath></text>
          <text x="100" y="112" text-anchor="middle" font-family="Shrikhand, Georgia, serif" font-size="30" fill="#FF2E93" stroke="#24082E" stroke-width="1.2">FAN</text></svg>
      </div>
{TV_HTML}
    </div>
  </div>
</section>

<section class="band b-gold" aria-labelledby="nation-title">
  <div class="wrap">
    {sec_head("State of the Nation", "We pulled these census figures from press coverage. Each one carries its date, and the Nation has grown since.", "nation-title")}
    <div class="stats">
      <div class="stat"><b>7.6M+</b><span>TikTok followers on the main account</span><em>TIME, JUL 2025</em></div>
      <div class="stat"><b>#4</b><span>Where the Report debuted on Spotify's US podcast chart</span><em>TODAY, OCT 2023</em></div>
      <div class="stat"><b>{len(COURT)}</b><span>Royal Court guests knighted so far</span><em>YOUTUBE, {MONTHS[int(COURT[-1][1][5:7])-1].upper()} {COURT[-1][1][:4]}</em></div>
      <div class="stat"><b>TIME100</b><span>Named one of TIME's 100 Creators of 2025</span><em>TIME, JUL 2025</em></div>
    </div>
  </div>
</section>

<section class="band b-pink" aria-labelledby="explore-title">
  <div class="wrap">
    {sec_head("Explore the Nation", "Four departments, one Supreme Leader. Pick a door.", "explore-title")}
    <div class="explore">
      <a class="door" href="report.html"><span class="eyebrow">Broadcast archive</span><h3>The Broski Report</h3><p>All {len(EPISODES)} episodes from 2023 to {EPISODES[-1][1][:4]}, searchable and playable, plus the running bits.</p><span class="go">Enter ↗</span></a>
      <a class="door" href="court.html"><span class="eyebrow">The throne room</span><h3>Royal Court</h3><p>All {len(COURT)} guests, how a court works, and a coat of arms maker for you.</p><span class="go">Enter ↗</span></a>
      <a class="door" href="music.html"><span class="eyebrow">The music era</span><h3>Music</h3><p>The singles, the influences, and the musicians she has knighted.</p><span class="go">Enter ↗</span></a>
      <a class="door" href="lore.html"><span class="eyebrow">Classified</span><h3>Lore &amp; Facts</h3><p>{len(FACTS)} sourced facts, the full history, and the citizenship exam.</p><span class="go">Enter ↗</span></a>
    </div>
  </div>
</section>

<section class="band b-violet" id="watch" aria-labelledby="watch-title">
  <div class="wrap">
    {sec_head("Watch the Nation", "Official videos from her channels. Start with the very first Royal Court, then the music.", "watch-title")}
    <div class="vids">
{video_cards()}
    </div>
  </div>
</section>

<section class="band b-cream" aria-labelledby="fotd-title">
  <div class="wrap">
    <div class="fotd" id="fotd">
      <span class="badge" aria-hidden="true">!</span>
      <div>
        <h3 id="fotd-title">Broski fact, freshly declassified</h3>
        <p id="fotd-text">{E(f0[1])}</p>
        <small>Source: <a id="fotd-src" href="{SOURCES[f0[2]][1]}" target="_blank" rel="noopener">{E(SOURCES[f0[2]][0])}</a></small>
      </div>
      <button class="btn gold" id="fotd-next" type="button">Another one</button>
    </div>
    <script type="application/json" id="facts-data">{fact_json}</script>
  </div>
</section>

<section class="band b-ink" id="gallery" aria-labelledby="gallery-title">
  <div class="wrap plate">
    <figure class="plate-art"><img src="seal.webp" width="1200" height="1600" alt="The Great Seal of Broski Nation: a gold ring reading The Great Seal of Broski Nation, Est. August VI, MMXIX, around a sunburst field. A kombucha bottle crest sits above a quartered shield with a microphone, a crown, a sun and a dragon, over a ribbon reading Nunc est bibendum."></figure>
    <div class="plate-text">
      <span class="eyebrow">The Gallery · Plate IX</span>
      <h2 id="gallery-title">The Great Seal.</h2>
      <p>Every nation needs a seal, so we drew one. Each piece stands for part of her story.</p>
      <dl class="plate-meta seal-key">
        <dt>Crest</dt><dd>A kombucha bottle, fizzing. The first sip, August 6, 2019.</dd>
        <dt>Microphone</dt><dd>The Broski Report, on air since May 2023.</dd>
        <dt>Crown</dt><dd>Royal Court. The ring holds one bead per knight, {len(COURT)} and counting.</dd>
        <dt>Sun</dt><dd>"The Sun," her debut single.</dd>
        <dt>Dragon</dt><dd>On the record since July 2024: dragons are real.</dd>
        <dt>Motto</dt><dd>Nunc est bibendum. Latin for "now, we drink."</dd>
      </dl>
      <p style="margin-top:1.2rem"><a href="#first-sip">See Plate VIII, First Sip ↓</a></p>
    </div>
  </div>
  <div class="wrap plate plate-two" id="first-sip">
    <div class="plate-text">
      <span class="eyebrow">Plate VIII</span>
      <h3 class="plate-sub">First Sip.</h3>
      <p>1,584 bubbles packed into a gold seal, broadcast signals off both flanks, and a crown built from rising fizz. The plate number, the year, and the n all point somewhere specific.</p>
    </div>
    <figure class="plate-art small"><img src="poster.webp" width="1200" height="1600" alt="Original poster: a gold seal packed with orange, pink and cream bubbles, pink broadcast arcs, a crown built from rising gold bubbles, and the words First Sip on electric violet."></figure>
  </div>
</section>

<section class="band b-violet" id="citizenship" aria-labelledby="cit-title">
  <div class="wrap citizen">
    <div>
      <h2 id="cit-title">Get your papers</h2>
      <p class="intro">Type your name and the Ministry will assign your post. This card is fan-made fun, not a real membership.</p>
      <form class="form" id="citForm">
        <label for="citName">Your name</label>
        <input id="citName" type="text" maxlength="28" autocomplete="off" placeholder="e.g. Thomas" required>
        <div class="row"><button class="btn gold" type="submit">Issue my papers</button><button class="btn" type="button" id="copyCard">Copy as text</button></div>
        <p class="status" id="citStatus" aria-live="polite"></p>
      </form>
    </div>
    <div class="card" id="card" aria-live="polite">
      <span class="holo" aria-hidden="true"></span>
      <div class="card-top"><b>Broski Nation<br>Citizenship Papers</b>{SEAL.replace('width="46" height="46"','width="50" height="50"')}</div>
      <div class="card-name" id="cName">Loyal Subject</div>
      <dl><dt>Assigned to</dt><dd id="cPost">Bureau of Kombucha Affairs</dd><dt>Clearance</dt><dd id="cClear">Hozier Level</dd><dt>Duty</dt><dd id="cDuty">Listen every Tuesday. No exceptions.</dd></dl>
      <div class="card-foot"><span id="cNo">CITIZEN NO. 0000519</span><span>EST. 2019 · UNOFFICIAL</span></div>
    </div>
  </div>
</section>

<section class="band b-gold" aria-labelledby="follow-title">
  <div class="wrap">
    {sec_head("Report for duty", "The official channels. Go follow the real thing.", "follow-title")}
    <div class="follow">
      <a href="https://www.tiktok.com/@brittany_broski" target="_blank" rel="noopener"><b>TikTok</b><span>@brittany_broski ↗</span></a>
      <a href="https://www.youtube.com/@Brittany_Broski" target="_blank" rel="noopener"><b>YouTube</b><span>@Brittany_Broski ↗</span></a>
      <a href="https://www.instagram.com/brittany_broski/" target="_blank" rel="noopener"><b>Instagram</b><span>@brittany_broski ↗</span></a>
      <a href="https://open.spotify.com/search/Brittany%20Broski/artists" target="_blank" rel="noopener"><b>Music</b><span>Brittany Broski ↗</span></a>
      <a href="https://broski.shop/" target="_blank" rel="noopener"><b>Shop</b><span>broski.shop ↗</span></a>
    </div>
  </div>
</section>
'''
page("index.html", "The Broski Bulletin", "index.html", home, ["wiki","time25","today","rcwiki","time19"], standalone=True)

# ---------------------------------------------------------------- REPORT
eps = []
for i,(s,d,t) in enumerate(EPISODES, 1):
    eps.append((i,s,d,t,tag_for(t)))
seasons = Counter(s for _,s,_,_,_ in eps)
tags = Counter(g for *_,g in eps)
TAG_ORDER = ["History","Crushes","Pop culture","Spooky","Music","Nation lore","Life"]
TAG_COL = {"History":"#FFC21A","Crushes":"#FF2E93","Pop culture":"#FF7A1A","Spooky":"#24082E","Music":"#19D3C0","Nation lore":"#5B1FE0","Life":"#FFF4E2"}

# horizontal bar chart of topics
bw, rowh, lab = 460, 34, 120
maxv = max(tags.values())
bars = []
for k, g in enumerate(TAG_ORDER):
    v = tags.get(g, 0); y = 10 + k*rowh; w = round((bw - lab - 50) * v / maxv)
    bars.append(f'<text x="{lab-10}" y="{y+19}" text-anchor="end" font-family="Familjen Grotesk, Arial, sans-serif" font-size="14" font-weight="700" fill="#24082E">{g}</text>'
                f'<rect x="{lab}" y="{y+4}" width="{max(w,4)}" height="22" rx="6" fill="{TAG_COL[g]}" stroke="#24082E" stroke-width="2.5"/>'
                f'<text x="{lab+max(w,4)+8}" y="{y+20}" font-family="DM Mono, monospace" font-size="13" fill="#24082E">{v}</text>')
chart_svg = f'<svg viewBox="0 0 {bw} {20+rowh*len(TAG_ORDER)}" role="img" aria-label="Episodes by topic: ' + ", ".join(f"{g} {tags.get(g,0)}" for g in TAG_ORDER) + '">' + "".join(bars) + "</svg>"

ep_rows = "\n".join(
    f'      <article class="ep" id="ep-{i:03d}" data-n="{i}" data-s="{s}" data-g="{E(g)}" data-t="{E(t.lower())}"{" hidden" if i>24 else ""}>'
    f'<span class="no">#{i:03d}</span><time datetime="{d}">{fmt(d)}</time><h4>{E(t)}</h4><span class="tag" data-g="{E(g)}">{E(g)}</span>'
    + (f'<button class="ep-go ep-play" type="button" data-vid="{EPISODE_VIDEO_IDS[i-1]}" aria-label="Play {E(t)} in the player">▶ Play</button></article>' if EMBED else
       f'<a class="ep-go" href="{watch_url(EPISODE_VIDEO_IDS[i-1], REPORT_PLAYLIST)}" target="_blank" rel="noopener" aria-label="Watch {E(t)} on YouTube">Watch ↗</a></article>')
    for i,s,d,t,g in eps)

season_chips = '<button class="chip" type="button" data-season="all" aria-pressed="true">All seasons</button>' + "".join(
    f'<button class="chip" type="button" data-season="{s}" aria-pressed="false">Season {s} · {seasons[s]}</button>' for s in sorted(seasons))
tag_chips = '<button class="chip" type="button" data-tag="all" aria-pressed="true">All topics</button>' + "".join(
    f'<button class="chip" type="button" data-tag="{E(g)}" aria-pressed="false">{E(g)}</button>' for g in TAG_ORDER)

LORE = [
 ("The Supreme Leader", "The Report frames Brittany as the fearless, tyrannical ruler of Broski Nation, and each episode as a national news blast for her loyal subjects.", "Show notes"),
 ("Broski Nation agencies", "The Nation keeps growing departments: a Space Program, Special Ops, a Royal Ballet School, and a School of Fashion and Horror. By late 2024 she declared the Broski Empire.", "Episodes #048, #073, #079, #095, #105"),
 ("Stanley", "The Report's creative director and editor. She gives him on-air credit for his creative work.", "Shortform notes"),
 ("The Irishman files", "In February 2024 she found an Irishman. In April 2025 she declared herself officially Irish. That August came a new favorite Irishman.", "Episodes #037, #091, #104"),
 ("Professor Broski", "History lessons arrive without warning: WWII, Victorian weirdos, the French Revolution, Chernobyl, and Churchill's War Room.", "Episodes #020, #058, #084, #087, #107"),
 ("The Jacob Elordi saga", "Late 2023 brought a plea to be freed from Jacob Elordi. Almost two years later came the apology.", "Episodes #027, #116"),
 ("The Stanley Tucci project", "In May 2024 she needed to feed Stanley Tucci Hamburger Helper. That Thanksgiving he landed in an episode title again, next to Kai Cenat.", "Episodes #051, #074"),
 ("The Santa investigation", "Santa is a dangerous rogue agent. Later findings identified him as God's brother. The case remains open.", "Episodes #039, #077"),
 ("Dragons are real", "She stated it on the record in July 2024 and brought dragons back with George Orwell that December.", "Episodes #059, #075"),
]
def ep_links(c):
    return re.sub(r"#(\d{3})", lambda m: f'<a href="#ep-{m.group(1)}">#{m.group(1)}</a>', E(c))
lore_cards = "\n".join(f'      <article><h3>{E(a)}</h3><p>{E(b)}</p><small>{ep_links(c)}</small></article>' for a,b,c in LORE)

report = page_hero("b-pink", "Now broadcasting", "The Broski Report",
    "Brittany launched the Report in May 2023 and runs it like a satirical state broadcast. Each Tuesday the Supreme Leader reports on whatever she is obsessing over, learning about, or crying about, with props and a lot of green screen.",
    [(str(len(EPISODES)),"episodes in our archive"),(str(len(seasons)),"seasons, 2023 to " + EPISODES[-1][1][:4]),("#4","Spotify US debut, May 2023"),("100","episodes by July 1, 2025")]) + f'''
<section class="band b-tang" id="tune-in" aria-labelledby="tune-title">
  <div class="wrap">
    {sec_head("Tune in", "The official Broski Report playlist on YouTube, every news blast from the Supreme Leader in one queue.", "tune-title")}
    {playlist_html(REPORT_PLAYLIST, "Broski Report", "Play the Broski Report", MIC_SVG, "report")}
  </div>
</section>

<section class="band b-violet" aria-labelledby="covers-title">
  <div class="wrap split">
    <div class="decree">
      <h3>What the Report covers</h3>
      <ul>
        <li><span>Pop culture and fandom, from heartthrob crushes to deep dives on Hozier, Beyoncé, and Chappell Roan.</span></li>
        <li><span>Surprise history lessons. Chernobyl, WWII, the Roman Colosseum, and Victorian oddities have all made the broadcast.</span></li>
        <li><span>Life updates told with total candor: travel to Ireland and Italy, theater kid memories, and the reality of influencing as a job.</span></li>
        <li><span>Bigger conversations too, like leaving the church, mortality, and the psychology of being a fangirl.</span></li>
        <li><span>A talk show format inspired by Hot Ones and Good Mythical Morning. She credits her production crew on air.</span></li>
      </ul>
      <div class="listen" aria-label="Listen">
        <a href="https://www.youtube.com/results?search_query=The+Broski+Report" target="_blank" rel="noopener">YouTube ↗</a>
        <a href="https://open.spotify.com/search/The%20Broski%20Report/podcasts" target="_blank" rel="noopener">Spotify ↗</a>
        <a href="https://podcasts.apple.com/us/search?term=The%20Broski%20Report" target="_blank" rel="noopener">Apple Podcasts ↗</a>
      </div>
    </div>
    <div>
      <div class="sec-head" style="grid-template-columns:minmax(0,1fr);margin-bottom:1.5rem"><h2 id="covers-title">What she talks about</h2><p>We sorted every episode title in our archive by topic. Life stories lead. History and the spooky stuff tie for second, with crushes one episode behind.</p></div>
      <div class="chart"><h3>Episodes by topic</h3>{chart_svg}</div>
    </div>
  </div>
</section>

<section class="band b-gold" id="archive" aria-labelledby="archive-title">
  <div class="wrap">
    {sec_head("The Archive", "Every Report episode from the May 2023 premiere to {fmt(EPISODES[-1][1])}. Search a title, filter by season or topic, then press play.", "archive-title")}
    <div class="tools">
      <label class="eyebrow" for="ep-search">Search episode titles</label>
      <input class="search" id="ep-search" type="search" placeholder="Try Hozier, dragons, or Irish" autocomplete="off">
      <div class="chips" role="group" aria-label="Filter by season">{season_chips}</div>
      <div class="chips" role="group" aria-label="Filter by topic">{tag_chips}</div>
      <div class="tools-row"><span class="count" id="ep-count" aria-live="polite">Showing 24 of {len(EPISODES)}</span><span style="display:flex;gap:.6rem;flex-wrap:wrap"><button class="btn small" id="ep-sort" type="button" aria-pressed="false">Newest first</button><button class="btn pink small" id="ep-random" type="button">Spin the archive</button></span></div>
    </div>
    <div class="archive" id="archive-list">
{ep_rows}
    </div>
    <p class="empty" id="ep-empty" hidden>No episodes match. Try a shorter search or another topic.</p>
    <div class="more-row"><button class="btn ink" id="ep-more" type="button">Show all {len(EPISODES)} episodes</button></div>
  </div>
</section>

<section class="band b-teal" aria-labelledby="lore-title">
  <div class="wrap">
    {sec_head("Running bits", "The recurring storylines of the Report, as told by its episode titles. Listen to the episodes for the full saga.", "lore-title")}
    <div class="lore">
{lore_cards}
    </div>
  </div>
</section>
'''
page("report.html", "The Broski Report · Broski Bulletin", "report.html", report, ["tvdb","rova","shortform","today","wiki"])

# ---------------------------------------------------------------- COURT
ARMS_DL = '<button class="btn gold" id="arms-dl" type="button">Download PNG</button>' if EMBED else ''
PLAYLIST_HTML = playlist_html(COURT_PLAYLIST, "Royal Court", "Play the full court", '<span class="pl-icon pl-crown" aria-hidden="true">♛</span>', "court")
cs = Counter(s for s,_,_ in COURT)
def guest_html(i, s, d, n):
    vid = COURT_VIDEO_IDS[i-1]
    attrs = f'id="knight-{i:02d}" data-s="{s}" data-n="{E(n.lower())}"'
    inner = f'<b>{E(n)}</b><span>No. {i:02d} · {fmt(d)}</span>'
    if not vid:
        return f'      <div class="guest gone" {attrs}>{inner}<em>No longer on YouTube</em></div>'
    if EMBED:
        return f'      <button class="guest" type="button" {attrs} data-vid="{vid}" data-title="Royal Court: {E(n)}">{inner}<em>▶ Play in the court</em></button>'
    return f'      <a class="guest" {attrs} href="{watch_url(vid, COURT_PLAYLIST)}" target="_blank" rel="noopener">{inner}<em>Watch ↗</em></a>'
guests = "\n".join(
    guest_html(i, s, d, n) for i,(s,d,n) in enumerate(COURT, 1))
court_chips = '<button class="chip" type="button" data-cs="all" aria-pressed="true">All seasons</button>' + "".join(
    f'<button class="chip" type="button" data-cs="{s}" aria-pressed="false">Season {s} · {cs[s]}</button>' for s in sorted(cs))

ICONS = {
 "crown":'<path d="M4 18h16l1-10-5 4-4-7-4 7-5-4z" fill="currentColor"/><rect x="4" y="19" width="16" height="2" fill="currentColor"/>',
 "dragon":'<path d="M3 17c3-1 4-4 7-4 2 0 3 2 5 2 3 0 4-3 6-5-1 4-2 9-7 9-3 0-4-2-6-2-2 0-3 1-5 0z" fill="currentColor"/><path d="M14 9l2-4 1 4 3-2-1 4" fill="currentColor"/>',
 "bottle":'<rect x="10" y="2" width="4" height="3" fill="currentColor"/><path d="M10 5h4v3c0 1 3 2 3 5v8c0 1-1 1-1 1H8s-1 0-1-1v-8c0-3 3-4 3-5z" fill="currentColor"/>',
 "mic":'<rect x="9" y="2" width="6" height="11" rx="3" fill="currentColor"/><path d="M6 11a6 6 0 0012 0M12 17v4M8 21h8" stroke="currentColor" stroke-width="2" fill="none"/>',
 "sword":'<path d="M12 2l2 3v10h-4V5z" fill="currentColor"/><rect x="7" y="15" width="10" height="2" fill="currentColor"/><rect x="11" y="17" width="2" height="5" fill="currentColor"/>',
 "harp":'<path d="M6 21V5c4-1 8 2 12 0v4c-3 2-6 6-8 12z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M9 7v11M12 8v7M15 8v4" stroke="currentColor" stroke-width="1.5"/>',
 "star":'<path d="M12 2l3 7h7l-6 4 2 8-6-5-6 5 2-8-6-4h7z" fill="currentColor"/>',
 "heart":'<path d="M12 21s-8-5-8-11a4 4 0 018-1 4 4 0 018 1c0 6-8 11-8 11z" fill="currentColor"/>',
 "ghost":'<path d="M5 21V10a7 7 0 0114 0v11l-2-2-2 2-3-2-3 2-2-2z" fill="currentColor"/><circle cx="9.5" cy="10" r="1.3" fill="#FFF4E2"/><circle cx="14.5" cy="10" r="1.3" fill="#FFF4E2"/>',
 "goblet":'<path d="M6 3h12c0 6-3 8-6 8s-6-2-6-8z" fill="currentColor"/><path d="M12 11v7M8 21h8" stroke="currentColor" stroke-width="2"/>',
}
icon_names = list(ICONS)
def icon_row(q, default):
    return "".join(f'<button class="icon-btn" type="button" data-q="{q}" data-icon="{n}" aria-label="{n}" aria-pressed="{"true" if n==default else "false"}"><svg viewBox="0 0 24 24" style="color:#24082E">{ICONS[n]}</svg></button>' for n in icon_names)
COLORS = ["#FF2E93","#FFC21A","#5B1FE0","#19D3C0","#FF7A1A","#33105F"]
def swatch_row(q, default):
    return "".join(f'<button class="swatch" type="button" data-q="{q}" data-color="{c}" style="background:{c}" aria-label="Field color {c}" aria-pressed="{"true" if c==default else "false"}"></button>' for c in COLORS)
DEF = [("crown","#FF2E93"),("bottle","#FFC21A"),("mic","#19D3C0"),("dragon","#5B1FE0")]
quarters = ["Upper left","Upper right","Lower left","Lower right"]
fields = "\n".join(f'''        <fieldset><legend>{quarters[i]}</legend><div class="icon-row">{icon_row(i, DEF[i][0])}</div><div class="swatches">{swatch_row(i, DEF[i][1])}</div></fieldset>''' for i in range(4))

court = page_hero("b-court", "Hear ye, hear ye", "The Royal Court",
    "Her medieval talk show premiered on YouTube in July 2023. Celebrities feast, give gifts, draw a coat of arms, and earn a seat on her council. She calls herself a Game of Thrones adult, and the show proves it.",
    [(str(len(COURT)),"guests knighted through " + MONTHS[int(COURT[-1][1][5:7])-1] + " " + COURT[-1][1][:4]),(str(len(cs)),"seasons and counting"),("2025","Webby Awards nominee"),("24.5M","combined views by spring 2025")]) + f'''
<section class="band b-pink" aria-labelledby="acts-title">
  <div class="wrap">
    {sec_head("How a court works", "Every episode runs in three acts. She took inspiration from Hot Ones, and she wants the costumes to make guests look ridiculous enough to drop the celebrity act.", "acts-title")}
    <div class="acts">
      <article class="act"><span class="eyebrow">Act I</span><h3>The Feast</h3><p>The guest dresses the part in a cape and hat, eats from the royal table, drinks from a goblet, and fields funny and personal questions.</p></article>
      <article class="act"><span class="eyebrow">Act II</span><h3>The Tribute</h3><p>The guest presents a gift to the crown, and the two of them talk it through on air.</p></article>
      <article class="act"><span class="eyebrow">Act III</span><h3>The Coat of Arms</h3><p>The guest draws a four-part coat of arms while answering the emotional questions. Then she knights them onto her council.</p></article>
    </div>
  </div>
</section>

<section class="band b-teal" id="watch-court" aria-labelledby="wc-title">
  <div class="wrap">
    {sec_head("Hold court", "The official Royal Court playlist, every episode in one place. Press play and let the council run.", "wc-title")}
    {PLAYLIST_HTML}
  </div>
</section>

<section class="band b-court" id="roll" aria-labelledby="roll-title">
  <div class="wrap">
    {sec_head("The Council Roll", f"Every guest from Orville Peck in July 2023 to {COURT[-1][2]} on {fmt(COURT[-1][1])}. Updated daily from YouTube. Search a name or summon one at random.", "roll-title")}
    <div class="tools">
      <label class="eyebrow" for="g-search" style="color:#FFC21A">Search the council</label>
      <input class="search" id="g-search" type="search" placeholder="Try Harry, Trixie, or Matt" autocomplete="off">
      <div class="chips" role="group" aria-label="Filter by season">{court_chips}</div>
      <div class="tools-row"><span class="count" id="g-count" aria-live="polite">{len(COURT)} knights</span><button class="btn gold small" id="g-random" type="button">Summon a knight</button></div>
    </div>
    <div class="roll-grid" id="roll-list">
{guests}
    </div>
    <p class="empty" id="g-empty" hidden>No knight by that name. Check the spelling, or they may not have been summoned yet.</p>
  </div>
</section>

<section class="band b-gold" id="arms" aria-labelledby="arms-title">
  <div class="wrap">
    {sec_head("Draw your coat of arms", "Act III, at home. Pick an emblem and a field color for each quarter, add a motto, and you are ready for knighthood.", "arms-title")}
    <div class="arms">
      <div class="arms-controls">
{fields}
        <fieldset><legend>Motto</legend><input class="search" id="motto" type="text" maxlength="34" value="Long live the Supreme Leader" autocomplete="off" style="box-shadow:none"></fieldset>
        <div class="row" style="display:flex;gap:.75rem;flex-wrap:wrap"><button class="btn pink" id="arms-random" type="button">Randomize my crest</button><button class="btn" id="arms-copy" type="button">Copy my blazon</button>{ARMS_DL}</div>
        <p class="status" id="arms-status" aria-live="polite" style="color:#24082E"></p>
      </div>
      <div class="shield-wrap">
        <svg id="shield" viewBox="0 0 240 280" role="img" aria-label="Your coat of arms preview"></svg>
        <p class="motto-out" id="motto-out">Long live the Supreme Leader</p>
      </div>
    </div>
    <script type="application/json" id="icon-data">{json.dumps(ICONS)}</script>
  </div>
</section>
'''
page("court.html", "Royal Court · Broski Bulletin", "court.html", court, ["rcwiki","rctvdb","rs23","bustle","atlantic"])

DISC_ART = {'Adore You': '<svg viewBox="0 0 200 120" aria-hidden="true"><rect width="200" height="120" fill="#5B1FE0"/><circle cx="60" cy="60" r="44" fill="#24082E"/><circle cx="60" cy="60" r="30" fill="none" stroke="#FF2E93" stroke-width="2"/><circle cx="60" cy="60" r="14" fill="#FFC21A"/><path d="M110 30 q20 30 0 60 M130 22 q28 38 0 76 M150 14 q36 46 0 92" stroke="#19D3C0" stroke-width="5" fill="none" stroke-linecap="round"/></svg>', 'The Sun': '<svg viewBox="0 0 200 120" aria-hidden="true"><rect width="200" height="120" fill="#FF2E93"/><circle cx="100" cy="68" r="34" fill="#FFC21A" stroke="#24082E" stroke-width="3"/><g stroke="#FFC21A" stroke-width="6" stroke-linecap="round"><path d="M100 14v14M100 108v8M48 68h-14M166 68h-14M62 30l9 9M138 30l-9 9M62 106l9-9M138 106l-9-9"/></g><circle cx="118" cy="58" r="24" fill="#FF2E93"/></svg>', 'Stained': '<svg viewBox="0 0 200 120" aria-hidden="true"><rect width="200" height="120" fill="#19D3C0"/><path d="M40 90 C60 30 90 100 110 50 S160 40 165 85 C150 105 70 110 40 90Z" fill="#24082E"/><circle cx="120" cy="70" r="11" fill="#FF2E93"/><circle cx="75" cy="78" r="6" fill="#FFC21A"/><circle cx="150" cy="30" r="5" fill="#5B1FE0"/></svg>'}
def disc_media(name, svg):
    vid = MUSIC_VIDEO_IDS[name]
    if EMBED:
        return (f'<button class="yt disc-yt" type="button" data-id="{vid}" aria-label="Play {E(name)}" '
                f'style="background-image:url(https://i.ytimg.com/vi/{vid}/hqdefault.jpg)"><span class="play" aria-hidden="true"></span></button>')
    return f'<a class="disc-link" href="{watch_url(vid)}" target="_blank" rel="noopener" aria-label="Watch {E(name)} on YouTube">{svg}<span class="disc-watch">Watch ↗</span></a>'

# ---------------------------------------------------------------- MUSIC
MUSO = ["Orville Peck","Charli XCX","Conan Gray","Maren Morris","Laufey","Trixie Mattel","Lewis Capaldi","Noah Cyrus","Marcus Mumford","Harry Styles","Sam Fender","Sombr"]
lookup = {n:(i,d) for i,(s,d,n) in enumerate(COURT,1)}
muso = "\n".join(f'      <div class="guest"><b>{E(n)}</b><span>No. {lookup[n][0]:02d} · {fmt(lookup[n][1])}</span></div>' for n in MUSO)
music = page_hero("b-tang", "Now playing", "The Music Era",
    "The theater kid who first sang in church signed with Atlantic and started releasing soulful, bluesy pop rock in 2025. She avoids genre labels on purpose and calls the sound a blend of all her favorite things.",
    [("3","official releases"),("3M+","streams for her first cover"),("4.5★","Harvard Crimson on The Sun"),("2025","the year the music started")]) + f'''
<section class="band b-cream" aria-labelledby="singles-title">
  <div class="wrap">
    {sec_head("The singles", "From a proof-of-concept cover to two originals, in order.", "singles-title")}
    <div class="music">
      <article class="disc">
        {disc_media("Adore You", DISC_ART["Adore You"])}
                <span class="meta">COVER · MAR 20, 2025</span><h3>Adore You</h3>
        <p>Her first official release: a reimagined Harry Styles song from the fan who calls him her idol. She describes it as the proof of concept for everything after. It passed 3 million global streams within weeks.</p>
      </article>
      <article class="disc">
        {disc_media("The Sun", DISC_ART["The Sun"])}
                <span class="meta">DEBUT SINGLE · APR 4, 2025</span><h3>The Sun</h3>
        <p>Produced and co-written with Luke Niccoli. A song about unrequited love, with bluegrass guitar and a big Texas-soul vocal. The Harvard Crimson gave it 4.5 stars.</p>
      </article>
      <article class="disc">
        {disc_media("Stained", DISC_ART["Stained"])}
                <span class="meta">SINGLE · MAY 29, 2025</span><h3>Stained</h3>
        <p>A dramatic, bluesy follow-up about being permanently marked by a relationship. Produced by Zhone and co-written with Zhone and Annika Bennett.</p>
      </article>
    </div>
  </div>
</section>

<section class="band b-violet" aria-labelledby="inf-title">
  <div class="wrap">
    {sec_head("The influences", "Church choir first. Then a teenage diet of boy bands and classic rock, then the moody singer-songwriters who shaped the record.", "inf-title")}
    <div class="influences"><span>Hozier</span><span>Florence + The Machine</span><span>Mumford &amp; Sons</span><span>One Direction</span><span>The Beatles</span><span>Harry Styles</span><span>The 1975</span></div>
    <p style="margin-top:1.75rem;max-width:40rem;color:#E9DAFF">As of late 2025 she was working on a concept album in that bluesy direction. When it drops, it goes here first.</p>
  </div>
</section>

<section class="band b-court" aria-labelledby="muso-title">
  <div class="wrap">
    {sec_head("Musicians at court", "Twelve musicians have taken the Royal Court challenge, including two of her biggest influences.", "muso-title")}
    <div class="roll-grid">
{muso}
    </div>
  </div>
</section>

<section class="band b-gold" aria-labelledby="listen-title">
  <div class="wrap">
    {sec_head("Press play", "Stream the singles where you listen.", "listen-title")}
    <div class="follow">
      <a href="https://open.spotify.com/search/Brittany%20Broski/artists" target="_blank" rel="noopener"><b>Spotify</b><span>Brittany Broski ↗</span></a>
      <a href="https://music.apple.com/us/search?term=Brittany%20Broski" target="_blank" rel="noopener"><b>Apple Music</b><span>Brittany Broski ↗</span></a>
      <a href="https://www.youtube.com/results?search_query=Brittany+Broski+The+Sun" target="_blank" rel="noopener"><b>YouTube</b><span>Visualizers ↗</span></a>
      <a href="https://www.tiktok.com/@brittany_broski" target="_blank" rel="noopener"><b>TikTok</b><span>Behind the songs ↗</span></a>
      <a href="https://broski.shop/" target="_blank" rel="noopener"><b>Shop</b><span>broski.shop ↗</span></a>
    </div>
  </div>
</section>
'''
page("music.html", "The Music Era · Broski Bulletin", "music.html", music, ["atlantic","dallas","fem","bustle","crimson","rcwiki"])

# ---------------------------------------------------------------- LORE
cats = ["Origins","Habits","Fandom","Shows","Music"]
fc = Counter(c for c,_,_ in FACTS)
fact_chips = '<button class="chip" type="button" data-fc="all" aria-pressed="true">All · ' + str(len(FACTS)) + '</button>' + "".join(
    f'<button class="chip" type="button" data-fc="{c}" aria-pressed="false">{c} · {fc[c]}</button>' for c in cats)
fact_cards = "\n".join(
    f'      <article class="fact" data-c="{c}"><span class="tag" data-c="{c}">{c}</span><p>{E(t)}</p><span class="fact-foot"><a class="src" href="{SOURCES[s][1]}" target="_blank" rel="noopener">{E(SOURCES[s][0])} ↗</a><button class="copy-fact" type="button">Copy</button></span></article>'
    for c,t,s in FACTS)
TL = [
 (False,"1997","The Supreme Leader is born","Brittany Alexis Tomlinson, born May 10. Raised in Dallas. Theater kid, improv kid, Tumblr fangirl."),
 (False,"2018","Texas A&M, magna cum laude","Three years, a communications degree, and a Spanish minor. Then a call center, then a bank."),
 (True,"Aug 2019","The first sip","On August 6 she posts 21 seconds of cream soda kombucha. It becomes a permanent reaction meme and one of TikTok's top ten videos of the year."),
 (True,"Sep 2019","Fired, then signed","The bank lets her go on September 4. By year's end she signs with UTA and moves to Los Angeles with Sarah Schauer."),
 (False,"2020","The LA era","A Super Bowl ad, the TikTok that sparked Ratatouille the Musical, and TikTok's New Year's Eve livestream with Lil Yachty."),
 (False,"2021","Host of For You","She hosts TikTok's official podcast, interviewing other creators."),
 (False,"2022","Violating Community Guidelines","A cult-favorite podcast about internet oddities with Sarah Schauer, plus Trixie Motel with Trixie Mattel."),
 (True,"2023","The Report and the Court","The Broski Report launches in May and debuts at number four on Spotify. Royal Court follows in July. In August she wins a Streamy Creator Honor."),
 (False,"2024","The Empire expands","Royal Court season two brings Charli XCX and Saoirse Ronan. The Report covers 48 episodes and declares the Broski Empire."),
 (True,"2025","Singer and honoree","\"Adore You,\" \"The Sun,\" and \"Stained\" arrive via Atlantic. TIME names her a TIME100 Creator. The Report hits 100 episodes."),
 (True,"2026","The idol takes the throne","Harry Styles sits at her Royal Court in February. In March she co-hosts the Vanity Fair Oscar party livestream."),
]
tl = "\n".join(f'      <div class="t{" big" if b else ""}"><time>{E(y)}</time><div><h3>{E(h)}</h3><p>{E(p)}</p></div></div>' for b,y,h,p in TL)

lore = page_hero("b-teal", "Classified", "Lore &amp; Facts",
    "Everything we could dig up from her interviews, show notes, and public appearances, each fact with a source you can check. Then prove your loyalty on the citizenship exam.",
    [(str(len(FACTS)),"sourced facts"),(str(len(QUIZ)),"exam questions"),("2019","year of the first sip"),("May 10","the Supreme Leader's birthday")]) + f'''
<section class="band b-violet" id="facts" aria-labelledby="facts-title">
  <div class="wrap">
    {sec_head("The fact files", "Filter by file. Every card links to where she said it or where it was reported.", "facts-title")}
    <div class="tools">
      <label class="eyebrow" for="f-search" style="color:#FFC21A">Search the files</label>
      <input class="search" id="f-search" type="search" placeholder="Try coffee, Harry, or bank" autocomplete="off">
      <div class="chips" role="group" aria-label="Filter facts">{fact_chips}</div>
      <div class="tools-row"><span class="count" id="f-count" aria-live="polite">{len(FACTS)} facts</span><button class="btn gold small" id="f-random" type="button">Surprise me</button></div>
    </div>
    <p class="empty" id="f-empty" hidden>No facts match. Try another word.</p>
    <div class="facts" id="fact-list">
{fact_cards}
    </div>
  </div>
</section>

<section class="band b-gold" aria-labelledby="history-title">
  <div class="wrap">
    {sec_head("Official History of the Nation", "Follow a communications grad from Dallas from a bank job to a Gen Z media empire, one year at a time.", "history-title")}
    <div class="timeline">
{tl}
    </div>
  </div>
</section>

<section class="band b-pink" id="quiz" aria-labelledby="quiz-title">
  <div class="wrap">
    {sec_head("The citizenship exam", f"{len(QUIZ)} questions. Every answer appears somewhere on this site, so no excuses.", "quiz-title")}
    <div class="quiz" id="quiz-box" tabindex="-1">
      <div class="quiz-top"><span class="count" id="q-num">Question 1 of {len(QUIZ)}</span><div class="progress" aria-hidden="true"><i id="q-bar"></i></div></div>
      <div id="q-stage">
        <p class="q" id="q-text">{E(QUIZ[0][0])}</p>
        <div class="answers" id="q-answers">{"".join(f'<button class="answer" type="button">{E(a)}</button>' for a in QUIZ[0][1])}</div>
        <p class="explain" id="q-explain" aria-live="polite"></p>
        <div class="quiz-foot"><button class="btn gold" id="q-next" type="button" hidden>Next question</button></div>
        <p class="quiz-keys">Keyboard: press 1 to 4 to answer, Enter for the next question. Questions shuffle every attempt.</p>
      </div>
      <div class="result" id="q-result" hidden>
        <span class="eyebrow">Your score</span><span class="score" id="q-score">0/{len(QUIZ)}</span><span class="rank" id="q-rank">Loyal Subject</span><p id="q-blurb"></p>
        <div class="row" style="display:flex;gap:.75rem;flex-wrap:wrap;justify-content:center"><button class="btn pink" id="q-again" type="button">Retake the exam</button><button class="btn" id="q-share" type="button">Copy my result</button></div>
        <div class="review" id="q-review"></div>
      </div>
    </div>
    <script type="application/json" id="quiz-data">{json.dumps(QUIZ)}</script>
  </div>
</section>
'''
lore_src = sorted({s for _,_,s in FACTS}, key=list(SOURCES).index)
page("lore.html", "Lore & Facts · Broski Bulletin", "lore.html", lore, lore_src)
print("built", len(EPISODES), "episodes,", len(COURT), "guests,", len(FACTS), "facts")
