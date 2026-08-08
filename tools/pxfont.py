"""
A 5x7 bitmap font.

Why this exists: any text that lives *inside* the pixel scene has to be baked
into the sprite. If it were DOM text it would be re-rasterised every time the
camera scales, coming out smooth and anti-aliased against art that is
deliberately hard-edged. Text in the reading UI is real HTML — this font is
only for lettering painted onto objects in the world, like the book cover.
"""

GLYPHS = {
    'A': ["  #  ", " # # ", "#   #", "#   #", "#####", "#   #", "#   #"],
    'B': ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    'C': [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    'D': ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    'E': ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    'F': ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    'G': [" ### ", "#   #", "#    ", "#  ##", "#   #", "#   #", " ### "],
    'H': ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    'I': [" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    'J': ["    #", "    #", "    #", "    #", "#   #", "#   #", " ### "],
    'K': ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    'L': ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    'M': ["#   #", "## ##", "# # #", "#   #", "#   #", "#   #", "#   #"],
    'N': ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    'O': [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    'P': ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    'Q': [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    'R': ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    'S': [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    'T': ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    'U': ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    'V': ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    'W': ["#   #", "#   #", "#   #", "#   #", "# # #", "## ##", "#   #"],
    'X': ["#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"],
    'Y': ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    'Z': ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    '0': [" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "],
    '1': ["  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    '2': [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    '3': ["#####", "   # ", "  #  ", "   # ", "    #", "#   #", " ### "],
    '4': ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    '5': ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    '6': ["  ## ", " #   ", "#    ", "#### ", "#   #", "#   #", " ### "],
    '7': ["#####", "    #", "   # ", "  #  ", " #   ", " #   ", " #   "],
    '8': [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    '9': [" ### ", "#   #", "#   #", " ####", "    #", "   # ", " ##  "],
    '.': ["     ", "     ", "     ", "     ", "     ", "     ", "  #  "],
    ',': ["     ", "     ", "     ", "     ", "     ", "  #  ", " #   "],
    '-': ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    "'": ["  #  ", "  #  ", "     ", "     ", "     ", "     ", "     "],
    '&': [" ##  ", "#  # ", "#  # ", " ##  ", "#  ##", "#  # ", " ## #"],
    '/': ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "],
    '!': ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
    '?': [" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "],
    ':': ["     ", "  #  ", "     ", "     ", "     ", "  #  ", "     "],
    '+': ["     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "],
    '(': ["   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "],
    ')': [" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "],
    ' ': ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
}

GW, GH = 5, 7


def text_width(s, spacing=1, scale=1):
    return (len(s) * (GW + spacing) - spacing) * scale


def draw_text(cv, x, y, s, col, spacing=1, scale=1, shadow=None):
    """
    Paint `s` at (x, y). `scale` multiplies each font pixel into a scale x scale
    block, which keeps the grid intact — never resample this.
    """
    s = s.upper()
    cx = x
    for ch in s:
        g = GLYPHS.get(ch)
        if g is None:
            cx += (GW + spacing) * scale
            continue
        for row, bits in enumerate(g):
            for col_i, bit in enumerate(bits):
                if bit != '#':
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        px_ = cx + col_i * scale + sx
                        py_ = y + row * scale + sy
                        if shadow is not None:
                            cv.px(px_ + scale, py_ + scale, shadow)
                        cv.px(px_, py_, col)
        cx += (GW + spacing) * scale
    return cx


def draw_text_centered(cv, cx, y, s, col, spacing=1, scale=1, shadow=None):
    w = text_width(s, spacing, scale)
    return draw_text(cv, cx - w // 2, y, s, col, spacing, scale, shadow)
