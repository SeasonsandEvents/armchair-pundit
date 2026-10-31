"""Make a 1000x1500 Pinterest image for every crossword, plus pins/daily.png.

Run from the repo root after build_pages.py:
    python3 tools/make_pins.py

The same images are each puzzle page's share image (og:image).
"""
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
OUT = ROOT / "pins"
OUT.mkdir(exist_ok=True)

PAPER, INK, MUTED, GREEN, FLAG, BLOCK, WHITE = (
    "#F7F8F4", "#16233A", "#5B6474", "#1F5B3A", "#E8B931", "#16233A", "#FFFFFF")
W, H = 1000, 1500


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


SLAB_B = lambda s: font("zilla-slab-latin-700-normal.woff", s)
SLAB_M = lambda s: font("zilla-slab-latin-500-normal.woff", s)
SANS = lambda s: font("source-sans-3-latin-400-normal.woff", s)
SANS_B = lambda s: font("source-sans-3-latin-600-normal.woff", s)

src = (ROOT / "index.html").read_text(encoding="utf-8")
a = src.index("const PUZZLES = ") + len("const PUZZLES = ")
PUZZLES = json.loads(src[a:src.index("const EPOCH")].strip().rstrip(";"))
INDEX = json.loads((ROOT / "puzzles" / "index.json").read_text(encoding="utf-8"))


def wrap(draw, text, f, width):
    lines, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if draw.textlength(t, font=f) <= width:
            line = t
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def centred(draw, y, text, f, fill, tracking=0):
    if tracking:
        w = sum(draw.textlength(ch, font=f) for ch in text) + tracking * (len(text) - 1)
        x = (W - w) / 2
        for ch in text:
            draw.text((x, y), ch, font=f, fill=fill)
            x += draw.textlength(ch, font=f) + tracking
    else:
        draw.text(((W - draw.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


def draw_grid(draw, p, top, max_w, max_h):
    cell = int(min(max_w / p["cols"], max_h / p["rows"]))
    gw, gh = cell * p["cols"], cell * p["rows"]
    x0, y0 = (W - gw) // 2, top
    letters = set()
    starts, n = {}, 0
    for wd in p["words"]:
        for i in range(len(wd["w"])):
            letters.add((wd["r"] + (i if wd["d"] == "D" else 0), wd["c"] + (i if wd["d"] == "A" else 0)))
    for r in range(p["rows"]):
        for c in range(p["cols"]):
            if any(w["r"] == r and w["c"] == c for w in p["words"]):
                n += 1
                starts[(r, c)] = n
    draw.rectangle([x0 - 4, y0 - 4, x0 + gw + 4, y0 + gh + 4], fill=BLOCK)
    nf = SANS_B(max(12, int(cell * 0.3)))
    for r in range(p["rows"]):
        for c in range(p["cols"]):
            x, y = x0 + c * cell, y0 + r * cell
            if (r, c) in letters:
                fill = FLAG if starts.get((r, c)) == 1 else WHITE
                draw.rectangle([x + 1, y + 1, x + cell - 1, y + cell - 1], fill=fill)
                if (r, c) in starts:
                    draw.text((x + 4, y + 2), str(starts[(r, c)]), font=nf, fill=INK)
    return y0 + gh + 4


def first_clue(p):
    w = sorted(p["words"], key=lambda w: (w["r"], w["c"], w["d"]))[0]
    enum = "" if re.search(r"\(\d[\d,]*\)\s*$", w["clue"]) else f" ({w.get('enum') or len(w['w'])})"
    return f"1 {'across' if w['d'] == 'A' else 'down'}: {w['clue']}{enum}"


def pin(p, kicker, headline, teaser, path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # header band
    d.rectangle([0, 0, W, 120], fill=GREEN)
    centred(d, 30, "INJURY TIME PUZZLES", SANS_B(30), WHITE, tracking=6)
    centred(d, 72, "FREE DAILY CROSSWORD", SANS(22), "#CFE3D6", tracking=5)
    # headline
    y = 170
    centred(d, y, kicker, SLAB_M(40), MUTED)
    y += 58
    hf = SLAB_B(76)
    for line in wrap(d, headline, hf, W - 120)[:3]:
        centred(d, y, line, hf, INK)
        y += 86
    y += 20
    # grid
    bottom = draw_grid(d, p, y, W - 160, 1500 - y - 430)
    # teaser clue
    y = bottom + 34
    tf = SANS(32)
    for line in wrap(d, teaser, tf, W - 160)[:3]:
        centred(d, y, line, tf, INK)
        y += 42
    # call to action
    box_top = H - 190
    d.rounded_rectangle([90, box_top, W - 90, box_top + 96], radius=14, fill=GREEN)
    centred(d, box_top + 22, "Play free online, no sign-up", SLAB_B(44), WHITE)
    centred(d, H - 72, "injurytimepuzzles.co.uk", SANS_B(34), GREEN)
    img.save(path, optimize=True)


for meta, p in zip(INDEX, PUZZLES):
    m = re.match(r"England's top flight, (.+)$", p["title"])
    if m:
        kicker, headline = "Football crossword", f"How well do you remember {m.group(1)}?"
    else:
        kicker, headline = "Golf crossword", p["title"]
    pin(p, kicker, headline, first_clue(p), OUT / f"{meta['slug']}.png")

# generic image for the home page and archive
pin(PUZZLES[1], "Football and golf", "A free sports crossword every day",
    "Twelve clues, one grid, a fresh puzzle every morning.", OUT / "daily.png")
print(f"{len(INDEX) + 1} pin images in {OUT}")
