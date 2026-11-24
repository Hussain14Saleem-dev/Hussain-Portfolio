/* =========================================================================
   Selected Work — the PowerPoint deck.

   Three projects, one slide each: a laptop and a phone showing the same site,
   what it is, what Hussain did on it, and the live link.

   Screenshots are read from deck/shots/ by filename. Any that are missing
   render as a dark device screen carrying the domain, so the deck is always
   complete and always rebuildable — drop a file in and run this again:

       node tools/build_deck.js

   Expected files (PNG or JPG, any size; the frame crops to fit):
       deck/shots/irshad-desktop.png    deck/shots/irshad-phone.png
       deck/shots/rabt-desktop.png      deck/shots/rabt-phone.png
       deck/shots/techzaar-desktop.png  deck/shots/techzaar-phone.png

   Desktop shots want a wide browser window (1440x900 or similar); phone
   shots want a real narrow viewport, not a desktop page scaled down.
   ========================================================================= */

const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');
const { applyTheme } = require(process.env.PPTX_SKILL
  ? path.join(process.env.PPTX_SKILL, 'scripts/apply_theme.js')
  : '/sessions/serene-blissful-bell/mnt/.claude/skills/pptx/scripts/apply_theme.js');

const ROOT = path.join(__dirname, '..');
const SHOTS = path.join(ROOT, 'deck', 'shots');
const OUT = path.join(ROOT, 'deck', 'Hussain-Alshikhy-Selected-Work.pptx');

/* The palette is the portfolio's own: the ink and teal of the room, gilt for
   the accent. A deck about that portfolio should not arrive in stock blue. */
const THEME = {
  name: 'Hussain Alshikhy — Selected Work',
  headFontFace: 'Arial',
  bodyFontFace: 'Calibri',
  colors: {
    dk1: '18141E',   // ink — body text
    lt1: 'FFFFFF',
    dk2: '12282A',   // deep teal — dark slides
    lt2: 'F4F1E8',   // warm paper
    accent1: 'F0B04E', // amber
    accent2: '388456', // green
    accent3: '3C588E', // blue
    accent4: 'B03E42', // red
    accent5: '5E9884', // pale teal
    accent6: '6E6A75', // muted grey for captions
    hlink: 'C48034',
    folHlink: '8C4E7A'
  }
};

const W = 13.333, H = 7.5;

const PROJECTS = [
  {
    slug: 'irshad',
    name: 'Irshad',
    arabic: 'منصّة إرشاد',
    kicker: 'Family counselling platform · Grids Company',
    url: 'irshad.ly',
    href: 'https://irshad.ly',
    role: 'Front end, back end and UI/UX',
    tint: '2C5F57',
    body: 'Connects Libyan families with qualified family and marriage counsellors. A consultation ' +
          'is posted anonymously — publicly, or to the specialist panel only — and answered by a ' +
          'qualified counsellor. A directory lists each specialist’s field, years of experience and ' +
          'rating, and appointments are booked by video, voice or text.',
    note: 'Built for people who cannot walk into a counselling centre: it removes the stigma, the ' +
          'distance and the need to leave the house. Backed by the Marriage Support Fund.',
    chips: ['Full stack', 'UI/UX', 'Arabic RTL', 'In progress'],
    devicesRight: true
  },
  {
    slug: 'rabt',
    name: 'Rabt',
    arabic: 'ربط',
    kicker: 'NFC digital card · Grids Company',
    url: 'rabt.grids.ly',
    href: 'https://rabt.grids.ly',
    role: 'Front end',
    tint: '26405E',
    body: 'A bio-link platform where one link carries everything you share, and a physical NFC card ' +
          'opens that profile on anyone’s phone with a tap. Companies list themselves in a business ' +
          'directory and issue cards across a whole team.',
    note: 'An established product with real users — the work was adding features and improvements ' +
          'inside a live production codebase.',
    chips: ['Front end', 'NFC', 'Live product'],
    devicesRight: false
  },
  {
    slug: 'techzaar',
    name: 'TechZaar Activities',
    arabic: '',
    kicker: 'Event companion site · GDG on Campus, LIMU',
    url: 'gdg-techzaar.vercel.app',
    href: 'https://gdg-techzaar.vercel.app',
    role: 'Built it',
    tint: '2F4A3A',
    body: 'A companion site helping attendees explore event content and locations — a home page ' +
          'presenting the available activities in a clear, organised layout, and a map page with a ' +
          '3D map pinpointing each activity location.',
    note: 'Used live, on phones, by people standing in a venue trying to find a room. That ruled the ' +
          'whole design.',
    chips: ['3D map', 'Wayfinding', 'Responsive'],
    devicesRight: true
  }
];

