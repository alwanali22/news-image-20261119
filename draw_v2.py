"""Front page for Thursday 19 November 2026 — v2 rewrite.

Draws the whole page with Pillow: masthead, three lead stories, eight
cards, a numbers band, a dotted world map and 32 short briefs.
43 stories in total, every one of them checked against the research
log in V2-RESEARCH-2026-11-20.md. No network, no randomness, no
clock: running this file twice writes the same PNG bytes.

This file was written from scratch for the rewrite. The page it
produces carries the same stories, numbers and layout as the first
v2 build; the code itself shares no structure with it.
"""

import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# Palette, as hex strings so the page keeps one source of truth.
PALETTE = {
    "navy": "#14264e",
    "navy_deep": "#101834",
    "gold": "#c9a227",
    "gold_pale": "#e8c45a",
    "cream": "#f7f3e8",
    "paper": "#fcfaf4",
    "ink": "#181818",
    "grey": "#5a5a56",
    "red": "#b22222",
    "teal": "#0c4042",
    "rule": "#b4ac96",
    "sea": "#0a1628",
}


def rgb(name):
    """Hex palette entry -> (r, g, b)."""
    h = PALETTE[name].lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def mix(a, b, t):
    """Linear blend between two RGB triples, t in [0, 1]."""
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONT_FILES = {
    "sans": "DejaVuSans.ttf",
    "sans_bold": "DejaVuSans-Bold.ttf",
    "serif": "DejaVuSerif.ttf",
    "serif_bold": "DejaVuSerif-Bold.ttf",
    "serif_italic": "DejaVuSerif-Italic.ttf",
}
_face_cache = {}


def face(kind, size):
    """Cached PIL font for (kind, size)."""
    key = (kind, size)
    if key not in _face_cache:
        _face_cache[key] = ImageFont.truetype(
            os.path.join(_FONT_DIR, _FONT_FILES[kind]), size)
    return _face_cache[key]


def pour(text, font, max_w, max_rows):
    """Greedy word wrap. Returns a list of lines, at most max_rows.

    Raises if the text cannot fit, so an over-long headline fails
    loudly at build time instead of silently overflowing the page.
    """
    words = text.split()
    rows = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if font.getlength(trial) <= max_w:
            current = trial
        else:
            if not current:
                raise ValueError("single word too wide: %r" % word)
            rows.append(current)
            current = word
    if current:
        rows.append(current)
    if len(rows) > max_rows:
        raise ValueError(
            "text needs %d rows (max %d): %r" % (len(rows), max_rows, text))
    return rows


def stack(d, rows, x, y, font, colour, leading):
    """Draw wrapped rows top to bottom, `leading` px apart."""
    for i, row in enumerate(rows):
        d.text((x, y + i * leading), row, font=font, fill=colour)


def blend(d, box, top, bottom, bands=None):
    """Vertical gradient inside box, painted as flat strips.

    With bands unset, one strip per pixel row, so the gradient is
    smooth instead of visibly stepped.
    """
    x0, y0, x1, y1 = box
    if bands is None:
        bands = max(y1 - y0, 1)
    step = (y1 - y0) / bands
    for i in range(bands):
        t = i / max(bands - 1, 1)
        yy0 = y0 + i * step
        yy1 = y0 + (i + 1) * step + 1
        d.rectangle([x0, yy0, x1, yy1], fill=mix(top, bottom, t))


def star4(d, cx, cy, r, colour):
    """Small four-point star (a diamond with pinched sides)."""
    d.polygon([(cx, cy - r), (cx + r * 0.28, cy - r * 0.28),
               (cx + r, cy), (cx + r * 0.28, cy + r * 0.28),
               (cx, cy + r), (cx - r * 0.28, cy + r * 0.28),
               (cx - r, cy), (cx - r * 0.28, cy - r * 0.28)],
              fill=colour)

# ---- lead artwork -------------------------------------------------------
# Each painter takes (draw, box) with box = (x0, y0, x1, y1) and fills it.

