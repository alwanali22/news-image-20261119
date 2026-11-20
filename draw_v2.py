"""draw_v2.py — generator for news-image-20261119 v2 (19 November 2026).

Draws one 1024x1024 infographic: masthead (with DATE CHECK) + 3 lead stories
+ 8 grid cards + numbers strip + dotted world map + 32 numbered briefs +
footer. Pure PIL, no network, no clock, no randomness: two runs write
byte-identical PNGs. 43 stories total.

Every story on the page happened, or was first reported, on Thursday
19 November 2026 (any time zone). Planned events are labelled as planned;
older news is labelled with its day (LAST NIGHT / YESTERDAY / TUESDAY /
WEDNESDAY). Results replace v1's plans: the trilateral ENDED with a
four-point peace declaration, Anthropic's ANT debuted and closed up 17%,
GTA VI launched. Real events use drawn scenes only — no news-agency photos,
no photo of another event passed off as today's. See V2-RESEARCH-2026-11-20.md.
"""

import hashlib
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---- palette ------------------------------------------------------------
NAVY = (20, 38, 78)
NAVY2 = (28, 52, 102)
GOLD = (201, 162, 39)
GOLD_LT = (232, 196, 90)
CREAM = (247, 243, 232)
PAPER = (252, 250, 244)
INK = (24, 24, 24)
MUTED = (90, 90, 86)
RED = (178, 34, 34)
RED_DK = (139, 26, 26)
TEAL = (18, 90, 92)
TEAL_DK = (12, 64, 66)
LINE = (180, 172, 150)
DOT = (120, 130, 110)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)          # masthead date
F_SERIF_IT = lambda s: font("DejaVuSerif-Italic.ttf", s)     # subline / footer
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)            # headlines
F_REG = lambda s: font("DejaVuSans.ttf", s)                 # body / briefs
F_OBL = lambda s: font("DejaVuSans-Oblique.ttf", s)


def wrap(draw, s, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, s, f, max_w, max_lines):
    """Wrap s; assert it fits max_lines lines at max_w. Returns lines."""
    lines = wrap(draw, s, f, max_w)
    assert len(lines) <= max_lines, (
        "TEXT OVERFLOW %r -> %d lines (max %d) at width %d"
        % (s, len(lines), max_lines, max_w))
    return lines


def draw_lines(draw, lines, x, y, f, fill, pitch):
    for i, line in enumerate(lines):
        draw.text((x, y + i * pitch), line, font=f, fill=fill)
    return y + len(lines) * pitch


def chip(draw, x, y, text, f, bg, fg=(255, 255, 255), pad_x=7, pad_y=3):
    w = int(draw.textlength(text, font=f)) + 2 * pad_x
    h = f.size + 2 * pad_y
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw.text((x + pad_x, y + pad_y), text, font=f, fill=fg)
    return w


# ---- dotted world map ---------------------------------------------------
# Coarse land grid, authored from geography knowledge: 60 columns of 6 deg
# longitude (-180..180), 30 rows of 4.5 deg latitude (75..-60). '#' = land.
LAND = [
    "........#########....###......#......#######################",
    "..#####.############.#####..#..##...########################",
    "..###################.###...#..####.########################",
    ".....################....#....##.###########################",
    ".........###########........#.#############################.",
    "..........##########.........##############################.",
    "..........##########.........##########################.....",
    "...........#########.........#######################.#......",
    "...........#########.........######################..#......",
    "............########.........######################.........",
    ".............#######.........#############.##.###...........",
    "............#####...........##############.##.###...........",
    ".............####...........###########....#.###............",
    "..............####...........##########......#####..........",
    "...............###............########.......########.......",
    ".................###..........########..........#########...",
    ".................#####........########..........######.###..",
    "..................#####.......########...........####..###..",
    "...................#####.......#######............###...#...",
    "...................######......#######.#.........#####......",
    "....................#####......#######.#.........######.....",
    "....................#####......#######.#.........######.....",
    "....................#####......#######...........######.....",
    "....................####.......######............######.##..",
    "....................####.......#####..............####..#...",
    "....................###.........###...............###...#...",
    "....................###.................................#...",
    "....................##......................................",
    "....................##......................................",
    "............................................................",
]
assert all(len(r) == 60 for r in LAND), "LAND rows must be 60 wide"
assert len(LAND) == 30, "LAND must have 30 rows"


