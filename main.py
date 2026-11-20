#!/usr/bin/env python3
"""news-image-20261120 - Sum up Friday 20 November 2026 world news in one image.

Pure Python 3.13 standard library (zlib + struct + math only). Draws a
1024x1024 front-page style image with the day's six top stories: a
full-width lead story, a 2x2 grid of four stories, and a bottom strip.
Each story has a kicker, a big headline, a short subhead and a small
drawn scene. Deterministic: fixed constants, no clock, no randomness,
no network. Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Stories (as reported on 20 November 2026):
 1. Trump, Xi and Putin sign a four-point "peace declaration" after
    their first-ever trilateral summit in Shenzhen: a nuclear war
    cannot be won and must never be fought, but no arms-control talks,
    no timetable, and no mention of Ukraine or Iran.
 2. Trump pushes the Iran war decision to 2027: no rush, he will
    "see what happens" after January 1.
 3. The International Court of Justice rules Myanmar committed
    genocide against the Rohingya minority.
 4. NASA confirms Voyager 1 is now a full light-day from Earth -
    24 hours for a radio signal to reach the probe.
 5. Cyclone Akvan bears down on Odisha: 300,000 evacuated, 423
    rescue teams deployed.
 6. Grand Theft Auto VI sales pass The Odyssey's $1.80 billion
    global run.
"""

import math
import os
import struct
import zlib

PAGE_W = 1024
PAGE_H = 1024

PAPER = (248, 244, 232)
INK = (17, 17, 17)
WHITE = (255, 255, 255)
RED = (180, 35, 24)
BAND = (241, 237, 226)
GREY = (120, 116, 104)
NIGHT = (24, 32, 54)
SEA = (44, 110, 150)
ORANGE = (226, 88, 34)
GOLD = (255, 210, 0)
DUSK = (214, 128, 60)
DESERT = (196, 158, 104)
OLIVE = (74, 92, 52)
EUBLUE = (0, 51, 153)
CHART = (16, 44, 34)
VIOLET = (120, 60, 160)
TEAL = (20, 110, 110)
STORM = (70, 90, 120)

# 5x7 pixel font. Every glyph is seven rows of five characters:
# "1" is an inked pixel, "0" is blank, leftmost character first.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "/": ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11001", "00010", "00100", "01000", "10011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


