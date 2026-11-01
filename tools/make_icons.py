"""Make the home-screen app icons in /icons.

Run from the repo root:
    python3 tools/make_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "icons"
OUT.mkdir(exist_ok=True)
GREEN, INK, FLAG, WHITE = "#1F5B3A", "#16233A", "#E8B931", "#FFFFFF"
FONT = ROOT / "tools" / "fonts" / "zilla-slab-latin-700-normal.woff"

# a little crossword: a cross of five cells, I T P across, the middle cell in gold
LAYOUT = [[None, "", None], ["I", "T", "P"], [None, "", None]]


def icon(size, safe=0.8):
    img = Image.new("RGB", (size, size), GREEN)
    d = ImageDraw.Draw(img)
    grid = size * safe * 0.78
    cell = grid / 3
    x0 = y0 = (size - grid) / 2
    f = ImageFont.truetype(str(FONT), int(cell * 0.62))
    gap = max(2, size // 128)
    for r, row in enumerate(LAYOUT):
        for c, ch in enumerate(row):
            if ch is None:
                continue
            x, y = x0 + c * cell, y0 + r * cell
            d.rectangle([x + gap, y + gap, x + cell - gap, y + cell - gap],
                        fill=FLAG if (r, c) == (1, 1) else WHITE)
            if ch:
                w = d.textlength(ch, font=f)
                d.text((x + (cell - w) / 2, y + cell * 0.12), ch, font=f, fill=INK)
    return img


icon(512, 0.8).save(OUT / "icon-maskable-512.png", optimize=True)   # Android adaptive: keep inside safe zone
icon(512, 1.0).save(OUT / "icon-512.png", optimize=True)
icon(192, 1.0).save(OUT / "icon-192.png", optimize=True)
icon(180, 1.0).save(OUT / "apple-touch-icon.png", optimize=True)
icon(48, 1.0).save(OUT / "favicon-48.png", optimize=True)
print("icons written to", OUT)
