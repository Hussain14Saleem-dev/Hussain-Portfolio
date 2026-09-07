# Hussain Alshikhy — Portfolio

A portfolio you read like a book. You land in a pixel-art room and there are two
books worth taking: the green one, lettered **HUSSAIN**, and further along the
same shelf the blue **CERTIFICATES**. Click either one, the camera follows it down to the
desk, the cover swings open, and the pages are inside.

The green book holds the profile, the skills, the experience and the contact
details, and nothing else: the projects live on the computer and the
certificates are the blue book, so neither is duplicated as a page. The
PROJECTS tab quits the book and opens the machine; the CERTS tab swaps volumes.

The two hero slots are the only fixed points on that shelf; everything around
them is generated. Two rules keep them readable. Neither slot may have a brown
or near-black spine beside, above or below it — brown reads as shelf woodwork
and near-black reads as a hole, and either one makes the book look wedged
against the frame rather than standing in a row of books. And the case's own
uprights are drawn from `bx`, so the slot coordinates are named `gx` and `cx`:
reusing `bx` for a slot redraws a full-height wooden post straight through the
book.

Down from the bookcase is the desk, and on it a beige CRT. Click it and the
camera pushes into the glass until the screen is the viewport, a small
operating system boots, and the seven **projects** are icons on its desktop. The four that are deployed
carry an OPEN SITE link, which opens the site **inside the portfolio** in a
pixel-framed browser rather than throwing the visitor out to a new tab. That
browser fills the whole screen of the CRT rather than being a small window on
its desktop. The first version left the site 1050x430, and a site whose hero is
`height: 100vh` has nowhere to go in 430px — you saw a sliver of it and a
scrollbar. It now gets 1312x764: a real viewport, still framed by the monitor,
and the monitor stretches a little while a site is open so the desktop keeps
the proportions it was designed at.

The drawn hand belongs to the room. It hides inside the book, inside the
computer's desktop and over a framed site, and the real pointer takes over —
those layers all sit outside `.stage`, which is the only thing given
`cursor: none`, so leaving the hand on drew it underneath the system arrow:
two cursors, one of them fake.

Over a framed site there is a second reason. `pointermove` does not cross
an origin boundary, so the drawn hand would freeze wherever it entered the
frame while the site drew a second, real cursor underneath it. The
other three say plainly that they are not deployed, because a button that goes
nowhere is worse than no button.

### Why the browser cannot tell you a site is blocked

A page can refuse to be framed with `X-Frame-Options` or a
`Content-Security-Policy: frame-ancestors` header. There is no way to detect
that from the parent page, and this was measured rather than assumed. Framing a
cross-origin page that *allows* it and one that *denies* it produces identical
observations:

| | allowed | `X-Frame-Options: DENY` |
| --- | --- | --- |
| `load` event | fires | fires |
| `contentDocument` | `null` | `null` |
| `contentWindow.location` | throws `SecurityError` | throws `SecurityError` |
| resource-timing `transferSize` | `0` | `0` |

So the browser here does not guess. It shows the frame, and for seven seconds
after it loads it offers a way out — *"nothing there? some sites refuse to be
embedded"* — with NEW TAB permanently on the chrome beside the address. The one
case that *is* detectable is a frame that never reports back at all, and a
fifteen-second watchdog covers that with a proper error panel.

Chrome logs its own `Refused to display ... X-Frame-Options` message when this
happens. That comes from the browser, not from this code, and cannot be
suppressed. Projects
deliberately live only here and not in the book: one home, no duplicated
content to keep in sync, and it gives the machine a reason to exist.

No framework. No bundler. No build step. No runtime dependencies. The
`index.html` in this repo is the file the browser runs.

---

## Running it locally

```bash
npm install     # once — installs live-server only
npm run dev     # http://localhost:5173
```

**Use the dev server rather than double-clicking `index.html`.** Web fonts are
always fetched with CORS, and a `file://` page has a null origin, so opening the
file directly makes the browser refuse the two pixel fonts and fall back to
system type. Everything else works from `file://`; only the fonts don't.

---

## How it's built

Two rendering approaches share one palette, which is the whole trick:

**The stage** — room, bookcase, book, hand. Real pixel art at a real pixel size:
a 480 x 560 world, viewed through a 480 x 270 camera window, scaled up with
`image-rendering: pixelated`. Moving the camera is a single `translate` +
`scale` on one element, so a "camera move" is one composited transform rather
than a redraw.

