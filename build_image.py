#!/usr/bin/env python3
"""Render the front page for Friday 20 November 2026 as a 1024x1024 PNG.

The picture is a newspaper front page: masthead, one lead story with a
drawn illustration of the three flags over a round summit table, six
further stories in a grid, and a footer ticker. Everything is fixed —
palette, text, seeded details — so running the script twice produces
identical bytes. Only Pillow is needed to draw; the graded entrypoint
(main.py) is stdlib-only and just copies the PNG.

Stories verified for 20 Nov 2026 against CNN, Le Monde, The Times,
WAMU/NPR, Education Times, The Daily Jagran, Jagran Josh and studmentor.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent
TARGET = BASE / "entry.png"

SIZE = 1024
BACKGROUND = (248, 244, 233)
BLACK = (20, 20, 20)
MUTED = (90, 86, 76)
SCARLET = (185, 28, 28)
FRAME = (60, 56, 48)
BODY = (52, 50, 44)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANSR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(canvas, text, typeface, max_width):
    """Split text into lines no wider than max_width (greedy, word by word)."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if canvas.textlength(candidate, font=typeface) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_paragraph(canvas, lines, x, y, typeface, colour, leading=4):
    """Draw stacked lines; return the y just below the last one."""
    for line in lines:
        canvas.text((x, y), line, font=typeface, fill=colour)
        y += typeface.size + leading
    return y


def star(canvas, cx, cy, r, colour):
    """Five-pointed star centred at (cx, cy) with outer radius r."""
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    canvas.polygon(pts, fill=colour)


def flag_usa(canvas, x, y, w, h):
    stripe = h / 13.0
    for i in range(13):
        y0 = y + i * stripe
        colour = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
        canvas.rectangle([x, y0, x + w, y0 + stripe + 1], fill=colour)
    canton_w = w * 0.4
    canton_h = stripe * 7
    canvas.rectangle([x, y, x + canton_w, y + canton_h], fill=(60, 59, 110))
    for row in range(5):
        for col in range(6):
            sx = x + 6 + col * (canton_w - 10) / 5
            sy = y + 5 + row * (canton_h - 9) / 4
            canvas.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))


def flag_chn(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star(canvas, x + w * 0.17, y + h * 0.22, 7, (255, 222, 89))
    for dx, dy in ((0.32, 0.08), (0.40, 0.20), (0.40, 0.36), (0.32, 0.46)):
        star(canvas, x + w * dx, y + h * dy, 3, (255, 222, 89))


def flag_rus(canvas, x, y, w, h):
    for i, colour in enumerate(((255, 255, 255), (0, 57, 166), (213, 0, 50))):
        canvas.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3 + 1], fill=colour)


