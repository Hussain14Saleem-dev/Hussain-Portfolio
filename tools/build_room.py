"""
Draws the room the visitor lands in: a bookcase up top, a desk below.

The world is 480x560. The camera shows a 480x270 window of it — the top of the
world for the bookcase scene, the bottom for the desk scene — so the drop from
shelf to desk is a real camera move through one continuous room, not a cut
between two pictures.
"""

import os
import sys
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxlib import Canvas, c, PAL, TRANSPARENT, wood_panel, book_spine, \
    fill_shelf_row, vine, BOOK_COLORS  # noqa: E402

W, H = 480, 560
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'assets', 'px')

# Fixed seed: the room must be identical on every rebuild, or the JS sprite
# offsets that point at the green book would drift.
rng = random.Random(20260808)


def wall(cv):
    cv.rect(0, 0, W, 472, c('teal_d'))

    # wallpaper: a wide vertical stripe one shade up. Kept faint on purpose —
    # at full contrast it reads as curtains rather than a wall.
    for x in range(0, W, 26):
        cv.dither(x, 0, 13, 472, c('teal'), 2)
        cv.dither(x + 13, 0, 13, 472, c('teal_dd'), 3)

    cv.grain(0, 0, W, 472, c('teal_dd'), rng, 0.03)

    # corner darkening so the room has depth instead of reading flat
    for i in range(70):
        a = int(120 * (1 - i / 70))
        cv.vline(i, 0, 472, c('teal_dd', a))
        cv.vline(W - 1 - i, 0, 472, c('teal_dd', a))
    for j in range(46):
        a = int(110 * (1 - j / 46))
        cv.hline(0, j, W, c('teal_dd', a))

    # picture rail + baseboard
    cv.rect(0, 452, W, 4, c('wood_d'))
    cv.hline(0, 452, W, c('wood_l'))
    cv.rect(0, 456, W, 16, c('wood_dd'))
    cv.hline(0, 456, W, c('wood_d'))
    cv.grain(0, 457, W, 14, c('ink2'), rng, 0.05)


def floor(cv):
    """
    Boards running away from the viewer. One wood tone with seams rather than
    alternating bands — banding at this scale reads as a staircase.
    """
    cv.rect(0, 470, W, H - 470, c('wood_dd'))
    cv.grain(0, 470, W, H - 470, c('wood_d'), rng, 0.07)

    # Long boards running left to right. Butt joints are rare and staggered —
    # a regular grid of them is what made the first attempt look like brick.
    y = 470
    gap = 8
    row = 0
    while y < H:
        cv.hline(0, y, W, c('ink', 120))          # seam
        cv.hline(0, y + 1, W, c('wood_d', 90))    # board catching the light
        cv.grain(0, y + 2, W, gap - 2, c('wood', 60), rng, 0.035)
        if row % 2 == 0:
            jx = (row * 151) % W
            cv.vline(jx, y + 1, gap - 1, c('ink', 110))
        y += gap
        gap += 3
        row += 1

    # the far end of the floor falls into shadow
    for j in range(470, 512):
        a = int(120 * (1 - (j - 470) / 42))
        cv.hline(0, j, W, c('ink', a))

    # warm pool thrown by the desk lamp
    for j in range(470, H):
        t = (j - 470) / (H - 470)
        a = int(26 * (1 - t))
        if a > 0:
            cv.hline(120, j, 200, c('amber', a))


def rug(cv):
    x, y, w, h = 120, 484, 246, 58
    cv.rect(x, y, w, h, c('red_d'))
    cv.frame(x, y, w, h, c('plum'))
    cv.rect(x + 6, y + 6, w - 12, h - 12, c('red'))
    cv.frame(x + 6, y + 6, w - 12, h - 12, c('gold'))
    cv.rect(x + 14, y + 14, w - 28, h - 28, c('red_d'))
    # a simple woven motif
    for i in range(x + 20, x + w - 20, 18):
        cv.rect(i, y + 20, 8, 4, c('gold'))
        cv.rect(i + 2, y + h - 24, 4, 4, c('plum'))
    cv.grain(x, y, w, h, c('ink2'), rng, 0.05)
    # fringe
    for i in range(x, x + w, 3):
        cv.vline(i, y + h, 2, c('cream_d'))