def lonlat_to_frac(lon, lat):
    """Equirectangular fraction over the LAND grid extent."""
    fx = (lon + 180.0) / 360.0
    fy = (75.0 - lat) / 135.0
    return fx, fy


def draw_dot_map(draw, x0, y0, w, h, dots):
    """Dotted world map; dots = list of (lon, lat, number)."""
    cols, rows = 60, 30
    cw, chh = w / cols, h / rows
    for r in range(rows):
        for c in range(cols):
            if LAND[r][c] == "#":
                cx = x0 + (c + 0.5) * cw
                cy = y0 + (r + 0.5) * chh
                draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=DOT)
    for lon, lat, num in dots:
        fx, fy = lonlat_to_frac(lon, lat)
        cx = x0 + fx * w
        cy = y0 + fy * h
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=RED,
                     outline=(255, 255, 255), width=2)
        f = F_BOLD(11)
        tw = draw.textlength(str(num), font=f)
        draw.text((cx - tw / 2, cy - 6), str(num), font=f, fill=(255, 255, 255))


# ---- drawn scenes (illustrations, never a fake news photo) --------------
def _vgrad(draw, x, y, w, h, top, bot):
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(top[k] + (bot[k] - top[k]) * t) for k in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=c)


def _flag_us(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(178, 34, 52))
    for i in range(7):
        yy = y + i * h / 6.5
        if i % 2 == 0:
            draw.rectangle([x, yy, x + w, yy + h / 13], fill=(255, 255, 255))
    cw, chh = w * 0.4, h * 0.54
    draw.rectangle([x, y, x + cw, y + chh], fill=(60, 59, 110))
    for r in range(3):
        for c in range(4):
            draw.ellipse([x + 3 + c * cw / 4.5, y + 3 + r * chh / 3.5,
                          x + 6 + c * cw / 4.5, y + 6 + r * chh / 3.5],
                         fill=(255, 255, 255))


def _flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.22, y + h * 0.28
    for k in range(5):
        ang = -90 + k * 72
        px = cx + 5 * math.cos(math.radians(ang))
        py = cy + 5 * math.sin(math.radians(ang))
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 222, 0))
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 222, 0))


def _flag_ru(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    draw.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    draw.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 50))

def scene_trilateral(draw, x, y, w, h):
    _vgrad(draw, x, y, w, h, (24, 44, 96), (66, 92, 150))
    draw.ellipse([x + w - 52, y + 10, x + w - 16, y + 46], fill=GOLD_LT)
    # Shenzhen skyline silhouette
    base = y + h - 26
    heights = [0.42, 0.62, 0.35, 0.78, 0.5, 0.66, 0.3, 0.55]
    bw = w / len(heights)
    for i, f in enumerate(heights):
        bh = h * f
        draw.rectangle([x + i * bw + 2, base - bh + 26, x + (i + 1) * bw - 2,
                        base + 26], fill=(16, 24, 52))
    # tallest tower with spire
    tx = x + w * 0.44
    draw.rectangle([tx - 7, base - h * 0.78 + 26, tx + 7, base + 26],
                   fill=(16, 24, 52))
    draw.polygon([(tx - 3, base - h * 0.78 + 26), (tx + 3, base - h * 0.78 + 26),
                  (tx, base - h * 0.98 + 26)], fill=(16, 24, 52))
    # three flags on poles above the skyline
    fy = y + 12
    fw, fh = 34, 22
    for i, fn in enumerate((_flag_us, _flag_cn, _flag_ru)):
        fx = x + 14 + i * 52
        draw.line([(fx, fy), (fx, fy + 46)], fill=(220, 220, 220), width=2)
        fn(draw, fx + 2, fy, fw, fh)
    draw.rectangle([x, base, x + w, base + 26], fill=(16, 24, 52))


