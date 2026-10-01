(() => {
'use strict';
const D = window.PORTFOLIO, $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
const root = document.documentElement;
const MODULOS = { servicos: 'Serviços', trabalhos: 'Trabalhos', critica: 'Crítica', livro: 'Livro', sobre: 'Sobre' };

/* ---------- Visualizações customizadas (?ver=) ----------
   ?ver=design                       → atalho fixo (PRESETS em build/data.py)
   ?ver=m:trabalhos,sobre|p:basement → módulos (m), projetos (p), veículos de crítica (f)
   &cor=ff4f1f                       → cor de destaque */
const parseVer = (v) => {
  if (!v) return null;
  if (D.presets[v]) return { ...D.presets[v], preset: v };
  const o = {};
  v.split('|').forEach(part => { const [k, val] = part.split(':'); if (k && val) o[k] = val.split(',').filter(Boolean); });
  return Object.keys(o).length ? o : null;
};
const encodeVer = (o) => ['m', 'p', 'f'].filter(k => o[k] && o[k].length).map(k => `${k}:${o[k].join(',')}`).join('|');
const params = new URLSearchParams(location.search);
const VER = parseVer(params.get('ver'));
const modOn = (m) => !VER || !VER.m || VER.m.includes(m);
const ORDEM = (VER && VER.p) ? D.ordem.filter(id => VER.p.includes(id)) : D.ordem.slice();
const fonteOn = (f) => !VER || !VER.f || VER.f.includes(f);

if (VER) {
  $$('[data-module]').forEach(el => { if (!modOn(el.dataset.module)) el.hidden = true; });
  $$('#work-grid .work-card').forEach(c => { if (!ORDEM.includes(c.dataset.project)) c.remove(); });
  // reordena cards conforme a seleção
  const g = $('#work-grid'); ORDEM.forEach(id => { const c = $(`#work-grid [data-project="${id}"]`); if (c) g.appendChild(c); });
  $$('.crit-row').forEach(r => { if (!fonteOn(r.dataset.f)) r.remove(); });
  if (!modOn('trabalhos')) $$('.experience-desc .section-link').forEach(a => a.remove());
}

/* ---------- Tema ---------- */
const themeBtns = $$('.theme-toggle-btn');
const syncTheme = () => themeBtns.forEach(b => b.setAttribute('aria-checked', root.dataset.theme === 'night' ? 'true' : 'false'));
syncTheme();
themeBtns.forEach(b => b.addEventListener('click', () => {
  const next = root.dataset.theme === 'night' ? 'day' : 'night';
  next === 'night' ? root.setAttribute('data-theme', 'night') : root.removeAttribute('data-theme');
  try { localStorage.setItem('theme-pref', next); } catch (e) {}
  syncTheme();
}));

/* ---------- Helpers ---------- */
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const buildCard = (p) => {
  const a = document.createElement('a'); a.className = 'work-card'; a.href = '#projeto/' + p.id; a.dataset.project = p.id;
  a.innerHTML = `<div class="work-card-media"><img src="${p.capa}" alt="${esc(p.titulo)}" loading="lazy" decoding="async"></div><p class="work-card-title">${esc(p.titulo)}</p><p class="work-card-tag">${esc(p.categorias.join(' · '))} — ${esc(p.ano)}</p>`;
  return a;
};
const open = (ov) => { ov.hidden = false; requestAnimationFrame(() => ov.classList.add('open')); document.body.style.overflow = 'hidden'; };
const close = (ov) => { ov.classList.remove('open'); setTimeout(() => { ov.hidden = true; }, 300); if (!$$('.project-modal-overlay.open, .lightbox-overlay.open, .panel-overlay:not([hidden])').filter(o => o !== ov).length) document.body.style.overflow = ''; };

/* ---------- Rotas (hash) ---------- */
const VIEWS = ['inicio', 'trabalhos', 'critica', 'sobre'];
let workRendered = false, critInit = false;
const showView = (v) => {
  if (v === 'trabalhos' && !modOn('trabalhos')) v = 'inicio';
  if (v === 'critica' && !modOn('critica')) v = 'inicio';
  if (v === 'sobre' && !modOn('sobre')) v = 'inicio';
  VIEWS.forEach(x => { $('#view-' + x).hidden = x !== v; });
  $$('.main-nav a').forEach(a => a.classList.toggle('current', a.dataset.nav === v));
  if (v === 'trabalhos') renderWork();
  if (v === 'critica') initCrit();
  document.title = v === 'inicio' ? D.titulo || document.title : document.title;
};
const route = () => {
  const h = decodeURIComponent(location.hash.slice(1));
  if (h.startsWith('projeto/')) { const id = h.split('/')[1]; if ($('#view-inicio').hidden && $('#view-trabalhos').hidden) showView('inicio'); openProject(id); return; }
  if (h === 'painel') { openPanel(); return; }
  closeAllModals();
  if (h === 'contato') { $('#contato').scrollIntoView({ behavior: 'smooth' }); $$('.main-nav a').forEach(a => a.classList.toggle('current', a.dataset.nav === 'contato')); return; }
  const v = VIEWS.includes(h) ? h : 'inicio';
  showView(v); window.scrollTo(0, 0);
};
window.addEventListener('hashchange', route);

const renderWork = () => {
  if (workRendered) return; workRendered = true;
  const g = $('#work-case-grid'); ORDEM.forEach(id => g.appendChild(buildCard(D.projetos[id])));
  const ex = $('#explorations-grid');
  ORDEM.forEach(id => D.projetos[id].galeria.slice(1, 4).forEach(src => {
    const b = document.createElement('button'); b.className = 'exploration-item'; b.type = 'button'; b.setAttribute('aria-label', 'Ampliar imagem de ' + D.projetos[id].titulo);
    b.innerHTML = `<img src="${src}" alt="" loading="lazy" decoding="async">`; b.onclick = () => openLightbox(src); ex.appendChild(b);
  }));
};

/* ---------- Crítica ---------- */
const initCrit = () => {
  if (critInit) return; critInit = true;
  const rows = $$('#crit-all .crit-row'); let cat = '';
  const apply = () => {
    const f = $('#crit-fonte').value, y = $('#crit-ano').value, q = $('#crit-busca').value.trim().toLowerCase();
    let n = 0;
    rows.forEach(r => { const ok = (!cat || r.dataset.c === cat) && (!f || r.dataset.f === f) && (!y || r.dataset.y === y) && (!q || r.textContent.toLowerCase().includes(q)); r.hidden = !ok; if (ok) n++; });
    $('#crit-count').textContent = `${n} ${n === 1 ? 'texto' : 'textos'}`;
  };
  $$('#crit-cats .chip').forEach(b => b.onclick = () => { $$('#crit-cats .chip').forEach(x => x.classList.toggle('on', x === b)); cat = b.dataset.cat; apply(); });
  ['#crit-fonte', '#crit-ano'].forEach(s => $(s).onchange = apply); $('#crit-busca').oninput = apply;
  if (VER && VER.f) $$('#crit-fonte option').forEach(o => { if (o.value && !VER.f.includes(o.value)) o.remove(); });
  apply();
};

/* ---------- Modal de projeto ---------- */
const pm = $('#pm-overlay'); let cur = -1, gi = 0;
const openProject = (id) => {
  const i = ORDEM.indexOf(id); if (i < 0) return;
  cur = i; renderProject(); if (pm.hidden) open(pm);
};
const renderProject = () => {
  const p = D.projetos[ORDEM[cur]]; gi = 0;
  $('#pm-track').innerHTML = p.galeria.map((s, i) => `<div class="pm-gallery-slide"><img src="${s}" alt="${esc(p.titulo)}, imagem ${i + 1} de ${p.galeria.length}" loading="${i < 2 ? 'eager' : 'lazy'}" decoding="async" data-src="${s}"></div>`).join('');
  $('#pm-dots').innerHTML = p.galeria.map((_, i) => `<span class="pm-dot${i ? '' : ' active'}"></span>`).join('');
  $('#pm-track').style.transform = 'translateX(0)';
  $('#pm-tags').innerHTML = p.categorias.map(c => `<span>${esc(c)}</span>`).join('');
  $('#pm-title').textContent = p.titulo; $('#pm-subtitle').textContent = p.subtitulo;
  $('#pm-cliente').textContent = p.cliente; $('#pm-ano').textContent = p.ano;
  const l = $('#pm-link'); l.hidden = !p.link; if (p.link) { l.href = p.link; l.textContent = p.link_txt || 'Ver ao vivo ↗'; }
  $('#pm-contexto').textContent = p.contexto; $('#pm-b-contexto').hidden = !p.contexto;
  $('#pm-solucao').textContent = p.solucao; $('#pm-b-solucao').hidden = !p.solucao;
  $('#pm-resp').innerHTML = p.responsabilidades.map(r => `<li>${esc(r)}</li>`).join(''); $('#pm-b-resp').hidden = !p.responsabilidades.length;
  $('#pm-ferr').innerHTML = p.ferramentas.map(r => `<span>${esc(r)}</span>`).join(''); $('#pm-b-ferr').hidden = !p.ferramentas.length;
  $('#pm-scroll').scrollTop = 0;
  const one = p.galeria.length < 2; $('#pm-gprev').hidden = one; $('#pm-gnext').hidden = one;
  $('#pm-prev').hidden = $('#pm-next').hidden = ORDEM.length < 2;
};
const navGal = (i) => {
  const n = $('#pm-track').children.length; if (!n) return; gi = (i + n) % n;
  $('#pm-track').style.transform = `translateX(-${gi * 100}%)`;
  $$('#pm-dots .pm-dot').forEach((d, k) => d.classList.toggle('active', k === gi));
};
const navProj = (d) => { cur = (cur + d + ORDEM.length) % ORDEM.length; history.replaceState(null, '', '#projeto/' + ORDEM[cur]); renderProject(); };
$('#pm-gprev').onclick = () => navGal(gi - 1); $('#pm-gnext').onclick = () => navGal(gi + 1);
$('#pm-prev').onclick = () => navProj(-1); $('#pm-next').onclick = () => navProj(1);
$('#pm-track').addEventListener('click', e => { const img = e.target.closest('img'); if (img) openLightbox(img.dataset.src); });
let tx = null; $('#pm-track').addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
$('#pm-track').addEventListener('touchend', e => { if (tx === null) return; const dx = e.changedTouches[0].clientX - tx; if (Math.abs(dx) > 40) navGal(gi + (dx < 0 ? 1 : -1)); tx = null; });
const leaveHash = () => { const v = VIEWS.find(x => !$('#view-' + x).hidden) || 'inicio'; history.pushState(null, '', v === 'inicio' ? location.pathname + location.search : '#' + v); };
$('#pm-close').onclick = () => { close(pm); leaveHash(); };

/* ---------- Modal de serviço ---------- */
const sm = $('#sm-overlay');
$$('[data-service-id]').forEach(card => {
  const go = () => {
    const s = D.servicos[card.dataset.serviceId]; if (!s) return;
    $('#sm-title').textContent = s.titulo; $('#sm-desc').textContent = s.desc;
    $('#sm-incluso').innerHTML = s.incluso.map(x => `<li>${esc(x)}</li>`).join('');
    $('#sm-processo').innerHTML = s.processo.map(x => `<li>${esc(x)}</li>`).join('');
    const rel = $('#sm-rel'); rel.innerHTML = '';
    const list = modOn('trabalhos') ? ORDEM.filter(id => D.projetos[id].servicos.includes(card.dataset.serviceId)) : [];
    list.forEach(id => { const c = buildCard(D.projetos[id]); c.addEventListener('click', () => close(sm)); rel.appendChild(c); });
    $('#sm-b-rel').hidden = !list.length;
    open(sm);
  };
  card.addEventListener('click', go); card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
});
$('#sm-close').onclick = () => close(sm);

/* ---------- Lightbox com zoom ---------- */
const lb = $('#lb-overlay'), lbImg = $('#lb-img'); let z = 1, px = 0, py = 0, drag = null;
const setT = () => { lbImg.style.transform = `translate(${px}px, ${py}px) scale(${z})`; };
const openLightbox = (src) => { lbImg.src = src; z = 1; px = py = 0; setT(); $('#lb-hint').classList.remove('hidden'); open(lb); };
$('#lb-stage').addEventListener('wheel', e => { e.preventDefault(); z = Math.min(5, Math.max(1, z * (e.deltaY < 0 ? 1.12 : 0.9))); if (z === 1) px = py = 0; setT(); $('#lb-hint').classList.add('hidden'); }, { passive: false });
lbImg.addEventListener('pointerdown', e => { if (z === 1) return; drag = { x: e.clientX - px, y: e.clientY - py }; lbImg.classList.add('dragging'); lbImg.setPointerCapture(e.pointerId); });
lbImg.addEventListener('pointermove', e => { if (!drag) return; px = e.clientX - drag.x; py = e.clientY - drag.y; setT(); });
lbImg.addEventListener('pointerup', () => { drag = null; lbImg.classList.remove('dragging'); });
lbImg.addEventListener('dblclick', () => { z = z > 1 ? 1 : 2.5; px = py = 0; setT(); });
$('#lb-close').onclick = () => close(lb);

/* ---------- Painel de visualizações (#painel) ---------- */
const panel = $('#panel');
const sha = async (t) => [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)))].map(b => b.toString(16).padStart(2, '0')).join('');
const openPanel = () => {
  panel.hidden = false; document.body.style.overflow = 'hidden';
  let ok = false; try { ok = sessionStorage.getItem('painel') === '1'; } catch (e) {}
  $('#panel-lock').hidden = ok; $('#panel-main').hidden = !ok; if (ok) buildPanel(); else $('#panel-pass').focus();
};
$('#panel-lock').addEventListener('submit', async e => {
  e.preventDefault();
  if (await sha($('#panel-pass').value) === D.senha) { try { sessionStorage.setItem('painel', '1'); } catch (er) {} $('#panel-lock').hidden = true; $('#panel-main').hidden = false; buildPanel(); }
  else $('#panel-err').hidden = false;
});
$('#panel-close').onclick = () => { panel.hidden = true; document.body.style.overflow = ''; leaveHash(); };
let panelBuilt = false;
const buildPanel = () => {
  if (panelBuilt) return; panelBuilt = true;
  const box = (wrap, name, items) => { $(wrap).innerHTML = Object.entries(items).map(([k, v]) => `<label><input type="checkbox" name="${name}" value="${k}" checked> ${esc(v)}</label>`).join(''); };
  box('#panel-mods', 'm', MODULOS);
  box('#panel-projs', 'p', Object.fromEntries(D.ordem.map(id => [id, D.projetos[id].titulo])));
  box('#panel-fontes', 'f', D.fontes);
  $('#panel-presets').innerHTML = Object.keys(D.presets).map(k => `<button type="button" class="preset" data-k="${k}">/${k}</button>`).join('');
  $$('#panel-presets .preset').forEach(b => b.onclick = () => { const p = D.presets[b.dataset.k];
    $$('#panel-main input[type=checkbox]').forEach(c => { const sel = p[c.name]; c.checked = !sel || sel.includes(c.value); }); gen(b.dataset.k); });
  $('#panel-main').addEventListener('change', () => gen());
  $('#panel-cor').oninput = () => { root.style.setProperty('--accent', $('#panel-cor').value); gen(); };
  $('#panel-cor-reset').onclick = () => { $('#panel-cor').value = '#ff4f1f'; root.style.setProperty('--accent', '#ff4f1f'); gen(); };
  $('#panel-copy').onclick = async () => { try { await navigator.clipboard.writeText($('#panel-url').value); $('#panel-copy').textContent = 'Copiado'; setTimeout(() => $('#panel-copy').textContent = 'Copiar', 1400); } catch (e) { $('#panel-url').select(); } };
  gen();
};
const gen = (preset) => {
  const base = location.origin + location.pathname;
  const cor = $('#panel-cor').value.replace('#', '').toLowerCase();
  let url;
  if (preset) url = new URL(location.pathname.replace(/[^/]*$/, '') + preset + '/', location.origin).href;
  else {
    const o = {};
    ['m', 'p', 'f'].forEach(k => { const all = $$(`#panel-main input[name=${k}]`), on = all.filter(c => c.checked).map(c => c.value); if (on.length < all.length) o[k] = on; });
    const v = encodeVer(o), q = new URLSearchParams(); if (v) q.set('ver', v); if (cor !== 'ff4f1f') q.set('cor', cor);
    url = base + (q.toString() ? '?' + q.toString().replace(/%3A/g, ':').replace(/%2C/g, ',').replace(/%7C/g, '|') : '');
  }
  $('#panel-url').value = url; $('#panel-open').href = url;
};