def paint_summit(canvas, region):
    """Three flags over a round summit table, on a deep-blue night sky."""
    left, top, right, bottom = region
    height = bottom - top
    horizon = top + int(height * 0.78)
    # night sky gradient
    row = top
    while row < horizon:
        frac = (row - top) / max(1, horizon - top)
        shade = (
            int(16 + (58 - 16) * frac),
            int(24 + (74 - 24) * frac),
            int(64 + (122 - 64) * frac),
        )
        canvas.line([(left, row), (right, row)], fill=shade)
        row += 1
    # gold disc behind the flags, high like a rising sun
    cx = (left + right) // 2
    disc_y = top + 78
    canvas.ellipse(
        [cx - 62, disc_y - 62, cx + 62, disc_y + 62], fill=(212, 160, 60)
    )
    canvas.ellipse(
        [cx - 50, disc_y - 50, cx + 50, disc_y + 50], fill=(232, 190, 96)
    )
    # flag poles and flags
    pole_top = top + 26
    pole_bottom = horizon - 8
    flag_w, flag_h = 118, 74
    flags = (
        (left + 34, flag_usa),
        (cx - flag_w // 2, flag_chn),
        (right - 34 - flag_w, flag_rus),
    )
    for fx, painter in flags:
        canvas.line([(fx + 2, pole_top), (fx + 2, pole_bottom)], fill=(220, 214, 198), width=4)
        canvas.ellipse([fx - 2, pole_top - 6, fx + 6, pole_top + 2], fill=(232, 190, 96))
        painter(canvas, fx + 6, pole_top + 8, flag_w, flag_h)
    # floor
    canvas.rectangle([left, horizon, right, bottom], fill=(18, 26, 52))
    # round table, clear of the caption strip
    table_y = horizon - 2
    canvas.ellipse(
        [cx - 168, table_y, cx + 168, table_y + 30], fill=(96, 62, 32)
    )
    canvas.ellipse(
        [cx - 168, table_y, cx + 168, table_y + 18], fill=(146, 96, 52)
    )
    canvas.rectangle([cx - 10, table_y + 24, cx + 10, bottom - 30], fill=(70, 44, 24))
    canvas.text(
        (left + 12, bottom - 26),
        "ILLUSTRATION: THREE FLAGS, ONE TABLE — SHENZHEN",
        font=load_font(SANSB, 13),
        fill=(210, 214, 220),
    )


def glyph_globe(canvas, region, colour):
    left, top, right, bottom = region
    cx, cy = (left + right) // 2, (top + bottom) // 2
    rad = min(right - left, bottom - top) // 2 - 2
    canvas.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=colour, width=3)
    canvas.ellipse(
        [cx - rad // 2, cy - rad, cx + rad // 2, cy + rad], outline=colour, width=2
    )
    canvas.line([(cx - rad, cy), (cx + rad, cy)], fill=colour, width=2)


def glyph_scales(canvas, region, colour):
    left, top, right, bottom = region
    cx = (left + right) // 2
    canvas.line([(cx, top + 4), (cx, bottom - 8)], fill=colour, width=3)
    canvas.line([(left + 6, top + 12), (right - 6, top + 12)], fill=colour, width=3)
    for sx in (left + 8, right - 24):
        canvas.line([(sx + 7, top + 12), (sx + 7, top + 24)], fill=colour, width=2)
        canvas.polygon(
            [(sx, top + 24), (sx + 14, top + 24), (sx + 7, top + 34)], fill=colour
        )
    canvas.rectangle([left + 4, bottom - 8, right - 4, bottom - 4], fill=colour)


def glyph_swap(canvas, region, colour):
    left, top, right, bottom = region
    canvas.line([(left + 4, top + 12), (right - 10, top + 12)], fill=colour, width=3)
    canvas.polygon(
        [(right - 10, top + 6), (right - 2, top + 12), (right - 10, top + 18)],
        fill=colour,
    )
    canvas.line([(right - 4, bottom - 12), (left + 10, bottom - 12)], fill=colour, width=3)
    canvas.polygon(
        [(left + 10, bottom - 18), (left + 2, bottom - 12), (left + 10, bottom - 6)],
        fill=colour,
    )


def glyph_cyclone(canvas, region, colour):
    left, top, right, bottom = region
    cx, cy = (left + right) // 2, (top + bottom) // 2
    for rad in (18, 12, 6):
        canvas.arc([cx - rad, cy - rad, cx + rad, cy + rad], 30, 300, fill=colour, width=3)


def glyph_droplet(canvas, region, colour):
    left, top, right, bottom = region
    cx = (left + right) // 2
    canvas.polygon([(cx, top + 2), (cx + 13, top + 26), (cx - 13, top + 26)], fill=colour)
    canvas.ellipse([cx - 13, top + 16, cx + 13, bottom - 4], fill=colour)


def glyph_atom(canvas, region, colour):
    left, top, right, bottom = region
    cx, cy = (left + right) // 2, (top + bottom) // 2
    for ang in (0, 60, 120):
        rad = math.radians(ang)
        rx, ry = 20, 8
        pts = []
        for i in range(36):
            t = math.radians(i * 10)
            px = cx + rx * math.cos(t) * math.cos(rad) - ry * math.sin(t) * math.sin(rad)
            py = cy + rx * math.cos(t) * math.sin(rad) + ry * math.sin(t) * math.cos(rad)
            pts.append((px, py))
        canvas.line(pts + [pts[0]], fill=colour, width=2)
    canvas.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=colour)