def scene_ipo(draw, x, y, w, h):
    # Record IPO bar chart: Anthropic $81.3bn vs SpaceX $75bn, on dark green.
    draw.rectangle([x, y, x + w, y + h], fill=(10, 44, 40))
    draw.line([(x, y + h - 26), (x + w, y + h - 26)], fill=(120, 160, 140),
              width=2)
    # SpaceX bar (shorter, grey-green)
    sx0, sx1 = x + w * 0.56, x + w * 0.74
    stop = y + h - 26
    s_top = stop - int((h - 40) * 75 / 81.3 * 0.82)
    draw.rectangle([sx0, s_top, sx1, stop], fill=(90, 130, 110))
    # ANT bar (taller, gold)
    ax0, ax1 = x + w * 0.14, x + w * 0.42
    a_top = stop - int((h - 40) * 0.82)
    draw.rectangle([ax0, a_top, ax1, stop], fill=GOLD)
    draw.rectangle([ax0, a_top, ax1, a_top + 5], fill=GOLD_LT)
    f_v = F_BOLD(15)
    draw.text((ax0 + 4, a_top - 20), "$81.3bn", font=f_v, fill=GOLD_LT)
    draw.text((sx0 + 2, s_top - 20), "$75bn", font=f_v, fill=(200, 220, 205))
    f_l = F_BOLD(11)
    draw.text((ax0 + 6, stop + 5), "ANT", font=f_l, fill=(255, 255, 255))
    draw.text((sx0 + 2, stop + 5), "SPACEX", font=f_l, fill=(200, 220, 205))
    # up arrow over the ANT bar
    draw.line([(ax1 + 14, a_top + 26), (ax1 + 30, a_top + 6)],
              fill=(120, 220, 140), width=4)
    draw.line([(ax1 + 30, a_top + 6), (ax1 + 22, a_top + 6)],
              fill=(120, 220, 140), width=4)
    draw.line([(ax1 + 30, a_top + 6), (ax1 + 30, a_top + 14)],
              fill=(120, 220, 140), width=4)


def scene_gta(draw, x, y, w, h):
    _vgrad(draw, x, y, w, h, (255, 122, 26), (148, 38, 120))
    draw.ellipse([x + w * 0.62, y + h * 0.16, x + w * 0.86, y + h * 0.52],
                 fill=(255, 214, 130))
    # sea
    draw.rectangle([x, y + h * 0.72, x + w, y + h], fill=(38, 28, 96))
    draw.line([(x, y + h * 0.72), (x + w, y + h * 0.72)], fill=GOLD_LT, width=2)
    # skyline silhouette
    base = y + h * 0.72
    heights = [0.5, 0.3, 0.66, 0.4, 0.58, 0.34, 0.46]
    bw = w / len(heights)
    for i, f in enumerate(heights):
        bh = h * f * 0.6
        draw.rectangle([x + i * bw + 2, base - bh, x + (i + 1) * bw - 2, base],
                       fill=(30, 16, 66))
    # palm silhouettes
    for px, s in ((x + w * 0.1, 1.0), (x + w * 0.9, 0.8)):
        draw.line([(px, base), (px, base - 34 * s)], fill=(20, 10, 44), width=3)
        for a in (-50, -20, 10, 40):
            ex = px + 16 * s * math.cos(math.radians(a - 90))
            ey = base - 34 * s + 12 * s * math.sin(math.radians(a - 90))
            draw.line([(px, base - 34 * s), (ex, ey)], fill=(20, 10, 44), width=3)


