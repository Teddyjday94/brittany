# The Broski Bulletin

An unofficial, fan-made Brittany Broski site. It is static HTML, CSS, and JS with no build step needed to view it.

## View it

YouTube only plays embedded videos on pages that have a web address. If you double-click `index.html`, the page opens as a local file with no address, and YouTube shows "Error 153: Video player configuration error." The site detects this and opens videos in a new YouTube tab instead.

To get the videos playing right on the page, serve the folder with a local web server:

```
cd broski-bulletin
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser. On Vercel or any other host, the videos play on the page automatically.

Fonts load from Google Fonts, and the hero's bubble animation loads p5.js from cdnjs. Both need an internet connection.

The Watch the Nation cards, the "Tune in" Broski Report playlist, and the "Hold court" Royal Court playlist all play through YouTube's privacy-enhanced player. The coat of arms maker can also save your crest as a PNG.

## What's inside

| File | What it is |
|---|---|
| `index.html` | Home: hero with the portrait and fizz animation, the Emergency Broadcast TV, video picks, daily fact, gallery, citizenship papers |
| `report.html` | Broski Report archive (136 episodes, each playable in the Tune in player), topic chart, running bits |
| `court.html` | Royal Court format, all 83 guests (each playable in the Hold court player), coat of arms maker |
| `music.html` | Singles with playable official videos, influences, musicians at court |
| `lore.html` | 33 sourced facts, timeline, citizenship exam |
| `styles.css` | Shared styles |
| `app.js` | Shared behavior. Each feature runs only on pages that contain its markup. |
| `motion.js` | Motion layer: scroll progress bar, reveals, parallax, fizz cursor, magnetic buttons, card tilt, sticky header, page wipes. Turns itself off for visitors with reduced motion; cursor effects run only with a mouse or trackpad. |
| `portrait.webp` | Hero portrait: a cutout of a still from Sarah Baska's 2021 YouTube video, licensed CC BY 3.0 on [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Brittany_Broski_cow_video_2021_05.png). The credit under the photo is required by the license, so keep it. `art/photo/make_portrait.py` rebuilds it. |
| `seal.webp` | The Great Seal of Broski Nation (Plate IX) |
| `poster.webp` | First Sip (Plate VIII) |
| `test_site.py` | Automated checks for every feature (230 checks across desktop, phone, and reduced motion). Run `python3 test_site.py` after changes. Needs Playwright with Chromium. |
| `contrast_audit.py` | Flags any text whose color contrast is below WCAG AA. Run `python3 contrast_audit.py`. |
| `update_feeds.py` | Daily updater: finds new episodes on YouTube and saves them to `auto_episodes.json`. |
| `data.py` | Every episode, guest, fact, video, and quiz question, with sources, plus the YouTube video IDs for every episode |
| `build.py` | Regenerates all five HTML pages from `data.py` |
| `art/` | Full-size art, the source files that draw it, and the design notes |

## Update content

Edit the lists in `data.py`, or the `VIDEOS` list near the top of `build.py` to add YouTube picks. Each pick uses the ID from its YouTube link. Then run:

```
EMBED=1 python3 build.py
```

`EMBED=1` turns on click-to-play videos. Leave it off to get plain link cards instead, which is the right choice for hosts that block embedded players. Don't hand-edit the HTML pages, because the next build overwrites them.

## Automatic updates

A GitHub Action (`.github/workflows/update.yml`) runs every day at 8:17 AM Central. It checks the Broski Report and Royal Court YouTube channels, adds any new episodes to `auto_episodes.json`, rebuilds the pages, and commits. Vercel then redeploys on its own.

- New Report episodes need to run at least 20 minutes, so clips and Shorts are skipped.
- New Royal Court episodes need a title like "Name Joins Brittany Broski's Royal Court". Other uploads are skipped.
- New episodes join the latest season. If a new season starts, change the season number for those entries in `data.py`.
- To update right away, open the repo's **Actions** tab, pick **Daily episode update**, and click **Run workflow**.
- If YouTube changes its page layout, the run fails and GitHub emails you. The site keeps working; it just stops picking up new episodes until `update_feeds.py` is adjusted.

## Redraw the art

- **Great Seal:** `art/great-seal.html` is an SVG drawing. To export it, run `python3 art/render.py "$PWD/art/great-seal.html" art/great-seal.png 2`, which needs Playwright with Chromium. Update the font paths at the top of the HTML first.
- **First Sip:** run `python3 art/poster.py`, which needs Pillow. Update its font path first.

## Deploy

The site is static, so Vercel needs no framework preset. Push this folder to a GitHub repo, import it in Vercel, and leave the build command empty.

## Notes

The site is not affiliated with Brittany Broski, The Broski Report, Royal Court, or Atlantic Records. Every fact links to a public source, and every video plays from her official YouTube uploads.