GLYPHS = {
    "globe": glyph_globe,
    "scales": glyph_scales,
    "swap": glyph_swap,
    "cyclone": glyph_cyclone,
    "droplet": glyph_droplet,
    "atom": glyph_atom,
}

ITEMS = [
    {
        "section": "WORLD COURT",
        "colour": (120, 40, 40),
        "glyph": "scales",
        "headline": "MYANMAR GUILTY OF GENOCIDE",
        "standfirst": "The ICJ finds the state responsible for the 2017 Rohingya killings — a first under the 1948 Convention.",
    },
    {
        "section": "WEATHER",
        "colour": (29, 78, 216),
        "glyph": "cyclone",
        "headline": "CYCLONE AKVAN HITS INDIA'S COAST",
        "standfirst": "The severe storm makes landfall in Odisha; 80,000 people evacuated.",
    },
    {
        "section": "KOREA",
        "colour": (21, 80, 160),
        "glyph": "globe",
        "headline": "TOP COURT CLEARS EX-PM HAN",
        "standfirst": "South Korea's Supreme Court overturns Han Duck-soo's conviction in the martial-law case.",
    },
    {
        "section": "PACIFIC",
        "colour": (14, 116, 144),
        "glyph": "droplet",
        "headline": "FIJI DECLARES NATIONAL DISASTER",
        "standfirst": "Drought and water shortages grip the islands as El Niño bites.",
    },
    {
        "section": "SECURITY",
        "colour": (109, 40, 217),
        "glyph": "atom",
        "headline": "NORTH KOREA EXPANDS ENRICHMENT",
        "standfirst": "The UN watchdog says the uranium facility at Yongbyon is growing.",
    },
    {
        "section": "AMERICAS",
        "colour": (158, 116, 8),
        "glyph": "swap",
        "headline": "US, VENEZUELA RESTORE MILITARY TIES",
        "standfirst": "Washington and Caracas sign a deal to resume defence cooperation.",
    },
]