def scene_kerch(draw, x, y, w, h):
    # Kerch Strait bridge at night, drawn: deck + arch, a broken gap in the
    # road span, explosion glow and smoke. Illustration, not a news photo.
    _vgrad(draw, x, y, w, h, (28, 34, 58), (12, 16, 34))
    draw.ellipse([x + w * 0.78, y + 8, x + w * 0.9, y + 26],
                 fill=(220, 210, 180))
    # water
    draw.rectangle([x, y + h * 0.7, x + w, y + h], fill=(10, 22, 40))
    # bridge deck, two segments with a gap in the middle (road span down)
    deck_y = y + h * 0.52
    draw.rectangle([x, deck_y, x + w * 0.42, deck_y + 8], fill=(90, 95, 110))
    draw.rectangle([x + w * 0.58, deck_y, x + w, deck_y + 8],
                   fill=(90, 95, 110))
    # arch over the rail span (right side)
    draw.arc([x + w * 0.55, deck_y - 34, x + w * 0.98, deck_y + 22],
             start=180, end=360, fill=(140, 145, 160), width=4)
    # rail pylons
    for px in (0.62, 0.74, 0.86, 0.95):
        draw.line([(x + w * px, deck_y), (x + w * px, deck_y + 18)],
                  fill=(90, 95, 110), width=3)
    # explosion glow at the gap + small dark smoke puffs hugging it
    gx, gy = x + w * 0.5, deck_y - 4
    draw.ellipse([gx - 22, gy - 16, gx + 22, gy + 14], fill=(255, 140, 40))
    draw.ellipse([gx - 9, gy - 7, gx + 9, gy + 7], fill=(255, 220, 120))
    draw.ellipse([gx - 20, gy - 28, gx - 6, gy - 16], fill=(70, 70, 80))
    draw.ellipse([gx + 4, gy - 32, gx + 16, gy - 20], fill=(60, 60, 70))
    draw.ellipse([gx - 4, gy - 40, gx + 8, gy - 30], fill=(80, 80, 90))


def scene_akvan(draw, x, y, w, h):
    _vgrad(draw, x, y, w, h, (16, 96, 110), (8, 52, 74))
    cx, cy = x + w * 0.5, y + h * 0.52
    for r, col in ((46, (200, 225, 230)), (36, (150, 200, 215)),
                   (26, (110, 175, 200)), (16, (70, 145, 180))):
        draw.arc([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8],
                 start=20, end=300, fill=col, width=5)
    draw.ellipse([cx - 8, cy - 7, cx + 8, cy + 7], fill=(255, 255, 255))
    # rain slashes
    for fx in (0.12, 0.3, 0.72, 0.88):
        rx = x + fx * w
        draw.line([(rx, y + 8), (rx - 6, y + 26)], fill=(200, 225, 230), width=2)
    draw.rectangle([x, y + h - 14, x + w, y + h], fill=(8, 40, 58))


def scene_berlin(draw, x, y, w, h):
    _vgrad(draw, x, y, w, h, (52, 78, 140), (24, 36, 72))
    # EU stars circle
    ccx, ccy = x + w * 0.5, y + h * 0.3
    for k in range(12):
        a = math.radians(-90 + k * 30)
        sx, sy = ccx + 34 * math.cos(a), ccy + 26 * math.sin(a)
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=GOLD_LT)
    # Brandenburg gate silhouette (lightened so it reads against dusk sky)
    base = y + h
    draw.rectangle([x + w * 0.14, base - 30, x + w * 0.86, base - 22],
                   fill=(96, 110, 156))
    for i in range(6):
        px = x + w * (0.16 + i * 0.136)
        draw.rectangle([px, base - 22, px + 8, base], fill=(96, 110, 156))
    draw.rectangle([x + w * 0.14, base - 38, x + w * 0.86, base - 30],
                   fill=(96, 110, 156))


def scene_markets(draw, x, y, w, h):
    # Falling market bars on a dark red-brown tape background.
    draw.rectangle([x, y, x + w, y + h], fill=(46, 18, 20))
    base = y + h - 22
    tops = [0.30, 0.44, 0.36, 0.58, 0.52, 0.72]
    bw = w / len(tops)
    for i, f in enumerate(tops):
        bh = (h - 34) * f
        col = (150, 40, 40) if i >= 3 else (110, 60, 60)
        draw.rectangle([x + i * bw + 4, base - bh, x + (i + 1) * bw - 4, base],
                       fill=col)
    # down-trend arrow
    draw.line([(x + 14, y + 16), (x + w - 18, y + h - 34)], fill=(255, 90, 80),
              width=4)
    draw.line([(x + w - 18, y + h - 34), (x + w - 34, y + h - 34)],
              fill=(255, 90, 80), width=4)
    draw.line([(x + w - 18, y + h - 34), (x + w - 18, y + h - 50)],
              fill=(255, 90, 80), width=4)
    f_v = F_BOLD(14)
    # label top-right, clear of the diagonal arrow (which starts top-left)
    draw.text((x + w - 64, y + 8), "-2.0%", font=f_v, fill=(255, 150, 140))