**The computer** — the same handover, done twice. `shots.screen` puts the
drawn 84x48 screen exactly over the viewport, then `#os` fades in on top of it.
The case is sized so its glass is close to the camera's 480x270 aspect: pushing
in only reads as "the screen became the page" if the two shapes agree. The
numbers live once, in `PC` in `tools/build_room.py`, and are repeated in the
`.pc` rule and in `shots.screen`.

**The reader** — the open book. Pixel *styling* (hard edges, the same 32
colours, pixel fonts) but **real HTML text at real sizes**. Text painted into a
bitmap at 8px cannot carry a CV, cannot be selected, cannot be indexed and
cannot be read aloud by a screen reader. The handover happens at peak zoom,
green cover to green cover, where it isn't visible.

**Page turns bend.** A leaf on a hinge, rotated as one rigid board, reads as a
flipping card rather than paper. So the turning leaf is sliced into ten nested
vertical strips, each rotated slightly relative to its parent, and the chain
approximates a curved surface — the technique behind Fabrizio Bianchi's
well-known CSS bending pen. Angles are computed per frame in JavaScript rather
than as keyframes, because the bend has to vary over the turn: the page is flat
when it starts, bows most in the middle of the arc, and flattens again as it
lands. Each strip's shading ramps to meet its neighbour's so the strips read as
one continuous surface instead of a fan.

The spread at rest is shaded too — paper lifts slightly at the outer edge,
catches the light across the middle and falls into shadow at the binding. Two
flat rectangles either side of a black bar is what made the book look like a
square.

The head and tail of the page block follow that curve as well. They are drawn
as SVG bands whose leaves dive into the gutter, because on a real open book the
edges are not straight — the pages bend down into the binding, and a ruler-flat
line across the top is what a closed ream of paper looks like, not an open
book. Only the outer curve carries an ink rim; the underside fades into the
paper, since outlining the whole band drew a hard line straight across the
page.

### The art

Every sprite is generated pixel by pixel by Python. Nothing was drawn in an
image editor and nothing was generated by a model.

```bash
python tools/build_room.py      # -> assets/px/room.png
python tools/build_sprites.py   # -> the book, hand, textures, icons, avatar
```

| File | What it is |
| --- | --- |
| `tools/pxlib.py` | The brush set — canvas, primitives, dithering, wood, book spines. Also the single source of truth for the 32-colour palette. |
| `tools/pxfont.py` | A 5x7 bitmap font. Text that lives *inside* the scene (the book cover, the spine) has to be baked into the sprite — as DOM text it would re-rasterise smooth every time the camera scaled. |
| `tools/build_room.py` | The room. Fixed RNG seed, because the CSS spine positions point at specific slots in the shelf. |
| `tools/build_avatar.py` | The portrait on the first page, from `assets/images/photo.png`. The photo is reduced to 64 large pixels *first*, so each one averages a real region, and only then mapped onto the palette — quantising at full resolution and shrinking afterwards produces speckle and the face dissolves. The purples and lighter teals are excluded from the mapping: with them available it reached for them along the edge of the hair, and magenta in a face reads as a compression artefact. |
| `tools/build_sprites.py` | Everything that moves, plus the eight 32x32 project icons on the desktop. Each is a plate with a motif: on a screen full of icons a consistent silhouette is what lets you tell them apart, and a motif alone at that size reads as noise. |

The palette in `pxlib.py` and the CSS custom properties in `style.css` are the
same 32 values. If one changes, change both — that shared palette is what makes
separately-authored assets look like one world.

---

## Structure

```
index.html              the stage, 15 spreads across two volumes, and the desktop
assets/docs/            the CV the Download button hands over
assets/
  css/style.css         everything visual, tokens at the top
  js/main.js            camera, scene machine, page turns, sound — no deps
  px/                   generated pixel art (~130 KB)
  fonts/                Silkscreen + Pixelify Sans, self-hosted (60 KB, OFL)
tools/                  the Python that draws assets/px
package.json            local dev server only — GitHub Pages ignores it
```

Total payload is about 280 KB including every sprite and both fonts.

---

## Things to fill in

Search `index.html` for `REPLACE-ME`:

Nothing. The CV is at `assets/docs/Hussain-Alshikhy-CV.docx` and the Download
button serves it directly; the LinkedIn URL is on the contact page. The LinkedIn and portfolio URLs came out of the
hyperlinks in the CV itself.