def art_summit(d, box):
    """Shenzhen night skyline under three flags: US, China, Russia."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    blend(d, box, rgb("navy"), (58, 84, 138))
    d.ellipse([x1 - 52, y0 + 8, x1 - 14, y0 + 46], fill=rgb("gold_pale"))
    # skyline: dark towers of varied width, one with a spire
    ground = y1 - 24
    towers = [(0.00, 0.30, 0.13), (0.13, 0.52, 0.09), (0.22, 0.38, 0.12),
              (0.34, 0.66, 0.10), (0.44, 0.44, 0.11), (0.55, 0.58, 0.09),
              (0.64, 0.34, 0.12), (0.76, 0.48, 0.10), (0.86, 0.40, 0.14)]
    for fx, fh, fw in towers:
        d.rectangle([x0 + fx * w, ground - fh * h,
                     x0 + (fx + fw) * w, ground], fill=rgb("navy_deep"))
    spire_x = x0 + 0.39 * w
    d.polygon([(spire_x - 4, ground - 0.66 * h), (spire_x + 4, ground - 0.66 * h),
               (spire_x, ground - 0.92 * h)], fill=rgb("navy_deep"))
    d.rectangle([x0, ground, x1, y1], fill=rgb("navy_deep"))
    # three flags on poles, left to right: US, China, Russia
    flag_w, flag_h = 36, 23
    for i, kind in enumerate(("us", "cn", "ru")):
        fx = x0 + 12 + i * 54
        fy = y0 + 10
        d.line([(fx, fy), (fx, fy + 48)], fill=(225, 225, 225), width=2)
        bx, by = fx + 3, fy
        if kind == "us":
            d.rectangle([bx, by, bx + flag_w, by + flag_h],
                        fill=(255, 255, 255))
            for s in range(7):
                if s % 2 == 0:
                    d.rectangle([bx, by + s * flag_h / 7,
                                 bx + flag_w, by + (s + 1) * flag_h / 7],
                                fill=(178, 34, 52))
            d.rectangle([bx, by, bx + flag_w * 0.42, by + flag_h * 0.55],
                        fill=(60, 60, 130))
            for r in range(3):
                for c in range(4):
                    d.ellipse([bx + 3 + c * 6, by + 3 + r * 4,
                               bx + 5 + c * 6, by + 5 + r * 4],
                              fill=(255, 255, 255))
        elif kind == "cn":
            d.rectangle([bx, by, bx + flag_w, by + flag_h],
                        fill=(222, 41, 16))
            star4(d, bx + 8, by + 7, 6, (255, 222, 0))
            for sx, sy in ((26, 4), (30, 9), (30, 14), (26, 18)):
                star4(d, bx + sx, by + sy, 2.5, (255, 222, 0))
        else:
            for j, col in enumerate(((255, 255, 255), (0, 57, 166),
                                     (211, 0, 0))):
                d.rectangle([bx, by + j * flag_h / 3,
                             bx + flag_w, by + (j + 1) * flag_h / 3],
                            fill=col)


def art_ipo(d, box):
    """Record IPO bar chart: ANT $81.3bn towers over SpaceX $75bn."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(10, 44, 40))
    base = y1 - 26
    d.line([(x0, base), (x1, base)], fill=(120, 160, 140), width=2)
    bars = [("ANT", 81.3, rgb("gold"), "$81.3bn", rgb("gold_pale")),
            ("SPACEX", 75.0, (96, 132, 112), "$75bn", (205, 222, 208))]
    for i, (name, value, colour, label, lab_col) in enumerate(bars):
        bx0 = x0 + w * (0.13 + i * 0.44)
        bx1 = x0 + w * (0.38 + i * 0.44)
        top = base - int((h - 44) * value / 81.3 * 0.86)
        d.rectangle([bx0, top, bx1, base], fill=colour)
        d.rectangle([bx0, top, bx1, top + 5], fill=lab_col)
        f_val = face("sans_bold", 15)
        d.text((bx0 + 2, top - 21), label, font=f_val, fill=lab_col)
        f_lab = face("sans_bold", 11)
        d.text((bx0 + 4, base + 5), name, font=f_lab, fill=(255, 255, 255))
    # green up-arrow climbing past the ANT bar
    ax = x0 + w * 0.44
    ay = y0 + h * 0.30
    d.line([(ax, ay + 22), (ax + 16, ay)], fill=(120, 220, 140), width=4)
    d.polygon([(ax + 16, ay), (ax + 8, ay), (ax + 16, ay + 8)],
              fill=(120, 220, 140))


