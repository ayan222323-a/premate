/* =========================================================
   PrepMate — app.js
   One file for everything (this replaces main.js, which base.html
   never loaded). Sections: theme, nav, toasts, AI overlay, forms,
   interview, practice test, confetti.
   ========================================================= */
(function () {
  'use strict';

  const root = document.documentElement;
  const $ = (sel, ctx) => (ctx || document).querySelector(sel);
  const $$ = (sel, ctx) => Array.from((ctx || document).querySelectorAll(sel));
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 1. Theme ---------- */
  function applyTheme(theme, save) {
    root.setAttribute('data-theme', theme);
    if (save) {
      try { localStorage.setItem('pm-theme', theme); } catch (e) { /* private mode */ }
    }
    $$('.js-theme-toggle').forEach((btn) => {
      btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
      btn.setAttribute('aria-label', theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
    });
    window.dispatchEvent(new CustomEvent('pm-theme-changed', { detail: { theme: theme } }));
  }

  window.pmToggleTheme = function () {
    applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
  };

  function initTheme() {
    applyTheme(root.getAttribute('data-theme') || 'light', false);
    $$('.js-theme-toggle').forEach((btn) => btn.addEventListener('click', window.pmToggleTheme));
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      let saved = null;
      try { saved = localStorage.getItem('pm-theme'); } catch (err) { /* ignore */ }
      if (!saved) applyTheme(e.matches ? 'dark' : 'light', false);
    });
  }

  /* ---------- 2. Navigation ---------- */
  function firstSegment(path) {
    return path.split('/').filter(Boolean)[0] || '';
  }

  function highlightActiveNav() {
    const here = location.pathname;
    const hereSeg = firstSegment(here);
    $$('[data-nav]').forEach((link) => {
      let path;
      try { path = new URL(link.getAttribute('href'), location.origin).pathname; } catch (e) { return; }
      const active = path === here || (hereSeg !== '' && firstSegment(path) === hereSeg);
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }

  function initTopbarScroll() {
    const bar = $('.pm-topbar');
    if (!bar) return;
    const check = () => bar.classList.toggle('scrolled', window.scrollY > 8);
    window.addEventListener('scroll', check, { passive: true });
    check();
  }

  /* ---------- 3. Toasts ---------- */
  const TOAST_ICONS = {
    success: 'bi-check-circle-fill',
    error: 'bi-x-circle-fill',
    danger: 'bi-x-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill'
  };

  function wireToast(toast) {
    const close = $('.pm-toast-close', toast);
    const dismiss = () => {
      toast.classList.add('dismissing');
      setTimeout(() => toast.remove(), 320);
    };
    if (close) close.addEventListener('click', dismiss);
    setTimeout(dismiss, 5000);
  }

  window.pmToast = function (message, type) {
    type = TOAST_ICONS[type] ? type : 'info';
    let box = $('.pm-toast-container');
    if (!box) {
      box = document.createElement('div');
      box.className = 'pm-toast-container';
      document.body.appendChild(box);
    }
    const toast = document.createElement('div');
    toast.className = 'pm-toast toast-' + type;
    toast.setAttribute('role', 'alert');

    const icon = document.createElement('span');
    icon.className = 'pm-toast-icon';
    icon.innerHTML = '<i class="bi ' + TOAST_ICONS[type] + '" aria-hidden="true"></i>';

    const body = document.createElement('span');
    body.className = 'pm-toast-body';
    body.textContent = message;

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'pm-toast-close';
    close.setAttribute('aria-label', 'Close');
    close.innerHTML = '&times;';

    toast.append(icon, body, close);
    box.appendChild(toast);
    wireToast(toast);
  };

  /* ---------- 4. AI loading overlay + forms ---------- */
  const AI_PRESETS = {
    interview: {
      title: 'Reading your resume',
      sub: 'This takes about 10 to 20 seconds. Keep this tab open.',
      msgs: ['Reading your resume...', 'Writing questions for your target role...', 'Balancing easy and hard questions...', 'Almost ready...']
    },
    test: {
      title: 'Preparing your test',
      sub: 'This takes about 5 to 15 seconds. Keep this tab open.',
      msgs: ['Picking topics...', 'Writing questions and answer options...', 'Checking the answer key...', 'Almost ready...']
    },
    notes: {
      title: 'Writing your notes',
      sub: 'This takes about 5 to 15 seconds. Keep this tab open.',
      msgs: ['Collecting the key points...', 'Writing a short revision sheet...', 'Almost ready...']
    },
    default: {
      title: 'AI is working',
      sub: 'This takes a few seconds. Keep this tab open.',
      msgs: ['Working on it...', 'Almost ready...']
    }
  };

  let overlayTimer = null;

  function buildOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'pm-loading-overlay';
    overlay.className = 'pm-loading-overlay';
    overlay.setAttribute('role', 'status');
    overlay.setAttribute('aria-live', 'polite');
    overlay.innerHTML =
      '<div class="pm-loading-box">' +
      '<div class="pm-loading-title" id="pm-ai-title"></div>' +
      '<div class="pm-write" aria-hidden="true"><span></span><span></span><span></span></div>' +
      '<div class="pm-loading-status" id="pm-ai-status"></div>' +
      '<div class="pm-loading-sub" id="pm-ai-sub"></div>' +
      '</div>';
    document.body.appendChild(overlay);
    return overlay;
  }

  window.pmShowAiOverlay = function (kind) {
    const preset = AI_PRESETS[kind] || AI_PRESETS.default;
    const overlay = $('#pm-loading-overlay') || buildOverlay();
    const status = $('#pm-ai-status', overlay);
    $('#pm-ai-title', overlay).textContent = preset.title;
    $('#pm-ai-sub', overlay).textContent = preset.sub;
    status.textContent = preset.msgs[0];
    overlay.classList.add('active');

    clearInterval(overlayTimer);
    let i = 0;
    overlayTimer = setInterval(() => {
      i = Math.min(i + 1, preset.msgs.length - 1);
      status.style.opacity = '0';
      setTimeout(() => { status.textContent = preset.msgs[i]; status.style.opacity = '1'; }, 200);
    }, 3200);
  };

  function hideOverlay() {
    clearInterval(overlayTimer);
    const overlay = $('#pm-loading-overlay');
    if (overlay) overlay.classList.remove('active');
  }

  function setBusy(btn, html) {
    if (!btn) return;
    btn.dataset.originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = html;
  }

  function initAiForms() {
    $$('form[data-ai-loading]').forEach((form) => {
      form.addEventListener('submit', (e) => {
        if (form.dataset.submitted === '1') { e.preventDefault(); return; }
        if (!form.checkValidity()) { e.preventDefault(); form.reportValidity(); return; }
        form.dataset.submitted = '1';
        setBusy($('button[type="submit"]', form), '<span class="pm-spinner" aria-hidden="true"></span> Working...');
        window.pmShowAiOverlay(form.dataset.aiLoading);
      });
    });

    // Back/forward cache restores the page mid-submit: reset it.
    window.addEventListener('pageshow', (e) => {
      if (!e.persisted) return;
      hideOverlay();
      $$('form[data-submitted="1"]').forEach((form) => {
        form.dataset.submitted = '0';
        const btn = $('button[type="submit"]', form);
        if (btn && btn.dataset.originalHtml) { btn.innerHTML = btn.dataset.originalHtml; btn.disabled = false; }
      });
    });
  }

  /* ---------- 5. Auth + upload ---------- */
  function initPasswordToggles() {
    $$('.pm-password-toggle').forEach((btn) => {
      btn.addEventListener('click', () => {
        const input = $('input', btn.closest('.pm-input-wrap'));
        if (!input) return;
        const show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        btn.innerHTML = '<i class="bi ' + (show ? 'bi-eye-slash' : 'bi-eye') + '" aria-hidden="true"></i>';
        btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
      });
    });
  }

  function formatSize(bytes) {
    return bytes >= 1048576 ? (bytes / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(bytes / 1024)) + ' KB';
  }

  function initDropZone() {
    const zone = $('#pm-drop-zone');
    const input = $('#pm-file-input');
    const label = $('#pm-file-label');
    if (!zone || !input || !label) return;
    const text = $('span', label);

    function showFile(file) {
      const isPdf = /\.pdf$/i.test(file.name) || file.type === 'application/pdf';
      if (!isPdf || file.size > 5 * 1024 * 1024) {
        input.value = '';
        zone.classList.remove('has-file');
        label.classList.add('visible', 'error');
        text.textContent = 'Resume must be a PDF under 5 MB.';
        return;
      }
      label.classList.remove('error');
      label.classList.add('visible');
      zone.classList.add('has-file');
      text.textContent = file.name + ' (' + formatSize(file.size) + ')';
    }

    ['dragenter', 'dragover'].forEach((evt) => zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.add('drag-over'); }));
    ['dragleave', 'drop'].forEach((evt) => zone.addEventListener(evt, (e) => { e.preventDefault(); zone.classList.remove('drag-over'); }));
    zone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files.length) {
        input.files = e.dataTransfer.files;
        showFile(e.dataTransfer.files[0]);
      }
    });
    input.addEventListener('change', () => { if (input.files.length) showFile(input.files[0]); });
    zone.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.click(); }
    });
  }

  /* ---------- 6. Interview room ---------- */
  function initRoom() {
    const box = $('#pm-answer-box');
    const counter = $('#pm-char-counter');
    if (!box || !counter) return;

    function update() {
      const len = box.value.length;
      counter.textContent = len + (len === 1 ? ' character' : ' characters');
      counter.classList.toggle('good', len >= 200);
      counter.classList.toggle('warn', len >= 80 && len < 200);
    }
    box.addEventListener('input', update);
    update();

    box.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const form = box.closest('form');
        if (form) form.requestSubmit();
      }
    });

    const form = $('#pm-room-form');
    const submit = $('#pm-room-submit');
    if (form && submit) {
      form.addEventListener('submit', (e) => {
        if (submit.disabled) { e.preventDefault(); return; }
        setBusy(submit, '<span class="pm-spinner" aria-hidden="true"></span> Scoring your answer...');
      });
    }
  }

  /* ---------- 7. Practice test ---------- */
  function initTake() {
    const form = $('#pm-take-form');
    if (!form) return;
    const names = Array.from(new Set($$('input[type="radio"]', form).map((r) => r.name)));
    const answeredEl = $('#pm-answered');
    const meter = $('#pm-take-meter');
    const label = $('#pm-submit-label');
    const timer = $('#pm-timer');
    const total = names.length;

    function update() {
      const answered = names.filter((n) => form.querySelector('input[name="' + n + '"]:checked')).length;
      if (answeredEl) answeredEl.textContent = answered + ' / ' + total;
      if (meter) meter.style.setProperty('--pct', total ? (answered / total) * 100 : 0);
      if (label) {
        const left = total - answered;
        label.textContent = left > 0 ? 'Submit test (' + left + ' unanswered)' : 'Submit test';
      }
    }
    form.addEventListener('change', update);
    update();

    const started = Date.now();
    if (timer) {
      setInterval(() => {
        const s = Math.floor((Date.now() - started) / 1000);
        timer.textContent = String(Math.floor(s / 60)).padStart(2, '0') + ':' + String(s % 60).padStart(2, '0');
      }, 1000);
    }

    form.addEventListener('submit', (e) => {
      const btn = $('button[type="submit"]', form);
      if (btn && btn.disabled) { e.preventDefault(); return; }
      setBusy(btn, '<span class="pm-spinner" aria-hidden="true"></span> Checking answers...');
    });
  }

  /* ---------- 8. Confetti (one burst, only for good scores) ---------- */
  function initCelebrate() {
    if (reduceMotion || !$('[data-celebrate]')) return;
    setTimeout(() => {
      if (typeof window.confetti !== 'function') return;
      window.confetti({
        particleCount: 80,
        spread: 75,
        origin: { y: 0.35 },
        colors: ['#2b44e0', '#d92d20', '#ffe14d'],
        disableForReducedMotion: true
      });
    }, 1100);
  }

  /* ---------- Boot ---------- */
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    highlightActiveNav();
    initTopbarScroll();
    $$('.pm-toast').forEach(wireToast);
    initAiForms();
    initPasswordToggles();
    initDropZone();
    initRoom();
    initTake();
    initCelebrate();
  });
})();
