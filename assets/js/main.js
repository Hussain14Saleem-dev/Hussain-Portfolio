/* ==========================================================================
   Hussain Alshikhy — pixel-art portfolio
   Vanilla JavaScript. No dependencies, no build step.

   Contents
     1  constants & helpers
     2  sound       — a tiny WebAudio chiptune synth, no audio files
     3  camera      — moves a 480x270 window around a 480x560 room
     4  scenes      — shelf -> pull -> drop -> desk -> open -> read
     5  reader      — spreads, 3D page turn, tabs, keyboard, deep links
     6  boot        — preload, then start (or skip straight in)
   ========================================================================== */

(function () {
  'use strict';

  /* ---------------------------------------------------------------- 1 --- */

  var doc = document;
  var root = doc.documentElement;
  var body = doc.body;

  var $ = function (sel, ctx) { return (ctx || doc).querySelector(sel); };
  var $$ = function (sel, ctx) {
    return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel));
  };

  var VIEW_W = 480, VIEW_H = 270;   // the camera window, in world pixels

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var el = {
    boot:     $('#boot'),
    bootFill: $('#bootFill'),
    bootHint: $('#bootHint'),
    world:    $('#world'),
    spine:    $('#spine'),
    spineBlue: $('#spineBlue'),
    deskCover: $('#deskCover'),
    deskInner: $('.deskbook__inner'),
    hand:     $('#hand'),
    deskBook: $('#deskBook'),
    dust:     $('#dust'),
    prompt:   $('#prompt'),
    reader:   $('#reader'),
    spreads:  $('#spreads'),
    curl:     $('#curl'),
    curlCast: $('#curlCast'),
    tabs:     $('#tabs'),
    prev:     $('#prev'),
    next:     $('#next'),
    pgNow:    $('#pgNow'),
    pgAll:    $('#pgAll'),
    btnShelf: $('#btnShelf'),
    hintKeys: $('#hintKeys'),

    // the desk lamp
    lamp:     $('#lamp'),
    lampDust: $('#lampDust'),
    cord:     $('#cord'),
    cordLine: $('#cordLine'),
    cordLit:  $('#cordLit'),
    cordGrab: $('#cordGrab'),

    // the second floor of the room: the desk, the computer, the projects
    floors:   $('#floors'),
    goUp:     $('#goUp'),
    goDown:   $('#goDown'),
    pc:       $('#pc'),
    os:       $('#os'),
    osBoot:   $('#osBoot'),
    osDesktop: $('#osDesktop'),
    osWins:   $('#osWins'),
    osBack:   $('#osBack'),
    osTip:    $('#osTip'),
    osPath:   $('#osPath'),
    osIdx:    $('#osIdx'),

    // the browser inside the computer
    web:      $('#web'),
    webFrame: $('#webFrame'),
    webUrl:   $('#webUrl'),
    webTab:   $('#webTab'),
    webOut:   $('#webOut'),
    webX:     $('#webX'),
    webReload: $('#webReload'),
    webLoad:  $('#webLoad'),
    webHint:  $('#webHint'),
    webHintOut: $('#webHintOut'),
    webFail:  $('#webFail')
  };

  /* Two volumes share the shelf, the desk and the reader. Only the contents
     and the binding colour differ, so `spreads` is simply repointed. */
  var VOLUMES = {
    portfolio: {
      cover: 'assets/px/book_cover_front.png',
      endpaper: 'assets/px/book_endpaper.png',
      spreads: $$('.spread[data-volume="portfolio"]', el.spreads)
    },
    certs: {
      cover: 'assets/px/book_cover_front_blue.png',
      endpaper: 'assets/px/book_endpaper_blue.png',
      spreads: $$('.spread[data-volume="certs"]', el.spreads)
    }
  };

  var vol = 'portfolio';
  var spreads = VOLUMES[vol].spreads;
  var current = 0;
  var busy = false;

  function setVolume(name) {
    if (!VOLUMES[name]) return;
    vol = name;
    spreads = VOLUMES[name].spreads;
    current = 0;
    body.setAttribute('data-volume', name);
    el.deskCover.src = VOLUMES[name].cover;
    el.deskInner.style.backgroundImage = 'url(\'' + VOLUMES[name].endpaper + '\')';
    el.pgAll.textContent = String(spreads.length);
    // everything from the other volume must be out of the way
    $$('.spread', el.spreads).forEach(function (sp) {
      sp.hidden = (sp.getAttribute('data-volume') !== name);
    });
  }

  function setScene(name) { body.setAttribute('data-scene', name); }
  function scene() { return body.getAttribute('data-scene'); }
  function say(text) { el.prompt.innerHTML = '<span>' + text + '</span>'; }
  function wait(ms, fn) { return setTimeout(fn, reduceMotion ? 0 : ms); }

  /* ---------------------------------------------------------------- 2 --- */
  /* Sound is synthesised, not sampled — a handful of oscillators costs
     nothing to download and stays in keeping with the rest of the site.
     Off by default: autoplaying audio is rude, and browsers block it anyway. */

  var Sfx = {
    ctx: null,
    // On, always. There is no switch any more. A browser will not let audio
    // start before a gesture, so the context is created and resumed on the
    // first click or key — see the one-shot listener in the wiring below.
    on: true,

    boot: function () {
      if (this.ctx) return;
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return;
      try { this.ctx = new AC(); } catch (e) { this.ctx = null; }
    },

    tone: function (freq, dur, type, vol, slideTo) {
      if (!this.on || !this.ctx) return;
      var t = this.ctx.currentTime;
      var osc = this.ctx.createOscillator();
      var gain = this.ctx.createGain();
      osc.type = type || 'square';
      osc.frequency.setValueAtTime(freq, t);
      if (slideTo) osc.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
      gain.gain.setValueAtTime(vol || 0.05, t);
      gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc.connect(gain).connect(this.ctx.destination);
      osc.start(t);
      osc.stop(t + dur + 0.02);
    },

    noise: function (dur, vol, hz) {
      if (!this.on || !this.ctx) return;
      var t = this.ctx.currentTime;
      var n = Math.floor(this.ctx.sampleRate * dur);
      var buf = this.ctx.createBuffer(1, n, this.ctx.sampleRate);
      var d = buf.getChannelData(0);
      for (var i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
      var src = this.ctx.createBufferSource();
      src.buffer = buf;
      var filt = this.ctx.createBiquadFilter();
      filt.type = 'bandpass';
      filt.frequency.value = hz || 1600;
      var gain = this.ctx.createGain();
      gain.gain.value = vol || 0.05;
      src.connect(filt).connect(gain).connect(this.ctx.destination);
      src.start(t);
    },

    click: function () { this.tone(660, 0.07, 'square', 0.05); },
    pull:  function () { this.noise(0.34, 0.05, 900); this.tone(180, 0.3, 'triangle', 0.05, 340); },
    thud:  function () { this.tone(90, 0.26, 'sine', 0.14, 48); this.noise(0.14, 0.05, 400); },
    /* Paper, not a hiss. A single filtered noise burst with a linear decay
       reads as static; a page turn is a rustle — a soft attack, a long ragged
       tail, and two passes at different brightnesses as the sheet bends and
       then lands. The wobble in the envelope is the part that sells it. */
    rustle: function (dur, vol, hz, q) {
      if (!this.on || !this.ctx) return;
      var t = this.ctx.currentTime;
      var n = Math.floor(this.ctx.sampleRate * dur);
      var buf = this.ctx.createBuffer(1, n, this.ctx.sampleRate);
      var d = buf.getChannelData(0);
      var wob = 0, drift = 0;
      for (var i = 0; i < n; i++) {
        var u = i / n;
        // fast attack, slow decay
        var env = u < 0.08 ? u / 0.08 : Math.pow(1 - (u - 0.08) / 0.92, 1.7);
        // a slow random walk over the top: fibres catching, not white noise
        drift += (Math.random() - 0.5) * 0.06;
        drift *= 0.96;
        wob = 0.65 + 0.35 * Math.sin(u * 34 + drift * 8);
        d[i] = (Math.random() * 2 - 1) * env * wob;
      }
      var src = this.ctx.createBufferSource();
      src.buffer = buf;
      var filt = this.ctx.createBiquadFilter();
      filt.type = 'bandpass';
      filt.frequency.setValueAtTime(hz, t);
      filt.frequency.exponentialRampToValueAtTime(hz * 0.45, t + dur);
      filt.Q.value = q || 0.9;
      var gain = this.ctx.createGain();
      gain.gain.value = vol;
      src.connect(filt).connect(gain).connect(this.ctx.destination);
      src.start(t);
    },

    page:  function () {
      var self = this;
      this.rustle(0.30, 0.075, 3000, 0.8);          // the sheet lifting
      setTimeout(function () { self.rustle(0.24, 0.055, 1500, 1.3); }, 90);
      setTimeout(function () {                       // and settling on the pile
        self.rustle(0.16, 0.045, 900, 1.6);
        self.tone(140, 0.05, 'sine', 0.025, 90);
      }, 210);
    },
    open:  function () {
      var self = this;
      [523, 659, 784, 1046].forEach(function (f, i) {
        setTimeout(function () { self.tone(f, 0.22, 'triangle', 0.05); }, i * 85);
      });
    }
  };

  /* ---------------------------------------------------------------- 3 --- */
  /* The room is one 480x560 image. The camera shows a 480x270 slice of it and
     is driven entirely by a translate+scale on the world element, so a "camera
     move" is a single composited transform rather than a redraw. */

  var shots = {
    shelf: { x: 240, y: 138, z: 1,    ms: 900 },
    // pull is per-book: it leans in on whichever spine was clicked, so the
    // book you took stays in the middle of frame while the camera tightens
    pull:  { x: 232, y: 158, z: 1.45, ms: 700 },
    pullCerts: { x: 356, y: 158, z: 1.45, ms: 700 },
    desk:  { x: 252, y: 340, z: 1.55, ms: 1150 },
    open:  { x: 254, y: 334, z: 3.3,  ms: 1000 },

    // the desk with nothing on it but the computer — where the down arrow goes
    deskIdle: { x: 244, y: 372, z: 1.25, ms: 1000 },
    // and the glass itself, filling the frame. The screen is 84x48, so at this
    // zoom it is the viewport, which is what makes the handover to the HTML
    // desktop invisible. Numbers come from PC in tools/build_room.py.
    screen:   { x: 358, y: 346, z: 5.62, ms: 900 }
  };

  var held = shots.shelf;

  function baseScale() {
    return Math.max(window.innerWidth / VIEW_W, window.innerHeight / VIEW_H);
  }

  function camera(shot, instant) {
    held = shot;
    var s = baseScale() * shot.z;
    root.style.setProperty('--cam-ms', (instant || reduceMotion ? 0 : shot.ms) + 'ms');
    root.style.setProperty('--cam-s', s);
    root.style.setProperty('--cam-x', (window.innerWidth / 2 - shot.x * s) + 'px');
    root.style.setProperty('--cam-y', (window.innerHeight / 2 - shot.y * s) + 'px');
  }

  window.addEventListener('resize', function () { camera(held, true); }, { passive: true });

  /* -- the pointer ------------------------------------------------------- */
  /* The pointing hand is the cursor, not a sign next to the book. It lives
     outside the world element so the camera never drags or scales it, and it
     is scaled to whole world pixels so it shares the art's pixel grid. */

  var Cursor = {
    node: $('#cursor'),
    x: -200,
    y: -200,
    scale: 3,
    queued: false,

    /* The fingertip occupies x=6..9 on row 0 of the sprite. That is the
       hotspot and it has to land exactly on the real pointer, otherwise the
       finger points at something other than what you click. */
    HOTSPOT_X: 8,

    supported: function () {
      return window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    },

    resize: function () {
      // clamped: below 2 the hand is illegible, above 4 it eats the screen
      this.scale = Math.max(2, Math.min(4, Math.round(baseScale())));
      root.style.setProperty('--cs', this.scale);
    },

    move: function (x, y) {
      this.x = x;
      this.y = y;
      if (this.queued) return;
      this.queued = true;
      requestAnimationFrame(this.paint.bind(this));
    },

    paint: function () {
      this.queued = false;
      // rounded to whole pixels: a fractional translate makes the compositor
      // resample the sprite and softens its edges
      var x = Math.round(this.x - this.HOTSPOT_X * this.scale);
      var y = Math.round(this.y);
      root.style.setProperty('--curx', x + 'px');
      root.style.setProperty('--cury', y + 'px');
    },

    init: function () {
      if (!this.supported()) return;

      body.classList.add('has-cursor');
      this.resize();

      var self = this;
      var HOT = '#spine, #deskBook, #prompt';

      doc.addEventListener('pointermove', function (e) {
        if (e.pointerType === 'touch') return;
        self.move(e.clientX, e.clientY);
        self.node.classList.remove('is-out');
        // only offer the tap when the thing under the finger is clickable
        var over = e.target && e.target.closest && e.target.closest(HOT);
        self.node.classList.toggle('is-over', !!over);
      }, { passive: true });

      doc.addEventListener('pointerdown', function () {
        self.node.classList.add('is-press');
      }, { passive: true });

      doc.addEventListener('pointerup', function () {
        self.node.classList.remove('is-press');
      }, { passive: true });

      // don't leave a hand stranded at the edge when the pointer leaves
      doc.addEventListener('pointerleave', function () {
        self.node.classList.add('is-out');
      });
      window.addEventListener('blur', function () {
        self.node.classList.add('is-out');
      });

      window.addEventListener('resize', function () { self.resize(); }, { passive: true });
    }
  };

  /* motes of dust drifting through the lamp light */
  function seedDust(n) {
    var frag = doc.createDocumentFragment();
    for (var i = 0; i < n; i++) {
      var m = doc.createElement('i');
      m.style.left = Math.random() * 480 + 'px';
      m.style.top = (120 + Math.random() * 420) + 'px';
      m.style.animationDuration = (5 + Math.random() * 7) + 's';
      m.style.animationDelay = (-Math.random() * 10) + 's';
      frag.appendChild(m);
    }
    el.dust.appendChild(frag);
  }

  /* ------------------------------------------------------------- 3b --- */
  /* The desk lamp. The cord is a real pull: press it, drag down, let go past
     the notch and it clicks over. Anything less springs back and nothing
     happens, which is what makes it feel like a switch rather than a button
     wearing a costume. */

  var Lamp = {
    // the cone sprite's own geometry, so the motes fall inside the light
    W: 88, DROP: 34, MOUTH: 30,

    /* -- the rope ------------------------------------------------------- */
    /* Verlet, because it is the cheapest way to get something that behaves
       like a cord: integrate positions, then repeatedly pull neighbouring
       points back to the segment length. Swing, sag and overshoot all fall
       out of that on their own — none of it is animated. */
    N: 9,                  // points, anchor included
    SEG: 1.9,              // world px between them
    GRAV: 0.32,
    DAMP: 0.986,
    ANCHOR_X: 36, ANCHOR_Y: 0,   // local to #cord
    NOTCH: 9,              // how far it must be pulled to count
    REACH: 30,             // and how far it will stretch before it stops

    on: true,
    pts: [],
    dragging: false,
    grabDX: 0, grabDY: 0,
    maxDrop: 0,
    still: 0,
    running: false,

    init: function () {
      var self = this;
      this.motes();

      for (var i = 0; i < this.N; i++) {
        this.pts.push({ x: this.ANCHOR_X, y: this.ANCHOR_Y + i * this.SEG,
                        px: this.ANCHOR_X, py: this.ANCHOR_Y + i * this.SEG });
      }
      this.draw();

      el.cordGrab.addEventListener('pointerdown', function (e) {
        var p = self.local(e);
        var tip = self.pts[self.N - 1];
        self.dragging = true;
        self.maxDrop = 0;
        // hold it where it was grabbed, so the bead does not jump to the
        // pointer the instant you touch it
        self.grabDX = tip.x - p.x;
        self.grabDY = tip.y - p.y;
        el.cordGrab.setPointerCapture(e.pointerId);
        Sfx.boot();
        self.wake();
      });

      el.cordGrab.addEventListener('pointermove', function (e) {
        if (!self.dragging) return;
        var p = self.local(e);
        self.target = { x: p.x + self.grabDX, y: p.y + self.grabDY };
      });

      var release = function () {
        if (!self.dragging) return;
        self.dragging = false;
        self.target = null;
        // judged on the deepest point of the pull, not where you let go, so a
        // sharp yank counts even though the cord is already on its way back
        if (self.maxDrop >= self.NOTCH) self.toggle();
        self.wake();
      };
      el.cordGrab.addEventListener('pointerup', release);
      el.cordGrab.addEventListener('pointercancel', release);

      el.cordGrab.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          // give the rope a shove so a keyboard press looks like a pull too
          var tip = self.pts[self.N - 1];
          tip.py = tip.y - 3.2;
          self.toggle();
          self.wake();
        }
      });
      el.cordGrab.addEventListener('click', function (e) { e.preventDefault(); });

      window.addEventListener('resize', function () { self.wake(); }, { passive: true });

      // Every so often something stirs it. A cord that is perfectly still
      // between visits reads as a drawing of a cord; one that drifts a pixel
      // now and then reads as an object in a room.
      (function breathe() {
        setTimeout(function () {
          if (!self.dragging) { self.nudge(0.22 * (Math.random() < 0.5 ? -1 : 1)); }
          breathe();
        }, 7000 + Math.random() * 7000);
      })();
    },

    /* a sideways shove, in world px per frame */
    nudge: function (v) {
      if (reduceMotion) return;
      for (var i = 2; i < this.N; i++) this.pts[i].px -= v * (i / this.N);
      this.wake();
    },

    /* pointer -> #cord's own coordinate space. The room is scaled by the
       camera, so screen pixels have to be divided by the live scale or the
       rope races the hand. */
    local: function (e) {
      var s = parseFloat(getComputedStyle(root).getPropertyValue('--cam-s')) || 1;
      var box = el.cord.getBoundingClientRect();
      return { x: (e.clientX - box.left) / s, y: (e.clientY - box.top) / s };
    },

    wake: function () {
      this.still = 0;
      if (this.running) return;
      this.running = true;
      var self = this;
      (function loop() {
        if (!self.running) return;
        self.step();
        self.draw();
        requestAnimationFrame(loop);
      })();
    },

    step: function () {
      var i, p;

      for (i = 1; i < this.N; i++) {
        p = this.pts[i];
        var vx = (p.x - p.px) * this.DAMP;
        var vy = (p.y - p.py) * this.DAMP;
        p.px = p.x; p.py = p.y;
        p.x += vx;
        p.y += vy + this.GRAV;
      }

      // four passes is enough for nine points to stop looking like elastic
      for (var k = 0; k < 4; k++) {
        this.pts[0].x = this.ANCHOR_X;
        this.pts[0].y = this.ANCHOR_Y;
        for (i = 0; i < this.N - 1; i++) {
          var a = this.pts[i], b = this.pts[i + 1];
          var dx = b.x - a.x, dy = b.y - a.y;
          var d = Math.sqrt(dx * dx + dy * dy) || 0.0001;
          var f = (d - this.SEG) / d * 0.5;
          if (i > 0) { a.x += dx * f; a.y += dy * f; }
          else { f *= 2; }                       // the anchor cannot move
          b.x -= dx * f; b.y -= dy * f;
        }
        if (this.dragging && this.target) {
          var tip = this.pts[this.N - 1];
          tip.x = this.target.x;
          tip.y = this.target.y;
          // and it is a cord, not a rubber band
          var ax = tip.x - this.ANCHOR_X, ay = tip.y - this.ANCHOR_Y;
          var len = Math.sqrt(ax * ax + ay * ay);
          if (len > this.REACH) {
            tip.x = this.ANCHOR_X + ax / len * this.REACH;
            tip.y = this.ANCHOR_Y + ay / len * this.REACH;
          }
        }
      }

      var end = this.pts[this.N - 1];
      if (this.dragging) {
        this.maxDrop = Math.max(this.maxDrop, end.y - this.ANCHOR_Y - (this.N - 1) * this.SEG);
      }

      // stop the loop once it has settled; a rope at rest costs nothing
      var moving = 0;
      for (i = 1; i < this.N; i++) {
        p = this.pts[i];
        moving = Math.max(moving, Math.abs(p.x - p.px) + Math.abs(p.y - p.py));
      }
      if (!this.dragging && moving < 0.02) {
        if (++this.still > 20) this.running = false;
      } else {
        this.still = 0;
      }
    },

    draw: function () {
      var dark = [], lit = [];
      for (var i = 0; i < this.N; i++) {
        // whole pixels: this is pixel art, and a rope sliding through
        // fractions of a pixel is the one thing that would give it away
        var rx = Math.round(this.pts[i].x), ry = Math.round(this.pts[i].y);
        dark.push(rx + ',' + ry);
        lit.push((rx + 1) + ',' + ry);
      }
      el.cordLine.setAttribute('points', dark.join(' '));
      el.cordLit.setAttribute('points', lit.join(' '));

      var end = this.pts[this.N - 1];
      el.cordGrab.style.left = (85 + Math.round(end.x) - 3) + 'px';
      el.cordGrab.style.top = (363 + Math.round(end.y) - 3) + 'px';
    },

    toggle: function () {
      this.on = !this.on;
      body.classList.toggle('lamp-off', !this.on);
      el.cordGrab.setAttribute('aria-pressed', String(this.on));
      // a cord switch is two sounds: the catch, then the click
      Sfx.tone(1180, 0.03, 'square', 0.05);
      setTimeout(function () { Sfx.tone(520, 0.06, 'square', 0.05); }, 55);
    },

    /* Motes seeded across the beam. Each starts somewhere inside the cone and
       falls to the desk, so one that begins near the shade has further to go
       than one that begins halfway down. */
    motes: function () {
      if (reduceMotion) return;
      var frag = doc.createDocumentFragment();
      for (var i = 0; i < 18; i++) {
        var y0 = Math.random() * (this.DROP - 6);
        var t = y0 / this.DROP;
        var half = (this.MOUTH + t * (this.W - 6 - this.MOUTH)) / 2;
        var m = doc.createElement('i');
        m.style.left = Math.round(this.W / 2 + (Math.random() * 2 - 1) * half * 0.82) + 'px';
        m.style.top = Math.round(y0) + 'px';
        m.style.setProperty('--fall', Math.round(this.DROP - y0 + 4) + 'px');
        m.style.animationDuration = (3.6 + Math.random() * 4.2).toFixed(2) + 's';
        m.style.animationDelay = (-Math.random() * 8).toFixed(2) + 's';
        frag.appendChild(m);
      }
      el.lampDust.appendChild(frag);
    }
  };

  /* ---------------------------------------------------------------- 4 --- */

  function toShelf() {
    setScene('shelf');
    // both books are back in their slots, so neither is the one being taken
    el.spine.classList.remove('is-taken');
    el.spineBlue.classList.remove('is-taken');
    el.deskBook.hidden = true;
    el.deskBook.classList.remove('is-dropping');
    el.reader.hidden = true;
    Os.close(true);
    say('TAKE A BOOK OFF THE SHELF');
    camera(shots.shelf);
    floors();
    if (history.replaceState) history.replaceState(null, '', location.pathname);
  }

  /* The desk with nothing on it. Reached by the down arrow rather than by
     taking a book, so there is no book on it — that is the whole difference
     between this and the `desk` scene. */
  function toDesk() {
    setScene('desk-idle');
    el.deskBook.hidden = true;
    el.deskBook.classList.remove('is-dropping');
    el.reader.hidden = true;
    Os.close(true);
    say('CLICK THE COMPUTER');
    camera(shots.deskIdle);
    Lamp.nudge(0.5);
    floors();
    if (history.replaceState) history.replaceState(null, '', '#desk');
  }

  /* An arrow is only offered when there is somewhere to go. */
  function floors() {
    var s = scene();
    // 'desk' is the book-just-landed scene: going up is the way to put it
    // back, and it is the only way out of there short of opening the book
    el.goUp.disabled = !(s === 'desk-idle' || s === 'desk');
    el.goDown.disabled = (s !== 'shelf');
  }

  function takeBook(which) {
    if (scene() !== 'shelf' || busy) return;
    busy = true;
    which = which || 'portfolio';
    setVolume(which);
    body.setAttribute('data-taking', which);

    // Mark the one book that is leaving the shelf. Everything the animation
    // does — the tip-out, the fade — hangs off this class, so the other book
    // is untouched and simply stays where it is.
    var taken = which === 'certs' ? el.spineBlue : el.spine;
    el.spine.classList.toggle('is-taken', taken === el.spine);
    el.spineBlue.classList.toggle('is-taken', taken === el.spineBlue);

    Sfx.boot();
    Sfx.click();
    el.hand.classList.add('is-press');

    wait(120, function () {
      el.hand.classList.remove('is-press');
      setScene('pull');
      Sfx.pull();
      camera(which === 'certs' ? shots.pullCerts : shots.pull);
    });

    // the camera drops to the desk while the book falls into frame
    wait(760, function () {
      setScene('drop');
      camera(shots.desk);
      el.deskBook.hidden = false;
      // reflow so the animation restarts reliably on a repeat visit
      void el.deskBook.offsetWidth;
      el.deskBook.classList.add('is-dropping');
    });

    wait(1500, function () {
      Sfx.thud();
      puff();
    });

    wait(1760, function () {
      setScene('desk');
      el.deskBook.classList.remove('is-dropping');
      say('CLICK THE BOOK TO OPEN');
      floors();
      busy = false;
    });
  }

  /* ------------------------------------------------------------- 4b --- */
  /* The computer. Same trick as the book: the camera pushes into the glass
     until the drawn 84x48 screen is the viewport, and the HTML desktop fades
     in over it. Painting the write-ups into the sprite would have made them
     unreadable, unselectable and invisible to a search engine. */

  var Os = {
    apps: [],
    wins: [],
    typing: null,

    init: function () {
      var self = this;
      this.apps = $$('.app', el.osDesktop);
      this.wins = $$('.win', el.osWins);
      el.osIdx.textContent = String(this.apps.length);

      this.apps.forEach(function (a) {
        a.setAttribute('aria-expanded', 'false');
        a.addEventListener('click', function () { self.run(a.getAttribute('data-app')); });
      });
      $$('[data-close]', el.osWins).forEach(function (b) {
        b.addEventListener('click', function () { self.close(); });
      });
      el.pc.addEventListener('click', function () { self.enter(); });
      el.osBack.addEventListener('click', function () { self.leave(); });
      window.addEventListener('resize', function () { self.fitWindows(); }, { passive: true });
      Web.init();
    },

    /* Where a project window may start: just under the first row of icons.
       Measured, because the icons must not move when a window opens and the
       window must not slice through them — the two constraints only meet if
       the number is read off the real layout. */
    fitWindows: function () {
      if (!this.apps.length) return;
      var main = el.osDesktop.parentNode.getBoundingClientRect();
      var rowTop = this.apps[0].getBoundingClientRect().top;
      var bottom = 0;
      this.apps.forEach(function (a) {
        var r = a.getBoundingClientRect();
        if (Math.abs(r.top - rowTop) < 4) bottom = Math.max(bottom, r.bottom);
      });
      root.style.setProperty('--win-top', Math.round(bottom - main.top + 10) + 'px');
    },

    enter: function () {
      if (scene() !== 'desk-idle' || busy) return;
      busy = true;
      Sfx.boot();
      Sfx.click();
      setScene('pc');
      camera(shots.screen);
      el.os.hidden = false;
      this.close(true);
      this.fitWindows();
      this.bootSequence();
    },

    /* Three lines typed onto the phosphor before the desktop appears. It
       covers the camera push, and a machine that switches on instantly is the
       one thing a CRT never did. */
    bootSequence: function () {
      var self = this;
      var lines = [
        'HUSSAIN OS 1.0',
        'READING C:\\PROJECTS ...',
        String(this.apps.length) + ' ITEMS FOUND. READY.'
      ];
      clearTimeout(this.typing);
      el.osBoot.hidden = false;
      el.osBoot.textContent = '';
      el.osDesktop.style.visibility = 'hidden';

      var i = 0;
      (function step() {
        if (i < lines.length) {
          el.osBoot.textContent += (i ? '\n' : '') + lines[i];
          Sfx.tone(880 + i * 120, 0.05, 'square', 0.035);
          i++;
          self.typing = wait(reduceMotion ? 0 : 380, step);
        } else {
          self.typing = wait(reduceMotion ? 0 : 420, function () {
            el.osBoot.hidden = true;
            el.osDesktop.style.visibility = '';
            busy = false;
          });
        }
      })();
    },

    run: function (slug) {
      Web.close();
      this.fitWindows();
      this.wins.forEach(function (w) {
        w.hidden = (w.getAttribute('data-app') !== slug);
      });
      this.apps.forEach(function (a) {
        a.setAttribute('aria-expanded', String(a.getAttribute('data-app') === slug));
      });
      var win = this.wins.filter(function (w) { return !w.hidden; })[0];
      if (!win) return;
      el.osPath.textContent = 'C:\\PROJECTS\\' + slug.toUpperCase();
      el.osTip.textContent = 'ESC OR X TO CLOSE';
      body.classList.add('os-busy');
      Sfx.click();
      // focus the window so a keyboard user lands inside what just opened
      var x = $('[data-close]', win);
      if (x) x.focus();
      requestAnimationFrame(function () { $('.win__body', win).scrollTop = 0; });
    },

    /* `silent` is used when leaving the machine entirely: there is no window
       to animate away, we just need the state reset for next time. */
    close: function (silent) {
      if (Web.isOpen()) Web.close();
      this.wins.forEach(function (w) { w.hidden = true; });
      this.apps.forEach(function (a) { a.setAttribute('aria-expanded', 'false'); });
      el.osPath.textContent = 'C:\\PROJECTS';
      el.osTip.textContent = 'PICK A PROJECT';
      body.classList.remove('os-busy');
      if (!silent) Sfx.click();
    },

    leave: function () {
      if (scene() !== 'pc') return;
      clearTimeout(this.typing);
      el.osDesktop.style.visibility = '';
      el.osBoot.hidden = true;
      this.close(true);
      el.os.hidden = true;
      busy = false;
      toDesk();
    },

    isOpen: function () { return scene() === 'pc'; }
  };

  /* ------------------------------------------------------------- 4c --- */
  /* The browser. A live project opens inside the portfolio instead of
     throwing the visitor out of it.

     The hard part is not the frame, it is failing well. A page that refuses
     to be framed cannot be detected from script: Chrome fires `load` on the
     blocked result and the frame reads as cross-origin exactly like a page
     that worked. So there are two safety nets — a watchdog for the case where
     nothing ever loads, and a NEW TAB control that is always on the bar, not
     hidden behind an error state that may never appear. */

  var Web = {
    url: '',
    watchdog: null,
    hintTimer: null,
    settled: false,

    init: function () {
      var self = this;

      el.webFrame.addEventListener('load', function () {
        // about:blank fires load too; only a real navigation counts
        if (!self.url || el.webFrame.getAttribute('src') === 'about:blank') return;
        self.settle();
      });

      el.webX.addEventListener('click', function () { self.close(); });
      el.webReload.addEventListener('click', function () { self.open(self.url); });

      // OPEN SITE stays a real anchor so middle-click, ctrl-click and a
      // no-JavaScript visitor all still reach the site. The plain click is
      // the only one we take over.
      $$('.oslink[href^="http"]', el.osWins).forEach(function (a) {
        a.addEventListener('click', function (e) {
          if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
          e.preventDefault();
          self.open(a.getAttribute('href'));
        });
      });
    },

    open: function (url) {
      if (!url) return;
      this.url = url;
      this.settled = false;
      clearTimeout(this.watchdog);

      el.webUrl.textContent = url.replace(/^https?:\/\//, '');
      el.webTab.href = url;
      el.webOut.href = url;
      el.webHintOut.href = url;
      el.webLoad.hidden = false;
      el.webHint.hidden = true;
      el.webFail.hidden = true;
      el.web.hidden = false;
      body.classList.add('os-web');

      // reset to about:blank first, or reopening the same project shows the
      // previous frame with no load event and the spinner never clears
      el.webFrame.setAttribute('src', 'about:blank');
      var frame = el.webFrame;
      requestAnimationFrame(function () { frame.setAttribute('src', url); });

      Sfx.click();
      el.webX.focus();

      var self = this;
      clearTimeout(this.hintTimer);
      // Only for the case where the frame never reports back at all. It is NOT
      // a blocked-page detector: a page blocked by X-Frame-Options fires load
      // like any other, so this timer would never see it.
      this.watchdog = setTimeout(function () {
        if (!self.settled) self.fail();
      }, 15000);
    },

    settle: function () {
      var self = this;
      this.settled = true;
      clearTimeout(this.watchdog);
      el.webLoad.hidden = true;

      // The frame says it loaded. Whether anything is actually visible in it
      // is unknowable from here, so offer the way out for a few seconds and
      // then get out of the way.
      el.webHint.hidden = false;
      clearTimeout(this.hintTimer);
      this.hintTimer = setTimeout(function () {
        el.webHint.hidden = true;
        self = null;
      }, 7000);
    },

    fail: function () {
      el.webLoad.hidden = true;
      el.webHint.hidden = true;
      el.webFail.hidden = false;
    },

    close: function () {
      if (el.web.hidden) return;          // nothing open; don't click at nobody
      clearTimeout(this.watchdog);
      clearTimeout(this.hintTimer);
      el.webHint.hidden = true;
      this.settled = false;
      this.url = '';
      el.web.hidden = true;
      el.webFrame.setAttribute('src', 'about:blank');   // stop it running
      body.classList.remove('os-web');
      Sfx.click();
    },

    isOpen: function () { return !el.web.hidden; }
  };

  /* a little cloud kicked up where the book lands */
  function puff() {
    for (var i = 0; i < 10; i++) {
      var p = doc.createElement('i');
      p.style.left = (208 + Math.random() * 92) + 'px';
      p.style.top = (394 + Math.random() * 6) + 'px';
      p.style.animationDuration = '1.1s';
      p.style.animationDelay = (Math.random() * 0.16) + 's';
      el.dust.appendChild(p);
      (function (node) { setTimeout(function () { node.remove(); }, 1500); })(p);
    }
  }

  function openBook() {
    if (scene() !== 'desk' || busy) return;
    busy = true;
    Sfx.open();
    setScene('open');
    camera(shots.open);

    // hand over to the reading UI at peak zoom, green cover to green cover
    wait(880, function () {
      setScene('read');
      el.reader.hidden = false;
      el.hintKeys.hidden = false;
      show(current);
      requestAnimationFrame(function () { Critter.place(current); });
      busy = false;
      var page = $('.page--l', spreads[current]) || $('.page', spreads[current]);
      if (page) { page.setAttribute('tabindex', '-1'); page.focus({ preventScroll: true }); }
    });
  }

  /* ---------------------------------------------------------------- 5 --- */

  function show(i) {
    spreads.forEach(function (s, k) { s.hidden = (k !== i); });
    current = i;
    el.pgNow.textContent = String(i + 1);
    el.prev.disabled = (i === 0);
    el.next.disabled = (i === spreads.length - 1);

    var tab = spreads[i].getAttribute('data-tab');
    if (vol === 'portfolio') {
      $$('button', el.tabs).forEach(function (b) {
        var target = spreads[+b.getAttribute('data-goto')];
        b.setAttribute('aria-current', String(!!target && target.getAttribute('data-tab') === tab));
      });
    }

    if (history.replaceState) history.replaceState(null, '', '#' + tab);
    $$('.page', spreads[i]).forEach(function (p) { p.scrollTop = 0; });
    requestAnimationFrame(function () { Critter.place(i); });
    AutoRead.begin(i);
  }

  var canFlip = function () {
    return !reduceMotion && window.innerWidth > 900;
  };

  /* A turn takes ~820ms. Presses that land during one used to be dropped on
     the floor, so tapping the arrow key quickly skipped pages. Remember the
     most recent request instead and run it as soon as the leaf settles. */
  var queued = null;

  function turn(dir) {
    if (busy) { queued = function () { turn(dir); }; return; }
    goTo(current + dir);
  }

  /* -- the curl ----------------------------------------------------------
     The leaf is sliced into nested vertical strips. Each strip is rotated a
     little relative to its parent, so the chain traces a curved surface.

     Angles per frame:
       total  = -180deg * eased(t)          the leaf's overall swing
       bend   = peaks in the middle of the turn, zero at both ends
       hinge  = total * (1 - bend)          most of the swing at the spine
       rest   = total * bend / (N - 1)      shared out to curve the free end

     At t=0 and t=1 bend is 0, so the page is perfectly flat when it starts
     and when it lands — it only bows while it is in the air. */

  var Curl = {
    // 10 strips: 8 reads as a hard-edged fan, past ~12 the extra clones cost
    // more than the smoothness is worth
    N: 10,
    segs: [],
    shades: [],

    /* The page clone must not carry its scroll trail: the SVG inside uses an
       id for its clipPath, and duplicating that id breaks the clip on the
       original. A turning leaf has no scroll position anyway. */
    cleanClone: function (page) {
      var node = page.cloneNode(true);
      var t = node.querySelector('.trail');
      if (t) t.parentNode.removeChild(t);
      node.classList.remove('has-trail');
      return node;
    },

    build: function (dir, fromPage, toPage) {
      var fwd = dir > 0;
      var box = fromPage.getBoundingClientRect();
      var dest = toPage.getBoundingClientRect();
      var w = box.width, segW = w / this.N;

      /* Lay the leaf exactly over the page it comes from, measured.
         It used to inherit top/height/left from CSS, which resolve against the
         board's PADDING box — so raising the board's vertical padding to make
         room for the page-edge bands made the turning leaf 60px taller than
         the page it was supposed to be. Measure, don't assume. */
      // parentNode, not offsetParent: the leaf is display:none until it is
      // built, and a hidden element has no offsetParent.
      // getBoundingClientRect includes the board's border but absolute
      // positioning is relative to its padding box, so take the border off.
      var boardEl = el.curl.parentNode;
      var board = boardEl.getBoundingClientRect();
      var bx = board.left + boardEl.clientLeft;
      var by = board.top + boardEl.clientTop;
      el.curl.className = 'curl ' + (fwd ? 'curl--fwd' : 'curl--back');
      el.curl.style.left = (box.left - bx) + 'px';
      el.curl.style.top = (box.top - by) + 'px';
      el.curl.style.width = w + 'px';
      el.curl.style.height = box.height + 'px';
      el.curl.innerHTML = '';

      this.segs = [];
      this.shades = [];

      var edge = fwd ? 'left' : 'right';
      var parent = el.curl;

      for (var i = 0; i < this.N; i++) {
        var seg = doc.createElement('div');
        seg.className = 'curl__seg';
        seg.style.width = (w - i * segW) + 'px';
        seg.style[edge] = (i === 0 ? 0 : segW) + 'px';

        var face = doc.createElement('div');
        face.className = 'curl__face';
        // +1px so neighbouring strips overlap; without it sub-pixel gaps show
        // up as bright hairlines down the curve
        face.style.width = (segW + 1) + 'px';

        // Both sides are built now, before the first frame. The earlier
        // version rewrote innerHTML on every strip at the half-way point,
        // which forced a reflow in the middle of the animation and spiked one
        // frame to 116ms. Swapping sides is now just a class change.
        var front = doc.createElement('div');
        front.className = 'curl__inner curl__inner--front';
        front.style.width = w + 'px';
        front.style[edge] = (-i * segW) + 'px';
        front.appendChild(this.cleanClone(fromPage));

        var back = doc.createElement('div');
        back.className = 'curl__inner curl__inner--back';
        back.style.width = w + 'px';
        back.style[edge] = (-i * segW) + 'px';
        back.appendChild(this.cleanClone(toPage));

        /* The shade belongs INSIDE the face. A segment is as wide as the whole
           remaining leaf (it has to be, so its children fit), so a shade sized
           to the segment covered everything to its right — ten translucent
           rectangles stacking up into ten visible vertical bands. */
        var shade = doc.createElement('div');
        shade.className = 'curl__shade';
        shade.style.width = segW + 'px';   // not segW+1: no double-darkened seam

        face.appendChild(front);
        face.appendChild(back);
        face.appendChild(shade);
        seg.appendChild(face);
        parent.appendChild(seg);

        this.segs.push(seg);
        this.shades.push(shade);
        parent = seg;
      }

      // the shadow the lifting leaf throws onto the page it uncovers
      el.curlCast.style.left = (dest.left - bx) + 'px';
      el.curlCast.style.top = (dest.top - by) + 'px';
      el.curlCast.style.width = dest.width + 'px';
      el.curlCast.style.height = dest.height + 'px';
      el.curlCast.style.transform = fwd ? 'none' : 'scaleX(-1)';
      el.curlCast.hidden = false;
      el.curl.hidden = false;
    },

    frame: function (t, dir) {
      var sign = dir > 0 ? -1 : 1;

      // ease the swing; keep the bend on raw time so it stays symmetric
      var e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
      var total = 180 * e;
      var bend = 0.40 * Math.sin(Math.PI * t);

      var hinge = total * (1 - bend);
      var rest = (this.N > 1) ? (total * bend) / (this.N - 1) : 0;

      /* Paper lighting at a given accumulated angle: nearly flat-on it picks
         up a faint sheen, and as it turns away it falls into shadow. Returning
         a colour rather than just an alpha lets one gradient carry both. */
      var tintAt = function (k) {
        var lit = Math.abs(Math.cos((hinge + rest * k) * Math.PI / 180));
        if (lit > 0.86) {
          return 'rgba(255,250,236,' + ((lit - 0.86) * 1.5).toFixed(3) + ')';
        }
        return 'rgba(24,20,30,' + ((0.86 - lit) * 0.9).toFixed(3) + ')';
      };

      for (var i = 0; i < this.N; i++) {
        this.segs[i].style.transform =
          'rotateY(' + ((i === 0 ? hinge : rest) * sign) + 'deg)';

        /* Each strip crosses edge-on at its own moment, because the curve
           means they are not all at the same angle. Swapping every strip to
           the far side at once showed the destination page mirrored on the
           strips that were still facing the reader. */
        this.segs[i].classList.toggle('is-back', (hinge + rest * i) > 90);

        // A flat tint per strip makes each one a visible band. Ramping the
        // tint across the strip to meet its neighbour's value hides the seam
        // and reads as one continuous curved surface.
        this.shades[i].style.background =
          'linear-gradient(to right, ' + tintAt(i) + ', ' + tintAt(i + 1) + ')';
      }

      // the shadow the leaf throws is strongest when it stands upright
      el.curlCast.style.opacity = Math.pow(Math.sin(Math.PI * t), 0.7).toFixed(3);
    },

    clear: function () {
      el.curl.hidden = true;
      el.curlCast.hidden = true;
      el.curl.innerHTML = '';
      this.segs = [];
      this.shades = [];
    }
  };

  function goTo(target) {
    if (busy) { queued = function () { goTo(target); }; return; }
    if (target === current || target < 0 || target >= spreads.length) return;

    Sfx.page();

    if (!canFlip()) { show(target); return; }


    busy = true;
    var from = spreads[current];
    var to = spreads[target];
    var fwd = target > current;

    // A closing page runs across the whole opening and so has neither half.
    // Fall back to whatever page it does have — without this, turning onto the
    // contact spread handed Curl a null and threw before the turn started.
    var half = function (sp, cls) { return $(cls, sp) || $('.page', sp); };
    var fromPage = fwd ? half(from, '.page--r') : half(from, '.page--l');
    var toPage = fwd ? half(to, '.page--l') : half(to, '.page--r');

    Curl.build(fwd ? 1 : -1, fromPage, toPage);

    // reveal the destination underneath straight away; the leaf covers the swap
    show(target);

    var DUR = 820;
    var t0 = null;

    function step(now) {
      if (t0 === null) t0 = now;
      var t = Math.min(1, (now - t0) / DUR);
      Curl.frame(t, fwd ? 1 : -1);
      if (t < 1) {
        requestAnimationFrame(step);
      } else {
        Curl.clear();
        busy = false;
        var q = queued;
        queued = null;
        if (q) q();
      }
    }

    // one frame of breathing room so the build's layout cost lands before
    // the timer starts, instead of eating the first animated frame
    Curl.frame(0, fwd ? 1 : -1);
    requestAnimationFrame(function () { requestAnimationFrame(step); });
  }

  /* -- the beetle --------------------------------------------------------
     Ambient life rather than a control. It picks a spot on the spread, walks
     there, stops to think, picks another. It faces where it is going (the
     sprite sheet holds eight headings), its legs alternate as it moves, and
     it scurries if the pointer comes near.

     It appears on every other spread, not all of them, so it stays a small
     surprise instead of wallpaper. */

  var Critter = {
    SPREADS: [1, 3, 5, 7],   // which spreads get one
    CELL: 24,
    SPEED: 20,               // px per second, ambling
    FLEE: 130,               // px per second, startled
    SCARE: 74,               // how close the pointer has to get

    node: null,
    host: null,
    x: 0, y: 0,
    tx: 0, ty: 0,
    dir: 4,
    phase: 0,
    stepAcc: 0,
    waitUntil: 0,
    fleeing: false,
    last: 0,
    running: false,

    enabled: function () {
      return !reduceMotion &&
             window.innerWidth > 900;
    },

    ensure: function () {
      if (this.node) return;
      this.node = doc.createElement('div');
      this.node.className = 'critter';
      this.node.setAttribute('aria-hidden', 'true');
    },

    bounds: function () {
      var r = this.host.getBoundingClientRect();
      return { w: r.width, h: r.height, rect: r };
    },

    pickTarget: function () {
      var b = this.bounds();
      var m = 26;
      this.tx = m + Math.random() * Math.max(1, b.w - m * 2);
      this.ty = m + Math.random() * Math.max(1, b.h - m * 2);
    },

    /* put one on the current spread, or take it away */
    place: function (index) {
      if (!this.enabled() || this.SPREADS.indexOf(index) === -1) {
        this.stop();
        return;
      }

      this.ensure();
      this.host = spreads[index];
      this.host.appendChild(this.node);

      var b = this.bounds();
      if (!b.w) return;

      // start somewhere random, already part-way through its wander
      this.x = 26 + Math.random() * Math.max(1, b.w - 52);
      this.y = 26 + Math.random() * Math.max(1, b.h - 52);
      this.pickTarget();
      this.waitUntil = 0;
      this.fleeing = false;
      this.draw();

      this.node.classList.add('is-awake');
      this.start();
    },

    stop: function () {
      this.running = false;
      if (this.node) {
        this.node.classList.remove('is-awake');
        if (this.node.parentNode) this.node.parentNode.removeChild(this.node);
      }
    },

    start: function () {
      if (this.running) return;
      this.running = true;
      this.last = 0;
      requestAnimationFrame(this.tick.bind(this));
    },

    scare: function (clientX, clientY) {
      if (!this.running || !this.host) return;
      var b = this.bounds();
      var px = clientX - b.rect.left, py = clientY - b.rect.top;
      var dx = this.x - px, dy = this.y - py;
      var d = Math.sqrt(dx * dx + dy * dy);
      if (d > this.SCARE) return;

      // bolt for a point directly away from the pointer, kept on the page
      var k = 190 / (d || 1);
      this.tx = Math.max(20, Math.min(b.w - 20, this.x + dx * k));
      this.ty = Math.max(20, Math.min(b.h - 20, this.y + dy * k));
      this.fleeing = true;
      this.waitUntil = 0;
    },

    tick: function (now) {
      if (!this.running) return;
      if (!this.last) this.last = now;
      var dt = Math.min(0.05, (now - this.last) / 1000);
      this.last = now;

      if (now >= this.waitUntil) {
        var dx = this.tx - this.x, dy = this.ty - this.y;
        var d = Math.sqrt(dx * dx + dy * dy);

        if (d < 3) {
          // arrived: think for a moment, then choose somewhere new
          this.fleeing = false;
          this.waitUntil = now + 700 + Math.random() * 3000;
          this.pickTarget();
        } else {
          var sp = (this.fleeing ? this.FLEE : this.SPEED) * dt;
          this.x += dx / d * Math.min(sp, d);
          this.y += dy / d * Math.min(sp, d);

          // heading, quantised to the eight drawn directions
          var ang = Math.atan2(dx, -dy) * 180 / Math.PI;
          this.dir = ((Math.round(ang / 45) % 8) + 8) % 8;

          // step the legs by distance covered, not by time
          this.stepAcc += sp;
          if (this.stepAcc > 5) { this.stepAcc = 0; this.phase ^= 1; }
        }
        this.draw();
      }

      requestAnimationFrame(this.tick.bind(this));
    },

    draw: function () {
      var half = this.CELL / 2;
      this.node.style.transform =
        'translate(' + Math.round(this.x - half) + 'px,' +
                       Math.round(this.y - half) + 'px)';
      this.node.style.backgroundPosition =
        (-this.dir * this.CELL) + 'px ' + (-this.phase * this.CELL) + 'px';
    }
  };

  /* -- auto-read ---------------------------------------------------------
     Pages that overflow drift down on their own, slowly, so nothing is left
     unreachable now that there is no scrollbar to hint at it. Any input —
     wheel, drag, touch, arrow key — hands control straight back to the reader,
     and the drift picks up again five seconds after they stop. */

  var AutoRead = {
    SPEED: 20,          // px per second
    IDLE: 5000,         // how long to wait after the reader takes over
    LEAD_IN: 1200,      // let the page turn finish before creeping

    items: [],
    running: false,
    last: 0,
    holdUntil: 0,

    enabled: function () {
      return !reduceMotion &&
             window.innerWidth > 900;
    },

    stop: function () {
      this.running = false;
      this.items = [];
    },

    begin: function (index) {
      this.stop();
      if (!this.enabled() || !spreads[index]) return;

      var pages = $$('.page', spreads[index]).filter(function (p) {
        return p.scrollHeight - p.clientHeight > 8;
      });
      if (!pages.length) return;

      this.items = pages.map(function (p) {
        return { page: p, pos: p.scrollTop };
      });
      this.holdUntil = performance.now() + this.LEAD_IN;
      this.last = 0;
      this.running = true;
      requestAnimationFrame(this.tick.bind(this));
    },

    /* the reader did something — back off, and resync to where they left it */
    nudge: function () {
      if (!this.running) return;
      this.holdUntil = performance.now() + this.IDLE;
      this.items.forEach(function (it) { it.pos = it.page.scrollTop; });
    },

    tick: function (now) {
      if (!this.running) return;
      if (!this.last) this.last = now;
      var dt = Math.min(0.05, (now - this.last) / 1000);
      this.last = now;

      // never creep during a page turn
      if (!busy && now >= this.holdUntil) {
        var step = this.SPEED * dt;
        this.items.forEach(function (it) {
          var max = it.page.scrollHeight - it.page.clientHeight;
          if (it.pos >= max) return;
          it.pos = Math.min(max, it.pos + step);
          // fractional accumulator: scrollTop is integer, and at 20px/s a
          // per-frame integer step would round to zero and never move
          it.page.scrollTop = it.pos;
        });
      }

      requestAnimationFrame(this.tick.bind(this));
    }
  };

  /* ---------------------------------------------------------------- 6 --- */

  var ASSETS = [
    'assets/px/room.png',
    'assets/px/book_spine.png',
    'assets/px/book_cover_front.png',
    'assets/px/book_endpaper.png',
    'assets/px/hand.png',
    'assets/px/avatar.png',
    'assets/px/tex_parchment.png',
    'assets/px/tex_leather.png',
    'assets/px/tex_wood.png'
  ];

  function preload(done) {
    var loaded = 0;
    var total = ASSETS.length;

    var tick = function () {
      loaded++;
      el.bootFill.style.width = Math.round(loaded / total * 100) + '%';
      if (loaded >= total) {
        el.bootHint.textContent = 'READY';
        wait(360, done);
      }
    };

    ASSETS.forEach(function (src) {
      var img = new Image();
      img.onload = tick;
      img.onerror = tick;   // a missing sprite must not strand the visitor
      img.src = src;
    });

    // never let a stalled request hold the page hostage
    setTimeout(function () { if (loaded < total) { loaded = total - 1; tick(); } }, 6000);
  }

  function tabFromHash() {
    var h = (location.hash || '').replace('#', '');
    if (!h) return -1;
    if (h === 'certs' || h === 'certificates') { setVolume('certs'); return 0; }
    setVolume('portfolio');
    for (var i = 0; i < spreads.length; i++) {
      if (spreads[i].getAttribute('data-tab') === h) return i;
    }
    return -1;
  }

  function jumpToReader(index) {
    setScene('read');
    el.deskBook.hidden = false;
    el.reader.hidden = false;
    el.hintKeys.hidden = false;
    camera(shots.open, true);
    show(index);   // show() already schedules the beetle for that spread
  }

  function start() {
    body.classList.remove('booting');
    seedDust(20);
    Cursor.init();
    Lamp.init();
    Os.init();
    window.addEventListener('resize', function () { Critter.place(current); }, { passive: true });

    // #desk and #projects drop you straight at the machine
    var h = (location.hash || '').replace('#', '').toLowerCase();
    if (h === 'desk' || h === 'projects') {
      toDesk();
      if (h === 'projects') wait(700, function () { Os.enter(); });
      return;
    }

    var deep = tabFromHash();
    if (deep >= 0 || reduceMotion) {
      // a shared link, or someone who asked for less motion, gets the book
      jumpToReader(deep >= 0 ? deep : 0);
    } else {
      toShelf();
    }
  }

  /* -- wiring ------------------------------------------------------------ */

  el.spine.addEventListener('click', function () { takeBook('portfolio'); });
  el.spineBlue.addEventListener('click', function () { takeBook('certs'); });

  var toCerts = $('#toCerts');
  if (toCerts) {
    toCerts.addEventListener('click', function () {
      setVolume('certs');
      show(0);
      Sfx.page();
    });
  }
  el.deskBook.addEventListener('click', openBook);
  el.prompt.addEventListener('click', function () {
    if (scene() === 'desk') openBook();
  });

  el.next.addEventListener('click', function () { turn(1); });
  el.prev.addEventListener('click', function () { turn(-1); });

  $$('button', el.tabs).forEach(function (b) {
    b.addEventListener('click', function () {
      // a tab can jump several spreads at once — goTo turns one leaf in the
      // right direction and lands directly on the target
      goTo(+b.getAttribute('data-goto'));
    });
  });

  el.goUp.addEventListener('click', function () { if (!busy) toShelf(); });
  el.goDown.addEventListener('click', function () { if (!busy) toDesk(); });

  el.btnShelf.addEventListener('click', function () {
    el.reader.hidden = true;
    el.hintKeys.hidden = true;
    AutoRead.stop();
    toShelf();
  });



  /* any real input hands scrolling back to the reader for a few seconds */
  ['wheel', 'pointerdown', 'touchstart', 'keydown'].forEach(function (ev) {
    el.reader.addEventListener(ev, function () { AutoRead.nudge(); }, { passive: true });
  });

  /* Audio cannot start before the visitor has touched something, so the
     context is created and resumed on the first gesture and then left alone.
     There is no sound toggle: it is on. */
  (function () {
    var arm = function () {
      Sfx.boot();
      if (Sfx.ctx && Sfx.ctx.state === 'suspended') Sfx.ctx.resume();
      ['pointerdown', 'keydown', 'touchstart'].forEach(function (ev) {
        doc.removeEventListener(ev, arm, true);
      });
    };
    ['pointerdown', 'keydown', 'touchstart'].forEach(function (ev) {
      doc.addEventListener(ev, arm, true);
    });
  })();

  /* Belt and braces on the native drag: -webkit-user-drag is not a standard
     property, so anything that ignores it is caught here instead. Only images
     are blocked — selecting and dragging the CV text is deliberate. */
  doc.addEventListener('dragstart', function (e) {
    if (e.target && e.target.tagName === 'IMG') e.preventDefault();
  });

  /* the beetle bolts if the pointer gets close */
  doc.addEventListener('pointermove', function (e) {
    if (e.pointerType === 'touch') return;
    Critter.scare(e.clientX, e.clientY);
  }, { passive: true });

  doc.addEventListener('keydown', function (e) {

    if (scene() === 'read') {
      if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); turn(1); }
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); turn(-1); }
      if (e.key === 'Home') { e.preventDefault(); show(0); }
      if (e.key === 'End') { e.preventDefault(); show(spreads.length - 1); }
      if (e.key === 'Escape') { el.reader.hidden = true; el.hintKeys.hidden = true; toShelf(); }
      return;
    }

    if (scene() === 'pc') {
      // Esc backs out one level: an open project first, then the machine
      if (e.key === 'Escape') {
        e.preventDefault();
        // one layer at a time: the site, then the project, then the machine
        if (Web.isOpen()) { Web.close(); return; }
        var openWin = Os.wins.filter(function (w) { return !w.hidden; })[0];
        if (openWin) Os.close(); else Os.leave();
      }
      return;
    }

    // up and down move between the bookcase and the desk
    if (e.key === 'ArrowUp' && scene() === 'desk-idle') { e.preventDefault(); toShelf(); return; }
    if (e.key === 'ArrowDown' && scene() === 'shelf') { e.preventDefault(); toDesk(); return; }

    if (e.key === 'Enter' || e.key === ' ') {
      if (scene() === 'desk') { e.preventDefault(); openBook(); }
      if (scene() === 'desk-idle' && doc.activeElement === body) { e.preventDefault(); Os.enter(); }
    }
  });

  /* swipe to turn on touch */
  (function () {
    var x0 = null, y0 = null;
    el.reader.addEventListener('touchstart', function (e) {
      x0 = e.changedTouches[0].clientX;
      y0 = e.changedTouches[0].clientY;
    }, { passive: true });

    el.reader.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      var dy = e.changedTouches[0].clientY - y0;
      // only a decisively horizontal swipe; vertical is scrolling the page
      if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.8) turn(dx < 0 ? 1 : -1);
      x0 = y0 = null;
    }, { passive: true });
  })();

  /* -- go ---------------------------------------------------------------- */

  setVolume('portfolio');
  camera(shots.shelf, true);
  preload(start);
})();
