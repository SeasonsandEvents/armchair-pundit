"""Make pins/football-quiz.png, the Pinterest and share image for the quiz page.

Run from the repo root:
    python3 tools/make_quiz_pin.py
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import quiz_page  # noqa: E402

FONTS = ROOT / "tools" / "fonts"
PAPER, INK, MUTED, GREEN, FLAG, WHITE = (
    "#F7F8F4", "#16233A", "#5B6474", "#1F5B3A", "#E8B931", "#FFFFFF")
W, H = 1000, 1500


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


SLAB_B = lambda s: font("zilla-slab-latin-700-normal.woff", s)
SLAB_M = lambda s: font("zilla-slab-latin-500-normal.woff", s)
SANS = lambda s: font("source-sans-3-latin-400-normal.woff", s)
SANS_B = lambda s: font("source-sans-3-latin-600-normal.woff", s)


def wrap(d, text, f, width):
    lines, line = [], ""
    for word in text.split():
        t = (line + " " + word).strip()
        if d.textlength(t, font=f) <= width:
            line = t
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def centred(d, y, text, f, fill, tracking=0):
    if tracking:
        w = sum(d.textlength(ch, font=f) for ch in text) + tracking * (len(text) - 1)
        x = (W - w) / 2
        for ch in text:
            d.text((x, y), ch, font=f, fill=fill)
            x += d.textlength(ch, font=f) + tracking
    else:
        d.text(((W - d.textlength(text, font=f)) / 2, y), text, font=f, fill=fill)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 120], fill=GREEN)
centred(d, 30, "INJURY TIME PUZZLES", SANS_B(30), WHITE, tracking=6)
centred(d, 72, "FREE FOOTBALL QUIZ", SANS(22), "#CFE3D6", tracking=5)

y = 170
centred(d, y, "30 questions and answers", SLAB_M(40), MUTED)
y += 60
for line in wrap(d, "Football general knowledge quiz", SLAB_B(84), W - 120):
    centred(d, y, line, SLAB_B(84), INK)
    y += 94
y += 30

samples = [quiz_page.ROUNDS[0][1][2][0], quiz_page.ROUNDS[1][1][1][0], quiz_page.ROUNDS[2][1][6][0],
           quiz_page.ROUNDS[2][1][9][0]]
qf, nf = SANS(34), SLAB_B(40)
for i, q in enumerate(samples, 1):
    lines = wrap(d, q, qf, W - 280)
    box_h = 40 + 44 * len(lines)
    d.rounded_rectangle([80, y, W - 80, y + box_h], radius=14, fill=WHITE, outline="#D9DDD3", width=2)
    d.ellipse([104, y + 20, 160, y + 76], fill=FLAG)
    d.text((132 - d.textlength(str(i), font=nf) / 2, y + 24), str(i), font=nf, fill=INK)
    ty = y + 20
    for line in lines:
        d.text((184, ty), line, font=qf, fill=INK)
        ty += 44
    y += box_h + 26

centred(d, y + 6, "1992 to today, in three rounds. How many can you get?", SANS(30), MUTED)

box_top = H - 190
d.rounded_rectangle([90, box_top, W - 90, box_top + 96], radius=14, fill=GREEN)
centred(d, box_top + 22, "Play free online, no sign-up", SLAB_B(44), WHITE)
centred(d, H - 72, "injurytimepuzzles.co.uk", SANS_B(34), GREEN)
out = ROOT / "pins" / "football-quiz.png"
img.save(out, optimize=True)
print(out)