def scene_voyager(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(6, 8, 26))
    stars = [(0.08, 0.2), (0.22, 0.1), (0.35, 0.3), (0.5, 0.12), (0.62, 0.28),
             (0.78, 0.14), (0.9, 0.32), (0.15, 0.55), (0.42, 0.62),
             (0.66, 0.5), (0.86, 0.62), (0.3, 0.78), (0.55, 0.82),
             (0.75, 0.78), (0.92, 0.85)]
    for fx, fy in stars:
        sx, sy = x + fx * w, y + fy * h
        draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    # dashed Earth -> Voyager line
    ex, ey = x + w * 0.1, y + h * 0.82
    vx, vy = x + w * 0.68, y + h * 0.3
    draw.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(70, 130, 200))
    draw.ellipse([ex - 3, ey - 4, ex + 1, ey + 1], fill=(120, 200, 120))
    n = 14
    for i in range(n):
        t0 = i / n
        t1 = (i + 0.55) / n
        draw.line([(ex + (vx - ex) * t0, ey + (vy - ey) * t0),
                   (ex + (vx - ex) * t1, ey + (vy - ey) * t1)],
                  fill=GOLD_LT, width=2)
    # spacecraft: dish + bus + boom + RTG (drawn larger to read at card size)
    draw.ellipse([vx - 32, vy - 10, vx + 8, vy + 16], fill=(205, 205, 210))
    draw.ellipse([vx - 27, vy - 6, vx + 3, vy + 12], fill=(150, 150, 158))
    draw.rectangle([vx - 2, vy - 5, vx + 18, vy + 11], fill=(185, 185, 192))
    draw.line([(vx + 16, vy + 3), (vx + 48, vy - 14)], fill=(205, 205, 210),
              width=3)
    draw.rectangle([vx + 46, vy - 19, vx + 55, vy - 8], fill=GOLD)
    draw.line([(vx + 2, vy + 10), (vx - 12, vy + 26)], fill=(200, 200, 205),
              width=2)


def scene_pew(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    cx, cy = x + w * 0.3, y + h * 0.52
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=(70, 130, 200))
    draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=(30, 70, 120),
                 width=2)
    draw.arc([cx - 24, cy - 24, cx + 24, cy + 24], start=200, end=340,
             fill=(120, 200, 120), width=8)
    # rising bars
    bx = x + w * 0.56
    for i, bh in enumerate((14, 24, 34)):
        draw.rectangle([bx + i * 18, y + h - 12 - bh, bx + i * 18 + 13,
                        y + h - 12], fill=(NAVY if i < 2 else GOLD))


def scene_science(draw, x, y, w, h):
    bands = [(150, 110, 70), (120, 88, 56), (232, 220, 190), (96, 70, 44),
             (170, 130, 86), (80, 58, 36)]
    bh = h / len(bands)
    for i, col in enumerate(bands):
        yy = y + i * bh
        draw.rectangle([x, yy, x + w, yy + bh + 1], fill=col)
        draw.line([(x, yy), (x + w, yy)], fill=(60, 44, 28), width=1)
    # the "missing" gap: a pale band with a question mark
    gy = y + 2 * bh
    draw.rectangle([x, gy, x + w, gy + bh], fill=(240, 234, 214))
    f = F_BOLD(20)
    draw.text((x + w / 2 - 7, gy + 2), "?", font=f, fill=RED_DK)


