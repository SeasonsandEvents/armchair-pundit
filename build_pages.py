"""Build one page per crossword, an archive page and the sitemap.

Run from the repo root after any change to the PUZZLES array in index.html:
    python3 build_pages.py

index.html stays the source of truth. Every page under /puzzles/ is generated
from it, so never edit those by hand.
"""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://injurytimepuzzles.co.uk"
TODAY = date.today().isoformat()

src = (ROOT / "index.html").read_text(encoding="utf-8")


def puzzles_from(page):
    a = page.index("const PUZZLES = ") + len("const PUZZLES = ")
    e = page.index("const EPOCH")
    return json.loads(page[a:e].strip().rstrip(";"))


PUZZLES = puzzles_from(src)


def slug_for(p):
    t = p["title"]
    m = re.match(r"England's top flight, (\d{4})[–-](\d{2,4})$", t)
    if m:
        return f"football-season-{m.group(1)}-{m.group(2)}"
    s = re.sub(r"[–—]", "-", t.lower())
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return f"{p['kind']}-{s}"


def season_of(p):
    m = re.match(r"England's top flight, (.+)$", p["title"])
    return m.group(1) if m else None


def page_title(p):
    s = season_of(p)
    if s:
        return f"{s} Football Crossword: England's Top Flight"
    return f"{p['title']}: Golf Crossword"


def heading(p):
    s = season_of(p)
    return f"The {s} season crossword" if s else f"{p['title']}: a golf crossword"


def description(p):
    n = len(p["words"])
    s = season_of(p)
    if s:
        return (f"A free {n}-clue crossword on the {s} season in England's top flight: "
                f"managers, players, cup finals and awards. Play online, no sign-up.")
    return (f"A free {n}-clue golf crossword: {p['title']}. "
            f"Champions, venues and moments from the majors. Play online, no sign-up.")


def intro(p):
    n = len(p["words"])
    s = season_of(p)
    if s:
        about = (f"How well do you remember the {s} season? {n} clues on the managers, "
                 f"players, results and awards from England's top flight that year.")
    else:
        about = f"{n} clues on {p['title']}, from the champions to the courses they won on."
    return (f'<p class="intro">{html.escape(about)} Fill it in below, check as you go, '
            f'and reveal a letter if you are stuck. A new crossword goes up every day: '
            f'<a href="/">play today\'s</a> or <a href="/puzzles/">browse every puzzle</a>.</p>')


SLUGS = [slug_for(p) for p in PUZZLES]
assert len(set(SLUGS)) == len(SLUGS), "duplicate slugs"


def numbered(p):
    """Same numbering as the page's own script, so the static clue list matches."""
    starts, n = {}, 0
    for r in range(p["rows"]):
        for c in range(p["cols"]):
            here = [w for w in p["words"] if w["r"] == r and w["c"] == c]
            if here:
                n += 1
                for w in here:
                    starts[id(w)] = n
    return sorted(p["words"], key=lambda w: starts[id(w)]), starts


def static_clues(p, d):
    words, starts = numbered(p)
    out = []
    for w in words:
        if w["d"] != d:
            continue
        enum = "" if re.search(r"\(\d[\d,]*\)\s*$", w["clue"]) else f"({w.get('enum') or len(w['w'])})"
        out.append(f'<li><b>{starts[id(w)]}</b><span>{html.escape(w["clue"])} '
                   f'<span class="enum">{enum}</span></span></li>')
    return "".join(out)


def set_meta(page, url, title, desc, image):
    page = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', page)
    page = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', page)
    page = re.sub(r'<meta property="og:title" content="[^"]*">',
                  f'<meta property="og:title" content="{html.escape(title)}">', page)
    page = re.sub(r'<meta property="og:description" content="[^"]*">',
                  f'<meta property="og:description" content="{html.escape(desc)}">', page)
    page = re.sub(r'<meta name="description" content="[^"]*">',
                  f'<meta name="description" content="{html.escape(desc)}">', page)
    page = re.sub(r"<title>[^<]*</title>", f"<title>{html.escape(title)}</title>", page)
    page = re.sub(r'\n<meta property="og:image"[^>]*>|\n<meta name="twitter:card"[^>]*>', "", page)
    page = page.replace(
        "<title>",
        f'<meta property="og:image" content="{image}">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n<title>', 1)
    return page