def bookcase(cv):
    bx, by, bw, bh = 44, 14, 392, 286
    ex, ey = bx + bw, by + bh
    t = 7  # frame thickness

    # back panel, in shadow
    cv.rect(bx, by, bw, bh, c('wood_dd'))
    cv.rect(bx + t, by + t, bw - 2 * t, bh - 2 * t, c('ink2'))
    cv.grain(bx + t, by + t, bw - 2 * t, bh - 2 * t, c('shadow'), rng, 0.06)

    inner_x0 = bx + t
    inner_x1 = ex - t

    # -- shelves -----------------------------------------------------------
    # row 1: base 104, row 2 (the big one): base 210, row 3: base 288

    # Two books matter on this shelf: the portfolio and the certificates.
    # Named gx/cx, NOT bx — bx is the bookcase's own left edge, four lines up,
    # and reusing it here redrew the case's left upright on top of the
    # certificates slot: a full-height wooden post straight through the book.
    gx, gw = 220, 22     # portfolio
    cx, cw = 344, 22     # certificates

    # A column of clear air around each hero book, on every row. Brown spines
    # read as shelf woodwork and near-black ones read as a hole, so a run of
    # either directly above, below or beside a hero book makes it look wedged
    # against the frame rather than standing in a row of books. Inside these
    # bands those two colourways are swapped out.
    clear = [(gx - 14, gw + 28), (cx - 14, cw + 28)]

    fill_shelf_row(cv, inner_x0 + 2, inner_x1 - 2, 104, 68, rng,
                   keep_clear=clear)
    fill_shelf_row(cv, inner_x0 + 2, inner_x1 - 2, 210, 88, rng,
                   skips=[(gx, gw), (cx, cw)], keep_clear=clear)
    fill_shelf_row(cv, inner_x0 + 2, inner_x1 - 2, 288, 66, rng,
                   keep_clear=clear)

    # shelf boards
    for sy in (104, 210):
        cv.rect(inner_x0, sy, inner_x1 - inner_x0, 6, c('wood'))
        cv.hline(inner_x0, sy, inner_x1 - inner_x0, c('wood_ll'))
        cv.hline(inner_x0, sy + 5, inner_x1 - inner_x0, c('wood_dd'))
        cv.grain(inner_x0, sy + 1, inner_x1 - inner_x0, 4, c('wood_d'), rng, 0.06)

    # -- outer frame -------------------------------------------------------
    wood_panel(cv, bx, by, bw, t, rng)                      # top
    wood_panel(cv, bx, ey - t - 5, bw, t + 5, rng)          # bottom
    wood_panel(cv, bx, by, t, bh, rng)                      # left
    wood_panel(cv, ex - t, by, t, bh, rng)                  # right
    cv.frame(bx, by, bw, bh, c('wood_dd'))

    # crown moulding
    cv.rect(bx - 6, by - 8, bw + 12, 8, c('wood_d'))
    cv.hline(bx - 6, by - 8, bw + 12, c('wood_l'))
    cv.hline(bx - 6, by - 1, bw + 12, c('wood_dd'))
    cv.rect(bx - 3, by - 5, bw + 6, 2, c('wood_ll'))

    # contact shadow under the whole unit
    cv.rect(bx, ey, bw, 3, c('ink', 90))

    return (gx, gw), (cx, cw)


def book_slot(cv, gx, gw):
    """
    The empty slot a book sits in. The books themselves are separate sprites so
    JavaScript can slide them out — this just draws the darkness behind them,
    which is only ever seen once a book has left the shelf.

    Exactly the book's footprint, nothing wider. It used to be drawn a pixel
    proud on each side with a shadow cast onto the neighbours, which meant that
    with the book in place all you saw was a black rule boxing it in.
    """
    cv.rect(gx, 210 - 96, gw, 96, c('ink2'))
    cv.vline(gx, 210 - 96, 96, c('ink'))          # inside of the recess, left
    cv.hline(gx, 210 - 96, gw, c('ink'))          # and its ceiling


def plant_on_top(cv):
    """Trailing plant sitting on the bookcase, vines down the left side."""
    px, py = 74, -2
    cv.rect(px, py, 26, 12, c('wood_l'))
    cv.rect(px + 1, py + 1, 24, 10, c('orange'))
    cv.hline(px + 1, py + 1, 24, c('amber'))
    cv.rect(px + 2, py + 10, 22, 3, c('wood_dd'))
    for i, vx in enumerate((px + 3, px + 9, px + 17, px + 23)):
        vine(cv, vx, py + 11, rng.randint(26, 62), rng)

    # a second pot on the right, smaller
    qx = 372
    cv.rect(qx, 0, 20, 10, c('red_d'))
    cv.rect(qx + 1, 1, 18, 8, c('red'))
    for vx in (qx + 3, qx + 11, qx + 16):
        vine(cv, vx, 9, rng.randint(18, 40), rng)


