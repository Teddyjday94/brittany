"""Functional tests for The Broski Bulletin. Run: python3 test_site.py  (needs Playwright + Chromium)."""
import sys, os
from playwright.sync_api import sync_playwright
from data import EPISODES, COURT

BASE = "file://" + os.path.dirname(os.path.abspath(__file__)) + "/"
results = []
def check(name, cond, info=""):
    results.append((name, bool(cond), info))

def run(width, reduced=False):
    tag = f"[{width}px{' reduced' if reduced else ''}]"
    ctx = browser.new_context(viewport={"width": width, "height": 900},
                              reduced_motion="reduce" if reduced else "no-preference",
                              permissions=["clipboard-read", "clipboard-write"])
    errs = []
    def page(name):
        p = ctx.new_page()
        p.on("pageerror", lambda e: errs.append(f"{name}: {e}"))
        p.goto(BASE + name); p.wait_for_timeout(400)
        return p

    # ---------- every page: no horizontal scroll, nav, back to top
    for name in ["index.html", "report.html", "court.html", "music.html", "lore.html"]:
        p = page(name)
        sw = p.evaluate("document.documentElement.scrollWidth"); cw = p.evaluate("document.documentElement.clientWidth")
        check(f"{tag} {name} no sideways scroll", sw <= cw + 1, f"{sw} > {cw}")
        check(f"{tag} {name} nav marks current page", p.locator('.nav a[aria-current="page"]').count() == 1)
        p.evaluate("window.scrollTo(0, 2000)"); p.wait_for_timeout(250)
        if p.evaluate("document.documentElement.scrollHeight") > 2900:
            check(f"{tag} {name} back-to-top appears", p.locator(".to-top").is_visible())
            p.click(".to-top"); p.wait_for_timeout(900)
            check(f"{tag} {name} back-to-top scrolls up", p.evaluate("window.scrollY") < 50, p.evaluate("window.scrollY"))
        p.close()

    # ---------- home
    p = page("index.html")
    h0 = p.inner_text("#tv-headline")
    check(f"{tag} TV prev disabled at start", p.locator("#tv-prev").is_disabled())
    p.click("#tv-next"); p.wait_for_timeout(2600)
    h1 = p.inner_text("#tv-headline")
    check(f"{tag} TV changes channel", h1 != h0 and len(h1) > 3, h1)
    check(f"{tag} TV watch link follows channel", "watch?v=" in p.get_attribute("#tv-find", "href"))
    check(f"{tag} TV archive link follows channel", p.get_attribute("#tv-ep", "href").startswith("report.html#ep-"))
    p.click("#tv-prev"); p.wait_for_timeout(2600)
    check(f"{tag} TV back returns", p.inner_text("#tv-headline") == h0, p.inner_text("#tv-headline"))
    p.click("#tv-scan"); p.wait_for_timeout(200)
    check(f"{tag} TV scan toggles on", p.get_attribute("#tv-scan", "aria-pressed") == "true")
    p.click("#tv-scan")
    check(f"{tag} TV scan toggles off", p.get_attribute("#tv-scan", "aria-pressed") == "false")
    f0 = p.inner_text("#fotd-text"); p.click("#fotd-next")
    check(f"{tag} fact of the day changes", p.inner_text("#fotd-text") != f0)
    p.fill("#citName", "Thomas"); p.click("#citForm button[type=submit]")
    check(f"{tag} citizenship card issues", p.inner_text("#cName") == "Thomas" and "Welcome" in p.inner_text("#citStatus"))
    p.fill("#citName", ""); p.click("#citForm button[type=submit]")
    check(f"{tag} citizenship requires a name", p.inner_text("#cName") == "Thomas")
    check(f"{tag} five video cards", p.locator(".vid").count() == 5)
    check(f"{tag} video cards have art", p.locator(".vid .card-art").count() == 5)
    check(f"{tag} gallery images load", p.evaluate("[...document.querySelectorAll('.plate-art img')].every(i=>i.complete&&i.naturalWidth>0)"))
    p.close()

    # ---------- report
    p = page("report.html")
    vis = lambda: p.evaluate("[...document.querySelectorAll('#archive-list .ep')].filter(r=>!r.hidden).length")
    check(f"{tag} archive shows 24 at rest", vis() == 24, vis())
    p.click("#ep-more"); check(f"{tag} show all reveals every episode", vis() == len(EPISODES), vis())
    p.fill("#ep-search", "hozier"); p.wait_for_timeout(250)
    check(f"{tag} search finds Hozier episodes", vis() == 2, vis())
    p.fill("#ep-search", "zzzz"); p.wait_for_timeout(250)
    check(f"{tag} empty state shows", p.locator("#ep-empty").is_visible())
    p.press("#ep-search", "Escape"); p.wait_for_timeout(200)
    p.click('[data-season="3"]'); check(f"{tag} season 3 filter", vis() == 38, vis())
    p.click('[data-tag="Spooky"]'); n = vis()
    check(f"{tag} season + topic filter", 0 < n < 38, n)
    p.click('[data-season="all"]'); p.click('[data-tag="all"]')
    p.click("#ep-sort"); first = p.evaluate("[...document.querySelectorAll('#archive-list .ep')].find(r=>!r.hidden).id")
    check(f"{tag} newest first sort", first == f"ep-{len(EPISODES):03d}", first)
    p.click("#ep-sort")
    p.click("#ep-random"); p.wait_for_timeout(300)
    check(f"{tag} spin picks an episode", p.locator(".ep.picked").count() == 1)
    p.click('.lore a[href="#ep-059"]'); p.wait_for_timeout(700)
    check(f"{tag} running-bit link jumps to episode", p.evaluate("!document.getElementById('ep-059').hidden && document.getElementById('ep-059').classList.contains('picked')"))
    check(f"{tag} every episode has a watch link", p.locator(".ep-go").count() == len(EPISODES))
    check(f"{tag} watch links are direct videos", p.evaluate("[...document.querySelectorAll('.ep-go')].every(a=>/watch\\?v=[\\w-]{11}/.test(a.href))"))
    check(f"{tag} report playlist present", p.locator("#tune-in .playlist").count() == 1)
    p.close()
    p = page("report.html#ep-100")
    p.wait_for_timeout(500)
    check(f"{tag} deep link #ep-100 opens", p.evaluate("!document.getElementById('ep-100').hidden"))
    p.close()

    # ---------- court
    p = page("court.html")
    g = lambda: p.evaluate("[...document.querySelectorAll('#roll-list .guest')].filter(r=>!r.hidden).length")
    from data import COURT
    check(f"{tag} all {len(COURT)} knights", g() == len(COURT), g())
    p.fill("#g-search", "harry"); check(f"{tag} knight search", g() == 1, g())
    p.fill("#g-search", ""); p.click('[data-cs="1"]'); check(f"{tag} knight season filter", g() == 7, g())
    p.click('[data-cs="all"]'); p.click("#g-random"); p.wait_for_timeout(300)
    check(f"{tag} summon a knight", p.locator(".guest.picked").count() == 1)
    check(f"{tag} guests link to their videos", p.locator("a.guest").count() == len(COURT) - 1 and p.evaluate("[...document.querySelectorAll('a.guest')].every(a=>/watch\\?v=[\\w-]{11}/.test(a.href))"))
    check(f"{tag} playlist present", p.locator(".playlist").count() == 1)
    before = p.inner_html("#shield")
    p.click('.icon-btn[data-q="0"][data-icon="ghost"]'); p.click('.swatch[data-q="0"][data-color="#FF7A1A"]')
    check(f"{tag} crest updates", p.inner_html("#shield") != before)
    p.fill("#motto", "Dragons are real"); check(f"{tag} motto updates", p.inner_text("#motto-out") == "Dragons are real")
    p.click("#arms-random"); check(f"{tag} randomize crest keeps 4 picks", p.locator('.icon-btn[aria-pressed="true"]').count() == 4)
    p.click("#arms-copy"); p.wait_for_timeout(200)
    check(f"{tag} blazon copy reports", len(p.inner_text("#arms-status")) > 5, p.inner_text("#arms-status"))
    p.close()

    # ---------- lore
    p = page("lore.html")
    fv = lambda: p.evaluate("[...document.querySelectorAll('#fact-list .fact')].filter(r=>!r.hidden).length")
    check(f"{tag} 33 facts", fv() == 33, fv())
    p.click('[data-fc="Music"]'); check(f"{tag} fact category filter", fv() == 4, fv())
    p.click('[data-fc="all"]'); p.fill("#f-search", "coffee"); check(f"{tag} fact search", fv() == 1, fv())
    p.fill("#f-search", ""); p.click("#f-random"); p.wait_for_timeout(200)
    check(f"{tag} surprise fact", p.locator(".fact.picked").count() == 1)
    p.locator(".copy-fact").first.click(); p.wait_for_timeout(150)
    check(f"{tag} copy fact feedback", p.locator(".copy-fact").first.inner_text() in ("Copied", "Blocked"))
    # quiz: answer everything with keyboard
    for i in range(12):
        p.locator("#q-answers .answer").first.focus()
        p.keyboard.press("1"); p.wait_for_timeout(60)
        check(f"{tag} quiz q{i+1} answered", p.locator("#q-next").is_visible())
        p.click("#q-next")
    check(f"{tag} quiz shows result", p.locator("#q-result").is_visible())
    check(f"{tag} quiz rank set", len(p.inner_text("#q-rank")) > 3)
    p.click("#q-again"); check(f"{tag} quiz retake resets", p.locator("#q-stage").is_visible() and "Question 1" in p.inner_text("#q-num"))
    p.close()

    # ---------- page wipe navigation
    p = page("index.html")
    p.click('.nav a[href="music.html"]'); p.wait_for_timeout(1400)
    check(f"{tag} nav navigates to music", p.url.endswith("music.html"), p.url)
    p.close()

    check(f"{tag} no script errors", not errs, "; ".join(errs[:3]))
    ctx.close()

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    run(1280); run(390); run(1280, reduced=True)
    browser.close()

fails = [r for r in results if not r[1]]
for n, ok, info in results:
    if not ok: print("FAIL", n, info)
print(f"{len(results)-len(fails)}/{len(results)} checks passed")
sys.exit(1 if fails else 0)