def art_vice(d, box):
    """Vice City sunset: orange sky, low sun, dark skyline, purple sea."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    blend(d, box, (255, 122, 26), (148, 38, 120))
    d.ellipse([x0 + w * 0.60, y0 + h * 0.14, x0 + w * 0.88, y0 + h * 0.52],
              fill=(255, 214, 130))
    sea_y = y0 + h * 0.72
    d.rectangle([x0, sea_y, x1, y1], fill=(38, 28, 96))
    d.line([(x0, sea_y), (x1, sea_y)], fill=rgb("gold_pale"), width=2)
    skyline = [0.46, 0.28, 0.62, 0.38, 0.54, 0.32, 0.44]
    bw = w / len(skyline)
    for i, f in enumerate(skyline):
        bh = h * f * 0.62
        d.rectangle([x0 + i * bw + 2, sea_y - bh,
                     x0 + (i + 1) * bw - 2, sea_y], fill=(30, 16, 66))
    # two palm silhouettes
    for px, s in ((x0 + w * 0.09, 1.0), (x0 + w * 0.92, 0.75)):
        top_y = sea_y - 30 * s
        d.line([(px, sea_y), (px, top_y)], fill=(20, 10, 44), width=3)
        for ang in (-55, -25, 5, 35, 65):
            ex = px + 15 * s * math.cos(math.radians(ang - 90))
            ey = top_y + 11 * s * math.sin(math.radians(ang - 90))
            d.line([(px, top_y), (ex, ey)], fill=(20, 10, 44), width=3)

# ---- card artwork -------------------------------------------------------

def art_bridge(d, box):
    """Kerch Strait at night: bridge deck with a gap, arch, fireball.

    Drawn illustration of the reported strike, not a news photograph.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    blend(d, box, (28, 34, 58), (12, 16, 34))
    d.ellipse([x0 + w * 0.80, y0 + 6, x0 + w * 0.92, y0 + 24],
              fill=(220, 210, 180))
    d.rectangle([x0, y0 + h * 0.70, x1, y1], fill=(10, 22, 40))
    deck = y0 + h * 0.52
    # deck in two pieces: the road span is down in the middle
    d.rectangle([x0, deck, x0 + w * 0.40, deck + 8], fill=(92, 97, 112))
    d.rectangle([x0 + w * 0.60, deck, x1, deck + 8], fill=(92, 97, 112))
    # arch over the surviving rail span, right side
    d.arc([x0 + w * 0.56, deck - 36, x0 + w * 0.99, deck + 20],
          start=180, end=360, fill=(142, 147, 162), width=4)
    for fx in (0.63, 0.75, 0.87, 0.96):
        d.line([(x0 + w * fx, deck), (x0 + w * fx, deck + 18)],
               fill=(92, 97, 112), width=3)
    # fireball at the gap, with small dark smoke puffs above it
    gx, gy = x0 + w * 0.50, deck - 4
    d.ellipse([gx - 21, gy - 15, gx + 21, gy + 13], fill=(255, 140, 40))
    d.ellipse([gx - 8, gy - 6, gx + 8, gy + 6], fill=(255, 220, 120))
    for sx, sy, sr in ((-14, -26, 7), (8, -30, 6), (0, -38, 5)):
        d.ellipse([gx + sx - sr, gy + sy - sr, gx + sx + sr, gy + sy + sr],
                  fill=(68, 68, 78))


def art_storm(d, box):
    """Cyclone Akvan: spiral bands over a teal sea, rain slashes."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    blend(d, box, (16, 96, 110), (8, 52, 74))
    cx, cy = x0 + w * 0.50, y0 + h * 0.52
    for r, col in ((44, (200, 225, 230)), (34, (150, 200, 215)),
                   (24, (110, 175, 200)), (14, (70, 145, 180))):
        d.arc([cx - r, cy - r * 0.78, cx + r, cy + r * 0.78],
              start=15, end=295, fill=col, width=5)
    d.ellipse([cx - 7, cy - 6, cx + 7, cy + 6], fill=(255, 255, 255))
    for fx in (0.10, 0.28, 0.70, 0.90):
        rx = x0 + fx * w
        d.line([(rx, y0 + 6), (rx - 5, y0 + 24)], fill=(200, 225, 230),
               width=2)
    d.rectangle([x0, y1 - 12, x1, y1], fill=(8, 40, 58))


def art_berlin(d, box):
    """Berlin: ring of EU stars over the Brandenburg Gate at dusk."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    blend(d, box, (52, 78, 140), (24, 36, 72))
    ccx, ccy = x0 + w * 0.50, y0 + h * 0.28
    for k in range(12):
        a = math.radians(-90 + k * 30)
        star4(d, ccx + 32 * math.cos(a), ccy + 24 * math.sin(a), 3.5,
              rgb("gold_pale"))
    base = y1
    gate_col = (96, 110, 156)
    # entablature + roof slab
    d.rectangle([x0 + w * 0.15, base - 36, x0 + w * 0.85, base - 28],
                fill=gate_col)
    d.rectangle([x0 + w * 0.15, base - 28, x0 + w * 0.85, base - 20],
                fill=gate_col)
    # six columns
    for i in range(6):
        px = x0 + w * (0.17 + i * 0.132)
        d.rectangle([px, base - 20, px + 8, base], fill=gate_col)