def string_lights(cv):
    """A sagging wire of bulbs across the wall above the desk."""
    y0 = 316
    pts = []
    for x in range(24, W - 20):
        t = (x - 24) / (W - 44)
        # three sags
        import math
        sag = abs(math.sin(t * 3.14159 * 3)) * 12
        pts.append((x, int(y0 + sag)))
    for x, y in pts:
        cv.px(x, y, c('ink'))
    for i in range(0, len(pts), 34):
        x, y = pts[i]
        cv.rect(x - 1, y + 1, 3, 2, c('wood_d'))
        cv.circle(x, y + 5, 2, c('amber'))
        cv.px(x, y + 4, c('amber_l'))
        cv.glow(x, y + 5, 9, c('amber', 16), steps=3)


def framed_picture(cv):
    # far left, clear of the desk lamp
    x, y, w, h = 12, 344, 46, 38
    cv.rect(x - 2, y - 2, w + 4, h + 4, c('wood_d'))
    cv.frame(x - 2, y - 2, w + 4, h + 4, c('wood_dd'))
    cv.hline(x - 2, y - 2, w + 4, c('wood_l'))
    cv.rect(x, y, w, h, c('teal_dd'))
    # a tiny landscape inside the frame
    cv.rect(x, y, w, 22, c('blue_d'))
    cv.circle(x + 40, y + 9, 5, c('amber_l'))
    for i in range(3):
        cv.line(x + 4 + i * 16, y + 22, x + 12 + i * 16, y + 10, c('teal_d'))
        cv.line(x + 12 + i * 16, y + 10, x + 20 + i * 16, y + 22, c('teal_d'))
    cv.rect(x, y + 22, w, h - 22, c('teal_d'))
    cv.dither(x, y + 22, w, 6, c('teal_l'), 2)
    cv.hline(x, y + h - 1, w, c('teal_dd'))


def wall_shelf(cv):
    # Moved off the right-hand wall to make room for the monitor. The right
    # side of the room is now the computer's, the left the lamp's.
    x, y, w = 150, 352, 84
    cv.rect(x, y, w, 5, c('wood'))
    cv.hline(x, y, w, c('wood_ll'))
    cv.hline(x, y + 4, w, c('wood_dd'))
    # brackets
    cv.line(x + 6, y + 5, x + 12, y + 12, c('wood_dd'))
    cv.line(x + w - 7, y + 5, x + w - 13, y + 12, c('wood_dd'))

    # small stack of books
    sy = y
    for col in (('red_d', 'red'), ('blue_d', 'blue'), ('grn_dd', 'grn_d')):
        sy -= 5
        cv.rect(x + 6, sy, 22, 5, c(col[1]))
        cv.hline(x + 6, sy, 22, c(col[0]))
        cv.vline(x + 26, sy, 5, c('cream_m'))

    # a little trophy
    tx = x + 44
    cv.rect(tx, y - 4, 10, 4, c('gold'))
    cv.rect(tx + 3, y - 8, 4, 4, c('amber'))
    cv.rect(tx + 1, y - 14, 8, 6, c('gold'))
    cv.px(tx, y - 12, c('gold'))
    cv.px(tx + 9, y - 12, c('gold'))
    cv.hline(tx + 2, y - 13, 4, c('amber_l'))

    # a mug with steam
    mx = x + 64
    cv.rect(mx, y - 9, 11, 9, c('cream'))
    cv.rect(mx + 1, y - 8, 9, 7, c('cream_l'))
    cv.rect(mx + 1, y - 8, 9, 2, c('teal_l'))
    cv.px(mx + 11, y - 7, c('cream'))
    cv.px(mx + 12, y - 6, c('cream'))
    cv.px(mx + 11, y - 5, c('cream'))