def scene_india_japan(draw, x, y, w, h):
    _vgrad(draw, x, y, w, h, (170, 205, 235), (120, 165, 210))
    # India flag
    ix, iy, iw, ih = x + 12, y + 12, 62, 36
    draw.rectangle([ix, iy, ix + iw, iy + ih / 3], fill=(255, 153, 51))
    draw.rectangle([ix, iy + ih / 3, ix + iw, iy + 2 * ih / 3],
                   fill=(255, 255, 255))
    draw.rectangle([ix, iy + 2 * ih / 3, ix + iw, iy + ih], fill=(19, 136, 8))
    draw.ellipse([ix + iw / 2 - 6, iy + ih / 2 - 6, ix + iw / 2 + 6,
                  iy + ih / 2 + 6], outline=(0, 0, 128), width=2)
    # Japan flag
    jx, jy = x + w - 74, y + 12
    draw.rectangle([jx, jy, jx + 62, jy + 36], fill=(255, 255, 255))
    draw.ellipse([jx + 21, jy + 8, jx + 41, jy + 28], fill=(188, 0, 45))
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(90, 120, 150))

# ---- content (all verified 19 Nov; see V2-RESEARCH-2026-11-20.md) -------
LEADS = [
    dict(num=1, scene=scene_trilateral, caption="SHENZHEN · KYLIN VILLA",
         kicker="1 · ASIA · SUMMIT",
         headline="Three leaders sign 'peace declaration'",
         deck="First-ever summit, 90 minutes at Kylin Villa. No deal on "
              "Ukraine or arms."),
    dict(num=2, scene=scene_ipo, caption="NASDAQ · TICKER ANT",
         kicker="2 · MARKETS · IPO",
         headline="Biggest IPO ever: Anthropic up 17%",
         deck="Priced at $83 on Wednesday; ANT opens at $111.50, closes at "
              "$97.17. $81.3bn raised."),
    dict(num=3, scene=scene_gta, caption="VICE CITY · LEONIDA",
         kicker="3 · CULTURE · GAMING",
         headline="GTA VI is out after 13 years",
         deck="Midnight unlock in every market. Metacritic 99; 2.3m watch "
              "on Twitch."),
]

CARDS = [
    dict(num=4, scene=scene_kerch, kicker="4 · UKRAINE · WAR",
         headline="Kerch Bridge hit a third time in four days",
         deck="Neptune missiles hit the rail span; trains halt, one line back."),
    dict(num=5, scene=scene_akvan, kicker="5 · SOUTH ASIA · WEATHER",
         headline="Cyclone Akvan nears coast, landfall due Friday",
         deck="440 km off Narsapur; landfall Fri near Gopalpur at "
              "90–100 km/h."),
    dict(num=6, scene=scene_berlin, kicker="6 · EUROPE · UKRAINE",
         headline="Berlin allies demand a winter energy ceasefire",
         deck="40+ partners back Ukraine; binding guarantees, €70bn aid."),
    dict(num=7, scene=scene_voyager, kicker="7 · SPACE · MILESTONE",
         headline="NASA confirms Voyager 1 is one light-day away",
         deck="Confirmed Thursday; crossed Wed. No science data since 14 Nov."),
    dict(num=8, scene=scene_markets, kicker="8 · MARKETS · STOCKS",
         headline="Wall Street sinks on Anthropic's big day",
         deck="Dow −1,101 to 49,097. S&P −2.0%, 6th straight loss; "
              "Nasdaq −2.3%."),
    dict(num=9, scene=scene_pew, kicker="9 · WORLD · RELIGION",
         headline="Islam 'largest faith by 2035', Pew finds",
         deck="Muslims to outnumber Christians within a decade, Pew "
              "projects."),
    dict(num=10, scene=scene_science, kicker="10 · SCIENCE",
         headline="Earth 'lost' a billion years of history",
         deck="Scientists may know why a billion years of rock is missing."),
    dict(num=11, scene=scene_india_japan, kicker="11 · ASIA · DEFENCE",
         headline="India, Japan deepen defence pact in Tokyo",
         deck="2+2 joint statement: 'Design with Japan, Make in India'."),
]

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
assert len(BRIEFS) == 32, "need exactly 32 briefs (stories 12–43)"