def art_slump(d, box):
    """Wall Street down day: falling red bars under a down arrow."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(46, 18, 20))
    base = y1 - 22
    heights = [0.32, 0.46, 0.38, 0.60, 0.54, 0.74]
    bw = w / len(heights)
    for i, f in enumerate(heights):
        bh = (h - 34) * f
        col = (150, 40, 40) if i >= 3 else (110, 60, 60)
        d.rectangle([x0 + i * bw + 4, base - bh,
                     x0 + (i + 1) * bw - 4, base], fill=col)
    # down-trend arrow, drawn over the bars
    d.line([(x0 + 12, y0 + 14), (x1 - 16, y0 + h - 32)], fill=(255, 90, 80),
           width=4)
    d.polygon([(x1 - 16, y0 + h - 32), (x1 - 32, y0 + h - 32),
               (x1 - 16, y0 + h - 48)], fill=(255, 90, 80))
    f_lab = face("sans_bold", 14)
    d.text((x1 - 62, y0 + 6), "-2.0%", font=f_lab, fill=(255, 150, 140))

def art_probe(d, box):
    """Voyager 1: dashed gold path from Earth to the spacecraft."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(6, 8, 26))
    dots = [(0.06, 0.18), (0.20, 0.08), (0.33, 0.26), (0.48, 0.10),
            (0.60, 0.26), (0.76, 0.12), (0.88, 0.30), (0.13, 0.52),
            (0.40, 0.60), (0.64, 0.48), (0.84, 0.60), (0.28, 0.76),
            (0.53, 0.80), (0.73, 0.76), (0.90, 0.84)]
    for fx, fy in dots:
        sx, sy = x0 + fx * w, y0 + fy * h
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    ex, ey = x0 + w * 0.10, y0 + h * 0.82
    vx, vy = x0 + w * 0.66, y0 + h * 0.30
    d.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(70, 130, 200))
    d.ellipse([ex - 3, ey - 4, ex + 1, ey + 1], fill=(120, 200, 120))
    steps = 14
    for i in range(steps):
        t0, t1 = i / steps, (i + 0.55) / steps
        d.line([(ex + (vx - ex) * t0, ey + (vy - ey) * t0),
                (ex + (vx - ex) * t1, ey + (vy - ey) * t1)],
               fill=rgb("gold_pale"), width=2)
    # the spacecraft: dish, body, boom, gold RTG
    d.ellipse([vx - 30, vy - 9, vx + 8, vy + 15], fill=(205, 205, 210))
    d.ellipse([vx - 25, vy - 5, vx + 3, vy + 11], fill=(150, 150, 158))
    d.rectangle([vx - 2, vy - 4, vx + 18, vy + 10], fill=(185, 185, 192))
    d.line([(vx + 16, vy + 3), (vx + 46, vy - 13)], fill=(205, 205, 210),
           width=3)
    d.rectangle([vx + 44, vy - 18, vx + 53, vy - 7], fill=rgb("gold"))


def art_faith(d, box):
    """Pew finding: a globe and three rising bars on pale paper."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d.rectangle(box, fill=(238, 232, 214))
    cx, cy = x0 + w * 0.30, y0 + h * 0.52
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(70, 130, 200))
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24],
              outline=(30, 70, 120), width=2)
    d.arc([cx - 24, cy - 24, cx + 24, cy + 24], start=200, end=340,
          fill=(120, 200, 120), width=8)
    bx = x0 + w * 0.56
    for i, bh in enumerate((14, 24, 34)):
        col = rgb("navy") if i < 2 else rgb("gold")
        d.rectangle([bx + i * 18, y1 - 12 - bh, bx + i * 18 + 13, y1 - 12],
                    fill=col)


def art_strata(d, box):
    """A billion missing years: rock strata with a pale gap and '?'."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    bands = [(150, 110, 70), (120, 88, 56), (232, 220, 190), (96, 70, 44),
             (170, 130, 86), (80, 58, 36)]
    bh = h / len(bands)
    for i, col in enumerate(bands):
        yy = y0 + i * bh
        d.rectangle([x0, yy, x1, yy + bh + 1], fill=col)
        d.line([(x0, yy), (x1, yy)], fill=(60, 44, 28), width=1)
    gap_y = y0 + 2 * bh
    d.rectangle([x0, gap_y, x1, gap_y + bh], fill=(240, 234, 214))
    f_q = face("sans_bold", 20)
    d.text((x0 + w / 2 - 7, gap_y + 2), "?", font=f_q, fill=rgb("red"))