def desk(cv):
    x, y, w = 70, 396, 340

    # top
    cv.rect(x, y, w, 13, c('wood_l'))
    cv.hline(x, y, w, c('wood_ll'))
    cv.grain(x, y + 1, w, 11, c('wood'), rng, 0.06)
    cv.hline(x, y + 12, w, c('wood_dd'))

    # front edge / apron
    cv.rect(x + 6, y + 13, w - 12, 9, c('wood'))
    cv.hline(x + 6, y + 13, w - 12, c('wood_l'))
    cv.hline(x + 6, y + 21, w - 12, c('wood_dd'))

    # a drawer with a brass pull
    dx = x + 190
    cv.rect(dx, y + 15, 74, 6, c('wood_d'))
    cv.frame(dx, y + 15, 74, 6, c('wood_dd'))
    cv.rect(dx + 32, y + 17, 10, 2, c('gold'))

    # legs
    for lx in (x + 12, x + w - 24):
        cv.rect(lx, y + 22, 12, 52, c('wood_d'))
        cv.vline(lx, y + 22, 52, c('wood'))
        cv.vline(lx + 11, y + 22, 52, c('wood_dd'))
        cv.rect(lx - 1, y + 72, 14, 4, c('wood_dd'))

    # shadow the desk casts on the floor
    cv.rect(x + 4, 470, w - 8, 6, c('ink', 70))


def desk_lamp(cv):
    """A compact bank-style lamp. Kept short so it clears the wall art."""
    bx, by = 92, 396

    # base
    cv.rect(bx, by - 4, 20, 4, c('ink2'))
    cv.rect(bx + 2, by - 6, 16, 3, c('shadow'))
    cv.hline(bx + 2, by - 6, 16, c('wood_d'))

    # upright, then a short angled arm
    cv.rect(bx + 8, by - 30, 3, 25, c('ink2'))
    cv.vline(bx + 8, by - 30, 25, c('shadow'))
    cv.line(bx + 9, by - 30, bx + 22, by - 38, c('ink2'))
    cv.line(bx + 9, by - 29, bx + 22, by - 37, c('shadow'))

    # shade, opening down-right over the desk
    sx, sy = bx + 18, by - 46
    cv.rect(sx, sy, 18, 4, c('red_d'))
    cv.rect(sx - 3, sy + 4, 24, 4, c('red'))
    cv.rect(sx - 6, sy + 8, 30, 4, c('red_d'))
    cv.hline(sx, sy, 18, c('plum'))
    cv.hline(sx - 6, sy + 11, 30, c('amber_l'))

    # A pin the cord hangs off, on the right of the shade.
    cv.rect(sx + 11, sy + 11, 2, 2, c('gold'))

    # No light baked in here any more. The lamp has a pull cord now and has to
    # be able to be off, so the cone is a separate sprite the page can hide —
    # see lamp_cone() in build_sprites.py and .lamp in style.css.
    #
    # LAMP is the shade's mouth, in world pixels: where the cone starts, how
    # wide it starts, and where the cord hangs from. main.js and the CSS both
    # place their elements from these.
    return dict(mouth_x=sx - 6, mouth_w=30, mouth_y=sy + 12,
                cord_x=sx + 11, cord_y=sy + 13)


# The screen, in world pixels. Everything else about the monitor is drawn
# relative to these four numbers, and main.js reads the same values to know
# where to put the click target and where to push the camera. Keep them here.
PC = dict(case_x=310, case_y=316, case_w=96, case_h=64,
          scr_x=316, scr_y=322, scr_w=84, scr_h=48)


