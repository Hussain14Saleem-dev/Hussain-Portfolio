"""
Every sprite that isn't the room: the portfolio book, the pointing hand,
tileable textures for the reading UI, the icon sheet and the avatar.

Sizes are chosen so the book reads at 1x on the desk and simply gets bigger
pixels as the camera pushes in — the way a zoom works in an actual pixel game,
rather than resampling the art.
"""

import os
import sys
import random

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxlib import Canvas, c, PAL, TRANSPARENT  # noqa: E402
from pxfont import draw_text_centered, draw_text, text_width  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'assets', 'px')

rng = random.Random(4242)

BOOK_W, BOOK_H = 96, 128     # a book, face on
SPINE_W, SPINE_H = 22, 96    # a book, spine on, sitting in the shelf

# Two volumes live on the shelf. Everything about a book's look comes from one
# of these, so adding a third would be a matter of adding an entry here.
SCHEMES = {
    'green': dict(dd='grn_dd', d='grn_d', m='grn', l='grn_l',
                  kicker='PORTFOLIO OF', foot='SOFTWARE ENGINEER',
                  sub='BENGHAZI LIBYA', spine='HUSSAIN'),
    'blue':  dict(dd='blu_dd', d='blu_d', m='blu', l='blu_l',
                  kicker='CERTIFICATES OF', foot='ACCOMPLISHMENTS',
                  sub='', spine='CERTIFICATES'),
}


# ---------------------------------------------------------------------------
# Shared ornament
# ---------------------------------------------------------------------------

def leather_fill(cv, x, y, w, h, rng, dd='grn_dd', d='grn_d', m='grn', l='grn_l'):
    """Green book cloth: base tone, mottling, and a lit top-left."""
    cv.rect(x, y, w, h, c(d))
    cv.scatter(x, y, w, h, c(m), 0.07, rng)
    cv.scatter(x, y, w, h, c(dd), 0.06, rng)
    # light falls from the upper left
    for j in range(h):
        for i in range(w):
            t = (i / w) * 0.6 + (j / h) * 0.4
            if t < 0.18 and (i + j) % 2 == 0:
                cv.px(x + i, y + j, c(l))
            elif t > 0.86 and (i + j) % 2 == 0:
                cv.px(x + i, y + j, c(dd))


def corner_flourish(cv, x, y, col, flip_x=False, flip_y=False):
    """A 9x9 gilt corner ornament."""
    pts = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
           (0, 1), (0, 2), (0, 3), (0, 4),
           (2, 2), (3, 2), (2, 3),
           (5, 1), (6, 2), (1, 5), (2, 6),
           (7, 3), (3, 7), (8, 5), (5, 8)]
    for dx, dy in pts:
        px_ = x + (-dx if flip_x else dx)
        py_ = y + (-dy if flip_y else dy)
        cv.px(px_, py_, col)


def diamond(cv, cx, cy, r, col):
    for j in range(-r, r + 1):
        span = r - abs(j)
        for i in range(-span, span + 1):
            cv.px(cx + i, cy + j, col)


# ---------------------------------------------------------------------------
# The book
# ---------------------------------------------------------------------------