# --- shared fixes on index.html itself -------------------------------------
home = src
# archive labels: format the UTC date in UTC, so visitors outside the UK see the right day
home = home.replace(
    "toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short'})",
    "toLocaleDateString('en-GB',{weekday:'short',day:'numeric',month:'short',timeZone:'UTC'})")
# "Today" on a puzzle's own page goes back to the home page
home = home.replace(
    "b.onclick=()=>{pidx=t;load();};",
    "b.onclick=()=>{if(typeof window.ITP_FIXED==='number'){location.href='/';return;}pidx=t;load();};")
# crawlable link to the archive, under the puzzle picker
ARCHIVE_LINK = '<p class="allp"><a href="/puzzles/">Every crossword so far</a></p>'
if 'class="allp"' not in home:
    home = home.replace('<div class="picker" id="picker" aria-label="Choose a puzzle"></div>\n  </div>',
                        '<div class="picker" id="picker" aria-label="Choose a puzzle"></div>\n  </div>\n  '
                        + ARCHIVE_LINK, 1)
EXTRA_CSS = (".intro{max-width:72ch;color:var(--muted);margin:-6px 0 16px}"
             ".allp{margin:-8px 0 14px;font-size:14px}.allp a,.intro a{color:var(--green)}")
if ".allp{" not in home:
    home = home.replace("</style>", EXTRA_CSS + "\n</style>", 1)
home = set_meta(home, f"{SITE}/", "Injury Time Puzzles: the Daily Crossword",
                "A free daily sports crossword from Injury Time Puzzles. Twelve clues, one grid, "
                "a fresh puzzle every day.", f"{SITE}/pins/daily.png")
(ROOT / "index.html").write_text(home, encoding="utf-8")

# --- one page per puzzle ---------------------------------------------------
out_dir = ROOT / "puzzles"
if out_dir.exists():
    shutil.rmtree(out_dir)
out_dir.mkdir()

for i, (p, slug) in enumerate(zip(PUZZLES, SLUGS)):
    url = f"{SITE}/puzzles/{slug}/"
    pg = set_meta(home, url, page_title(p), description(p), f"{SITE}/pins/{slug}.png")
    pg = pg.replace('<h2 id="ptitle"></h2>', f'<h2 id="ptitle">{html.escape(heading(p))}</h2>', 1)
    pg = pg.replace(ARCHIVE_LINK, intro(p), 1)
    pg = pg.replace('<ol id="across"></ol>', f'<ol id="across">{static_clues(p, "A")}</ol>', 1)
    pg = pg.replace('<ol id="down"></ol>', f'<ol id="down">{static_clues(p, "D")}</ol>', 1)
    # play this puzzle, not today's; a "carry on" link still wins
    pg = pg.replace("\napplyHandoff();", f"\nwindow.ITP_FIXED={i};pidx={i};\napplyHandoff();", 1)
    # load() writes the plain title into the heading; keep ours
    pg = pg.replace("$('ptitle').textContent=P.title;",
                    "if(typeof window.ITP_FIXED!=='number')$('ptitle').textContent=P.title;", 1)
    d = out_dir / slug
    d.mkdir()
    (d / "index.html").write_text(pg, encoding="utf-8")

# --- archive page ------------------------------------------------------------
style = home[home.index("<style>"):home.index("</style>") + len("</style>")]
fonts = re.search(r'<link rel="preconnect"[^\n]*\n<link rel="stylesheet"[^\n]*', home).group(0)


def season_key(p):
    s = season_of(p)
    return int(s[:4]) if s else 0


football = sorted([(p, s) for p, s in zip(PUZZLES, SLUGS) if p["kind"] == "football"],
                  key=lambda x: season_key(x[0]))
golf = [(p, s) for p, s in zip(PUZZLES, SLUGS) if p["kind"] != "football"]


def items(group, label):
    return "".join(f'<li><a href="/puzzles/{s}/">{html.escape(label(p))}</a></li>' for p, s in group)