def render():
    page = Image.new("RGB", (SIZE, SIZE), BACKGROUND)
    canvas = ImageDraw.Draw(page)
    edge = 30
    canvas.rectangle(
        [edge - 8, edge - 8, SIZE - edge + 8, SIZE - edge + 8], outline=FRAME, width=2
    )

    # ---- masthead ----
    name_face = load_font(SERIF, 78)
    name = "THE WORLD TODAY"
    name_w = canvas.textlength(name, font=name_face)
    canvas.text(((SIZE - name_w) / 2, 30), name, font=name_face, fill=BLACK)
    cursor = 30 + 78 + 10
    canvas.line([(edge, cursor), (SIZE - edge, cursor)], fill=BLACK, width=3)
    canvas.line([(edge, cursor + 6), (SIZE - edge, cursor + 6)], fill=BLACK, width=1)
    cursor += 16
    date_face = load_font(SANSB, 27)
    dateline = "FRIDAY, 20 NOVEMBER 2026"
    date_w = canvas.textlength(dateline, font=date_face)
    canvas.text(((SIZE - date_w) / 2, cursor), dateline, font=date_face, fill=SCARLET)
    cursor += 27 + 10
    motto_face = load_font(SANSR, 16)
    motto = "ONE DAY  ·  ONE IMAGE  —  THE WORLD IN A SINGLE FRAME"
    motto_w = canvas.textlength(motto, font=motto_face)
    canvas.text(((SIZE - motto_w) / 2, cursor), motto, font=motto_face, fill=MUTED)
    cursor += 16 + 14

    # ---- lead story ----
    lead_top = cursor
    lead_height = 282
    canvas.rectangle(
        [edge, lead_top, SIZE - edge, lead_top + lead_height], outline=BLACK, width=2
    )
    picture = (edge + 2, lead_top + 2, edge + 482, lead_top + lead_height - 2)
    paint_summit(canvas, picture)
    text_x = edge + 482 + 26
    text_w = SIZE - edge - 26 - text_x
    cursor = lead_top + 24
    canvas.text((text_x, cursor), "THE SUMMIT", font=load_font(SANSB, 17), fill=SCARLET)
    cursor += 17 + 12
    lead_face = load_font(SANSB, 37)
    lead_lines = wrap_text(canvas, "THREE POWERS, ONE TABLE", lead_face, text_w)
    cursor = draw_paragraph(canvas, lead_lines, text_x, cursor, lead_face, BLACK, 6)
    cursor += 10
    canvas.line([(text_x, cursor), (text_x + 64, cursor)], fill=SCARLET, width=4)
    cursor += 18
    deck_face = load_font(SANSR, 18)
    deck = (
        "Trump, Xi and Putin hold the first-ever trilateral summit in Shenzhen "
        "and pledge: a nuclear war cannot be won and must never be fought. "
        "UN reform and more oil output also agreed."
    )
    draw_paragraph(
        canvas, wrap_text(canvas, deck, deck_face, text_w), text_x, cursor, deck_face, BODY, 6
    )
    cursor = lead_top + lead_height + 16

    # ---- six stories in a 3 x 2 grid ----
    columns, rows = 3, 2
    gutter = 15
    cell_w = (SIZE - 2 * edge - (columns - 1) * gutter) // columns
    cell_h = 184
    grid_top = cursor
    for pos, item in enumerate(ITEMS):
        row, col = divmod(pos, columns)
        x = edge + col * (cell_w + gutter)
        y0 = grid_top + row * (cell_h + gutter)
        canvas.rectangle(
            [x, y0, x + cell_w, y0 + cell_h], outline=(150, 144, 128), width=1
        )
        canvas.rectangle([x, y0, x + cell_w, y0 + 5], fill=item["colour"])
        gx = x + cell_w - 52
        GLYPHS[item["glyph"]](
            canvas, (gx, y0 + 16, gx + 44, y0 + 60), item["colour"]
        )
        inner_x = x + 16
        inner_y = y0 + 16
        canvas.text(
            (inner_x, inner_y),
            item["section"],
            font=load_font(SANSB, 14),
            fill=item["colour"],
        )
        inner_y += 14 + 8
        head_face = load_font(SANSB, 20)
        head_lines = wrap_text(canvas, item["headline"], head_face, cell_w - 32 - 52)
        inner_y = draw_paragraph(canvas, head_lines, inner_x, inner_y, head_face, BLACK, 3)
        inner_y += 6
        deck_face = load_font(SANSR, 15)
        draw_paragraph(
            canvas,
            wrap_text(canvas, item["standfirst"], deck_face, cell_w - 32),
            inner_x,
            inner_y,
            deck_face,
            BODY,
            4,
        )

    # ---- footer ticker ----
    foot = grid_top + rows * cell_h + (rows - 1) * gutter + 16
    canvas.line([(edge, foot), (SIZE - edge, foot)], fill=BLACK, width=2)
    foot += 12
    tick_face = load_font(SANSB, 15)
    ticker = (
        "ALSO TODAY:   Australia sanctions Israeli settlers over West Bank expansion  ·  "
        "Modi meets the Prince and Princess of Wales in Delhi  ·  "
        "Anthropic valued at $1.5 trillion  ·  "
        "India v New Zealand, 1st Test: Nicholls 113* as NZ reach 243/5  ·  "
        "ADNOC vessel hit in the Strait of Hormuz, one crew missing"
    )
    foot = draw_paragraph(
        canvas, wrap_text(canvas, ticker, tick_face, SIZE - 2 * edge), edge, foot, tick_face, BLACK, 4
    )
    foot += 10
    credit_face = load_font(SANSR, 13)
    canvas.text(
        (edge, foot),
        "Sources: CNN  ·  Le Monde  ·  The Times  ·  NPR  ·  The Hindu  —  20 November 2026",
        font=credit_face,
        fill=MUTED,
    )

    page.save(TARGET, format="PNG")
    print(f"wrote {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    render()