/* ---------------------------------------------------------------- shots -- */

function shot(slug, kind) {
  for (const ext of ['png', 'jpg', 'jpeg', 'webp']) {
    const p = path.join(SHOTS, `${slug}-${kind}.${ext}`);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

/* ------------------------------------------------------------- devices --- */
/* Drawn, not pasted: a flat laptop and phone in the deck's own colours, with
   the screenshot inset into the glass. A picture of a real laptop would drag
   its own lighting and perspective into every slide. */

function laptop(slide, x, y, w, img, tint, url) {
  const h = w * 0.625;                 // 16:10 lid
  const bez = 0.07;

  slide.addShape('roundRect', {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: '1C1A22' },
    line: { color: '0E0D12', width: 1 },
    shadow: { type: 'outer', angle: 90, blur: 18, offset: 6, opacity: 0.28, color: '18141E' },
    objectName: 'laptop lid'
  });

  const sx = x + bez, sy = y + bez, sw = w - bez * 2, sh = h - bez * 2;
  if (img) {
    slide.addImage({ path: img, x: sx, y: sy, w: sw, h: sh, sizing: { type: 'cover', w: sw, h: sh }, objectName: 'desktop screenshot' });
  } else {
    placeholder(slide, sx, sy, sw, sh, tint, url, 12);
  }

  // base: a thin deck and a wider foot, which is all a flat laptop needs
  slide.addShape('roundRect', {
    x: x - w * 0.045, y: y + h + 0.015, w: w * 1.09, h: 0.13, rectRadius: 0.06,
    fill: { color: '2A2731' }, line: { type: 'none' }, objectName: 'laptop base'
  });
  slide.addShape('roundRect', {
    x: x + w * 0.42, y: y + h + 0.045, w: w * 0.16, h: 0.045, rectRadius: 0.02,
    fill: { color: '45414E' }, line: { type: 'none' }, objectName: 'laptop notch'
  });
}

function phone(slide, x, y, h, img, tint) {
  const w = h * 0.486;                 // 19.5:9
  const bez = 0.055;

  slide.addShape('roundRect', {
    x, y, w, h, rectRadius: 0.14,
    fill: { color: '1C1A22' },
    line: { color: '0E0D12', width: 1 },
    shadow: { type: 'outer', angle: 90, blur: 16, offset: 5, opacity: 0.34, color: '18141E' },
    objectName: 'phone body'
  });

  const sx = x + bez, sy = y + bez, sw = w - bez * 2, sh = h - bez * 2;
  if (img) {
    slide.addImage({ path: img, x: sx, y: sy, w: sw, h: sh, sizing: { type: 'cover', w: sw, h: sh }, objectName: 'phone screenshot' });
  } else {
    placeholder(slide, sx, sy, sw, sh, tint, 'MOBILE', 9);
  }

  slide.addShape('roundRect', {
    x: x + w * 0.34, y: y + 0.085, w: w * 0.32, h: 0.075, rectRadius: 0.04,
    fill: { color: '0E0D12' }, line: { type: 'none' }, objectName: 'phone notch'
  });
}

/* A screen with nothing in it yet. Deliberately calm rather than alarming —
   the deck is presentable as it stands. */
function placeholder(slide, x, y, w, h, tint, url, fs_) {
  slide.addShape('rect', { x, y, w, h, fill: { color: tint }, line: { type: 'none' }, objectName: 'screen' });
  slide.addText(url, {
    isTextBox: true, x, y: y + h / 2 - 0.3, w, h: 0.3,
    align: 'center', fontSize: fs_, color: 'FFFFFF', bold: true, charSpacing: 1, margin: 0
  });
  slide.addText('screenshot to come', {
    isTextBox: true, x, y: y + h / 2, w, h: 0.26,
    align: 'center', fontSize: fs_ - 2, color: 'FFFFFF', transparency: 45, margin: 0
  });
}

/* ----------------------------------------------------------------- deck -- */

function build() {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.author = 'Hussain Alshikhy';
  pres.title = 'Selected Work';
  pres.subject = 'Selected web projects';

  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: 'DARK',
    background: { color: THEME.colors.dk2 },
    objects: [
      { text: { text: 'Hussain Alshikhy', options: {
        x: 0.75, y: H - 0.72, w: 5, h: 0.3, fontSize: 11, color: C.accent6, margin: 0, isTextBox: true } } }
    ]
  });

  pres.defineSlideMaster({
    title: 'WORK',
    background: { color: 'FFFFFF' },
    /* No footer on the layout: the devices sit on a dark field that swaps
       sides slide to slide, and a fixed grey footer disappeared into it on
       every left-hand one. Each slide places its own, over the white. */
    slideNumber: { x: W - 1.0, y: H - 0.62, w: 0.5, h: 0.3, fontSize: 10, color: THEME.colors.accent6, align: 'right' }
  });

  /* -- 1. title -------------------------------------------------------- */
  pres.addSection({ title: 'Opening' });
  const t = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Opening' });

  /* Name and description, nothing else. One column, left, with the slide left
     deliberately open on the right — a contents list here only repeated the
     three slides that follow it. */
  t.addShape('rect', { x: 0.75, y: 2.12, w: 0.5, h: 0.07,
    fill: { color: THEME.colors.accent1 }, line: { type: 'none' }, objectName: 'rule' });

  t.addText('Hussain', { isTextBox: true, x: 0.75, y: 2.45, w: 9, h: 1.0,
    fontSize: 60, bold: true, color: 'FFFFFF', margin: 0 });
  t.addText('Alshikhy', { isTextBox: true, x: 0.75, y: 3.35, w: 9, h: 1.0,
    fontSize: 60, bold: true, color: THEME.colors.accent1, margin: 0 });

  t.addText('Full-Stack Web Developer & UI/UX Designer', {
    isTextBox: true, x: 0.78, y: 4.45, w: 8, h: 0.4,
    fontSize: 19, color: THEME.colors.accent5, margin: 0 });

  t.addText(
    'Fourth-year Software Engineering student at the Libyan International Medical University ' +
    'and a working web developer at Grids Company in Benghazi. Front end is where I spend most ' +
    'of my time — structure, layout and responsiveness — and I design the interfaces as well as ' +
    'build them.',
    { isTextBox: true, x: 0.78, y: 5.0, w: 7.6, h: 1.3,
      fontSize: 15, color: 'CFCBC2', margin: 0, lineSpacingMultiple: 1.3 });

  t.addNotes('Hussain Alshikhy — full-stack web developer and UI/UX designer, Benghazi.');

  /* -- 2..5. one slide per project ------------------------------------- */
  pres.addSection({ title: 'Projects' });

  PROJECTS.forEach((p) => {
    const s = pres.addSlide({ masterName: 'WORK', sectionTitle: 'Projects' });
    const right = p.devicesRight;

    /* Two columns that never touch. The devices get a tinted field and stay
       inside it — an earlier pass let the phone hang over the divide, where
       it sat on top of the tech chips and hid one of them. */
    const FIELD = 6.43;
    const fieldX = right ? W - FIELD : 0;
    const textX  = right ? 0.75 : 7.0;
    const textW  = 5.38;

    s.addShape('rect', { x: fieldX, y: 0, w: FIELD, h: H,
      fill: { color: p.tint }, line: { type: 'none' }, objectName: 'device field' });

    s.addText(p.kicker.toUpperCase(), { isTextBox: true, x: textX, y: 0.85, w: textW, h: 0.3,
      fontSize: 11, bold: true, color: THEME.colors.accent1, charSpacing: 1.4, margin: 0 });

    const heading = p.arabic
      ? [{ text: p.name, options: { fontSize: 38, bold: true, color: THEME.colors.dk1 } },
         { text: '   ' + p.arabic, options: { fontSize: 23, color: THEME.colors.accent6 } }]
      : [{ text: p.name, options: { fontSize: 38, bold: true, color: THEME.colors.dk1 } }];
    s.addText(heading, { isTextBox: true, x: textX, y: 1.2, w: textW, h: 0.7, margin: 0 });

    /* Body and note in one box, as two paragraphs. Separate boxes at fixed
       y left a hole under the shorter write-ups and nearly collided under
       the longer ones; flowing them together fixes both. */
    s.addText([
      { text: p.body, options: { fontSize: 14, color: '3A3640', breakLine: true, paraSpaceAfter: 10 } },
      { text: p.note, options: { fontSize: 12.5, italic: true, color: '6E6A75' } }
    ], { isTextBox: true, x: textX, y: 2.02, w: textW, h: 3.0,
         lineSpacingMultiple: 1.28, margin: 0, valign: 'top' });

    s.addText([
      { text: 'MY ROLE   ', options: { fontSize: 10, bold: true, color: THEME.colors.accent6, charSpacing: 1.2 } },
      { text: p.role, options: { fontSize: 13, bold: true, color: THEME.colors.dk1 } }
    ], { isTextBox: true, x: textX, y: 5.22, w: textW, h: 0.32, margin: 0 });

    /* Chips, wrapping rather than running off the column. The width estimate
       is per-character at 11pt — the first one was three times too generous
       and pushed the last chip under the phone. */
    let cx = textX, cy = 5.66;
    p.chips.forEach((chip) => {
      const w = 0.082 * chip.length + 0.40;
      if (cx + w > textX + textW) { cx = textX; cy += 0.44; }
      s.addShape('roundRect', { x: cx, y: cy, w, h: 0.34, rectRadius: 0.17,
        fill: { color: 'F1EEE7' }, line: { color: 'DDD8CC', width: 1 }, objectName: `chip ${chip}` });
      s.addText(chip, { isTextBox: true, x: cx, y: cy + 0.025, w, h: 0.3,
        align: 'center', fontSize: 11, color: '4A4651', margin: 0 });
      cx += w + 0.13;
    });

    s.addShape('roundRect', { x: textX, y: 6.33, w: 3.25, h: 0.5, rectRadius: 0.25,
      fill: { color: THEME.colors.dk1 }, line: { type: 'none' }, objectName: 'link button' });
    s.addText(p.url, {
      isTextBox: true, x: textX, y: 6.41, w: 3.25, h: 0.34, align: 'center',
      fontSize: 13, bold: true, color: 'FFFFFF', margin: 0,
      hyperlink: { url: p.href, tooltip: `Open ${p.name}` }
    });

    const lapW = 5.2;
    const lapX = fieldX + (FIELD - lapW) / 2 + (right ? 0.25 : -0.25);
    laptop(s, lapX, 1.5, lapW, shot(p.slug, 'desktop'), '1F1D26', p.url);
    phone(s, right ? fieldX + 0.14 : fieldX + FIELD - 1.72, 3.4, 2.9,
          shot(p.slug, 'phone'), '1F1D26');

    s.addText('Selected Work · Hussain Alshikhy', { isTextBox: true,
      x: textX, y: H - 0.62, w: 4.2, h: 0.3,
      fontSize: 10, color: THEME.colors.accent6, margin: 0, objectName: 'footer' });

    s.addNotes(`${p.name} — ${p.href}. Role: ${p.role}.`);
  });

  /* -- 6. close -------------------------------------------------------- */
  pres.addSection({ title: 'Closing' });
  const c = pres.addSlide({ masterName: 'DARK', sectionTitle: 'Closing' });

  /* Thank you and three ways to reach him. Nothing else on it. */
  c.addShape('rect', { x: 0.75, y: 2.45, w: 0.5, h: 0.07,
    fill: { color: THEME.colors.accent1 }, line: { type: 'none' }, objectName: 'rule' });

  c.addText('Thank you', { isTextBox: true, x: 0.75, y: 2.78, w: 9, h: 1.05,
    fontSize: 58, bold: true, color: 'FFFFFF', margin: 0 });

  const rows = [
    ['Email', 'hussain14saleem1@gmail.com', 'mailto:hussain14saleem1@gmail.com'],
    ['Phone', '(+218) 916 765 318', null],
    ['LinkedIn', 'linkedin.com/in/hussain-saleem', 'https://www.linkedin.com/in/hussain-saleem-801879388/']
  ];
  rows.forEach((r, i) => {
    const y = 4.2 + i * 0.62;
    c.addText(r[0].toUpperCase(), { isTextBox: true, x: 0.78, y: y + 0.06, w: 1.3, h: 0.32,
      fontSize: 10, bold: true, color: THEME.colors.accent6, charSpacing: 1.2, margin: 0 });
    c.addText(r[1], Object.assign({ isTextBox: true, x: 2.1, y, w: 6, h: 0.4,
      fontSize: 17, color: 'FFFFFF', margin: 0 }, r[2] ? { hyperlink: { url: r[2] } } : {}));
  });

  c.addNotes('Contact details.');

  return pres;
}

(async () => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const pres = build();
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);

  const missing = [];
  PROJECTS.forEach((p) => {
    if (!shot(p.slug, 'desktop')) missing.push(`${p.slug}-desktop`);
    if (!shot(p.slug, 'phone')) missing.push(`${p.slug}-phone`);
  });
  console.log('wrote', OUT);
  console.log(missing.length ? 'placeholders still showing for: ' + missing.join(', ')
                             : 'every screenshot found');
})();