NUMBERS = [
    ("$81.3bn", "Anthropic IPO, biggest ever"),
    ("$97.17", "ANT close, up 17%"),
    ("99", "GTA VI Metacritic"),
    ("−1,101", "Dow points lost"),
    ("90–100", "Akvan km/h at landfall"),
    ("90 min", "Trilateral talks"),
]

MAP_DOTS = [
    (114.1, 22.5, 1), (-74.0, 40.7, 2), (-80.2, 25.8, 3),
    (36.5, 45.3, 4), (81.1, 16.4, 5), (13.4, 52.5, 6),
    (-118.1, 34.1, 7), (139.7, 35.7, 11),
]
# NOTE: no dot for story 9 (Pew, Washington DC) — it sits ~4 px from the
# New York dot and would be hidden behind it (same defect class as the
# 20261120 v1 map: pin 2 Washington hidden behind pin 6 New York).


# ---- layout -------------------------------------------------------------
def draw_masthead(draw):
    draw.rectangle([0, 0, W, 98], fill=NAVY)
    f_kick = F_BOLD(13)
    draw.text((12, 10), "THE DAY IN WORLD NEWS", font=f_kick, fill=GOLD_LT)
    right = "43 STORIES · 4 CONTINENTS · ONE PAGE"
    draw.text((W - 12 - draw.textlength(right, font=f_kick), 10), right,
              font=f_kick, fill=GOLD_LT)
    f_date = F_SERIF(52)
    date = "Thursday 19 November 2026"
    assert draw.textlength(date, font=f_date) <= 1000, "date too wide"
    draw.text((12, 28), date, font=f_date, fill=(255, 255, 255))
    f_sub = F_SERIF_IT(15)
    draw.text((12, 80),
              "Every story on this page happened, or was first reported, "
              "on this day.",
              font=f_sub, fill=(200, 205, 220))
    f_dc = F_BOLD(11)
    dc = "DATE CHECK: EVERY STORY 19 NOV 2026"
    draw.text((W - 12 - draw.textlength(dc, font=f_dc), 82), dc,
              font=f_dc, fill=GOLD_LT)
    draw.rectangle([0, 98, W, 101], fill=GOLD)


def draw_lead(draw, x, lead):
    w = 324
    y = 108
    lead["scene"](draw, x, y, w, 130)
    draw.rectangle([x, 238, x + w, 256], fill=TEAL_DK)
    f_cap = F_BOLD(11)
    draw.text((x + 8, 242), lead["caption"], font=f_cap, fill=(255, 255, 255))
    f_kick = F_BOLD(12)
    draw.text((x, 264), lead["kicker"], font=f_kick, fill=RED)
    f_head = F_BOLD(24)
    lines = fit_lines(draw, lead["headline"], f_head, w, 2)
    draw_lines(draw, lines, x, 282, f_head, INK, 29)
    f_deck = F_REG(13)
    dlines = fit_lines(draw, lead["deck"], f_deck, w, 2)
    draw_lines(draw, dlines, x, 344, f_deck, (60, 60, 58), 16)


def draw_card(draw, x, y, card):
    w, h = 243, 174
    draw.rectangle([x, y, x + w, y + h], fill=PAPER, outline=LINE, width=1)
    card["scene"](draw, x + 1, y + 1, w - 2, 66)
    f_kick = F_BOLD(11)
    draw.text((x + 8, y + 74), card["kicker"], font=f_kick, fill=RED)
    f_head = F_BOLD(15)
    lines = fit_lines(draw, card["headline"], f_head, w - 16, 2)
    draw_lines(draw, lines, x + 8, y + 92, f_head, INK, 18)
    f_deck = F_REG(12)
    dlines = fit_lines(draw, card["deck"], f_deck, w - 16, 2)
    draw_lines(draw, dlines, x + 8, y + 130, f_deck, (60, 60, 58), 15)


def draw_numbers(draw):
    draw.rectangle([0, 758, W, 798], fill=NAVY)
    f_lab = F_BOLD(12)
    draw.text((12, 766), "BY THE", font=f_lab, fill=GOLD_LT)
    draw.text((12, 780), "NUMBERS", font=f_lab, fill=GOLD_LT)
    f_val = F_BOLD(22)
    f_cap = F_REG(10)
    x = 118
    for val, cap in NUMBERS:
        assert draw.textlength(val, font=f_val) <= 148, "number too wide: " + val
        draw.text((x, 762), val, font=f_val, fill=GOLD_LT)
        draw.text((x, 784), cap, font=f_cap, fill=(210, 214, 226))
        x += 152