Nothing in the book is written on the author's behalf. Two sets of lines used
to be: a *"where I have used it"* note under each certificate and an
observation under each project, both inferred rather than supplied. They are
gone. What remains on the certificate pages — *"what it covered"* and the skill
chips — is still descriptive rather than quoted from the CV, and can go the
same way on request.

All ten certificate scans are in `assets/images/`. They are printed on the page
— no frame, no plate, no drop shadow; a picture in a book does not sit above the
paper. The box each one fits into is still a fixed height, because the issuers
use three aspect ratios and left to themselves the scans came out at wildly
different sizes, but the box has no appearance of its own so nothing about it
shows. Nine share one height; NVIDIA's is the only portrait scan and gets its
own, taller, or at a shared height it came out half the width of the rest.

Those images opt out of the global `image-rendering: pixelated`: it is there
for the sprites, and forced onto a photograph of paper it turns the
certificate's own type into rubble.

`assets/px/avatar.png` is now generated from the real photograph — see
`tools/build_avatar.py`. It used to be a drawn placeholder. A real photo can be converted to
a pixel portrait on the same palette.

---

## Controls

Your mouse pointer *is* the pixel hand while you're in the room — it taps when
it's over something clickable, presses when you click, and hands back to the
normal cursor once the book is open, so text stays selectable. On touch devices
there's no pointer to replace, so a static bobbing hand points at the book
instead.

The book has a rail of tabs down its right edge — Profile, Experience, Skills,
Contact — and a single **SHELF** control on the left. Neither the projects nor
the certificates have a tab: the projects are on the computer downstairs and
the certificates are the blue book on the shelf. Nothing that lives somewhere
else gets a door in here.

| | |
| --- | --- |
| Up / Down arrow, or the arrows on the left | move between the bookcase and the desk |
| Click the green or blue book | take it off the shelf |
| Click the computer | open the projects |
| Click the book on the desk | open it |
| Arrow keys | turn pages |
| `Home` / `End` | first / last spread |
| `Esc` | back to the shelf |
| swipe | turn pages on touch |

**SHELF** returns to the room, and the same arrow appears on the desk the
moment a book lands there, so there is always a visible way back.

Sound is on and has no switch. There are no audio files: every effect is
oscillators and filtered noise built at runtime. A browser will not start audio
before a gesture, so the context is created and resumed on the first click or
key and then left alone. The page turn is not a noise burst — it is three
overlapping rustles with a soft attack, a ragged tail and a slow random walk
over the envelope, because a flat decay on filtered noise reads as static
rather than as paper.

### The lamp

The desk lamp has a pull cord, and the cord is an actual rope: nine points run
through a Verlet solver. Integrate each point, then pull neighbours back to the
segment length four times a frame — swing, sag and overshoot all fall out of
that on their own, none of it is keyframed. Drag it sideways and it follows
sideways; let go and it crosses the anchor and oscillates down to rest.

Past a nine-pixel pull it clicks the light on or off; anything shorter and
nothing happens, which is what separates a switch from a button in a costume.
The decision is made on the deepest point of the pull rather than where you let
go, so a sharp yank still counts even though the cord is already on its way
back. The drag divides the pointer's travel by the live camera scale, since a
screen pixel is not a world pixel and the rope would otherwise race the hand.

Two details worth keeping. The loop stops itself once the rope settles, so a
cord at rest costs nothing — and something stirs it every seven to fourteen
seconds, because a cord that is perfectly still between visits reads as a
drawing of a cord rather than an object in a room. A keyboard cannot drag, so
Enter shoves the rope and toggles.

The light itself is a sprite (`lamp_cone()`), not a CSS gradient. A gradient is
rasterised after the camera's fractional scale and comes out as a smooth smear
against hard-edged art, and the cone wants stepped bands — a thing you draw,
not a thing you tween. It used to be baked into `room.png` as a dithered glow,
which had to go: light you cannot switch off is not a switch.

Two things that took a second pass. `Canvas.px` blends towards the destination,
and on a transparent canvas the destination is black, so amber at alpha 100
came out muddy brown at alpha 100 rather than translucent amber — a sprite that
is nothing but translucency has to write its channels directly. And the first
cone sat around alpha 100, which over a teal wall averages to olive: it read as
grey-green haze, not lamplight.

Dust falls through the beam, seeded across it so a mote starting near the shade
has further to travel than one starting halfway down. It fades in discrete
steps rather than smoothly — `steps()` on the whole animation moves the motes
in whole pixels too, which is what keeps them looking drawn.

### On a phone

Phones get a different interface, not the same one shrunk. Three things forced
that, and all three were measured rather than guessed.

