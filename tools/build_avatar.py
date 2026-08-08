"""
Turns the real photograph into the pixel portrait on the book's first page.

Not a filter: the photo is reduced to a handful of large pixels first, so each
one is an average of a real region, and only then mapped onto the fixed
palette. Quantising at full resolution and shrinking afterwards produces
speckle — every pixel picks a different palette entry and the face dissolves.
"""

import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pxlib import Canvas, c, PAL  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'images', 'photo.png')
OUT = os.path.join(ROOT, 'assets', 'px', 'avatar.png')

SIZE = 72            # the frame, as the page expects it
INNER = 64           # the portrait inside it
CROP = (0.13, 0.02, 0.90, 0.80)   # head and shoulders, as a fraction of the photo

# The palette minus the greens and reds that have no business in a face: a
# skin ramp out of the creams and woods, hair and coat out of the inks and
# blues, and the wall behind him out of the teals.
# The purples and the lighter teals are deliberately absent. With them in the
# set the mapper reached for them along the edge of the hair, and a face with
# magenta and green speckle in it reads as a compression artefact, not as art.
FACE_SET = ['ink', 'ink2', 'shadow', 'wood_dd', 'wood_d', 'wood', 'wood_l',
            'wood_ll', 'cream_d', 'cream_m', 'cream', 'cream_l', 'white',
            'amber_d', 'amber', 'blue_d', 'blue', 'teal_dd', 'teal_d',
            'blu_dd', 'blu_d', 'blu', 'blu_l']


def nearest(rgb, names):
    r, g, b = rgb
    best, bd = names[0], 1e9
    for n in names:
        pr, pg, pb = PAL[n]
        # weighted towards how the eye actually weights the channels
        d = 2.4 * (pr - r) ** 2 + 4.2 * (pg - g) ** 2 + 1.8 * (pb - b) ** 2
        if d < bd:
            bd, best = d, n
    return best


def build():
    im = Image.open(SRC).convert('RGB')
    w, h = im.size
    box = (int(CROP[0] * w), int(CROP[1] * h), int(CROP[2] * w), int(CROP[3] * h))
    im = im.crop(box)

    # square it off around the face rather than squashing it
    side = min(im.size)
    left = (im.width - side) // 2
    im = im.crop((left, 0, left + side, side))

    # a little more contrast and colour survives the reduction better
    from PIL import ImageEnhance
    im = ImageEnhance.Contrast(im).enhance(1.22)
    im = ImageEnhance.Color(im).enhance(1.15)

    small = im.resize((INNER, INNER), Image.LANCZOS)
    px = small.load()

    cv = Canvas(SIZE, SIZE)
    off = (SIZE - INNER) // 2

    for j in range(INNER):
        for i in range(INNER):
            cv.px(off + i, off + j, c(nearest(px[i, j], FACE_SET)))

    # the same plate the drawn placeholder had, so the page is unchanged
    cv.frame(0, 0, SIZE, SIZE, c('ink'))
    cv.frame(1, 1, SIZE - 2, SIZE - 2, c('gold'))
    cv.frame(2, 2, SIZE - 4, SIZE - 4, c('ink'))

    cv.save(OUT)
    print('avatar.png %dx%d -> %s' % (SIZE, SIZE, OUT))


if __name__ == '__main__':
    build()
