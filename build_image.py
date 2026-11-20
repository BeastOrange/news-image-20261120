#!/usr/bin/env python3
"""Draw THE WORLD TODAY for Friday 20 November 2026, 1024x1024 PNG.

Layout: a serif masthead with the date in red, a lead panel pairing a
drawn summit scene (three flags above a round table) with the day's
biggest story, six boxed stories in two rows of three, and a footer
ticker of shorter items. Every coordinate, colour and string is a
literal in this file, so the output is byte-identical on every run.
Pillow does the drawing; main.py (stdlib only) just copies the PNG.

Stories checked for 20 Nov 2026 against CNN, Le Monde, The Times,
WAMU/NPR, Education Times, The Daily Jagran, Jagran Josh, studmentor.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"

PAGE = 1024
MARGIN = 30
PAPER = (248, 244, 233)
INK = (20, 20, 20)
GREY = (90, 86, 76)
RED = (185, 28, 28)
RULE = (60, 56, 48)
TEXT = (52, 50, 44)
HAIRLINE = (150, 144, 128)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def face(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)


SERIF_B = "DejaVuSerif-Bold.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS_R = "DejaVuSans.ttf"


def fit(draw, text, font, width):
    """Greedy word wrap returning a list of lines fitting `width`."""
    out, buf = [], ""
    for word in text.split():
        trial = f"{buf} {word}".strip()
        if not buf or draw.textlength(trial, font=font) <= width:
            buf = trial
        else:
            out.append(buf)
            buf = word
    if buf:
        out.append(buf)
    return out


def blurb(draw, lines, x, y, font, colour, gap=4):
    for line in lines:
        draw.text((x, y), line, font=font, fill=colour)
        y += font.size + gap
    return y


def five_star(draw, cx, cy, outer, colour):
    pts = []
    for i in range(10):
        a = math.radians(i * 36 - 90)
        r = outer if i % 2 == 0 else outer * 0.42
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    draw.polygon(pts, fill=colour)


def stars_and_stripes(draw, x, y, w, h):
    band = h / 13
    for i in range(13):
        draw.rectangle(
            [x, y + i * band, x + w, y + (i + 1) * band + 1],
            fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255),
        )
    cw, ch = w * 0.4, band * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(60, 59, 110))
    for r in range(5):
        for c in range(6):
            px = x + 6 + c * (cw - 10) / 5
            py = y + 5 + r * (ch - 9) / 4
            draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))


def china_flag(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    five_star(draw, x + w * 0.17, y + h * 0.22, 7, (255, 222, 89))
    for fx, fy in ((0.32, 0.08), (0.40, 0.20), (0.40, 0.36), (0.32, 0.46)):
        five_star(draw, x + w * fx, y + h * fy, 3, (255, 222, 89))


def russia_flag(draw, x, y, w, h):
    for i, col in enumerate(((255, 255, 255), (0, 57, 166), (213, 0, 50))):
        draw.rectangle(
            [x, y + i * h / 3, x + w, y + (i + 1) * h / 3 + 1], fill=col
        )


def summit_scene(draw, box):
    """Night sky, gold sun, three flags on poles, round table below."""
    x0, y0, x1, y1 = box
    mid = (x0 + x1) // 2
    floor = y0 + int((y1 - y0) * 0.78)
    for yy in range(y0, floor):
        t = (yy - y0) / max(1, floor - y0)
        draw.line(
            [(x0, yy), (x1, yy)],
            fill=(int(16 + 42 * t), int(24 + 50 * t), int(64 + 58 * t)),
        )
    sun_y = y0 + 78
    for rad, col in ((62, (212, 160, 60)), (50, (232, 190, 96))):
        draw.ellipse(
            [mid - rad, sun_y - rad, mid + rad, sun_y + rad], fill=col
        )
    fw, fh = 118, 74
    pole_top, pole_base = y0 + 26, floor - 8
    for fx, painter in (
        (x0 + 34, stars_and_stripes),
        (mid - fw // 2, china_flag),
        (x1 - 34 - fw, russia_flag),
    ):
        draw.line([(fx + 2, pole_top), (fx + 2, pole_base)], fill=(220, 214, 198), width=4)
        draw.ellipse([fx - 2, pole_top - 6, fx + 6, pole_top + 2], fill=(232, 190, 96))
        painter(draw, fx + 6, pole_top + 8, fw, fh)
    draw.rectangle([x0, floor, x1, y1], fill=(18, 26, 52))
    ty = floor - 2
    draw.ellipse([mid - 168, ty, mid + 168, ty + 30], fill=(96, 62, 32))
    draw.ellipse([mid - 168, ty, mid + 168, ty + 18], fill=(146, 96, 52))
    draw.rectangle([mid - 10, ty + 24, mid + 10, y1 - 30], fill=(70, 44, 24))
    draw.text(
        (x0 + 12, y1 - 26),
        "ILLUSTRATION: THREE FLAGS, ONE TABLE — SHENZHEN",
        font=face(SANS_B, 13),
        fill=(210, 214, 220),
    )


def icon_globe(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=3)
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r], outline=col, width=2)
    draw.line([(cx - r, cy), (cx + r, cy)], fill=col, width=2)


def icon_scales(draw, box, col):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.line([(cx, y0 + 4), (cx, y1 - 8)], fill=col, width=3)
    draw.line([(x0 + 6, y0 + 12), (x1 - 6, y0 + 12)], fill=col, width=3)
    for sx in (x0 + 8, x1 - 24):
        draw.line([(sx + 7, y0 + 12), (sx + 7, y0 + 24)], fill=col, width=2)
        draw.polygon([(sx, y0 + 24), (sx + 14, y0 + 24), (sx + 7, y0 + 34)], fill=col)
    draw.rectangle([x0 + 4, y1 - 8, x1 - 4, y1 - 4], fill=col)


def icon_swap(draw, box, col):
    x0, y0, x1, y1 = box
    draw.line([(x0 + 4, y0 + 12), (x1 - 10, y0 + 12)], fill=col, width=3)
    draw.polygon([(x1 - 10, y0 + 6), (x1 - 2, y0 + 12), (x1 - 10, y0 + 18)], fill=col)
    draw.line([(x1 - 4, y1 - 12), (x0 + 10, y1 - 12)], fill=col, width=3)
    draw.polygon([(x0 + 10, y1 - 18), (x0 + 2, y1 - 12), (x0 + 10, y1 - 6)], fill=col)


def icon_storm(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for rad in (18, 12, 6):
        draw.arc([cx - rad, cy - rad, cx + rad, cy + rad], 30, 300, fill=col, width=3)


def icon_drop(draw, box, col):
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    draw.polygon([(cx, y0 + 2), (cx + 13, y0 + 26), (cx - 13, y0 + 26)], fill=col)
    draw.ellipse([cx - 13, y0 + 16, cx + 13, y1 - 4], fill=col)


def icon_atom(draw, box, col):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    for tilt in (0, 60, 120):
        a = math.radians(tilt)
        pts = []
        for i in range(36):
            t = math.radians(i * 10)
            pts.append((
                cx + 20 * math.cos(t) * math.cos(a) - 8 * math.sin(t) * math.sin(a),
                cy + 20 * math.cos(t) * math.sin(a) + 8 * math.sin(t) * math.cos(a),
            ))
        draw.line(pts + [pts[0]], fill=col, width=2)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=col)


ICONS = {
    "globe": icon_globe,
    "scales": icon_scales,
    "swap": icon_swap,
    "storm": icon_storm,
    "drop": icon_drop,
    "atom": icon_atom,
}

STORIES = [
    ("WORLD COURT", (120, 40, 40), "scales",
     "MYANMAR GUILTY OF GENOCIDE",
     "The ICJ finds the state responsible for the 2017 Rohingya killings — a first under the 1948 Convention."),
    ("WEATHER", (29, 78, 216), "storm",
     "CYCLONE AKVAN HITS INDIA'S COAST",
     "The severe storm makes landfall in Odisha; 80,000 people evacuated."),
    ("KOREA", (21, 80, 160), "globe",
     "TOP COURT CLEARS EX-PM HAN",
     "South Korea's Supreme Court overturns Han Duck-soo's conviction in the martial-law case."),
    ("PACIFIC", (14, 116, 144), "drop",
     "FIJI DECLARES NATIONAL DISASTER",
     "Drought and water shortages grip the islands as El Niño bites."),
    ("SECURITY", (109, 40, 217), "atom",
     "NORTH KOREA EXPANDS ENRICHMENT",
     "The UN watchdog says the uranium facility at Yongbyon is growing."),
    ("AMERICAS", (158, 116, 8), "swap",
     "US, VENEZUELA RESTORE MILITARY TIES",
     "Washington and Caracas sign a deal to resume defence cooperation."),
]

TICKER = (
    "ALSO TODAY:   Australia sanctions Israeli settlers over West Bank expansion  ·  "
    "Modi meets the Prince and Princess of Wales in Delhi  ·  "
    "Anthropic valued at $1.5 trillion  ·  "
    "India v New Zealand, 1st Test: Nicholls 113* as NZ reach 243/5  ·  "
    "ADNOC vessel hit in the Strait of Hormuz, one crew missing"
)

LEAD_DECK = (
    "Trump, Xi and Putin hold the first-ever trilateral summit in Shenzhen "
    "and pledge: a nuclear war cannot be won and must never be fought. "
    "UN reform and more oil output also agreed."
)


def masthead(draw, y):
    title = face(SERIF_B, 78)
    name = "THE WORLD TODAY"
    w = draw.textlength(name, font=title)
    draw.text(((PAGE - w) / 2, 30), name, font=title, fill=INK)
    y = 30 + 78 + 10
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=3)
    draw.line([(MARGIN, y + 6), (PAGE - MARGIN, y + 6)], fill=INK, width=1)
    y += 16
    stamp = face(SANS_B, 27)
    day = "FRIDAY, 20 NOVEMBER 2026"
    w = draw.textlength(day, font=stamp)
    draw.text(((PAGE - w) / 2, y), day, font=stamp, fill=RED)
    y += 27 + 10
    tag = face(SANS_R, 16)
    line = "ONE DAY  ·  ONE IMAGE  —  THE WORLD IN A SINGLE FRAME"
    w = draw.textlength(line, font=tag)
    draw.text(((PAGE - w) / 2, y), line, font=tag, fill=GREY)
    return y + 16 + 14


def lead_panel(draw, y):
    height = 282
    draw.rectangle(
        [MARGIN, y, PAGE - MARGIN, y + height], outline=INK, width=2
    )
    summit_scene(draw, (MARGIN + 2, y + 2, MARGIN + 482, y + height - 2))
    tx = MARGIN + 482 + 26
    tw = PAGE - MARGIN - 26 - tx
    cy = y + 24
    draw.text((tx, cy), "THE SUMMIT", font=face(SANS_B, 17), fill=RED)
    cy += 17 + 12
    head = face(SANS_B, 37)
    cy = blurb(draw, fit(draw, "THREE POWERS, ONE TABLE", head, tw), tx, cy, head, INK, 6)
    cy += 10
    draw.line([(tx, cy), (tx + 64, cy)], fill=RED, width=4)
    cy += 18
    deck = face(SANS_R, 18)
    blurb(draw, fit(draw, LEAD_DECK, deck, tw), tx, cy, deck, TEXT, 6)
    return y + height + 16


def story_grid(draw, y):
    cols, rows, gap = 3, 2, 15
    cw = (PAGE - 2 * MARGIN - (cols - 1) * gap) // cols
    ch = 184
    for n, (section, col, icon, head, stand) in enumerate(STORIES):
        r, c = divmod(n, cols)
        x = MARGIN + c * (cw + gap)
        y0 = y + r * (ch + gap)
        draw.rectangle([x, y0, x + cw, y0 + ch], outline=HAIRLINE, width=1)
        draw.rectangle([x, y0, x + cw, y0 + 5], fill=col)
        gx = x + cw - 52
        ICONS[icon](draw, (gx, y0 + 16, gx + 44, y0 + 60), col)
        ix, iy = x + 16, y0 + 16
        draw.text((ix, iy), section, font=face(SANS_B, 14), fill=col)
        iy += 14 + 8
        hf = face(SANS_B, 20)
        iy = blurb(draw, fit(draw, head, hf, cw - 32 - 52), ix, iy, hf, INK, 3)
        iy += 6
        df = face(SANS_R, 15)
        blurb(draw, fit(draw, stand, df, cw - 32), ix, iy, df, TEXT, 4)
    return y + rows * ch + (rows - 1) * gap + 16


def footer(draw, y):
    draw.line([(MARGIN, y), (PAGE - MARGIN, y)], fill=INK, width=2)
    y += 12
    tf = face(SANS_B, 15)
    y = blurb(draw, fit(draw, TICKER, tf, PAGE - 2 * MARGIN), MARGIN, y, tf, INK, 4)
    y += 10
    draw.text(
        (MARGIN, y),
        "Sources: CNN  ·  Le Monde  ·  The Times  ·  NPR  ·  The Hindu  —  20 November 2026",
        font=face(SANS_R, 13),
        fill=GREY,
    )


def main():
    sheet = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(sheet)
    draw.rectangle(
        [MARGIN - 8, MARGIN - 8, PAGE - MARGIN + 8, PAGE - MARGIN + 8],
        outline=RULE,
        width=2,
    )
    y = masthead(draw, 0)
    y = lead_panel(draw, y)
    y = story_grid(draw, y)
    footer(draw, y)
    sheet.save(OUT, format="PNG")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