**The room did not fit.** The camera covered a 480x270 landscape window, so on
a 390x844 phone it scaled to fill the height and showed about half the room's
width — the lamp and its pull cord were off screen at every zoom, and the
camera left 200px of empty background above the bookcase because the clamp
that keeps the room in frame skipped the axis where the room exactly fitted.
In portrait the camera now *fits* the room instead of covering the screen, and
centres it on any axis where it fits.

**19px is not a tap target.** A book spine is 22 world pixels, about 19 CSS
pixels on a phone. So in portrait the room becomes a pane at the top with its
own 480x560 shape — no letterboxing — and the space beneath it holds three
buttons that do exactly what tapping the objects does. The objects stay
tappable too; each has an invisible pad bringing it to 44px.

**The book had no navigation.** The tab rail and SHELF hang off the sides of
the book, and the old mobile rule reflowed them to sit *after* the board — at
y=1050 in an 844px viewport. They are now a fixed two-row bar at the bottom.
Two things had to be fixed to get there: the desktop rules pin them at
`top: 34px`, so setting only `bottom` left both edges applied and each bar
stretched 1400px tall; and `.book` sets `perspective`, which establishes a
containing block for fixed descendants, so they were being pinned to the book
rather than to the screen. The page curl is off at that width, so the 3D
context had nothing left to do.

Smaller things: interface type has a 12px floor, the desktop icons go to three
columns and then two, the README note is the first thing dropped on a short
screen rather than the last thing to fit, and `.os__main` clips rather than
scrolls — an absolutely positioned child of a scroll container is laid out
against scrolled content, and the note was spilling over QUIT TO ROOM and
swallowing the tap.

Verified at 320x568, 360x800, 390x844, 768x1024 and 844x390: no horizontal
overflow, nothing under 12px, every control at least 40x40 of real hit area,
and the whole journey — book, computer, project, certificates — completed by
tap.

### The beetle

Some spreads have a beetle on them. It wanders — picks a spot, walks there,
stops to think, picks another — and it bolts if the pointer gets close. It's on
every other spread rather than all of them, so it stays a small surprise rather
than wallpaper.

It started life as the scrollbar, walking a dashed route as you scrolled. That
was a worse idea than it sounded: these pages barely overflow, so the thing had
almost nothing to indicate and mostly sat still. Now it's just ambient life, and
the pages have an ordinary (pixel-styled) scrollbar again.

It's drawn **parametrically at each of eight headings** rather than drawn once
and rotated — rotating the sprite 45 degrees, even with nearest-neighbour,
shattered the legs and feelers into loose pixels. `_beetle()` in
`tools/build_sprites.py` rasterises the body, legs and antennae along the
heading vector, walking screen pixels and projecting each back into the bug's
own frame. Projecting the other way leaves holes on the diagonals.

`pointer-events: none`, so it can never block selecting the text it walks over.
Hidden on touch, and under `prefers-reduced-motion` — a bug crawling across the
page is exactly the movement that setting is asking not to have.

### A note on symbols

There are no icon glyphs anywhere in the interface, on purpose. Characters like
`♪`, `☰`, `↩`, `◀`, `▶` are not in Silkscreen or Pixelify Sans, so the browser
silently substitutes a system font for them — which is why they looked like
emoji dropped into pixel art. Every label is now plain text the pixel fonts
actually contain. Before adding any symbol, check it against
`assets/fonts/*.woff2`; if it isn't in the cmap, it will fall back and look
wrong.

The small 16x16 sprite icons that used to sit beside headings and contact rows
are also gone — at body-text size they read as emoji rather than as part of the
artwork. `assets/px/icons.png` and its generator are still in the repo if they
are ever wanted back.

---

## Accessibility and indexing

- Every word of the CV is real text in the DOM, not baked into images.
- **TEXT** mode gives one linear column — better for screen readers, skimming
  and printing. `Ctrl/Cmd+P` prints one spread per page.
- `prefers-reduced-motion` skips the whole cinematic and opens the book directly;
  the page-turn animation is disabled too.
- Deep links work: `#skills`, `#work`, `#projects`, `#certs`, `#contact` open
  straight to that spread, which also means a shared link lands somewhere useful.
- The book and the shelf are real `<button>`s, reachable by keyboard.
- Decorative sprites are `aria-hidden`; the room is not announced as content.

---

## Deploy

Push and enable GitHub Pages (Settings → Pages → deploy from branch). No build
command, no output directory.
