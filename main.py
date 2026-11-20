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

W = 1024
H = 1024

PAPER = (248, 244, 232)
INK = (17, 17, 17)
WHITE = (255, 255, 255)
RED = (180, 35, 24)
BAND = (241, 237, 226)
GREY = (120, 116, 104)
NIGHT = (24, 32, 54)
SEA = (44, 110, 150)
SKY = (232, 236, 240)
ORANGE = (226, 88, 34)
GOLD = (255, 210, 0)
DUSK = (214, 128, 60)
DESERT = (196, 158, 104)
OLIVE = (74, 92, 52)
EUBLUE = (0, 51, 153)
CHART = (16, 44, 34)
PINK = (255, 120, 160)
VIOLET = (120, 60, 160)
TEAL = (20, 110, 110)
STORM = (70, 90, 120)

# 5x7 pixel font: each glyph is 7 rows, low 5 bits, bit 4 = leftmost pixel.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
}


class Canvas:
    """A plain RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        # Fill row by row with a slice assignment: same pixels, less code.
        row = bytes(c) * w
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                x0 = max(x, 0)
                x1 = min(x + w, self.w)
                if x1 > x0:
                    i = (yy * self.w + x0) * 3
                    self.px[i:i + 3 * (x1 - x0)] = row[3 * (x0 - x):3 * (x1 - x)]

    def frame(self, x, y, w, h, c, t=2):
        # Four bars make the frame; corners are drawn twice, harmlessly.
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        # Bresenham's walk; each step stamps a t-by-t block.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - t) * (r - t) <= d <= r * r:
                    self.set(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                    (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or yy == ymax and yy == max(ay, by):
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)


def text_w(s, scale):
    # Six pixels per character cell (five glyph pixels plus spacing).
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, c):
    """Draw uppercase text; any character outside the font is blank."""
    cx = x
    for ch in s:
        rows = FONT.get(ch) or FONT[" "]
        for r, bits in enumerate(rows):
            for col in range(5):
                if bits >> (4 - col) & 1:
                    cv.rect(cx + col * scale, y + r * scale,
                            scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_c(cv, x, y, w, s, scale, c):
    """Draw text centred in the band starting at x with width w."""
    draw_text(cv, x + (w - text_w(s, scale)) // 2, y, s, scale, c)


def wrap(s, max_w, scale):
    """Greedy word wrap into lines that fit max_w pixels at scale."""
    lines = []
    for word in s.split(" "):
        if lines and text_w(lines[-1] + " " + word, scale) <= max_w:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines


def starburst(cv, cx, cy, r, c):
    """A twelve-spike explosion burst centred on (cx, cy)."""
    for k in range(12):
        ang = math.radians(k * 30)
        reach = r if k % 2 == 0 else r // 2
        x1 = cx + int(reach * math.cos(ang))
        y1 = cy + int(reach * math.sin(ang))
        cv.line(cx, cy, x1, y1, c, 3)
    cv.disc(cx, cy, r // 3, c)


# ---------------------------------------------------------------- scenes
# Each scene draws inside the band (bx, by, w, h) it is given.

def scene_pact(cv, bx, by, w, h, accent):
    # Shenzhen at dusk: tower skyline, three flag poles (China, US,
    # Russia) and a white dove carrying an olive branch above them.
    cv.rect(bx, by, w, h, (200, 214, 230))
    # Low sun over the skyline.
    cv.disc(bx + w - 52, by + 34, 20, (240, 170, 60))
    # Skyline: stepped towers of different heights.
    towers = ((0, 120, 46, 80), (52, 96, 40, 104), (98, 132, 52, 68),
              (156, 84, 44, 116), (206, 116, 48, 84), (260, 92, 44, 108),
              (310, 128, 52, 72))
    for (tx, ty, tw, th) in towers:
        cv.rect(bx + tx, by + ty, tw, th, (52, 62, 84))
    # Lit windows on the towers.
    for (tx, ty, tw, th) in towers:
        for wy in range(ty + 10, ty + th - 8, 16):
            for wx in range(tx + 8, tx + tw - 8, 14):
                cv.rect(bx + wx, by + wy, 5, 6, GOLD)
    # Ground and red carpet.
    cv.rect(bx, by + h - 18, w, 18, (70, 76, 92))
    cv.rect(bx + w // 2 - 90, by + h - 18, 180, 18, RED)
    # Three flag poles with China, US and Russia flags.
    flags = (
        ((222, 41, 16), (222, 41, 16), (222, 41, 16)),   # China red
        ((200, 40, 40), (255, 255, 255), (200, 40, 40)),  # US stripes
        ((255, 255, 255), (0, 60, 160), (200, 40, 40)),   # Russia bands
    )
    for i, bands in enumerate(flags):
        fx = bx + 44 + i * 116
        cv.vline(fx, by + 78, h - 96, INK, 3)
        for j, col in enumerate(bands):
            cv.rect(fx + 3, by + 80 + j * 12, 78, 12, col)
        cv.frame(fx + 3, by + 80, 78, 36, INK, 1)
    # China stars, US blue corner.
    starburst(cv, bx + 44 + 12, by + 86, 6, GOLD)
    cv.rect(bx + 44 + 116 + 3, by + 80, 30, 12, (0, 40, 104))
    cv.disc(bx + 44 + 116 + 18, by + 86, 4, WHITE)
    # A white dove above the flags, olive branch in its beak.
    dx, dy = bx + w // 2, by + 40
    cv.disc(dx, dy, 12, WHITE)
    cv.disc(dx + 12, dy + 2, 8, WHITE)
    cv.tri(dx + 18, dy - 2, dx + 30, dy + 2, dx + 18, dy + 6, GOLD)
    cv.line(dx - 10, dy - 6, dx - 2, dy - 18, WHITE, 4)
    cv.line(dx - 2, dy - 18, dx + 10, dy - 8, WHITE, 4)
    cv.line(dx + 20, dy + 2, dx + 34, dy + 10, OLIVE, 3)
    cv.disc(dx + 34, dy + 10, 3, OLIVE)
    cv.disc(dx + 30, dy + 6, 3, OLIVE)


def scene_calendar(cv, bx, by, w, h, accent):
    # A wall calendar turned to a new year: big 2027, a clock, and a
    # torn-off 2026 page. 48px band.
    cv.rect(bx, by, w, h, (236, 228, 210))
    # Torn 2026 page behind, tilted.
    cv.tri(bx + 12, by + 40, bx + 30, by + 6, bx + 52, by + 40, GREY)
    draw_text(cv, bx + 22, by + 20, "26", 2, WHITE)
    # The calendar sheet.
    cv.rect(bx + 48, by + 4, 150, h - 8, WHITE)
    cv.frame(bx + 48, by + 4, 150, h - 8, INK, 2)
    cv.rect(bx + 48, by + 4, 150, 10, RED)
    draw_text(cv, bx + 58, by + 18, "2027", 3, INK)
    draw_text(cv, bx + 128, by + 22, "JAN 1", 2, RED)
    # A clock face on the right.
    cx, cy = bx + 260, by + 24
    cv.disc(cx, cy, 16, WHITE)
    cv.ring(cx, cy, 16, INK, 2)
    cv.line(cx, cy, cx, cy - 10, INK, 2)
    cv.line(cx, cy, cx + 8, cy + 4, INK, 2)
    cv.disc(cx, cy, 2, INK)
    # "SEE WHAT HAPPENS" caption band on the far right.
    draw_text(cv, bx + 300, by + 10, "SEE WHAT", 2, INK)
    draw_text(cv, bx + 300, by + 28, "HAPPENS", 2, INK)


def scene_justice(cv, bx, by, w, h, accent):
    # The scales of justice in front of a courthouse colonnade.
    # 48px band.
    cv.rect(bx, by, w, h, (222, 214, 196))
    # Courthouse columns.
    for i in range(5):
        cv.rect(bx + 8 + i * 18, by + 6, 8, h - 14, (180, 172, 150))
    cv.rect(bx, by, w, 5, (150, 140, 118))
    # The scales: central pole, beam, two hanging pans.
    cx, cy = bx + 150, by + 24
    cv.vline(cx, by + 6, h - 14, INK, 3)
    cv.hline(cx - 34, by + 10, 68, INK, 3)
    cv.tri(cx - 34, by + 10, cx - 46, by + 30, cx - 22, by + 30, GOLD)
    cv.tri(cx + 34, by + 10, cx + 22, by + 30, cx + 46, by + 30, GOLD)
    cv.rect(cx - 8, by + h - 10, 16, 4, INK)
    # A gavel on the right.
    cv.line(bx + w - 90, by + 30, bx + w - 50, by + 14, (120, 84, 50), 4)
    cv.rect(bx + w - 56, by + 6, 22, 10, (120, 84, 50))
    draw_text(cv, bx + w - 150, by + 26, "ICJ", 3, INK)


def scene_voyager(cv, bx, by, w, h, accent):
    # Deep space: starfield, the Voyager probe with its big dish, and
    # radio arcs travelling home. 48px band.
    cv.rect(bx, by, w, h, NIGHT)
    # Fixed stars.
    stars = ((14, 8), (60, 26), (110, 10), (170, 30), (230, 8),
             (300, 22), (360, 10), (410, 28), (40, 38), (200, 40),
             (330, 38), (440, 14))
    for (sx, sy) in stars:
        cv.disc(bx + sx, by + sy, 1, WHITE)
    # Radio arcs travelling left, back toward Earth, drawn first so
    # the probe sits on top of them.
    px, py = bx + 90, by + 24
    for r in (22, 32, 42):
        cv.ring(px - 10, py, r, GOLD, 2)
    # The probe: dish, body, boom and antenna.
    cv.tri(px - 6, py - 12, px - 6, py + 12, px + 12, py, WHITE)
    cv.rect(px + 12, py - 5, 26, 10, (200, 200, 210))
    cv.line(px + 38, py, px + 62, py - 8, (200, 200, 210), 2)
    cv.disc(px + 64, py - 9, 3, GOLD)
    # Earth, small and blue, at the far left.
    cv.disc(bx + 18, by + 24, 7, SEA)
    cv.disc(bx + 16, by + 22, 3, (120, 200, 120))
    # "1 LIGHT-DAY" callout on the right.
    draw_text(cv, bx + 250, by + 8, "1 LIGHT-DAY", 3, WHITE)
    draw_text(cv, bx + 250, by + 30, "FROM EARTH", 2, GOLD)


def scene_cyclone(cv, bx, by, w, h, accent):
    # A cyclone spiral over the sea, rain slanting in, waves below.
    # 48px band.
    cv.rect(bx, by, w, h, STORM)
    # Spiral arms: three arcs of decreasing radius.
    cx, cy = bx + 110, by + 24
    for r in (18, 12, 6):
        cv.ring(cx, cy, r, WHITE, 2)
    cv.disc(cx, cy, 4, WHITE)
    # Slanting rain on the left.
    for i in range(6):
        cv.line(bx + 8 + i * 12, by + 6, bx + 2 + i * 12, by + 20,
                (180, 200, 220), 2)
    # Waves at the very bottom, below the callout text.
    for i in range(8):
        wx = bx + 200 + i * 28
        cv.line(wx, by + h - 4, wx + 12, by + h - 8, WHITE, 2)
        cv.line(wx + 12, by + h - 8, wx + 24, by + h - 4, WHITE, 2)
    # "300,000 EVACUATED" callout on the right, clear of the waves.
    draw_text(cv, bx + 190, by + 4, "300,000", 3, WHITE)
    draw_text(cv, bx + 190, by + 26, "EVACUATED", 2, GOLD)


def scene_gta2(cv, bx, by, w, h, accent):
    # Vice City at sunset again, this time with a gold box-office
    # tally: the VI and a $1.8 BN callout. 64px band.
    cv.rect(bx, by, w, h, (255, 150, 110))
    cv.rect(bx, by + h // 2, w, h - h // 2, VIOLET)
    cv.disc(bx + w // 2, by + 26, 16, (255, 220, 90))
    cv.hline(bx + w // 2 - 16, by + 26, 32, (255, 150, 110), 2)
    # Skyline silhouettes.
    cv.rect(bx + 16, by + h - 22, 26, 22, INK)
    cv.rect(bx + 48, by + h - 30, 20, 30, INK)
    cv.rect(bx + w - 66, by + h - 26, 24, 26, INK)
    cv.rect(bx + w - 36, by + h - 20, 22, 20, INK)
    # Palm trees at the edges, clear of the VI in the centre.
    for px in (bx + 64, bx + w - 64):
        cv.line(px, by + h - 4, px + 4, by + 10, (40, 26, 16), 4)
        for (dx, dy) in ((-14, -4), (-8, -10), (2, -12), (12, -8),
                         (16, -2)):
            cv.line(px + 4, by + 10, px + 4 + dx, by + 10 + dy,
                    (20, 120, 60), 2)
    # Big dark VI in the centre, over the sun, so it reads.
    draw_text(cv, bx + w // 2 - 24, by + 14, "VI", 4, INK)


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

def panel(cv, x, y, w, h, color, kicker, band, ky):
    """A white story panel with a coloured kicker band on top."""
    cv.rect(x, y, w, h, WHITE)
    cv.frame(x, y, w, h, INK, 2)
    cv.rect(x, y, w, band, color)
    draw_text(cv, x + 14, y + ky, kicker, 3, WHITE)


def sub_lines(cv, x, y, text, max_w, scale, dy=18, max_lines=3):
    """Draw a wrapped subhead, one line per dy pixels, at most max_lines."""
    for i, line in enumerate(wrap(text, max_w, scale)[:max_lines]):
        draw_text(cv, x, y + i * dy, line, scale, INK)


def build():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    cv.hline(24, 16, 976, RED, 4)
    draw_text_c(cv, 0, 34, W, "THE WORLD IN ONE DAY", 6, INK)
    draw_text_c(cv, 0, 92, W, "FRIDAY 20 NOVEMBER 2026", 5, RED)
    cv.hline(24, 142, 976, RED, 4)
    # Lead story: full-width panel with a scene on its right.
    px, py, pw, ph = 24, 158, 976, 258
    panel(cv, px, py, pw, ph, LEAD["color"], LEAD["kicker"], 34, 7)
    draw_text(cv, px + 14, py + 46, LEAD["head"][0], 6, INK)
    draw_text(cv, px + 14, py + 92, LEAD["head"][1], 6, INK)
    sub_lines(cv, px + 14, py + 150, LEAD["sub"], 556, 2)
    sx, sy = px + 600, py + 44
    cv.rect(sx, sy, 362, 200, NIGHT)
    cv.frame(sx, sy, 362, 200, GREY, 1)
    LEAD["scene"](cv, sx, sy, 362, 200, LEAD["color"])
    # Grid: 2 columns x 2 rows of 480 x 196 panels.
    for i, st in enumerate(GRID):
        px = 24 + (i % 2) * (480 + 16)
        py = 432 + (i // 2) * (196 + 16)
        panel(cv, px, py, 480, 196, st["color"], st["kicker"], 30, 6)
        draw_text(cv, px + 12, py + 38, st["head"][0], 4, INK)
        draw_text(cv, px + 12, py + 66, st["head"][1], 4, INK)
        sub_lines(cv, px + 12, py + 100, st["sub"], 456, 2, 16, 2)
        bx, by = px + 14, py + 140
        cv.rect(bx, by, 452, 48, BAND)
        cv.frame(bx, by, 452, 48, GREY, 1)
        st["scene"](cv, bx, by, 452, 48, st["color"])
    # Bottom strip: the GTA VI story, with a scene on its right.
    px, py, pw, ph = 24, 856, 976, 84
    cv.rect(px, py, pw, ph, WHITE)
    cv.frame(px, py, pw, ph, INK, 2)
    cv.rect(px, py, 8, ph, STRIP["color"])
    draw_text(cv, px + 20, py + 12, STRIP["head"], 4, INK)
    sub_lines(cv, px + 20, py + 48, STRIP["sub"], 660, 2, 16, 2)
    sx, sy = px + 700, py + 10
    cv.rect(sx, sy, 262, 64, BAND)
    cv.frame(sx, sy, 262, 64, GREY, 1)
    STRIP["scene"](cv, sx, sy, 262, 64, STRIP["color"])
    # Footer.
    cv.hline(24, 956, 976, INK, 2)
    draw_text_c(cv, 0, 970, W,
                "SIX STORIES FROM ONE DAY - FRIDAY 20 NOVEMBER 2026", 2, INK)
    return cv


def png_bytes(cv):
    """Encode the canvas as a 1024x1024 RGB PNG, filter 0 per row."""

    def chunk(kind, data):
        body = struct.pack(">I", len(data)) + kind + data
        return body + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