/* ---------- Header ---------- */
const fh = $('#floating-header'), th = $('header.top-header'); let lastY = scrollY, tick = false;
addEventListener('scroll', () => { if (tick) return; tick = true; requestAnimationFrame(() => {
  const y = scrollY, dy = y - lastY; th.classList.toggle('scrolled', y > 20);
  if (Math.abs(dy) > 10 || y <= 0) { fh.classList.toggle('visible', dy < 0 && y > 300); lastY = y; } tick = false; }); }, { passive: true });

/* ---------- Teclado e overlays ---------- */
const closeAllModals = () => { [lb, pm, sm].forEach(o => { if (!o.hidden) close(o); }); if (!panel.hidden) { panel.hidden = true; document.body.style.overflow = ''; } };
[pm, sm, lb].forEach(ov => ov.addEventListener('click', e => { if (e.target === ov) ov.querySelector('.pm-close, .lightbox-close').click(); }));
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { const o = [lb, pm, sm].find(x => !x.hidden); if (o) o.querySelector('.pm-close, .lightbox-close').click(); else if (!panel.hidden) $('#panel-close').click(); }
  if (!pm.hidden && lb.hidden) { if (e.key === 'ArrowRight') navGal(gi + 1); if (e.key === 'ArrowLeft') navGal(gi - 1); }
});

/* ---------- Revelar ao rolar ---------- */
if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
  const io = new IntersectionObserver(es => es.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in-view'); io.unobserve(en.target); } }), { threshold: 0.12 });
  $$('.section-block .max-w, .section-block .section-grid').forEach(el => { el.classList.add('reveal'); io.observe(el); });
}
if (VER && VER.preset) { const b = document.createElement('p'); b.className = 'ver-badge'; b.textContent = 'Seleção: ' + VER.preset; document.body.appendChild(b); setTimeout(() => b.remove(), 4000); }
route();
})();
