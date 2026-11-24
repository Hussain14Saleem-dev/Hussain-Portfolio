Screenshots for the deck
========================

Drop eight images in this folder, then rebuild:

    node tools/build_deck.js

Any slot without a file shows a dark device screen with the domain on it, so
the deck is always presentable — it just isn't finished.

Filenames (PNG or JPG, either works):

    irshad-desktop.png      irshad-phone.png        irshad.ly
    rabt-desktop.png        rabt-phone.png          rabt.grids.ly
    arcade-desktop.png      arcade-phone.png        gdg-g.vercel.app
    techzaar-desktop.png    techzaar-phone.png      gdg-techzaar.vercel.app

How to take them
----------------

DESKTOP  A normal browser window, roughly 1440 x 900, top of the page. The
         frame crops to 16:10, so anything much taller gets trimmed at the
         bottom — capture the hero, not the whole page.

PHONE    A real narrow viewport, not a desktop page scaled down. In Chrome:
         F12, then the phone icon (Ctrl+Shift+M), pick iPhone 14 Pro or any
         390-wide device, reload, screenshot. The frame crops to 19.5:9.

Trim the browser chrome — address bar, tabs, bookmarks — out of both. The
deck draws its own laptop and phone around the image, so a second set of
browser furniture inside it looks like a screenshot of a screenshot.
