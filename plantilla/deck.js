// Navegación de la presentación y el modo ?revisar.
(() => {
  const root = document.documentElement;
  const slides = Array.from(document.querySelectorAll('.slide'));
  const total = slides.length;
  const pad = (n) => String(n).padStart(2, '0');
  const counter = document.querySelector('.nav .count');
  const progress = document.querySelector('.progress');
  const nav = document.querySelector('.nav');
  const hint = document.querySelector('.hint');
  const prevBtn = nav.querySelector('[data-go="prev"]');
  const nextBtn = nav.querySelector('[data-go="next"]');
  let cur = 0;

  slides.forEach((s, i) => {
    const pg = s.querySelector('.pg');
    if (pg) pg.textContent = pad(i + 1) + ' / ' + pad(total);
    s.setAttribute('aria-label', 'Diapositiva ' + (i + 1) + ' de ' + total);
  });

  const scrollMode = () => root.classList.contains('mode-scroll');

  function fit() {
    const w = window.innerWidth, h = window.innerHeight;
    const scroll = w < 760 || (w < 1000 && h > w);
    root.classList.toggle('mode-scroll', scroll);
    root.classList.toggle('mode-deck', !scroll);
    root.style.setProperty('--s', Math.min(w / 1920, h / 1080));
    slides.forEach((s, i) => {
      if (scroll || i === cur) s.removeAttribute('aria-hidden');
      else s.setAttribute('aria-hidden', 'true');
    });
  }

  function go(n) {
    n = Math.max(0, Math.min(total - 1, n));
    slides[cur].classList.remove('is-active');
    cur = n;
    slides[cur].classList.add('is-active');
    slides.forEach((s, i) => {
      if (scrollMode() || i === cur) s.removeAttribute('aria-hidden');
      else s.setAttribute('aria-hidden', 'true');
    });
    counter.textContent = pad(cur + 1) + ' / ' + pad(total);
    progress.style.width = ((cur + 1) / total * 100) + '%';
    prevBtn.disabled = cur === 0;
    nextBtn.disabled = cur === total - 1;
    try { history.replaceState(null, '', '#' + (cur + 1)); } catch (e) {}
  }

  function fullscreen() {
    const el = document.documentElement;
    if (!document.fullscreenElement) { (el.requestFullscreen || el.webkitRequestFullscreen || function () {}).call(el); }
    else { (document.exitFullscreen || document.webkitExitFullscreen || function () {}).call(document); }
  }

  document.addEventListener('keydown', (e) => {
    if (scrollMode() || e.metaKey || e.ctrlKey || e.altKey) return;
    const k = e.key;
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(k)) {
      if (k === 'Enter' && e.target.closest && e.target.closest('button')) return;
      e.preventDefault(); go(cur + 1);
    } else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(k)) {
      e.preventDefault(); go(cur - 1);
    } else if (k === 'Home') { e.preventDefault(); go(0); }
    else if (k === 'End') { e.preventDefault(); go(total - 1); }
    else if (k === 'f' || k === 'F') { fullscreen(); }
    wake();
  });

  nav.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    const a = b.dataset.go;
    if (a === 'prev') go(cur - 1);
    else if (a === 'next') go(cur + 1);
    else if (a === 'full') fullscreen();
  });

  let tx = null, ty = null;
  document.addEventListener('touchstart', (e) => { if (scrollMode()) return; tx = e.touches[0].clientX; ty = e.touches[0].clientY; }, { passive: true });
  document.addEventListener('touchend', (e) => {
    if (scrollMode() || tx === null) return;
    const dx = e.changedTouches[0].clientX - tx, dy = e.changedTouches[0].clientY - ty;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) go(cur + (dx < 0 ? 1 : -1));
    tx = ty = null;
  });

  let idle;
  function wake() {
    nav.classList.remove('idle'); hint.classList.remove('idle');
    clearTimeout(idle);
    idle = setTimeout(() => { nav.classList.add('idle'); hint.classList.add('idle'); }, 2600);
  }
  document.addEventListener('mousemove', wake);

  window.addEventListener('resize', fit);
  window.addEventListener('hashchange', () => {
    const n = parseInt(location.hash.slice(1), 10);
    if (n && n - 1 !== cur) go(n - 1);
  });

  fit();
  const start = parseInt(location.hash.slice(1), 10);
  go(start ? start - 1 : 0);
  requestAnimationFrame(() => requestAnimationFrame(() => root.classList.remove('no-anim')));
    wake();

  // ?revisar: marca en rojo lo que se sale del espacio de cada diapositiva (sobre el pie o por la derecha,
  // o texto que no cabe en su tarjeta) y deja la lista en <body data-desbordes>. Lo usa scripts/armar.py.
  if (/[?&]revisar\b/.test(location.search)) {
    root.classList.add('revisar');
    const revisar = () => {
      const malas = [];
      slides.forEach((s, i) => {
        const sr = s.getBoundingClientRect();
        const k = sr.width / 1920 || 1;
        const abajo = sr.top + 985 * k, derecha = sr.left + 1820 * k;
        let mal = false;
        s.querySelectorAll('*').forEach((el) => {
          if (el.closest('.foot, .screen, .aviso-desborde, .sr')) return;
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height) return;
          if (r.bottom > abajo + 1 || r.right > derecha + 1) { el.classList.add('desborde'); mal = true; }
        });
        s.querySelectorAll('.card, .tile, .mode, .pillar, .quote, .needs, .fact, .step, .row, .compare > div').forEach((el) => {
          if (el.scrollHeight > el.clientHeight + 2 || el.scrollWidth > el.clientWidth + 2) { el.classList.add('desborde'); mal = true; }
        });
        // Dentro de cada teléfono: nada puede quedar debajo del botón de abajo, la barra de pestañas o el borde.
        s.querySelectorAll('.screen').forEach((pantalla) => {
          const pr = pantalla.getBoundingClientRect();
          const tapa = pantalla.querySelector('.ap-btn, .tabbar');
          const limite = (tapa ? tapa.getBoundingClientRect().top + 2 : pr.bottom - 4);
          // Solo lo que se lee (textos, pills, íconos): una tarjeta puede pasar bajo la barra, como en una lista con scroll.
          pantalla.querySelectorAll('.ap *').forEach((el) => {
            const tieneTexto = Array.from(el.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
            if (!tieneTexto && !el.matches('.pill, .badge, svg')) return;
            const r = el.getBoundingClientRect();
            if (!r.width || !r.height || el.closest('.map')) return;
            if (r.bottom > limite + 1) { el.classList.add('desborde'); mal = true; }
          });
        });
        if (mal) {
          malas.push(i + 1);
          const aviso = document.createElement('div');
          aviso.className = 'aviso-desborde';
          aviso.textContent = 'Se sale del espacio · diapositiva ' + (i + 1);
          s.appendChild(aviso);
        }
      });
      document.body.setAttribute('data-desbordes', malas.join(','));
      document.body.setAttribute('data-revisado', 'si');
    };
    // Sin requestAnimationFrame: en Chrome sin ventana a veces no corre y la medición nunca se escribe.
    let hecho = false;
    const una = () => { if (!hecho) { hecho = true; revisar(); } };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => setTimeout(una, 30));
    setTimeout(una, 1500);
  }
})();
