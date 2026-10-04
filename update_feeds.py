"""Checks the Broski Report and Royal Court YouTube channels for new episodes.

New episodes are appended to auto_episodes.json, which data.py merges into the
site data. Run by .github/workflows/update.yml once a day; safe to run by hand:

    python3 update_feeds.py && EMBED=1 python3 build.py

Exit codes: 0 = ran fine (check the printed summary), 1 = YouTube's page format
changed or a request failed, so nothing was written.
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from data import EPISODE_VIDEO_IDS, COURT_VIDEO_IDS, EPISODES, COURT

HERE = os.path.dirname(os.path.abspath(__file__))
AUTO = os.path.join(HERE, "auto_episodes.json")
CHANNELS = {
    "report": "UCdEwstTO8WsTHCyzrCSfXCQ",   # BroskiReport
    "court": "UCMSqyGyyqI_zWkyS22pk7bA",    # Royal Court
}
MIN_REPORT_SECONDS = 20 * 60          # skip clips and compilations shorter than a full episode
COURT_TITLE = re.compile(r"^(?P<guest>.+?)\s+Joins?\s+Brittany(?:\s+Broski)?['’]s\s+Royal Court", re.I)
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36",
           "Accept-Language": "en-US,en;q=0.9",
           "Cookie": "CONSENT=YES+cb; SOCS=CAI"}   # skip YouTube's cookie-consent interstitial


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def initial_data(html):
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    if not m:
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        raise RuntimeError("ytInitialData not found; page title was "
                           + repr(title.group(1)[:80] if title else html[:120]))
    return json.loads(m.group(1))


DURATION = re.compile(r'"(?:text|simpleText)":"((?:\d+:)?\d{1,2}:\d{2})"')
AGO = re.compile(r'"(?:content|simpleText)":"(?:Streamed |Premiered )?(\d+)\s*(second|sec|s|minute|min|m|hour|hr|h|day|d|week|wk|w|month|mo|year|yr|y)s?\s+ago"', re.I)
UNIT_DAYS = {"second": 0, "sec": 0, "s": 0, "minute": 0, "min": 0, "m": 0, "hour": 0, "hr": 0, "h": 0,
             "day": 1, "d": 1, "week": 7, "wk": 7, "w": 7, "month": 30, "mo": 30, "year": 365, "yr": 365, "y": 365}


def to_seconds(text):
    secs = 0
    for part in text.split(":"):
        secs = secs * 60 + int(part)
    return secs


def to_date(blob):
    """Posting date from YouTube's relative label ("4d ago", "3 hours ago"). Exact to the day for daily runs."""
    m = AGO.search(blob)
    days = int(m.group(1)) * UNIT_DAYS[m.group(2).lower()] if m else 0
    today = datetime.now(ZoneInfo("America/Chicago")).date()
    return (today - timedelta(days=days)).isoformat()


def channel_videos(html):
    """Return [(video_id, title, seconds, date)] newest first from a channel's /videos page."""
    found, seen = [], set()
    def add(vid, title, blob):
        if vid and title and vid not in seen:
            seen.add(vid)
            d = DURATION.search(blob)
            found.append((vid, title, to_seconds(d.group(1)) if d else 0, to_date(blob)))
    def walk(o):
        if isinstance(o, dict):
            if "lockupViewModel" in o and o["lockupViewModel"].get("contentId"):
                l = o["lockupViewModel"]
                title = (((l.get("metadata") or {}).get("lockupMetadataViewModel") or {}).get("title") or {}).get("content")
                add(l["contentId"], title, json.dumps(l, ensure_ascii=False, separators=(",", ":"))); return
            if "videoRenderer" in o:
                v = o["videoRenderer"]; runs = (v.get("title") or {}).get("runs") or []
                add(v.get("videoId"), runs[0]["text"] if runs else None, json.dumps(v, ensure_ascii=False, separators=(",", ":"))); return
            for val in o.values(): walk(val)
        elif isinstance(o, list):
            for val in o: walk(val)
    walk(initial_data(html))
    return found


def main():
    auto = {"report": [], "court": [], "skipped": []}
    if os.path.exists(AUTO):
        auto.update(json.load(open(AUTO, encoding="utf-8")))
    skipped = set(auto["skipped"]) | {e["id"] for e in auto["report"] + auto["court"]}
    known = {"report": set(EPISODE_VIDEO_IDS) | skipped, "court": {v for v in COURT_VIDEO_IDS if v} | skipped}
    added = []
    changed_skips = False
    for show, channel in CHANNELS.items():
        vids = channel_videos(get(f"https://www.youtube.com/channel/{channel}/videos"))
        if not vids:
            raise RuntimeError(f"no videos parsed for {show}; page format may have changed")
        new = [v for v in vids if v[0] not in known[show]]
        for vid, title, seconds, date in reversed(new):   # oldest first, so the archive stays in order
            if show == "court":
                m = COURT_TITLE.match(title)
                if not m:
                    print(f"skip court video (not an episode): {title}"); auto["skipped"].append(vid); changed_skips = True; continue
                auto["court"].append({"id": vid, "date": date, "guest": m.group("guest").strip()})
            else:
                if seconds and seconds < MIN_REPORT_SECONDS:
                    print(f"skip report video (only {seconds}s): {title}"); auto["skipped"].append(vid); changed_skips = True; continue
                auto["report"].append({"id": vid, "date": date, "title": title})
            added.append(f"{show}: {date} {title}")
    if added or changed_skips:
        with open(AUTO, "w", encoding="utf-8") as f:
            json.dump(auto, f, indent=1, ensure_ascii=False); f.write("\n")
    print(f"{len(added)} new episode(s)" + "".join("\n  " + a for a in added))
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"changed={'true' if added else 'false'}\n")
            f.write(f"summary={'; '.join(added)[:900]}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Update failed: {e}", file=sys.stderr)
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error title=Episode update failed::{e}")
        sys.exit(1)
