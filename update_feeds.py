"""Checks the Broski Report and Royal Court YouTube channels for new episodes.

New episodes are appended to auto_episodes.json, which data.py merges into the
site data. Run by .github/workflows/update.yml once a day; safe to run by hand:

    python3 update_feeds.py && EMBED=1 python3 build.py

Exit codes: 0 = ran fine (check the printed summary), 1 = YouTube's page format
changed or a request failed, so nothing was written.
"""
import json, os, re, sys, time, urllib.request
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


def channel_videos(html):
    """Return [(video_id, title)] newest first from a channel's /videos page."""
    found, seen = [], set()
    def walk(o):
        if isinstance(o, dict):
            if "lockupViewModel" in o and o["lockupViewModel"].get("contentId"):
                l = o["lockupViewModel"]
                title = (((l.get("metadata") or {}).get("lockupMetadataViewModel") or {}).get("title") or {}).get("content")
                if title and l["contentId"] not in seen:
                    seen.add(l["contentId"]); found.append((l["contentId"], title))
                return
            if "videoRenderer" in o:
                v = o["videoRenderer"]; runs = (v.get("title") or {}).get("runs") or []
                if v.get("videoId") and runs and v["videoId"] not in seen:
                    seen.add(v["videoId"]); found.append((v["videoId"], runs[0]["text"]))
                return
            for val in o.values(): walk(val)
        elif isinstance(o, list):
            for val in o: walk(val)
    walk(initial_data(html))
    return found


def video_details(html):
    """Return (YYYY-MM-DD, length_seconds) from a watch page."""
    date = re.search(r'"(?:publishDate|uploadDate)":"(\d{4}-\d{2}-\d{2})', html)
    length = re.search(r'"lengthSeconds":"(\d+)"', html)
    if not date:
        raise RuntimeError("publish date not found on watch page")
    return date.group(1), int(length.group(1)) if length else 0


def main():
    auto = {"report": [], "court": [], "skipped": []}
    if os.path.exists(AUTO):
        auto.update(json.load(open(AUTO, encoding="utf-8")))
    skipped = set(auto["skipped"])
    known = {"report": set(EPISODE_VIDEO_IDS) | skipped, "court": {v for v in COURT_VIDEO_IDS if v} | skipped}
    added = []
    changed_skips = False
    for show, channel in CHANNELS.items():
        vids = channel_videos(get(f"https://www.youtube.com/channel/{channel}/videos"))
        if not vids:
            raise RuntimeError(f"no videos parsed for {show}; page format may have changed")
        new = [(vid, title) for vid, title in vids if vid not in known[show]]
        for vid, title in reversed(new):            # oldest first, so the archive stays in order
            if show == "court":
                m = COURT_TITLE.match(title)
                if not m:
                    print(f"skip court video (not an episode): {title}"); auto["skipped"].append(vid); changed_skips = True; continue
            date, seconds = video_details(get(f"https://www.youtube.com/watch?v={vid}"))
            time.sleep(1)
            if show == "report":
                if seconds and seconds < MIN_REPORT_SECONDS:
                    print(f"skip report video (only {seconds}s): {title}"); auto["skipped"].append(vid); changed_skips = True; continue
                auto["report"].append({"id": vid, "date": date, "title": title})
            else:
                auto["court"].append({"id": vid, "date": date, "guest": m.group("guest").strip()})
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
