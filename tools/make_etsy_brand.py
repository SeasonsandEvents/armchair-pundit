"""Make the Etsy shop brand images in etsy-assets/ (logo, seller photo, big banner).

Run from the repo root:
    python3 tools/make_etsy_brand.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "etsy-assets"
OUT.mkdir(exist_ok=True)
FONTS = ROOT / "tools" / "fonts"
GREEN, INK, FLAG, WHITE, PAPER, MUTED = "#1F5B3A", "#16233A", "#E8B931", "#FFFFFF", "#F7F8F4", "#5B6474"
SLAB_B = lambda s: ImageFont.truetype(str(FONTS / "zilla-slab-latin-700-normal.woff"), s)
SLAB_M = lambda s: ImageFont.truetype(str(FONTS / "zilla-slab-latin-500-normal.woff"), s)
SANS_B = lambda s: ImageFont.truetype(str(FONTS / "source-sans-3-latin-600-normal.woff"), s)

LAYOUT = [[None, "", None], ["I", "T", "P"], [None, "", None]]


def cross(d, cx, cy, grid, cell_fill, mid_fill, ink):
    cell = grid / 3
    x0, y0 = cx - grid / 2, cy - grid / 2
    f = SLAB_B(int(cell * 0.62))
    gap = max(2, int(grid / 90))
    for r, row in enumerate(LAYOUT):
        for c, ch in enumerate(row):
            if ch is None:
                continue
            x, y = x0 + c * cell, y0 + r * cell
            d.rectangle([x + gap, y + gap, x + cell - gap, y + cell - gap],
                        fill=mid_fill if (r, c) == (1, 1) else cell_fill)
            if ch:
                w = d.textlength(ch, font=f)
                d.text((x + (cell - w) / 2, y + cell * 0.12), ch, font=f, fill=ink)


def spaced(d, y, text, f, fill, width, tracking):
    w = sum(d.textlength(ch, font=f) for ch in text) + tracking * (len(text) - 1)
    x = (width - w) / 2
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + tracking


# Logo: green ground, the I-T-P cross, name underneath
S = 1000
img = Image.new("RGB", (S, S), GREEN)
d = ImageDraw.Draw(img)
cross(d, S / 2, S * 0.42, S * 0.52, WHITE, FLAG, INK)
spaced(d, S * 0.76, "INJURY TIME PUZZLES", SANS_B(54), WHITE, S, 8)
img.save(OUT / "logo.png", optimize=True)

# Seller photo: the inverse, paper ground with green cells
img = Image.new("RGB", (S, S), PAPER)
d = ImageDraw.Draw(img)
cross(d, S / 2, S / 2, S * 0.62, GREEN, FLAG, WHITE)
img.save(OUT / "seller.png", optimize=True)

# Big banner 3360x840: typographic, everything kept central so it survives a crop
W, H = 3360, 840
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 18], fill=GREEN)
d.rectangle([0, H - 18, W, H], fill=GREEN)
f1 = SLAB_B(150)
a, b = "Injury Time ", "Puzzles"
wa, wb = d.textlength(a, font=f1), d.textlength(b, font=f1)
icon = 190
gapx = 50
total = icon + gapx + wa + wb
x = (W - total) / 2
cross(d, x + icon / 2, 300, icon, GREEN, FLAG, WHITE)
x += icon + gapx
d.text((x, 205), a, font=f1, fill=INK)
d.text((x + wa, 205), b, font=f1, fill=GREEN)
d.line([(W / 2 - 260, 445), (W / 2 + 260, 445)], fill=FLAG, width=6)
t = "Printable sports crosswords and quizzes"
f2 = SLAB_M(72)
d.text(((W - d.textlength(t, font=f2)) / 2, 490), t, font=f2, fill=MUTED)
spaced(d, 640, "FOOTBALL  ·  GOLF  ·  DARTS", SANS_B(48), GREEN, W, 10)
img.save(OUT / "banner.png", optimize=True)
print("written to", OUT)