def book_cover(front=True, sk='green'):
    """
    Front (or back) cover of the portfolio, 96x128.

    Every measurement here is checked against the 96px width — the first draft
    set the title at 2x with letter spacing, which came out 106px wide and hung
    off both edges of the book.
    """
    S = SCHEMES[sk]
    cv = Canvas(BOOK_W, BOOK_H)
    w, h = BOOK_W, BOOK_H

    cv.rect(0, 0, w, h, c('ink'))
    leather_fill(cv, 1, 1, w - 2, h - 2, rng, S['dd'], S['d'], S['m'], S['l'])

    # the spine side is darker where the boards bend
    cv.rect(1, 1, 7, h - 2, c(S['dd']))
    cv.dither(8, 1, 4, h - 2, c(S['dd']), 2)
    cv.vline(2, 1, h - 2, c(S['d']))

    # fore-edge highlight
    cv.vline(w - 2, 2, h - 4, c(S['l']))
    cv.vline(w - 3, 2, h - 4, c(S['m']))

    if not front:
        cv.frame(10, 8, w - 18, h - 16, c('amber_d'))
        diamond(cv, w // 2, h // 2, 7, c('amber_d'))
        return cv

    # double gilt rule, inset far enough that 85px of lettering still clears it
    cv.frame(3, 3, w - 6, h - 6, c('gold'))
    cv.frame(6, 6, w - 12, h - 12, c('amber_d'))
    for fx, fy, ax, ay in ((4, 4, False, False), (w - 5, 4, True, False),
                           (4, h - 5, False, True), (w - 5, h - 5, True, True)):
        corner_flourish(cv, fx, fy, c('gold'), ax, ay)

    mid = w // 2

    # -- title block -------------------------------------------------------
    draw_text_centered(cv, mid, 15, S['kicker'], c('amber_d'), spacing=0, scale=1)
    # spacing=0 at 2x: HUSSAIN is 70px, ALSHIKHY is 80px, both inside 96
    draw_text_centered(cv, mid, 25, 'HUSSAIN', c('gold'), spacing=0, scale=2,
                       shadow=c(S['dd']))
    draw_text_centered(cv, mid, 41, 'ALSHIKHY', c('gold'), spacing=0, scale=2,
                       shadow=c(S['dd']))

    cv.hline(18, 60, w - 36, c('amber_d'))
    diamond(cv, mid - 24, 60, 2, c('gold'))
    diamond(cv, mid + 23, 60, 2, c('gold'))

    # -- emblem: an open book inside a gilt diamond -----------------------
    ex, ey = mid, 80
    diamond(cv, ex, ey, 12, c(S['dd']))
    diamond(cv, ex, ey, 11, c('gold'))
    diamond(cv, ex, ey, 9, c(S['dd']))
    cv.rect(ex - 7, ey - 3, 6, 7, c('cream'))
    cv.rect(ex + 2, ey - 3, 6, 7, c('cream'))
    cv.rect(ex - 1, ey - 4, 2, 9, c('gold'))
    for k in range(1, 6, 2):
        cv.hline(ex - 6, ey - 2 + k, 4, c('cream_d'))
        cv.hline(ex + 3, ey - 2 + k, 4, c('cream_d'))

    # -- foot --------------------------------------------------------------
    cv.hline(18, 100, w - 36, c('amber_d'))
    # a volume with one line in the foot centres that line instead of leaving
    # a gap where the second one used to be
    if S['sub']:
        draw_text_centered(cv, mid, 104, S['foot'], c('gold'), spacing=0)
        draw_text_centered(cv, mid, 113, S['sub'], c('amber_d'), spacing=0)
    else:
        draw_text_centered(cv, mid, 108, S['foot'], c('gold'), spacing=0)

    return cv


def book_closed():  # noqa: F811  (kept for reference; not shipped)
    """
    The whole closed book as it sits on the desk: cover, plus the page block
    showing along the fore-edge and the foot. Those visible page lines are the
    detail that sells it as a real book rather than a green rectangle.
    """
    cv = Canvas(BOOK_W + 8, BOOK_H + 6)

    # page block, offset down-right from the board
    px0, py0 = 4, 3
    cv.rect(px0 + BOOK_W - 4, py0 + 3, 7, BOOK_H - 6, c('cream_m'))
    cv.rect(px0 + 6, py0 + BOOK_H - 3, BOOK_W - 6, 5, c('cream_m'))
    # individual leaves
    for j in range(py0 + 4, py0 + BOOK_H - 4, 2):
        cv.hline(px0 + BOOK_W - 4, j, 7, c('cream_d'))
    for i in range(px0 + 7, px0 + BOOK_W, 2):
        cv.vline(i, py0 + BOOK_H - 3, 5, c('cream_d'))
    cv.rect(px0 + BOOK_W - 4, py0 + 3, 7, 2, c('cream_l'))

    # the cover on top
    cover = book_cover(front=True)
    cv.paste(cover, px0, py0)

    # head and tail bands, and a ribbon marker escaping the foot
    cv.rect(px0 + BOOK_W - 4, py0 + 2, 6, 3, c('red'))
    cv.rect(px0 + BOOK_W - 4, py0 + BOOK_H - 6, 6, 3, c('red'))
    cv.rect(px0 + 30, py0 + BOOK_H, 5, 9, c('red'))
    cv.rect(px0 + 30, py0 + BOOK_H + 9, 5, 3, c('red_d'))
    cv.px(px0 + 30, py0 + BOOK_H + 11, TRANSPARENT)
    cv.px(px0 + 34, py0 + BOOK_H + 11, TRANSPARENT)

    # drop shadow onto the desk
    cv.rect(px0 + 2, py0 + BOOK_H + 2, BOOK_W, 3, c('ink', 80))
    return cv


def book_spine_sprite(sk='green'):
    """
    The book as it appears on the shelf — spine out. The title is drawn flat
    and rotated a quarter turn, the way spine lettering actually reads.
    """
    S = SCHEMES[sk]
    cv = Canvas(SPINE_W, SPINE_H + 10)
    w, h = SPINE_W, SPINE_H

    # Edged in the book's own darkest shade, not in ink. A black outline is
    # what every other spine on the shelf does without, so on these two it
    # didn't read as a book — it read as a black rule ruled around the book.
    cv.rect(0, 0, w, h, c(S['dd']))
    leather_fill(cv, 1, 1, w - 2, h - 2, rng, S['dd'], S['d'], S['m'], S['l'])
    cv.vline(0, 0, h, c(S['l']))          # lit left edge, same as its neighbours
    cv.vline(w - 1, 0, h, c(S['dd']))     # shadowed right edge

    # raised bands, kept clear of the lettering band in the middle
    for by in (7, 84):
        cv.rect(1, by, w - 2, 3, c(S['m']))
        cv.hline(1, by, w - 2, c(S['l']))
        cv.hline(1, by + 2, w - 2, c(S['dd']))
        cv.hline(1, by - 1, w - 2, c('gold'))
        cv.hline(1, by + 3, w - 2, c('gold'))

    # The label canvas must be at least as long as the word or PIL silently
    # crops the tail off. Measured, not guessed: the two volumes have titles of
    # different lengths and the shorter one has to sit centred too.
    tw = text_width(S['spine'], spacing=0)
    label = Canvas(max(tw + 2, 80), 9)
    draw_text(label, 0, 1, S['spine'], c('gold'), spacing=0)
    rot = label.img.rotate(-90, expand=True)
    # rotate(-90) sends source x to destination y, so the word occupies the
    # first `tw` pixels of the rotated strip. Centre that between the bands.
    top = 11 + ((84 - 11) - tw) // 2
    cv.img.alpha_composite(rot, ((w - rot.width) // 2, top))

    cv.hline(4, 78, w - 8, c('amber_d'))
    cv.hline(4, 15, w - 8, c('amber_d'))

    # head and tail caps
    cv.rect(1, 1, w - 2, 2, c(S['dd']))
    cv.rect(1, h - 3, w - 2, 2, c(S['dd']))

    # No page-edge stripe down the side any more: a single cream line against
    # the neighbouring spines read as a misaligned seam, not as paper.
    cv.rect(7, h, 4, 8, c('red'))
    cv.px(7, h + 8, c('red_d'))
    cv.px(10, h + 8, c('red_d'))

    return cv


def book_pageblock():
    """
    The block of leaves under the cover.

    Earlier versions drew every individual leaf as a 1px stripe. At the
    camera's zoom those stripes became a tall shimmering barcode down the side
    of the book that read as misalignment rather than as paper. A closed book
    seen face-on really only shows a narrow, fairly uniform cream edge — so
    that is all this draws now: a solid block with a soft edge and a single
    seam. Quiet beats detailed at this size.
    """
    w, h = BOOK_W + 3, BOOK_H
    cv = Canvas(w, h)

    cv.rect(0, 0, w, h, c('cream'))
    cv.hline(0, 0, w, c('cream_l'))          # lit top edge
    cv.vline(w - 2, 1, h - 2, c('cream_m'))  # the fore-edge falls away
    cv.vline(w - 1, 1, h - 1, c('cream_d'))
    cv.hline(1, h - 2, w - 1, c('cream_m'))
    cv.hline(0, h - 1, w, c('cream_d'))

    # one seam where the leaves meet the board, and the head/tail bands
    cv.vline(2, 1, h - 2, c('cream_m'))
    cv.rect(w - 3, 1, 3, 3, c('red'))
    cv.rect(w - 3, h - 4, 3, 3, c('red'))

    return cv


def cert_placeholder():
    """
    Stands in for a certificate scan that has not been supplied. Drawn to look
    like a certificate rather than like an error, so a gap in the collection
    still reads as deliberate.
    """
    w, h = 168, 122
    cv = Canvas(w, h)

    cv.rect(0, 0, w, h, c('cream_m'))
    cv.frame(0, 0, w, h, c('ink'))
    cv.rect(4, 4, w - 8, h - 8, c('cream_l'))
    cv.frame(6, 6, w - 12, h - 12, c('blu_d'))
    cv.frame(8, 8, w - 16, h - 16, c('gold'))

    for fx, fy, ax, ay in ((10, 10, False, False), (w - 11, 10, True, False),
                           (10, h - 11, False, True), (w - 11, h - 11, True, True)):
        corner_flourish(cv, fx, fy, c('blu_l'), ax, ay)

    draw_text_centered(cv, w // 2, 24, 'CERTIFICATE', c('blu_d'), spacing=0)
    cv.hline(38, 34, w - 76, c('gold'))

    # ruled lines standing in for the wording
    r = random.Random(9)
    for i, y in enumerate(range(46, 84, 9)):
        ln = r.randint(60, 104)
        cv.hline((w - ln) // 2, y, ln, c('cream_d'))

    # wax seal with a ribbon
    sx, sy = w // 2, 86
    cv.rect(sx - 4, sy + 4, 4, 12, c('red_d'))
    cv.rect(sx + 1, sy + 4, 4, 12, c('red_d'))
    cv.circle(sx, sy, 9, c('ink'))
    cv.circle(sx, sy, 8, c('red'))
    cv.circle(sx, sy, 5, c('red_d'))
    cv.hline(sx - 3, sy - 1, 7, c('gold'))

    draw_text_centered(cv, w // 2, h - 14, 'SCAN TO FOLLOW', c('cream_d'), spacing=0)
    return cv


def book_open_inner(sk='green'):
    """
    The inside of the front board — marbled endpaper. Shown for a few frames
    as the cover swings open.
    """
    cv = Canvas(BOOK_W, BOOK_H)
    cv.rect(0, 0, BOOK_W, BOOK_H, c('cream_m'))
    cv.frame(0, 0, BOOK_W, BOOK_H, c('ink'))
    cv.rect(3, 3, BOOK_W - 6, BOOK_H - 6,
            c('plum' if sk == 'green' else 'blu_d'))
    # combed marbling
    import math
    for j in range(4, BOOK_H - 4):
        off = int(math.sin(j / 7.0) * 3 + math.sin(j / 2.3) * 1.5)
        for i in range(4, BOOK_W - 4, 11):
            cv.px(i + off, j, c('cream_m', 150))
            cv.px(i + off + 1, j, c('red_d', 120))
        if j % 17 == 0:
            cv.hline(4, j, BOOK_W - 8, c('gold', 55))
    cv.frame(3, 3, BOOK_W - 6, BOOK_H - 6, c('gold'))
    return cv


# ---------------------------------------------------------------------------
# The pointing hand
# ---------------------------------------------------------------------------

#   Anatomy notes, because the first two attempts got this wrong:
#   * The three folded fingers are ONE silhouette stepping down to the right.
#     Outlining each knuckle separately makes them read as extra stunted
#     fingers instead of a fist.
#   * The creases between those fingers are short VERTICAL lines drawn inside
#     the silhouette. Single scattered pixels just read as freckles.
#   * The thumb crosses in front of the palm, so it needs its own outline where
#     it overlaps — that edge is what makes it a thumb and not a mitten.
HAND_ROWS = [
    "......####..............",
    ".....#WGGG#.............",
    ".....#WGGG#.............",
    ".....#WGGG#.............",
    ".....#WGGG#.............",
    ".....#WGGG#.............",
    ".....#WGGG#.............",
    ".....#WGGG#.............",
    ".....#WGGG#####.........",
    ".....#WGGGGGGGG#........",
    ".....#WGGGGGGGG###......",
    ".....#WGGGGGGGGGGG#.....",
    "..##.#WGGGGGGGGGGG##....",
    ".#WGG#GGGGGGGGGGGGGGGG#.",
    ".#WGGGGGGGGGGGGGGGGGGG#.",
    ".#WGGGGGGGGGGGGGGGGGGG#.",
    ".#WGGGGGGGGGGGGGGGGGGS#.",
    "..#GGGGGGGGGGGGGGGGGGS#.",
    "..#GGGGGGGGGGGGGGGGGSS#.",
    "...#GGGGGGGGGGGGGGGSSS#.",
    "...#GGGGGGGGGGGGGGSSSS#.",
    "....##################..",
    "....#CCCCCCCCCCCCCCCC#..",
    "....#oooooooooooooooo#..",
    "....#CCCCCCCCCCCCCCCC#..",
    "....#kkkkkkkkkkkkkkkk#..",
    "....##################..",
]

# vertical gaps between the folded fingers: (x, y, length)
HAND_CREASES = [(15, 12, 8), (18, 14, 6)]
# the fold where the index finger leaves the fist
HAND_BASE_CREASE = (7, 13, 4)
# a lit pixel on top of each knuckle
HAND_KNUCKLE_LIGHT = [(12, 9, 2), (16, 11, 2), (19, 13, 1)]

HAND_COLS = {
    '#': 'ink', 'W': 'white', 'G': 'cream_l', 'S': 'cream_m',
    'c': 'cream_d',                       # crease between folded fingers
    'C': 'red', 'o': 'orange', 'k': 'red_d',
}


def _hand_frame(pressed=False):
    """
    A white-gloved pointing hand — the arcade-cabinet cursor. White glove is a
    deliberate choice: this sprite sits on top of a shelf full of saturated
    book spines, and a skin tone would vanish into the wood.

    `pressed` folds the index finger down for the click frame.
    """
    rows = HAND_ROWS
    if pressed:
        # Drop six rows out of the finger shaft and pad the top back out. The
        # fist keeps its original row indices, so creases must NOT be offset —
        # only the finger moves.
        rows = (["." * len(HAND_ROWS[0])] * 6) + HAND_ROWS[:1] + HAND_ROWS[7:]

    h = len(rows)
    w = max(len(r) for r in rows)
    cv = Canvas(w, h)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in HAND_COLS:
                cv.px(x, y, c(HAND_COLS[ch]))

    # creases and knuckle highlights go on top of the fill, never as part of
    # the mask — that way the silhouette stays one clean shape
    for x, y, ln in HAND_CREASES:
        cv.vline(x, y, ln, c('cream_d'))
    bx, by, bln = HAND_BASE_CREASE
    cv.hline(bx, by, bln, c('cream_d'))
    for x, y, ln in HAND_KNUCKLE_LIGHT:
        cv.hline(x, y, ln, c('white'))

    return cv


def hand():
    """Two frames side by side: idle (pointing) and pressed."""
    a, b = _hand_frame(False), _hand_frame(True)
    sheet = Canvas(a.w * 2, a.h)
    sheet.paste(a, 0, 0)
    sheet.paste(b, a.w, 0)
    return sheet


# ---------------------------------------------------------------------------
# The scroll bug
# ---------------------------------------------------------------------------

#   A beetle that wanders the page. It has to face where it is walking, so it
#   is drawn PARAMETRICALLY at each of eight headings rather than drawn once
#   and rotated: rotating the sprite by 45 degrees — even with nearest
#   neighbour — shattered the legs and antennae into loose pixels. Drawing the
#   body, legs and feelers along the heading vector keeps every angle clean.

import math

BUG_CELL = 24
BUG_DIRS = 8


def _beetle(cv, cx, cy, deg, phase):
    """
    One beetle, centred at (cx, cy), facing `deg` clockwise from north.

    Filled shapes are rasterised by walking SCREEN pixels and projecting each
    back into the bug's own frame. Walking the bug's grid forward and rounding
    into screen space instead leaves holes at 45 degrees — the diagonals came
    out looking like they had been sprayed on.
    """
    th = math.radians(deg)
    fx, fy = math.sin(th), -math.cos(th)     # forward (screen y grows down)
    rx, ry = math.cos(th), math.sin(th)      # right

    A, B = 8.0, 6.0          # body semi-axes: along heading, across
    HU, HA, HB = 8.0, 4.6, 4.2   # head offset and semi-axes

    for py in range(cv.h):
        for px in range(cv.w):
            dx, dy = px - cx, py - cy
            u = dx * fx + dy * fy
            v = dx * rx + dy * ry

            body = (u / A) ** 2 + (v / B) ** 2
            head = ((u - HU) / HA) ** 2 + (v / HB) ** 2

            if head <= 1.0:
                cv.px(px, py, c('ink2'))
            elif head <= 1.55:
                cv.px(px, py, c('ink'))

            if body <= 1.0:
                col = 'red_d'
                if abs(v) < 0.8 and -7 < u < 6:
                    col = 'ink'                      # elytra seam
                elif 0.5 < u < 5 and 1.8 < abs(v) < 4.6:
                    col = 'red'                      # lit patch
                if 2.5 < u < 4.5 and -4.2 < v < -2.4:
                    col = 'orange'                   # glint
                cv.px(px, py, c(col))
            elif body <= 1.34:
                cv.px(px, py, c('ink'))

    # legs and feelers: dense sampling along each line so nothing breaks up
    def stroke(u0, v0, u1, v1, col):
        n = int(max(abs(u1 - u0), abs(v1 - v0)) * 4) + 2
        for i in range(n + 1):
            t = i / n
            u = u0 + (u1 - u0) * t
            v = v0 + (v1 - v0) * t
            cv.px(round(cx + u * fx + v * rx),
                  round(cy + u * fy + v * ry), col)

    for i, u0 in enumerate((3.6, 0.0, -3.6)):
        lean = 2.4 if (i + phase) % 2 else -2.4
        for side in (-1, 1):
            stroke(u0, side * 4.5, u0 - lean, side * 10.5, c('ink'))

    for side in (-1, 1):
        stroke(9.5, side * 1.8, 14.5, side * 6.0, c('ink'))


def bug_sprite():
    """Sheet of 8 headings x 2 walk phases, each drawn from scratch."""
    sheet = Canvas(BUG_CELL * BUG_DIRS, BUG_CELL * 2)
    for phase in (0, 1):
        for d in range(BUG_DIRS):
            cell = Canvas(BUG_CELL, BUG_CELL)
            _beetle(cell, BUG_CELL // 2, BUG_CELL // 2, d * 45, phase)
            sheet.paste(cell, d * BUG_CELL, phase * BUG_CELL)
    return sheet


# ---------------------------------------------------------------------------
# Tileable textures for the reading UI
# ---------------------------------------------------------------------------

def parchment(size=64):
    """Seamless paper tooth. Kept very low contrast — it sits under body text."""
    cv = Canvas(size, size, bg='cream')
    r = random.Random(7)
    for _ in range(size * size // 7):
        x, y = r.randrange(size), r.randrange(size)
        cv.px(x, y, c('cream_m', 70))
    for _ in range(size * size // 14):
        x, y = r.randrange(size), r.randrange(size)
        cv.px(x, y, c('cream_l', 120))
    # a few fibre flecks
    for _ in range(10):
        x, y = r.randrange(size - 3), r.randrange(size)
        cv.hline(x, y, r.randint(2, 3), c('cream_d', 60))
    return cv


def leather_tile(size=32, sk='green'):
    """Seamless book cloth for the binding around the pages."""
    S = SCHEMES[sk]
    cv = Canvas(size, size, bg=S['d'])
    r = random.Random(11)
    cv.scatter(0, 0, size, size, c(S['m']), 0.09, r)
    cv.scatter(0, 0, size, size, c(S['dd']), 0.08, r)
    for _ in range(8):
        x, y = r.randrange(size - 4), r.randrange(size)
        cv.hline(x, y, r.randint(2, 4), c(S['l'], 60))
    return cv


def wood_tile(size=48):
    """Seamless dark wood — the desk surface behind the open book."""
    cv = Canvas(size, size, bg='wood_dd')
    r = random.Random(13)
    # speckle kept low — at 0.2 density this read as gravel, not timber
    cv.scatter(0, 0, size, size, c('wood_d'), 0.07, r)
    cv.scatter(0, 0, size, size, c('ink'), 0.05, r)
    for j in range(0, size, 12):
        cv.hline(0, j, size, c('ink', 110))
        cv.hline(0, j + 1, size, c('wood_d', 70))
        for _ in range(2):
            x = r.randrange(size - 10)
            cv.hline(x, j + r.randint(3, 9), r.randint(6, 10), c('wood_d', 90))
    return cv


# ---------------------------------------------------------------------------
# The lamp light
#
# A sprite rather than a CSS gradient, for two reasons. A gradient is resampled
# after the camera's fractional scale and comes out as a smooth smear against
# hard-edged art; and the light wants stepped bands, which is a thing you draw,
# not a thing you tween.
# ---------------------------------------------------------------------------

CONE_W, CONE_H = 88, 48          # 34 rows of cone, then the pool on the desk
CONE_MOUTH = 30                  # matches the shade's mouth in build_room.py
CONE_FALL = 34                   # shade to desk, in world pixels


def _lit(cv, x, y, rgb, a):
    """
    Write a straight (unpremultiplied) colour with an alpha.

    Canvas.px blends towards the destination, and on a transparent pixel the
    destination is black — drawing amber at alpha 100 there gives a muddy
    brown at alpha 100, not translucent amber. For a sprite that is nothing
    but translucency, the channels have to be set directly.
    """
    if 0 <= x < cv.w and 0 <= y < cv.h and a > 0:
        if a > cv.p[x, y][3]:
            cv.p[x, y] = (rgb[0], rgb[1], rgb[2], min(255, a))


def lamp_cone():
    cone = Canvas(CONE_W, CONE_H)
    mid = CONE_W // 2
    warm = PAL['amber']
    bright = PAL['amber_l']
    # (the white tier is gone — see the comment in the loop below)

    for j in range(CONE_FALL):
        t = j / (CONE_FALL - 1)
        half = CONE_MOUTH / 2 + t * (CONE_W - 6 - CONE_MOUTH) / 2
        # Strong. Amber at a low alpha over a teal wall averages out olive —
        # the first pass sat around 100 and read as grey-green haze, not light.
        base = int(196 - 96 * t)
        core = half * 0.42

        for i in range(CONE_W):
            d = abs(i - mid + 0.5)
            if d > half:
                continue
            edge = 1 - (d / half)                # 0 at the rim, 1 up the middle
            a = int(base * (0.52 + 0.48 * edge))

            # Vertical banding, the way a shade with a scalloped rim throws it.
            # Quantised to a few widths so it reads as drawn, not as noise.
            if int(d) % 7 in (3, 4):
                a += 26
            # and the whole thing steps down in four bands rather than fading
            a = (a // 22) * 22

            # Warm the whole way out. A white core read as fog rather than
            # lamplight, and amber at the rim went olive against the teal wall,
            # so only the very middle is near-white and only the outermost
            # sliver is the deep amber.
            # No white core at all. Even confined to the top few rows it
            # rendered as a pale rectangle hanging behind the cord — a second
            # object in the scene rather than a highlight in the light.
            if edge > 0.30:
                col = bright
            else:
                col = warm

            # dither the outer two pixels so the rim is stepped, not a hard line
            if d > half - 2 and (i + j) % 2:
                a = a // 2
            _lit(cone, i, j, col, a)

    # the pool it puts on the desk, flattened because the desk is seen edge on
    for j in range(CONE_FALL, CONE_H):
        k = j - CONE_FALL
        t = k / (CONE_H - CONE_FALL - 1)
        half = (CONE_W - 6) / 2 * (1 - t * 0.55)
        for i in range(CONE_W):
            d = abs(i - mid + 0.5)
            if d > half:
                continue
            a = int(96 * (1 - t) * (1 - (d / half) * 0.6))
            a = (a // 16) * 16
            if (i + j) % 2:
                a = a // 2
            _lit(cone, i, j, warm, a)

    return cone


# ---------------------------------------------------------------------------
# Application icons — the projects, as things you click on a desktop
#
# 32x32 each, one file per project so the markup can name them. Every one is a
# plate plus a motif: on a desktop full of icons, a consistent silhouette is
# what lets you tell them apart at a glance, and a motif alone at this size
# just reads as noise on the wallpaper.
# ---------------------------------------------------------------------------

APP_SIZE = 32


def _plate(cv, dark, base, light):
    """A 32x32 app tile: rounded corners, lit top-left, shadowed bottom-right."""
    s = APP_SIZE
    cv.rect(0, 0, s, s, c(base))
    cv.rect(0, 0, s, 2, c(light))
    cv.vline(0, 0, s, c(light))
    cv.rect(0, s - 2, s, 2, c(dark))
    cv.vline(s - 1, 0, s, c(dark))
    cv.frame(0, 0, s, s, c('ink'))
    # knock the four corners off so it reads as a tile, not a box
    for cxp, cyp in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):
        cv.px(cxp, cyp, TRANSPARENT)
    for cxp, cyp in ((1, 0), (0, 1), (s - 2, 0), (s - 1, 1),
                     (1, s - 1), (0, s - 2), (s - 2, s - 1), (s - 1, s - 2)):
        cv.px(cxp, cyp, c('ink'))


def app_rabt():
    """An NFC card, mid-tap: the arcs are the whole idea of the product."""
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'blue_d', 'blue', 'teal_ll')
    cv.rect(5, 11, 15, 11, c('cream'))
    cv.frame(5, 11, 15, 11, c('ink'))
    cv.hline(5, 11, 15, c('cream_l'))
    cv.rect(7, 13, 5, 5, c('amber'))          # the chip
    cv.frame(7, 13, 5, 5, c('wood_dd'))
    cv.hline(14, 14, 4, c('cream_d'))
    cv.hline(14, 16, 4, c('cream_d'))
    cv.hline(7, 20, 11, c('cream_d'))
    for r, col in ((4, 'amber_l'), (7, 'amber'), (10, 'amber_d')):
        for j in range(-r, r + 1):
            for i in range(0, r + 1):
                d = i * i + j * j
                if r * r - r <= d <= r * r + r and i >= abs(j) * 0.6:
                    cv.px(21 + i, 16 + j, c(col))
    return cv


def app_qaemati():
    """A QR code on a menu card — how a diner actually meets this product."""
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'red_d', 'red', 'orange')
    cv.rect(6, 5, 20, 24, c('cream_l'))
    cv.frame(6, 5, 20, 24, c('ink'))
    cv.rect(8, 7, 16, 16, c('white'))
    r = random.Random(7)
    for j in range(8):
        for i in range(8):
            if r.random() < 0.45:
                cv.rect(8 + i * 2, 7 + j * 2, 2, 2, c('ink2'))
    for ox, oy in ((0, 0), (12, 0), (0, 12)):          # finder patterns
        cv.rect(8 + ox, 7 + oy, 4, 4, c('cream_l'))
        cv.frame(8 + ox, 7 + oy, 4, 4, c('ink2'))
    cv.hline(9, 25, 14, c('cream_d'))
    cv.hline(9, 27, 9, c('cream_d'))
    return cv


def app_arcade():
    """A joystick and two buttons. Reads as arcade at any size."""
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'ink2', 'shadow', 'purple')
    cv.rect(4, 20, 24, 8, c('ink2'))
    cv.hline(4, 20, 24, c('shadow'))
    cv.rect(10, 12, 3, 9, c('cream_d'))
    cv.vline(10, 12, 9, c('cream_l'))
    cv.circle(11, 9, 4, c('red'))
    cv.circle(11, 9, 4, c('red_d'), fill=False)
    cv.rect(9, 6, 3, 2, c('orange'))
    cv.rect(8, 19, 7, 3, c('wood_dd'))
    for bx, col, colr in ((19, 'amber', 'amber_d'), (24, 'grn_l', 'grn_dd')):
        cv.circle(bx, 22, 3, c(col))
        cv.circle(bx, 22, 3, c(colr), fill=False)
        cv.px(bx - 1, 20, c('amber_l' if col == 'amber' else 'grn_ll'))
    return cv


def app_techzaar():
    """A pin dropped on a folded map — the site is a map of the event."""
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'teal_dd', 'teal_d', 'teal_l')
    cv.rect(4, 8, 24, 18, c('cream'))
    cv.frame(4, 8, 24, 18, c('ink'))
    cv.rect(5, 9, 7, 16, c('cream_l'))                 # the three folded panels
    cv.rect(20, 9, 7, 16, c('cream_m'))
    for fx in (12, 19):
        cv.vline(fx, 9, 16, c('cream_d'))
    for y0, x0, w in ((13, 5, 22), (20, 5, 22)):       # roads across
        cv.hline(x0, y0, w, c('teal_l'))
    cv.vline(9, 9, 16, c('teal_l'))
    cv.vline(24, 9, 16, c('teal_l'))

    # a proper teardrop pin: a round head tapering to a point. Drawn row by
    # row because the circle primitive degenerates into a diamond at r < 4.
    px0, py0 = 18, 11
    for j, (off, wid) in enumerate(((2, 5), (1, 7), (0, 9), (0, 9),
                                    (0, 9), (1, 7), (2, 5), (3, 3), (4, 1))):
        cv.hline(px0 + off - 4, py0 + j, wid, c('red'))
    cv.hline(px0 - 2, py0, 5, c('red_d'))
    cv.hline(px0 - 3, py0 + 1, 2, c('red_d'))
    cv.rect(px0 - 1, py0 + 2, 3, 3, c('cream_l'))      # the hole in the head
    cv.px(px0, py0 + 3, c('cream'))
    cv.rect(px0 - 2, py0 + 10, 5, 2, c('ink', 110))    # its shadow on the map
    return cv


def app_archive():
    """A filing cabinet with a drawer out. It is a records system."""
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'wood_dd', 'wood_d', 'wood_l')
    cv.rect(6, 5, 20, 23, c('cream_d'))
    cv.frame(6, 5, 20, 23, c('ink'))
    for j in range(3):
        dy = 6 + j * 8
        cv.rect(7, dy, 18, 6, c('cream_m'))
        cv.frame(7, dy, 18, 6, c('wood_dd'))
        cv.rect(14, dy + 2, 4, 2, c('gold'))
    # the middle drawer pulled out, with a folder standing in it
    cv.rect(4, 14, 22, 7, c('cream'))
    cv.frame(4, 14, 22, 7, c('ink'))
    cv.rect(12, 16, 4, 2, c('gold'))
    cv.rect(8, 11, 11, 4, c('amber'))
    cv.hline(8, 11, 11, c('amber_l'))
    cv.frame(8, 11, 11, 4, c('wood_dd'))
    return cv


def app_deeplearning():
    """Three layers of nodes, wired up. The standard picture of a net."""
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'purple', 'plum', 'amber_l')
    layers = [(7, (8, 16, 24)), (16, (11, 21)), (25, (8, 16, 24))]
    for i in range(len(layers) - 1):
        for y0 in layers[i][1]:
            for y1 in layers[i + 1][1]:
                cv.line(layers[i][0], y0, layers[i + 1][0], y1, c('purple'))
    # Nodes as 4x4 tiles with the corners taken off. cv.circle at r=2 draws a
    # plus sign, not a dot — at this size the primitive is the wrong tool.
    for lx, ys in layers:
        for y0 in ys:
            cv.rect(lx - 2, y0 - 2, 4, 4, c('amber'))
            for ox, oy in ((-2, -2), (1, -2), (-2, 1), (1, 1)):
                cv.px(lx + ox, y0 + oy, c('wood_dd'))
            cv.px(lx - 1, y0 - 1, c('amber_l'))
    return cv


def app_azure():
    """Containers stacked under a cloud."""
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'blue_d', 'blue', 'teal_ll')
    # a cloud with a flat underside — three humps over one bar, which is what
    # makes a blob read as a cloud rather than as a spill
    for x0, w0, y0 in ((8, 6, 8), (14, 8, 6), (21, 5, 9)):
        cv.rect(x0, y0, w0, 14 - y0, c('cream_l'))
        cv.hline(x0 + 1, y0, w0 - 2, c('white'))
        cv.px(x0, y0, c('cream'))
        cv.px(x0 + w0 - 1, y0, c('cream'))
    cv.rect(7, 11, 20, 4, c('cream_l'))
    cv.hline(7, 14, 20, c('cream_d'))
    cv.px(7, 11, c('cream'))
    cv.px(26, 11, c('cream'))
    for j, (bx, bw) in enumerate(((6, 8), (15, 8), (10, 9))):
        by = 17 + j * 4
        cv.rect(bx, by, bw, 4, c('amber'))
        cv.hline(bx, by, bw, c('amber_l'))
        cv.frame(bx, by, bw, 4, c('wood_dd'))
        cv.vline(bx + bw // 2, by + 1, 2, c('amber_d'))
    return cv


def app_portfolio():
    """
    This room, as an icon. No longer on the desktop — the projects are the
    seven things built for other people — but kept because it costs nothing
    and the room is the obvious thing to add back.
    """
    cv = Canvas(APP_SIZE, APP_SIZE)
    _plate(cv, 'grn_dd', 'grn_d', 'grn_l')
    cv.rect(4, 22, 24, 3, c('wood'))
    cv.hline(4, 22, 24, c('wood_ll'))
    cv.hline(4, 24, 24, c('wood_dd'))
    for i, (bx, bw, bh, col, dk) in enumerate((
            (5, 3, 12, 'red', 'red_d'), (9, 3, 15, 'blue', 'blue_d'),
            (17, 4, 13, 'amber', 'amber_d'), (22, 3, 16, 'plum', 'purple'),
            (26, 2, 11, 'teal_l', 'teal_dd'))):
        cv.rect(bx, 22 - bh, bw, bh, c(col))
        cv.vline(bx, 22 - bh, bh, c(dk))
        cv.hline(bx, 22 - bh, bw, c(dk))
    # the green one, standing proud in the middle
    cv.rect(13, 4, 4, 18, c('grn'))
    cv.vline(13, 4, 18, c('grn_ll'))
    cv.vline(16, 4, 18, c('grn_dd'))
    cv.hline(13, 4, 4, c('grn_dd'))
    for gy in (7, 12, 19):
        cv.hline(13, gy, 4, c('gold'))
    return cv


APPS = [
    ('rabt',        app_rabt),
    ('qaemati',     app_qaemati),
    ('arcade',      app_arcade),
    ('techzaar',    app_techzaar),
    ('archive',     app_archive),
    ('deeplearning', app_deeplearning),
    ('azure',       app_azure),
]


# ---------------------------------------------------------------------------
# Icons — one 16x16 cell each, laid out in a 8-column sheet
# ---------------------------------------------------------------------------

def icon_sheet():
    names = ['code', 'palette', 'cloud', 'brain', 'bug', 'cap', 'mail',
             'phone', 'pin', 'github', 'linkedin', 'star', 'trophy', 'book',
             'gamepad', 'terminal']
    cols, cell = 8, 16
    rows = (len(names) + cols - 1) // cols
    cv = Canvas(cols * cell, rows * cell)

    def at(i):
        return (i % cols) * cell, (i // cols) * cell

    ink = c('ink')

    # code </>
    x, y = at(0)
    # chevrons need a gap in the middle or they merge into an X
    for k in range(3):
        cv.px(x + 4 - k, y + 8 - k, c('teal_ll')); cv.px(x + 4 - k, y + 8 + k, c('teal_ll'))
        cv.px(x + 5 - k, y + 8 - k, c('teal_ll')); cv.px(x + 5 - k, y + 8 + k, c('teal_ll'))
        cv.px(x + 11 + k, y + 8 - k, c('teal_ll')); cv.px(x + 11 + k, y + 8 + k, c('teal_ll'))
        cv.px(x + 10 + k, y + 8 - k, c('teal_ll')); cv.px(x + 10 + k, y + 8 + k, c('teal_ll'))
    cv.line(x + 9, y + 3, x + 7, y + 13, c('amber'))

    # palette
    x, y = at(1)
    cv.circle(x + 8, y + 8, 6, c('cream_m'))
    cv.circle(x + 8, y + 8, 6, ink, fill=False)
    cv.circle(x + 11, y + 9, 2, c('cream'))
    for (dx, dy, col) in ((-3, -2, 'red'), (0, -4, 'blue'), (3, -2, 'gold'), (-4, 2, 'grn')):
        cv.px(x + 8 + dx, y + 8 + dy, c(col))
        cv.px(x + 8 + dx + 1, y + 8 + dy, c(col))

    # cloud
    x, y = at(2)
    cv.circle(x + 6, y + 9, 3, c('teal_ll')); cv.circle(x + 10, y + 9, 4, c('teal_ll'))
    cv.rect(x + 4, y + 9, 9, 3, c('teal_ll'))
    cv.hline(x + 4, y + 12, 9, ink)

    # brain
    x, y = at(3)
    cv.circle(x + 8, y + 8, 5, c('plum'))
    cv.circle(x + 8, y + 8, 5, ink, fill=False)
    for k in range(-3, 4, 3):
        cv.vline(x + 8 + k, y + 5, 7, c('red_d'))

    # bug
    x, y = at(4)
    cv.rect(x + 5, y + 5, 6, 8, c('grn_l'))
    cv.frame(x + 5, y + 5, 6, 8, ink)
    cv.hline(x + 2, y + 7, 3, ink); cv.hline(x + 11, y + 7, 3, ink)
    cv.hline(x + 2, y + 11, 3, ink); cv.hline(x + 11, y + 11, 3, ink)
    cv.px(x + 6, y + 3, ink); cv.px(x + 9, y + 3, ink)

    # graduation cap
    x, y = at(5)
    for k in range(6):
        cv.hline(x + 2 + k, y + 5 + k, 12 - 2 * k, c('ink2'))
    cv.hline(x + 1, y + 5, 14, c('blue'))
    cv.hline(x + 2, y + 4, 12, c('blue'))
    cv.vline(x + 13, y + 6, 5, c('gold'))

    # mail
    x, y = at(6)
    cv.rect(x + 2, y + 4, 12, 9, c('cream'))
    cv.frame(x + 2, y + 4, 12, 9, ink)
    cv.line(x + 2, y + 4, x + 8, y + 9, ink)
    cv.line(x + 13, y + 4, x + 8, y + 9, ink)

    # phone
    x, y = at(7)
    cv.rect(x + 5, y + 2, 7, 12, c('ink2'))
    cv.frame(x + 5, y + 2, 7, 12, ink)
    cv.rect(x + 6, y + 4, 5, 7, c('teal_ll'))
    cv.hline(x + 7, y + 12, 3, c('cream_d'))

    # pin
    x, y = at(8)
    cv.circle(x + 8, y + 6, 4, c('red'))
    cv.circle(x + 8, y + 6, 4, ink, fill=False)
    cv.circle(x + 8, y + 6, 1, c('cream_l'))
    cv.line(x + 8, y + 10, x + 8, y + 14, ink)

    # github
    x, y = at(9)
    cv.circle(x + 8, y + 8, 6, c('ink2'))
    cv.circle(x + 8, y + 8, 6, ink, fill=False)
    cv.rect(x + 5, y + 9, 6, 5, c('cream_l'))
    cv.px(x + 6, y + 6, c('cream_l')); cv.px(x + 10, y + 6, c('cream_l'))

    # linkedin
    x, y = at(10)
    cv.rect(x + 2, y + 2, 12, 12, c('blue'))
    cv.frame(x + 2, y + 2, 12, 12, ink)
    cv.rect(x + 4, y + 7, 2, 5, c('cream_l'))
    cv.px(x + 5, y + 5, c('cream_l'))
    cv.rect(x + 8, y + 7, 2, 5, c('cream_l'))
    cv.rect(x + 10, y + 8, 2, 4, c('cream_l'))

    # star
    x, y = at(11)
    for j, wdt in enumerate((1, 3, 5, 11, 9, 7, 9)):
        cv.rect(x + 8 - wdt // 2, y + 2 + j, wdt, 1, c('gold'))
    cv.px(x + 6, y + 10, c('gold')); cv.px(x + 10, y + 10, c('gold'))
    cv.px(x + 5, y + 11, c('gold')); cv.px(x + 11, y + 11, c('gold'))

    # trophy
    x, y = at(12)
    cv.rect(x + 4, y + 3, 8, 6, c('gold'))
    cv.rect(x + 6, y + 9, 4, 3, c('amber_d'))
    cv.rect(x + 3, y + 12, 10, 2, c('gold'))
    cv.px(x + 3, y + 4, c('gold')); cv.px(x + 12, y + 4, c('gold'))
    cv.hline(x + 5, y + 4, 3, c('amber_l'))

    # book
    x, y = at(13)
    cv.rect(x + 3, y + 3, 10, 11, c('grn'))
    cv.frame(x + 3, y + 3, 10, 11, ink)
    cv.vline(x + 5, y + 4, 9, c('grn_dd'))
    cv.hline(x + 7, y + 6, 4, c('gold'))
    cv.hline(x + 7, y + 9, 4, c('gold'))

    # gamepad
    x, y = at(14)
    cv.rect(x + 2, y + 6, 12, 6, c('ink2'))
    cv.frame(x + 2, y + 6, 12, 6, ink)
    cv.px(x + 5, y + 8, c('cream_l')); cv.hline(x + 4, y + 9, 3, c('cream_l'))
    cv.px(x + 5, y + 10, c('cream_l'))
    cv.px(x + 11, y + 8, c('red')); cv.px(x + 10, y + 10, c('teal_ll'))

    # terminal
    x, y = at(15)
    cv.rect(x + 2, y + 3, 12, 10, c('ink'))
    cv.frame(x + 2, y + 3, 12, 10, c('teal_l'))
    cv.line(x + 4, y + 6, x + 6, y + 8, c('grn_l'))
    cv.line(x + 6, y + 8, x + 4, y + 10, c('grn_l'))
    cv.hline(x + 8, y + 10, 4, c('grn_l'))

    return cv, names


# ---------------------------------------------------------------------------
# Avatar — a placeholder portrait until a real photo is supplied
# ---------------------------------------------------------------------------

def avatar(size=72):
    cv = Canvas(size, size)
    skin = c('cream_m')
    skin_l = c('cream')
    skin_d = c('cream_d')
    hair = c('ink2')
    hair_l = c('shadow')
    ink = c('ink')

    cv.rect(0, 0, size, size, c('teal_d'))
    cv.dither(0, 0, size, size, c('teal'), 3)
    cv.glow(size // 2, 30, 30, c('teal_l', 40), steps=3)

    # shoulders / hoodie
    cv.rect(10, 54, 52, 18, c('red_d'))
    cv.rect(12, 56, 48, 16, c('red'))
    cv.hline(12, 56, 48, c('plum'))
    cv.rect(28, 54, 16, 6, skin_d)   # neck

    # head
    cv.rect(20, 16, 32, 38, skin)
    cv.frame(20, 16, 32, 38, ink)
    cv.rect(22, 18, 12, 14, skin_l)
    cv.rect(44, 30, 8, 20, skin_d)

    # hair
    cv.rect(18, 10, 36, 14, hair)
    cv.frame(18, 10, 36, 14, ink)
    cv.rect(18, 22, 5, 16, hair)
    cv.rect(49, 22, 5, 16, hair)
    cv.hline(21, 11, 18, hair_l)
    for i in range(20, 52, 4):
        cv.vline(i, 12, 8, hair_l)

    # brows, eyes
    cv.hline(25, 30, 7, ink)
    cv.hline(40, 30, 7, ink)
    cv.rect(26, 33, 5, 4, c('white'))
    cv.rect(41, 33, 5, 4, c('white'))
    cv.rect(28, 34, 2, 3, c('wood_dd'))
    cv.rect(43, 34, 2, 3, c('wood_dd'))
    cv.px(28, 34, ink)
    cv.px(43, 34, ink)

    # nose, mouth
    cv.vline(35, 38, 5, skin_d)
    cv.hline(34, 43, 3, skin_d)
    cv.hline(31, 47, 9, c('red_d'))
    cv.hline(32, 48, 7, c('plum'))

    # a hint of beard shadow
    cv.dither(24, 44, 24, 8, skin_d, 3)

    # frame
    cv.frame(0, 0, size, size, ink)
    cv.frame(1, 1, size - 2, size - 2, c('gold'))
    cv.frame(2, 2, size - 4, size - 4, ink)
    return cv


# ---------------------------------------------------------------------------

def build():
    os.makedirs(OUT, exist_ok=True)
    made = []

    def save(cv, name, preview_scale=4):
        p = os.path.join(OUT, name)
        cv.save(p)
        made.append((name, cv.w, cv.h))
        return cv

    save(book_cover(True), 'book_cover_front.png')
    save(book_cover(False), 'book_cover_back.png')
    save(book_cover(True, 'blue'), 'book_cover_front_blue.png')
    save(book_spine_sprite('blue'), 'book_spine_blue.png')
    save(book_open_inner('blue'), 'book_endpaper_blue.png')
    save(cert_placeholder(), 'cert_placeholder.png')
    save(book_pageblock(), 'book_pages.png')
    save(book_open_inner(), 'book_endpaper.png')
    save(book_spine_sprite(), 'book_spine.png')
    save(hand(), 'hand.png')
    save(bug_sprite(), 'bug.png')
    save(parchment(), 'tex_parchment.png')
    save(leather_tile(), 'tex_leather.png')
    save(leather_tile(sk='blue'), 'tex_leather_blue.png')
    save(wood_tile(), 'tex_wood.png')
    # avatar.png is NOT written here. tools/build_avatar.py owns it, and it is
    # built from the real photograph; when both scripts wrote it, whichever ran
    # last won and running the sprite build silently reverted the portrait to
    # the old drawn placeholder.
    save(lamp_cone(), 'lamp_cone.png')

    for slug, fn in APPS:
        save(fn(), 'app_' + slug + '.png')

    sheet, names = icon_sheet()
    save(sheet, 'icons.png')

    # contact sheet so the whole set can be eyeballed in one go
    pad = 8
    items = [(n, Image.open(os.path.join(OUT, n))) for n, _, _ in made]
    cw = sum(im.width for _, im in items) + pad * (len(items) + 1)
    ch = max(im.height for _, im in items) + pad * 2
    sheet_img = Image.new('RGBA', (cw, ch), (40, 34, 48, 255))
    x = pad
    for _, im in items:
        sheet_img.alpha_composite(im, (x, pad))
        x += im.width + pad
    sheet_img.resize((cw * 3, ch * 3), Image.NEAREST).save(
        os.path.join(OUT, '_preview_sprites@3x.png'))

    for n, w, h in made:
        print('  %-24s %3d x %3d' % (n, w, h))
    print('icons:', ', '.join(names))


if __name__ == '__main__':
    build()