def draw_bottom(draw):
    f_title = F_BOLD(13)
    draw.text((12, 804), "WHERE THE NEWS HAPPENED", font=f_title, fill=INK)
    draw.rectangle([12, 821, 490, 822], fill=RED)
    draw_dot_map(draw, 12, 828, 478, 128, MAP_DOTS)
    # "the day sweeps west" dashed arc under the map
    ax0, ay0, ax1, ay1 = 30, 962, 470, 962
    for i in range(24):
        t0, t1 = i / 24, (i + 0.55) / 24
        x0 = ax0 + (ax1 - ax0) * t0
        x1 = ax0 + (ax1 - ax0) * t1
        y0 = ay0 - 26 * math.sin(math.pi * t0)
        y1 = ay0 - 26 * math.sin(math.pi * t1)
        draw.line([(x0, y0), (x1, y1)], fill=(150, 110, 20), width=2)
    draw.polygon([(ax0, ay0), (ax0 + 14, ay0 - 4), (ax0 + 14, ay0 + 4)],
                 fill=(150, 110, 20))
    f_arc = F_BOLD(10)
    draw.text((190, 968), "THE DAY SWEEPS WEST", font=f_arc,
              fill=(150, 110, 20))
    f_leg = F_REG(10)
    draw.text((12, 984), "Numbered dots mark stories 1–7 and 11.",
              font=f_leg, fill=MUTED)
    # briefs, two columns x sixteen rows
    draw.text((500, 804), "ALSO ON THURSDAY 19 NOVEMBER — 32 MORE STORIES",
              font=f_title, fill=INK)
    draw.rectangle([500, 821, 1012, 822], fill=RED)
    # briefs, two columns x sixteen rows, pitch 10.5: last row top 983.5,
    # descenders end ~995, footer italic starts at 1000 (was 11 -> collided)
    f_b = F_REG(10)
    col_w = 250
    for i, b in enumerate(BRIEFS):
        text = "%d. %s" % (12 + i, b)
        assert draw.textlength(text, font=f_b) <= col_w - 4, (
            "brief too wide: %r" % text)
        col = 0 if i < 16 else 1
        row = i % 16
        bx = 500 + col * 262
        by = 826 + row * 10.5
        draw.text((bx, by), text, font=f_b, fill=INK)


def draw_footer(draw):
    f_it = F_SERIF_IT(12)
    line = "The world's news for Thursday 19 November 2026"
    tw = draw.textlength(line, font=f_it)
    draw.text(((W - tw) / 2, 1000), line, font=f_it, fill=MUTED)
    f_src = F_REG(9)
    src = ("Disputed claims are attributed. Sources: AP · Reuters · BBC · "
           "NASA/JPL · IMD · Ukrinform · PIB India · WSJ · Investors.com.")
    tw = draw.textlength(src, font=f_src)
    draw.text(((W - tw) / 2, 1013), src, font=f_src, fill=MUTED)


def build():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    draw_masthead(draw)
    for i, lead in enumerate(LEADS):
        draw_lead(draw, 12 + i * 338, lead)
    draw.line([(12, 388), (1012, 388)], fill=LINE, width=1)
    for r in range(2):
        for c in range(4):
            card = CARDS[r * 4 + c]
            draw_card(draw, 10 + c * 254, 398 + r * 178, card)
    draw_numbers(draw)
    draw_bottom(draw)
    draw_footer(draw)
    img.save(OUT, format="PNG", optimize=True)
    data = open(OUT, "rb").read()
    print("wrote %s (%d bytes) sha256=%s" % (
        OUT, len(data), hashlib.sha256(data).hexdigest()))
    assert img.size == (1024, 1024)
    assert len(data) <= 1048576, "entry over 1 MiB"


if __name__ == "__main__":
    build()