arch_desc = ("Every free crossword from Injury Time Puzzles: a crossword for each season of "
             "England's top flight since 1992–93, plus golf's majors. Play any of them online.")
archive = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{html.escape(arch_desc)}">
<link rel="canonical" href="{SITE}/puzzles/">
<meta property="og:url" content="{SITE}/puzzles/">
<meta property="og:title" content="Every crossword | Injury Time Puzzles">
<meta property="og:description" content="{html.escape(arch_desc)}">
<meta property="og:image" content="{SITE}/pins/daily.png">
<title>Football and Golf Crosswords, Season by Season</title>
{fonts}
{style}
<style>.arch h2{{font-family:var(--display);font-weight:500;font-size:22px;margin:22px 0 8px}}
.arch ul{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:6px 18px}}
.arch a{{color:var(--green);font-weight:600;text-decoration:none}}.arch a:hover{{text-decoration:underline}}
.arch p{{max-width:72ch;color:var(--muted)}}</style>
</head>
<body>
<div class="wrap">
  <header><h1 class="brand"><a href="/" style="color:inherit;text-decoration:none">Injury Time <span>Puzzles</span></a></h1></header>
  <main class="arch">
    <p>Every crossword we have published, free to play in your browser. There is a new one
    every day on the <a href="/">home page</a>.</p>
    <h2>England's top flight, season by season</h2>
    <ul>{items(football, lambda p: season_of(p) + " season")}</ul>
    <h2>Golf</h2>
    <ul>{items(golf, lambda p: p["title"])}</ul>
  </main>
</div>
</body>
</html>
"""
(out_dir / "index.html").write_text(archive, encoding="utf-8")

# --- embed page: today's crossword for other sites to show in an iframe -------
EMBED_CSS = """<style>
header,.sub .picker select,.allp,.handoff,#handBtn,#bigBtn,.signup,.shelf,.done-panel p a[href="#signup"]{display:none!important}
.wrap{padding-block:8px 8px}.sub{margin:4px 0 10px}
.embed-foot{margin-top:12px;font-size:14px;text-align:center;color:var(--muted)}
.embed-foot a{color:var(--green);font-weight:600}
</style>"""
embed = set_meta(home, f"{SITE}/", "Injury Time Puzzles: the Daily Crossword",
                 "A free daily sports crossword from Injury Time Puzzles.", f"{SITE}/pins/daily.png")
embed = embed.replace("<title>", '<meta name="robots" content="noindex">\n<base target="_blank">\n<title>', 1)
embed = embed.replace("</style>", "</style>\n" + EMBED_CSS, 1)
embed = embed.replace(
    '<section class="signup"',
    '<p class="embed-foot">A free sports crossword every day from '
    '<a href="https://injurytimepuzzles.co.uk/?utm_source=embed" rel="noopener">Injury Time Puzzles</a>'
    ' &middot; <a href="https://injurytimepuzzles.co.uk/puzzles/?utm_source=embed" rel="noopener">every season so far</a></p>\n'
    '  <section class="signup"', 1)
(ROOT / "embed").mkdir(exist_ok=True)
(ROOT / "embed" / "index.html").write_text(embed, encoding="utf-8")

# --- sitemap -----------------------------------------------------------------
urls = [(f"{SITE}/", "daily"), (f"{SITE}/puzzles/", "weekly")] + \
       [(f"{SITE}/puzzles/{s}/", "monthly") for s in SLUGS]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, f in urls:
    sm.append(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <changefreq>{f}</changefreq>\n  </url>")
sm.append("</urlset>\n")
(ROOT / "sitemap.xml").write_text("\n".join(sm), encoding="utf-8")

# slug list for the pin builder and the Pinterest schedule
(ROOT / "puzzles" / "index.json").write_text(json.dumps(
    [{"i": i, "slug": s, "title": p["title"], "kind": p["kind"], "heading": heading(p),
      "description": description(p)} for i, (p, s) in enumerate(zip(PUZZLES, SLUGS))],
    ensure_ascii=False, indent=1), encoding="utf-8")

print(f"{len(PUZZLES)} puzzle pages, archive and sitemap ({len(urls)} URLs) written")