def art_tokyo(d, box):
    """India and Japan: the two flags side by side under a pale sky."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    blend(d, box, (170, 205, 235), (120, 165, 210))
    # Indian flag, left
    ix, iy, iw, ih = x0 + 12, y0 + 12, 62, 36
    for j, col in enumerate(((255, 153, 51), (255, 255, 255),
                             (19, 136, 8))):
        d.rectangle([ix, iy + j * ih / 3, ix + iw, iy + (j + 1) * ih / 3],
                    fill=col)
    d.ellipse([ix + iw / 2 - 6, iy + ih / 2 - 6, ix + iw / 2 + 6,
               iy + ih / 2 + 6], outline=(0, 0, 128), width=2)
    # Japanese flag, right
    jx, jy = x0 + w - 74, y0 + 12
    d.rectangle([jx, jy, jx + 62, jy + 36], fill=(255, 255, 255))
    d.ellipse([jx + 21, jy + 8, jx + 41, jy + 28], fill=(188, 0, 45))
    d.rectangle([x0, y1 - 8, x1, y1], fill=(90, 120, 150))

# ---- page content -------------------------------------------------------
# Each lead: (artwork, caption, kicker, headline, deck).
# Each card: (artwork, kicker, headline, deck).
# All facts verified in V2-RESEARCH-2026-11-20.md.

LEADS = [
    (art_summit, "SHENZHEN · KYLIN VILLA", "1 · ASIA · SUMMIT",
     "Three leaders sign 'peace declaration'",
     "First-ever summit, 90 minutes at Kylin Villa. No deal on "
     "Ukraine or arms."),
    (art_ipo, "NASDAQ · TICKER ANT", "2 · MARKETS · IPO",
     "Biggest IPO ever: Anthropic up 17%",
     "Priced at $83 on Wednesday; ANT opens at $111.50, closes at "
     "$97.17. $81.3bn raised."),
    (art_vice, "VICE CITY · LEONIDA", "3 · CULTURE · GAMING",
     "GTA VI is out after 13 years",
     "Midnight unlock in every market. Metacritic 99; 2.3m watch "
     "on Twitch."),
]

CARDS = [
    (art_bridge, "4 · UKRAINE · WAR",
     "Kerch Bridge hit a third time in four days",
     "Neptune missiles hit the rail span; trains halt, one line back."),
    (art_storm, "5 · SOUTH ASIA · WEATHER",
     "Cyclone Akvan nears coast, landfall due Friday",
     "440 km off Narsapur; landfall Fri near Gopalpur at 90–100 km/h."),
    (art_berlin, "6 · EUROPE · UKRAINE",
     "Berlin allies demand a winter energy ceasefire",
     "40+ partners back Ukraine; binding guarantees, €70bn aid."),
    (art_probe, "7 · SPACE · MILESTONE",
     "NASA confirms Voyager 1 is one light-day away",
     "Confirmed Thursday; crossed Wed. No science data since 14 Nov."),
    (art_slump, "8 · MARKETS · STOCKS",
     "Wall Street sinks on Anthropic's big day",
     "Dow −1,101 to 49,097. S&P −2.0%, 6th straight loss; Nasdaq −2.3%."),
    (art_faith, "9 · WORLD · RELIGION",
     "Islam 'largest faith by 2035', Pew finds",
     "Muslims to outnumber Christians within a decade, Pew projects."),
    (art_strata, "10 · SCIENCE",
     "Earth 'lost' a billion years of history",
     "Scientists may know why a billion years of rock is missing."),
    (art_tokyo, "11 · ASIA · DEFENCE",
     "India, Japan deepen defence pact in Tokyo",
     "2+2 joint statement: 'Design with Japan, Make in India'."),
]

# Stories 12–43, in reading order, two columns of sixteen.
BRIEFS = [
    "Trump–Xi extend trade truce (REPORTED)",
    "Putin: no deal; vows a hard reply",
    "Ferry to Crimea starts Friday",
    "Kyiv drones kill 2, injure 5",
    "Walmart beats; shares fall 1%",
    "Jobless claims 203,000; 1.76m still out",
    "Nvidia −3.3%, sixth day down",
    "APEC ends in thin trade pledges",
    "Trump flies home, skips reporters",
    "Eisenkot woos ultra-Orthodox",
    "Kahana elected speaker (TUESDAY)",
    "Senators warn of AI cyber peril (WED.)",
    "Mélenchon 'could win' — minister (WED.)",
    "Carney widens China thaw (TUESDAY)",
    "Fed minutes back hikes (LAST NIGHT)",
    "Jeffries nominated Speaker (LAST NIGHT)",
    "Modi meets William, Kate (LAST NIGHT)",
    "Australia sanctions settlers (YESTERDAY)",
    "PSN down on launch eve (LAST NIGHT)",
    "GTA VI: 2.3m watch on Twitch",
    "GTA VI: no PC version, no date",
    "GTA VI costs $79.99; 212 GB download",
    "Anthropic revenue run rate $81bn a year",
    "IPO demand ran ~7× the shares offered",
    "One Kerch rail line reopens by afternoon",
    "Saudi, Qatar condemn Gulf strikes",
    "Rubio: no imminent threat to US cities",
    "Odisha shuts schools in 11 districts",
    "Voyager heads for Gliese 445",
    "Gulf: Iran hit Kuwait, Bahrain (WED.)",
    "US hit Qeshm on Tuesday",
    "Colts at Texans in Thursday night NFL",
]
assert len(BRIEFS) == 32, "the briefs must number exactly 32"

NUMBERS = [
    ("$81.3bn", "Anthropic IPO, biggest ever"),
    ("$97.17", "ANT close, up 17%"),
    ("99", "GTA VI Metacritic"),
    ("−1,101", "Dow points lost"),
    ("90–100", "Akvan km/h at landfall"),
    ("90 min", "Trilateral talks"),
]

# Map pins as (longitude, latitude, story number). Story 9 (Pew, based
# in Washington DC) has no pin: it would sit ~4 px from the New York
# pin and be hidden behind it.
PINS = [
    (114.1, 22.5, 1), (-74.0, 40.7, 2), (-80.2, 25.8, 3),
    (36.5, 45.3, 4), (81.1, 16.4, 5), (13.4, 52.5, 6),
    (-118.1, 34.1, 7), (139.7, 35.7, 11),
]

# ---- dotted world map ---------------------------------------------------
# Land as latitude bands: (latitude, [(lon_lo, lon_hi), ...]).
# Dots every 6 degrees of longitude inside each span. Written from
# geography, not copied from any earlier grid.

LAND_BANDS = [
    (78, [(-58, -20)]),
    (72, [(-168, -90), (-58, -20), (15, 180)]),
    (66, [(-168, -55), (-55, -20), (5, 180)]),
    (60, [(-168, -55), (-45, -20), (-10, 180)]),
    (54, [(-165, -55), (-10, 180)]),
    (48, [(-125, -65), (-10, 140)]),
    (42, [(-125, -70), (-10, 145)]),
    (36, [(-120, -75), (-10, 140)]),
    (30, [(-115, -80), (-10, 125)]),
    (24, [(-110, -80), (-15, 125)]),
    (18, [(-105, -85), (-15, 50), (95, 110)]),
    (12, [(-100, -80), (-15, 45), (95, 105)]),
    (6, [(-80, -75), (-10, 45), (95, 105)]),
    (0, [(-80, -35), (-10, 40), (95, 140)]),
    (-6, [(-80, -35), (10, 40), (95, 145)]),
    (-12, [(-75, -35), (12, 40), (130, 150)]),
    (-18, [(-70, -40), (15, 35), (115, 150)]),
    (-24, [(-70, -40), (15, 35), (115, 150)]),
    (-30, [(-70, -55), (15, 30), (115, 150)]),
    (-36, [(-70, -55), (115, 150)]),
    (-42, [(-70, -65), (145, 150)]),
    (-48, [(-70, -65)]),
    (-54, [(-70, -65)]),
]
MAP_TOP_LAT = 84
MAP_SPAN_LAT = 144  # 84 down to -60
DOT_COLOUR = (120, 130, 110)


def _project(box, lon, lat):
    """Lon/lat -> pixel inside the map box."""
    x0, y0, x1, y1 = box
    px = x0 + (lon + 180) / 360 * (x1 - x0)
    py = y0 + (MAP_TOP_LAT - lat) / MAP_SPAN_LAT * (y1 - y0)
    return px, py


def dotted_map(d, box):
    """Paint the dotted continents, then the numbered story pins."""
    for lat, spans in LAND_BANDS:
        for lo, hi in spans:
            lon = lo
            while lon <= hi:
                px, py = _project(box, lon, lat)
                d.ellipse([px - 2, py - 2, px + 2, py + 2],
                          fill=DOT_COLOUR)
                lon += 6
    f_num = face("sans_bold", 10)
    for lon, lat, num in PINS:
        px, py = _project(box, lon, lat)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=rgb("red"),
                  outline=(255, 255, 255), width=2)
        label = str(num)
        d.text((px - f_num.getlength(label) / 2, py - 5), label,
               font=f_num, fill=(255, 255, 255))


# ---- page layout --------------------------------------------------------
LEAD_X0, LEAD_STEP, LEAD_W = 12, 338, 324
CARD_W, CARD_H = 243, 174
CARD_X0, CARD_DX, CARD_Y0, CARD_DY = 10, 254, 398, 178


def header(d):
    d.rectangle([0, 0, PAGE_W, 98], fill=rgb("navy"))
    f_kick = face("sans_bold", 13)
    d.text((12, 10), "THE DAY IN WORLD NEWS", font=f_kick,
           fill=rgb("gold_pale"))
    right = "43 STORIES · 4 CONTINENTS · ONE PAGE"
    d.text((PAGE_W - 12 - f_kick.getlength(right), 10), right,
           font=f_kick, fill=rgb("gold_pale"))
    f_date = face("serif_bold", 52)
    date = "Thursday 19 November 2026"
    assert f_date.getlength(date) <= 1000, "date line too wide"
    d.text((12, 28), date, font=f_date, fill=(255, 255, 255))
    f_sub = face("serif_italic", 15)
    d.text((12, 80),
           "Every story on this page happened, or was first reported, "
           "on this day.",
           font=f_sub, fill=(200, 205, 220))
    f_dc = face("sans_bold", 11)
    dc = "DATE CHECK: EVERY STORY 19 NOV 2026"
    d.text((PAGE_W - 12 - f_dc.getlength(dc), 82), dc, font=f_dc,
           fill=rgb("gold_pale"))
    d.rectangle([0, 98, PAGE_W, 101], fill=rgb("gold"))


def lead_block(d, x, lead):
    art, caption, kicker, headline, deck = lead
    art(d, (x, 108, x + LEAD_W, 238))
    d.rectangle([x, 238, x + LEAD_W, 256], fill=rgb("teal"))
    f_cap = face("sans_bold", 11)
    d.text((x + 8, 242), caption, font=f_cap, fill=(255, 255, 255))
    f_kick = face("sans_bold", 12)
    d.text((x, 264), kicker, font=f_kick, fill=rgb("red"))
    f_head = face("sans_bold", 24)
    stack(d, pour(headline, f_head, LEAD_W, 2), x, 282, f_head,
          rgb("ink"), 29)
    f_deck = face("sans", 13)
    stack(d, pour(deck, f_deck, LEAD_W, 2), x, 344, f_deck, (60, 60, 58),
          16)


def story_card(d, x, y, card):
    art, kicker, headline, deck = card
    d.rectangle([x, y, x + CARD_W, y + CARD_H], fill=rgb("paper"),
                outline=rgb("rule"), width=1)
    art(d, (x + 1, y + 1, x + CARD_W - 1, y + 67))
    f_kick = face("sans_bold", 11)
    d.text((x + 8, y + 74), kicker, font=f_kick, fill=rgb("red"))
    f_head = face("sans_bold", 15)
    stack(d, pour(headline, f_head, CARD_W - 16, 2), x + 8, y + 92,
          f_head, rgb("ink"), 18)
    f_deck = face("sans", 12)
    stack(d, pour(deck, f_deck, CARD_W - 16, 2), x + 8, y + 130,
          f_deck, (60, 60, 58), 15)

def stat_band(d):
    d.rectangle([0, 758, PAGE_W, 798], fill=rgb("navy"))
    f_lab = face("sans_bold", 12)
    d.text((12, 766), "BY THE", font=f_lab, fill=rgb("gold_pale"))
    d.text((12, 780), "NUMBERS", font=f_lab, fill=rgb("gold_pale"))
    f_val = face("sans_bold", 22)
    f_cap = face("sans", 10)
    x = 118
    for value, caption in NUMBERS:
        assert f_val.getlength(value) <= 148, "number too wide: " + value
        d.text((x, 762), value, font=f_val, fill=rgb("gold_pale"))
        d.text((x, 784), caption, font=f_cap, fill=(210, 214, 226))
        x += 152


def world_and_briefs(d):
    f_title = face("sans_bold", 13)
    d.text((12, 804), "WHERE THE NEWS HAPPENED", font=f_title,
           fill=rgb("ink"))
    d.rectangle([12, 821, 490, 822], fill=rgb("red"))
    dotted_map(d, (12, 828, 490, 956))
    # dashed arc, "the day sweeps west", arrowhead at the left end
    ax0, ay0, ax1 = 30, 962, 470
    for i in range(24):
        t0, t1 = i / 24, (i + 0.55) / 24
        d.line([(ax0 + (ax1 - ax0) * t0, ay0 - 26 * math.sin(math.pi * t0)),
                (ax0 + (ax1 - ax0) * t1, ay0 - 26 * math.sin(math.pi * t1))],
               fill=(150, 110, 20), width=2)
    d.polygon([(ax0, ay0), (ax0 + 14, ay0 - 4), (ax0 + 14, ay0 + 4)],
              fill=(150, 110, 20))
    f_arc = face("sans_bold", 10)
    d.text((190, 968), "THE DAY SWEEPS WEST", font=f_arc,
           fill=(150, 110, 20))
    f_leg = face("sans", 10)
    d.text((12, 984), "Numbered dots mark stories 1–7 and 11.",
           font=f_leg, fill=rgb("grey"))
    # briefs: two columns of sixteen, 10 px type on a 10.5 px pitch
    d.text((500, 804), "ALSO ON THURSDAY 19 NOVEMBER — 32 MORE STORIES",
           font=f_title, fill=rgb("ink"))
    d.rectangle([500, 821, 1012, 822], fill=rgb("red"))
    f_b = face("sans", 10)
    for i, brief in enumerate(BRIEFS):
        line = "%d. %s" % (12 + i, brief)
        assert f_b.getlength(line) <= 246, "brief too wide: %r" % line
        col, row = (0, i) if i < 16 else (1, i - 16)
        d.text((500 + col * 262, 826 + row * 10.5), line, font=f_b,
               fill=rgb("ink"))


def colophon(d):
    f_it = face("serif_italic", 12)
    line = "The world's news for Thursday 19 November 2026"
    d.text(((PAGE_W - f_it.getlength(line)) / 2, 1000), line, font=f_it,
           fill=rgb("grey"))
    f_src = face("sans", 9)
    src = ("Disputed claims are attributed. Sources: AP · Reuters · BBC · "
           "NASA/JPL · IMD · Ukrinform · PIB India · WSJ · Investors.com.")
    d.text(((PAGE_W - f_src.getlength(src)) / 2, 1013), src, font=f_src,
           fill=rgb("grey"))


def render_page():
    img = Image.new("RGB", (PAGE_W, PAGE_H), rgb("cream"))
    d = ImageDraw.Draw(img)
    header(d)
    for i, lead in enumerate(LEADS):
        lead_block(d, LEAD_X0 + i * LEAD_STEP, lead)
    d.line([(12, 388), (1012, 388)], fill=rgb("rule"), width=1)
    for r in range(2):
        for c in range(4):
            story_card(d, CARD_X0 + c * CARD_DX, CARD_Y0 + r * CARD_DY,
                       CARDS[r * 4 + c])
    stat_band(d)
    world_and_briefs(d)
    colophon(d)
    img.save(OUT, format="PNG", optimize=True)
    data = open(OUT, "rb").read()
    print("wrote %s (%d bytes) sha256=%s" % (
        OUT, len(data), hashlib.sha256(data).hexdigest()))
    assert img.size == (1024, 1024)
    assert len(data) <= 1048576, "entry over 1 MiB"


if __name__ == "__main__":
    render_page()