def monitor(cv):
    """
    A chunky beige CRT — the projects live in it.

    Sized so its screen is close to the camera's 480x270 aspect: pushing in
    until the glass fills the frame is the same handover the book does, and it
    only reads as "the screen became the page" if the shapes agree.
    """
    y = 396
    cx, cy = PC['case_x'], PC['case_y']
    cw, ch = PC['case_w'], PC['case_h']
    sx, sy = PC['scr_x'], PC['scr_y']
    sw, sh = PC['scr_w'], PC['scr_h']

    # Neck and foot, drawn first so the keyboard sits in front of them. The
    # foot reaches the desk line: an earlier version stopped 8px short and put
    # the keyboard 2px below that, which left a strip of wall showing between
    # them and the whole monitor hovering above the desk.
    cv.rect(cx + 34, cy + ch, 28, 6, c('cream_d'))          # neck
    cv.vline(cx + 34, cy + ch, 6, c('cream_m'))
    cv.vline(cx + 61, cy + ch, 6, c('wood_l'))
    foot_y = cy + ch + 6
    cv.rect(cx + 22, foot_y, 52, y - foot_y, c('cream_m'))  # foot, down to y
    cv.hline(cx + 22, foot_y, 52, c('cream_l'))
    cv.vline(cx + 22, foot_y, y - foot_y, c('cream_l'))
    cv.vline(cx + 73, foot_y, y - foot_y, c('wood_l'))

    # the case: lit along the top, falling away down the right
    cv.rect(cx, cy, cw, ch, c('cream_d'))
    cv.hline(cx + 1, cy + 1, cw - 2, c('cream_m'))
    cv.hline(cx + 2, cy + 2, cw - 4, c('cream_l'))
    cv.vline(cx + 1, cy + 1, ch - 2, c('cream_m'))
    cv.rect(cx + cw - 3, cy + 2, 2, ch - 4, c('wood_l'))
    cv.rect(cx + 2, cy + ch - 3, cw - 4, 2, c('wood_l'))
    cv.frame(cx, cy, cw, ch, c('wood_dd'))
    cv.grain(cx + 2, cy + 2, cw - 4, ch - 4, c('cream_m'), rng, 0.03)

    # the glass, recessed: dark rim above and left, a highlight below and right
    cv.rect(sx - 2, sy - 2, sw + 4, sh + 4, c('wood_dd'))
    cv.hline(sx - 2, sy + sh + 1, sw + 4, c('cream_m'))
    cv.vline(sx + sw + 1, sy - 2, sh + 4, c('cream_m'))
    cv.rect(sx, sy, sw, sh, c('teal_dd'))
    cv.frame(sx, sy, sw, sh, c('ink'))

    # what is on it at rest: a directory of projects, waiting to be opened
    for i in range(3):
        for j in range(2):
            ix, iy = sx + 9 + i * 25, sy + 9 + j * 18
            cv.rect(ix, iy, 11, 9, c('teal_l'))
            cv.hline(ix, iy, 11, c('teal_ll'))
            cv.rect(ix + 2, iy + 2, 7, 2, c('teal_dd'))
            cv.hline(ix, iy + 11, 11, c('teal'))
            cv.hline(ix + 1, iy + 13, 9, c('teal'))
    # a caret blinking in the corner, so it reads as awake
    cv.rect(sx + sw - 6, sy + sh - 6, 3, 4, c('grn_l'))

    # scanlines and the bloom off the phosphor
    for j in range(sy + 1, sy + sh - 1, 2):
        cv.hline(sx + 1, j, sw - 2, c('ink', 46))
    cv.glow(sx + sw // 2, sy + sh // 2, 34, c('teal_ll', 9), steps=4)

    # vent slots and a power light on the chin
    for i in range(cx + 8, cx + 40, 3):
        cv.vline(i, cy + ch - 8, 4, c('wood_l'))
    cv.rect(cx + cw - 11, cy + ch - 7, 2, 2, c('grn_l'))
    cv.px(cx + cw - 11, cy + ch - 7, c('grn_ll'))

    # Keyboard, in front of the foot and resting on the desk. Wider than the
    # foot so the foot's shoulders still read either side of it, and flush to
    # the desk line so there is nothing between the two.
    kx, kw = cx + 4, cw - 8
    cv.rect(kx, y - 7, kw, 7, c('cream_d'))
    cv.hline(kx, y - 7, kw, c('cream_l'))
    cv.hline(kx, y - 1, kw, c('wood_dd'))
    cv.vline(kx, y - 7, 7, c('cream_m'))
    cv.vline(kx + kw - 1, y - 7, 7, c('wood_l'))
    for i in range(kx + 3, kx + kw - 3, 4):
        cv.vline(i, y - 5, 3, c('wood_d'))


def desk_clutter(cv):
    y = 396

    # stack of books, left of centre
    sx, sy = 148, y
    for col in (('purple', 'plum'), ('wood_dd', 'wood_d'), ('blue_d', 'blue')):
        sy -= 6
        cv.rect(sx, sy, 34, 6, c(col[1]))
        cv.hline(sx, sy, 34, c(col[0]))
        cv.hline(sx, sy + 5, 34, c(col[0]))
        cv.vline(sx + 32, sy + 1, 4, c('cream_m'))
        sx += 1

    monitor(cv)

    # NOTE: x 188..308 is deliberately left bare. That is where the book lands
    # after the camera drops, and anything drawn there would end up poking out
    # from behind it. The monitor starts at 310 for exactly that reason.

    # loose paper and a pencil, tucked by the lamp
    cv.rect(118, y - 3, 26, 3, c('cream_l'))
    cv.hline(118, y - 3, 26, c('white'))
    cv.rect(114, y - 2, 18, 1, c('amber'))
    cv.px(113, y - 2, c('ink'))


def sleeping_cat(cv):
    """
    A ginger cat asleep on the rug. Drawn big enough to read as a cat at 1x —
    the first version was 26px wide and registered as a smudge.
    """
    x, y = 246, 496
    body = c('orange')
    lit = c('amber')
    dark = c('wood_d')
    edge = c('ink')

    # Curled body as a proper ellipse. The first version was 52x11 and read as
    # a smear; a sleeping cat needs to be round.
    bw, bh = 50, 22
    cxx, cyy = x + bw // 2, y + bh // 2
    for j in range(-bh // 2 - 1, bh // 2 + 2):
        for i in range(-bw // 2 - 1, bw // 2 + 2):
            d = (i * i) / ((bw / 2) ** 2) + (j * j) / ((bh / 2) ** 2)
            if d <= 1.0:
                cv.px(cxx + i, cyy + j, body)
            elif d <= 1.22:
                cv.px(cxx + i, cyy + j, edge)

    # lit along the top, shadowed underneath
    cv.dither(x + 10, y + 3, 30, 4, lit, 2)
    cv.dither(x + 6, y + 15, 38, 4, dark, 2)

    # tabby stripes following the curve of the back
    for i in range(4):
        sx = x + 9 + i * 8
        cv.vline(sx, y + 3 + (i % 2), 5, dark)
        cv.vline(sx + 1, y + 4 + (i % 2), 4, dark)

    # head, tucked to the right
    hx, hy = x + 34, y + 5
    cv.rect(hx, hy, 18, 13, body)
    cv.frame(hx, hy, 18, 13, edge)
    cv.dither(hx + 1, hy + 1, 16, 4, lit, 2)
    # ears
    for ex in (hx + 1, hx + 12):
        cv.px(ex + 2, hy - 3, edge)
        cv.rect(ex, hy - 2, 5, 2, body)
        cv.px(ex + 1, hy - 2, edge)
        cv.px(ex + 2, hy - 1, c('plum'))
    # eyes closed, content
    cv.hline(hx + 3, hy + 6, 4, edge)
    cv.px(hx + 2, hy + 5, edge)
    cv.px(hx + 7, hy + 5, edge)
    cv.hline(hx + 11, hy + 6, 4, edge)
    cv.px(hx + 10, hy + 5, edge)
    cv.px(hx + 15, hy + 5, edge)
    # muzzle
    cv.rect(hx + 7, hy + 8, 4, 2, c('cream_m'))
    cv.px(hx + 8, hy + 8, c('plum'))
    cv.px(hx + 9, hy + 8, c('plum'))
    # whiskers
    cv.hline(hx - 4, hy + 9, 4, c('cream_d'))
    cv.hline(hx + 18, hy + 9, 4, c('cream_d'))

    # tail curled around the front
    for k, (tx, ty) in enumerate(((2, 17), (-4, 18), (-10, 17), (-14, 13),
                                  (-16, 9), (-14, 6))):
        cv.rect(x + tx, y + ty, 4, 3, body)
        cv.px(x + tx, y + ty - 1, edge)
        cv.px(x + tx, y + ty + 3, edge)
        if k > 2:
            cv.px(x + tx + 1, y + ty, lit)
    cv.px(x - 15, y + 5, lit)

    # contact shadow
    cv.rect(x - 12, y + 21, 66, 2, c('ink', 70))


def build():
    os.makedirs(OUT, exist_ok=True)
    cv = Canvas(W, H)

    wall(cv)
    string_lights(cv)
    framed_picture(cv)
    wall_shelf(cv)
    floor(cv)
    rug(cv)
    green, blue = bookcase(cv)
    book_slot(cv, *green)
    book_slot(cv, *blue)
    plant_on_top(cv)
    desk(cv)
    lamp = desk_lamp(cv)
    desk_clutter(cv)
    sleeping_cat(cv)

    path = os.path.join(OUT, 'room.png')
    cv.save(path)
    print('room.png', W, 'x', H, '->', path)
    print('portfolio slot:    x=%d w=%d, base_y=210' % green)
    print('certificates slot: x=%d w=%d, base_y=210' % blue)
    print('lamp: mouth x=%(mouth_x)d w=%(mouth_w)d y=%(mouth_y)d, '
          'cord x=%(cord_x)d y=%(cord_y)d' % lamp)

    # a 2x preview so the art can be eyeballed at a sane size
    cv.img.resize((W * 2, H * 2), Image.NEAREST).save(
        os.path.join(OUT, '_preview_room@2x.png'))


if __name__ == '__main__':
    from PIL import Image
    build()