class Sheet:
    """A plain RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.buf = bytearray(bg) * (width * height)

    def put_pixel(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            at = (y * self.w + x) * 3
            self.buf[at] = colour[0]
            self.buf[at + 1] = colour[1]
            self.buf[at + 2] = colour[2]

    def fill_box(self, x, y, w, h, colour):
        # One slice per row: the same pixels, written row by row.
        stripe = bytes(colour) * w
        left = max(x, 0)
        right = min(x + w, self.w)
        if right <= left:
            return
        for yy in range(max(y, 0), min(y + h, self.h)):
            at = (yy * self.w + left) * 3
            self.buf[at:at + 3 * (right - left)] = stripe[3 * (left - x):3 * (right - x)]

    def draw_box(self, x, y, w, h, colour, thick=2):
        self.fill_box(x, y, w, thick, colour)
        self.fill_box(x, y + h - thick, w, thick, colour)
        self.fill_box(x, y, thick, h, colour)
        self.fill_box(x + w - thick, y, thick, h, colour)

    def h_rule(self, x, y, w, colour, thick=1):
        self.fill_box(x, y, w, thick, colour)

    def v_rule(self, x, y, h, colour, thick=1):
        self.fill_box(x, y, thick, h, colour)

    def segment(self, x0, y0, x1, y1, colour, thick=1):
        # Bresenham's walk; every step stamps a thick-by-thick block.
        run = abs(x1 - x0)
        rise = -abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        err = run + rise
        px, py = x0, y0
        half = thick // 2
        while True:
            self.fill_box(px - half, py - half, thick, thick, colour)
            if px == x1 and py == y1:
                return
            twice = 2 * err
            if twice >= rise:
                err += rise
                px += step_x
            if twice <= run:
                err += run
                py += step_y

    def blob(self, cx, cy, r, colour):
        # Filled disc, one horizontal run per row.
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) * (yy - cy))))
            self.fill_box(cx - dx, yy, 2 * dx + 1, 1, colour)

    def halo(self, cx, cy, r, colour, thick=3):
        # A ring: pixels whose distance from the centre is near r.
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - thick) * (r - thick) <= d2 <= r * r:
                    self.put_pixel(xx, yy, colour)

    def wedge(self, ax, ay, bx, by, cx, cy, colour):
        # Filled triangle by scanlines between its three edges.
        top = min(ay, by, cy)
        bottom = max(ay, by, cy)
        edges = ((ax, ay, bx, by), (bx, by, cx, cy), (cx, cy, ax, ay))
        for yy in range(top, bottom + 1):
            hits = []
            for (x1, y1, x2, y2) in edges:
                if y1 == y2:
                    continue
                low, high = (y1, y2) if y1 < y2 else (y2, y1)
                if low <= yy < high or (yy == bottom and yy == high):
                    hits.append(x1 + (x2 - x1) * (yy - y1) / (y2 - y1))
            if len(hits) >= 2:
                self.fill_box(int(min(hits)), yy,
                              int(max(hits)) - int(min(hits)) + 1, 1, colour)


def measure(text, scale):
    # Six pixels per character cell (five glyph pixels plus spacing).
    return len(text) * 6 * scale


def blit_text(sheet, x, y, text, scale, colour):
    """Draw uppercase text; any character outside the font is blank."""
    cursor = x
    for ch in text:
        rows = GLYPHS.get(ch) or GLYPHS[" "]
        for row_no, row in enumerate(rows):
            for col_no, bit in enumerate(row):
                if bit == "1":
                    sheet.fill_box(cursor + col_no * scale,
                                   y + row_no * scale, scale, scale, colour)
        cursor += 6 * scale
    return cursor


def blit_centred(sheet, x, y, width, text, scale, colour):
    """Draw text centred in the band starting at x with width w."""
    blit_text(sheet, x + (width - measure(text, scale)) // 2,
              y, text, scale, colour)


def wrap_words(text, max_w, scale):
    """Greedy word wrap into lines that fit max_w pixels at scale."""
    out = []
    for word in text.split(" "):
        if out and measure(out[-1] + " " + word, scale) <= max_w:
            out[-1] += " " + word
        else:
            out.append(word)
    return out


def burst(sheet, cx, cy, r, colour):
    """A twelve-spike explosion burst centred on (cx, cy)."""
    for k in range(12):
        ang = math.radians(k * 30)
        reach = r if k % 2 == 0 else r // 2
        sheet.segment(cx, cy,
                      cx + int(reach * math.cos(ang)),
                      cy + int(reach * math.sin(ang)), colour, 3)
    sheet.blob(cx, cy, r // 3, colour)


# ---------------------------------------------------------------- scenes
# Each scene draws inside the band (bx, by, w, h) it is given.

def scene_pact(sheet, bx, by, w, h, accent):
    # Shenzhen at dusk: tower skyline, three flag poles (China, US,
    # Russia) and a white dove carrying an olive branch above them.
    sheet.fill_box(bx, by, w, h, (200, 214, 230))
    # Low sun over the skyline.
    sheet.blob(bx + w - 52, by + 34, 20, (240, 170, 60))
    # Skyline: stepped towers of different heights.
    towers = ((0, 120, 46, 80), (52, 96, 40, 104), (98, 132, 52, 68),
              (156, 84, 44, 116), (206, 116, 48, 84), (260, 92, 44, 108),
              (310, 128, 52, 72))
    for (tx, ty, tw, th) in towers:
        sheet.fill_box(bx + tx, by + ty, tw, th, (52, 62, 84))
    # Lit windows on the towers.
    for (tx, ty, tw, th) in towers:
        for wy in range(ty + 10, ty + th - 8, 16):
            for wx in range(tx + 8, tx + tw - 8, 14):
                sheet.fill_box(bx + wx, by + wy, 5, 6, GOLD)
    # Ground and red carpet.
    sheet.fill_box(bx, by + h - 18, w, 18, (70, 76, 92))
    sheet.fill_box(bx + w // 2 - 90, by + h - 18, 180, 18, RED)
    # Three flag poles with China, US and Russia flags.
    flags = (
        ((222, 41, 16), (222, 41, 16), (222, 41, 16)),   # China red
        ((200, 40, 40), (255, 255, 255), (200, 40, 40)),  # US stripes
        ((255, 255, 255), (0, 60, 160), (200, 40, 40)),   # Russia bands
    )
    for i, bands in enumerate(flags):
        fx = bx + 44 + i * 116
        sheet.v_rule(fx, by + 78, h - 96, INK, 3)
        for j, col in enumerate(bands):
            sheet.fill_box(fx + 3, by + 80 + j * 12, 78, 12, col)
        sheet.draw_box(fx + 3, by + 80, 78, 36, INK, 1)
    # China stars, US blue corner.
    burst(sheet, bx + 44 + 12, by + 86, 6, GOLD)
    sheet.fill_box(bx + 44 + 116 + 3, by + 80, 30, 12, (0, 40, 104))
    sheet.blob(bx + 44 + 116 + 18, by + 86, 4, WHITE)
    # A white dove above the flags, olive branch in its beak.
    dx, dy = bx + w // 2, by + 40
    sheet.blob(dx, dy, 12, WHITE)
    sheet.blob(dx + 12, dy + 2, 8, WHITE)
    sheet.wedge(dx + 18, dy - 2, dx + 30, dy + 2, dx + 18, dy + 6, GOLD)
    sheet.segment(dx - 10, dy - 6, dx - 2, dy - 18, WHITE, 4)
    sheet.segment(dx - 2, dy - 18, dx + 10, dy - 8, WHITE, 4)
    sheet.segment(dx + 20, dy + 2, dx + 34, dy + 10, OLIVE, 3)
    sheet.blob(dx + 34, dy + 10, 3, OLIVE)
    sheet.blob(dx + 30, dy + 6, 3, OLIVE)


def scene_calendar(sheet, bx, by, w, h, accent):
    # A wall calendar turned to a new year: big 2027, a clock, and a
    # torn-off 2026 page. 48px band.
    sheet.fill_box(bx, by, w, h, (236, 228, 210))
    # Torn 2026 page behind, tilted.
    sheet.wedge(bx + 12, by + 40, bx + 30, by + 6, bx + 52, by + 40, GREY)
    blit_text(sheet, bx + 22, by + 20, "26", 2, WHITE)
    # The calendar sheet.
    sheet.fill_box(bx + 48, by + 4, 150, h - 8, WHITE)
    sheet.draw_box(bx + 48, by + 4, 150, h - 8, INK, 2)
    sheet.fill_box(bx + 48, by + 4, 150, 10, RED)
    blit_text(sheet, bx + 58, by + 18, "2027", 3, INK)
    blit_text(sheet, bx + 128, by + 22, "JAN 1", 2, RED)
    # A clock face on the right.
    cx, cy = bx + 260, by + 24
    sheet.blob(cx, cy, 16, WHITE)
    sheet.halo(cx, cy, 16, INK, 2)
    sheet.segment(cx, cy, cx, cy - 10, INK, 2)
    sheet.segment(cx, cy, cx + 8, cy + 4, INK, 2)
    sheet.blob(cx, cy, 2, INK)
    # "SEE WHAT HAPPENS" caption band on the far right.
    blit_text(sheet, bx + 300, by + 10, "SEE WHAT", 2, INK)
    blit_text(sheet, bx + 300, by + 28, "HAPPENS", 2, INK)


def scene_justice(sheet, bx, by, w, h, accent):
    # The scales of justice in front of a courthouse colonnade.
    # 48px band.
    sheet.fill_box(bx, by, w, h, (222, 214, 196))
    # Courthouse columns.
    for i in range(5):
        sheet.fill_box(bx + 8 + i * 18, by + 6, 8, h - 14, (180, 172, 150))
    sheet.fill_box(bx, by, w, 5, (150, 140, 118))
    # The scales: central pole, beam, two hanging pans.
    cx, cy = bx + 150, by + 24
    sheet.v_rule(cx, by + 6, h - 14, INK, 3)
    sheet.h_rule(cx - 34, by + 10, 68, INK, 3)
    sheet.wedge(cx - 34, by + 10, cx - 46, by + 30, cx - 22, by + 30, GOLD)
    sheet.wedge(cx + 34, by + 10, cx + 22, by + 30, cx + 46, by + 30, GOLD)
    sheet.fill_box(cx - 8, by + h - 10, 16, 4, INK)
    # A gavel on the right.
    sheet.segment(bx + w - 90, by + 30, bx + w - 50, by + 14, (120, 84, 50), 4)
    sheet.fill_box(bx + w - 56, by + 6, 22, 10, (120, 84, 50))
    blit_text(sheet, bx + w - 150, by + 26, "ICJ", 3, INK)


def scene_voyager(sheet, bx, by, w, h, accent):
    # Deep space: starfield, the Voyager probe with its big dish, and
    # radio arcs travelling home. 48px band.
    sheet.fill_box(bx, by, w, h, NIGHT)
    # Fixed stars.
    stars = ((14, 8), (60, 26), (110, 10), (170, 30), (230, 8),
             (300, 22), (360, 10), (410, 28), (40, 38), (200, 40),
             (330, 38), (440, 14))
    for (sx, sy) in stars:
        sheet.blob(bx + sx, by + sy, 1, WHITE)
    # Radio arcs travelling left, back toward Earth, drawn first so
    # the probe sits on top of them.
    px, py = bx + 90, by + 24
    for r in (22, 32, 42):
        sheet.halo(px - 10, py, r, GOLD, 2)
    # The probe: dish, body, boom and antenna.
    sheet.wedge(px - 6, py - 12, px - 6, py + 12, px + 12, py, WHITE)
    sheet.fill_box(px + 12, py - 5, 26, 10, (200, 200, 210))
    sheet.segment(px + 38, py, px + 62, py - 8, (200, 200, 210), 2)
    sheet.blob(px + 64, py - 9, 3, GOLD)
    # Earth, small and blue, at the far left.
    sheet.blob(bx + 18, by + 24, 7, SEA)
    sheet.blob(bx + 16, by + 22, 3, (120, 200, 120))
    # "1 LIGHT-DAY" callout on the right.
    blit_text(sheet, bx + 250, by + 8, "1 LIGHT-DAY", 3, WHITE)
    blit_text(sheet, bx + 250, by + 30, "FROM EARTH", 2, GOLD)


def scene_cyclone(sheet, bx, by, w, h, accent):
    # A cyclone spiral over the sea, rain slanting in, waves below.
    # 48px band.
    sheet.fill_box(bx, by, w, h, STORM)
    # Spiral arms: three rings of decreasing radius.
    cx, cy = bx + 110, by + 24
    for r in (18, 12, 6):
        sheet.halo(cx, cy, r, WHITE, 2)
    sheet.blob(cx, cy, 4, WHITE)
    # Slanting rain on the left.
    for i in range(6):
        sheet.segment(bx + 8 + i * 12, by + 6, bx + 2 + i * 12, by + 20,
                      (180, 200, 220), 2)
    # Waves at the very bottom, below the callout text.
    for i in range(8):
        wx = bx + 200 + i * 28
        sheet.segment(wx, by + h - 4, wx + 12, by + h - 8, WHITE, 2)
        sheet.segment(wx + 12, by + h - 8, wx + 24, by + h - 4, WHITE, 2)
    # "300,000 EVACUATED" callout on the right, clear of the waves.
    blit_text(sheet, bx + 190, by + 4, "300,000", 3, WHITE)
    blit_text(sheet, bx + 190, by + 26, "EVACUATED", 2, GOLD)


def scene_gta2(sheet, bx, by, w, h, accent):
    # Vice City at sunset again, this time with a gold box-office
    # tally: the VI and a $1.8 BN callout. 64px band.
    sheet.fill_box(bx, by, w, h, (255, 150, 110))
    sheet.fill_box(bx, by + h // 2, w, h - h // 2, VIOLET)
    sheet.blob(bx + w // 2, by + 26, 16, (255, 220, 90))
    sheet.h_rule(bx + w // 2 - 16, by + 26, 32, (255, 150, 110), 2)
    # Skyline silhouettes.
    sheet.fill_box(bx + 16, by + h - 22, 26, 22, INK)
    sheet.fill_box(bx + 48, by + h - 30, 20, 30, INK)
    sheet.fill_box(bx + w - 66, by + h - 26, 24, 26, INK)
    sheet.fill_box(bx + w - 36, by + h - 20, 22, 20, INK)
    # Palm trees at the edges, clear of the VI in the centre.
    for px in (bx + 64, bx + w - 64):
        sheet.segment(px, by + h - 4, px + 4, by + 10, (40, 26, 16), 4)
        for (dx, dy) in ((-14, -4), (-8, -10), (2, -12), (12, -8),
                         (16, -2)):
            sheet.segment(px + 4, by + 10, px + 4 + dx, by + 10 + dy,
                          (20, 120, 60), 2)
    # Big dark VI in the centre, over the sun, so it reads.
    blit_text(sheet, bx + w // 2 - 24, by + 14, "VI", 4, INK)


LEAD = {
    "kicker": "CHINA - SUMMIT", "color": (158, 43, 37),
    "head": ["TRUMP, XI, PUTIN", "SIGN PEACE PACT"],
    "sub": "FIRST-EVER TRILATERAL SUMMIT: A FOUR-POINT PEACE DECLARATION - NUCLEAR WAR CANNOT BE WON, BUT NO WORD ON UKRAINE OR IRAN.",
    "scene": scene_pact,
}

GRID = [
    {"kicker": "GULF - IRAN", "color": (158, 43, 37),
     "head": ["IRAN DECISION", "PUSHED TO 2027"],
     "sub": "TRUMP SAYS NO RUSH ON IRAN: HE WILL SEE WHAT HAPPENS AFTER JAN 1.",
     "scene": scene_calendar},
    {"kicker": "WORLD COURT", "color": (29, 78, 137),
     "head": ["MYANMAR GUILTY", "OF GENOCIDE"],
     "sub": "WORLD COURT: MYANMAR COMMITTED GENOCIDE AGAINST ROHINGYA.",
     "scene": scene_justice},
    {"kicker": "SPACE - NASA", "color": (24, 32, 54),
     "head": ["VOYAGER 1 HITS", "ONE LIGHT-DAY"],
     "sub": "NASA CONFIRMS VOYAGER 1 IS NOW A FULL LIGHT-DAY FROM EARTH.",
     "scene": scene_voyager},
    {"kicker": "WEATHER - INDIA", "color": (70, 90, 120),
     "head": ["CYCLONE AKVAN", "HITS ODISHA"],
     "sub": "300,000 EVACUATED AS CYCLONE AKVAN BEARS DOWN ON ODISHA.",
     "scene": scene_cyclone},
]

STRIP = {
    "kicker": "CULTURE - GAMES", "color": (120, 60, 160),
    "head": "GTA VI TOPS $1.8 BN",
    "sub": "GTA VI SALES PASS THE ODYSSEY'S $1.80 BILLION GLOBAL RUN.",
    "scene": scene_gta2,
}


# ---------------------------------------------------------------- layout

def draw_panel(sheet, x, y, w, h, colour, kicker, band_h, text_y):
    """A white story panel with a coloured kicker band on top."""
    sheet.fill_box(x, y, w, h, WHITE)
    sheet.draw_box(x, y, w, h, INK, 2)
    sheet.fill_box(x, y, w, band_h, colour)
    blit_text(sheet, x + 14, y + text_y, kicker, 3, WHITE)


def sub_block(sheet, x, y, text, max_w, scale, step=18, most=3):
    """Draw a wrapped subhead, one line per step pixels, at most most."""
    for i, line in enumerate(wrap_words(text, max_w, scale)[:most]):
        blit_text(sheet, x, y + i * step, line, scale, INK)


def compose():
    sheet = Sheet(PAGE_W, PAGE_H, PAPER)
    # Masthead.
    sheet.h_rule(24, 16, 976, RED, 4)
    blit_centred(sheet, 0, 34, PAGE_W, "THE WORLD IN ONE DAY", 6, INK)
    blit_centred(sheet, 0, 92, PAGE_W, "FRIDAY 20 NOVEMBER 2026", 5, RED)
    sheet.h_rule(24, 142, 976, RED, 4)
    # Lead story: full-width panel with a scene on its right.
    px, py, pw, ph = 24, 158, 976, 258
    draw_panel(sheet, px, py, pw, ph, LEAD["color"], LEAD["kicker"], 34, 7)
    blit_text(sheet, px + 14, py + 46, LEAD["head"][0], 6, INK)
    blit_text(sheet, px + 14, py + 92, LEAD["head"][1], 6, INK)
    sub_block(sheet, px + 14, py + 150, LEAD["sub"], 556, 2)
    sx, sy = px + 600, py + 44
    sheet.fill_box(sx, sy, 362, 200, NIGHT)
    sheet.draw_box(sx, sy, 362, 200, GREY, 1)
    LEAD["scene"](sheet, sx, sy, 362, 200, LEAD["color"])
    # Grid: 2 columns x 2 rows of 480 x 196 panels.
    for i, story in enumerate(GRID):
        px = 24 + (i % 2) * (480 + 16)
        py = 432 + (i // 2) * (196 + 16)
        draw_panel(sheet, px, py, 480, 196, story["color"],
                   story["kicker"], 30, 6)
        blit_text(sheet, px + 12, py + 38, story["head"][0], 4, INK)
        blit_text(sheet, px + 12, py + 66, story["head"][1], 4, INK)
        sub_block(sheet, px + 12, py + 100, story["sub"], 456, 2, 16, 2)
        bx, by = px + 14, py + 140
        sheet.fill_box(bx, by, 452, 48, BAND)
        sheet.draw_box(bx, by, 452, 48, GREY, 1)
        story["scene"](sheet, bx, by, 452, 48, story["color"])
    # Bottom strip: the GTA VI story, with a scene on its right.
    px, py, pw, ph = 24, 856, 976, 84
    sheet.fill_box(px, py, pw, ph, WHITE)
    sheet.draw_box(px, py, pw, ph, INK, 2)
    sheet.fill_box(px, py, 8, ph, STRIP["color"])
    blit_text(sheet, px + 20, py + 12, STRIP["head"], 4, INK)
    sub_block(sheet, px + 20, py + 48, STRIP["sub"], 660, 2, 16, 2)
    sx, sy = px + 700, py + 10
    sheet.fill_box(sx, sy, 262, 64, BAND)
    sheet.draw_box(sx, sy, 262, 64, GREY, 1)
    STRIP["scene"](sheet, sx, sy, 262, 64, STRIP["color"])
    # Footer.
    sheet.h_rule(24, 956, 976, INK, 2)
    blit_centred(sheet, 0, 970, PAGE_W,
                 "SIX STORIES FROM ONE DAY - FRIDAY 20 NOVEMBER 2026", 2, INK)
    return sheet


def encode_png(sheet):
    """Encode the sheet as a 1024x1024 RGB PNG, filter 0 per row."""

    def pack(kind, payload):
        framed = struct.pack(">I", len(payload)) + kind + payload
        return framed + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", sheet.w, sheet.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for row_no in range(sheet.h):
        raw.append(0)
        raw += sheet.buf[row_no * sheet.w * 3:(row_no + 1) * sheet.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + pack(b"IHDR", header)
            + pack(b"IDAT", zlib.compress(bytes(raw), 6))
            + pack(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(compose())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), PAGE_W, PAGE_H))


if __name__ == "__main__":
    main()
