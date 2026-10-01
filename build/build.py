#!/usr/bin/env python3
"""Gera index.html, atalhos (/design, /redacao...), sitemap e robots a partir de build/data.py.
Uso: python3 build/build.py"""
import json, os, re, html, hashlib, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'build'))
from data import *

E = lambda s: html.escape(s, quote=True)
IMG = lambda pid, n: f'assets/img/{pid}/{n}.webp'
def size(pid, n):
    with Image.open(os.path.join(ROOT, IMG(pid, n))) as im: return im.size

# ---------- dados para o JS ----------
projetos_js = {}
for p in PROJETOS:
    projetos_js[p['id']] = {**p, 'capa': IMG(p['id'], p['capa']), 'galeria': [IMG(p['id'], g) for g in p['galeria']]}
criticas_js = [{'d': d, 'f': f, 'c': c, 't': t, 'u': u, 'co': co} for d, f, c, t, u, co in CRITICAS]
DATA = {'ordem': [p['id'] for p in PROJETOS], 'projetos': projetos_js, 'servicos': SERVICOS, 'criticas': criticas_js,
        'fontes': FONTES, 'presets': PRESETS, 'senha': hashlib.sha256(PAINEL_SENHA.encode()).hexdigest()}

# ---------- blocos pré-renderizados (SEO / sem JS) ----------
def card(p, eager=False):
    w, h = size(p['id'], p['capa'])
    return (f'<a class="work-card" href="#projeto/{p["id"]}" data-project="{p["id"]}">'
            f'<div class="work-card-media"><img src="{IMG(p["id"], p["capa"])}" alt="{E(p["titulo"])}: {E(p["subtitulo"])}" width="{w}" height="{h}" loading="{"eager" if eager else "lazy"}" decoding="async"></div>'
            f'<p class="work-card-title">{E(p["titulo"])}</p><p class="work-card-tag">{E(" · ".join(p["categorias"]))} — {E(p["ano"])}</p></a>')
cards_home = ''.join(card(p, i < 3) for i, p in enumerate(PROJETOS))
servicos_html = ''.join(
    f'<div class="service-card" data-service-id="{k}" role="button" tabindex="0"><div><p class="service-index">{s["idx"]}</p><div class="service-icon" aria-hidden="true">{s["icone"]}</div></div>'
    f'<div><h3 class="service-title">{E(s["titulo"])}</h3><p class="service-tagline">{E(s["tagline"])}</p><p class="service-desc">{E(s["resumo"])}</p></div></div>'
    for k, s in SERVICOS.items())
marquee_html = ''.join(f'<span class="marquee-logo">{E(m)}</span>' for m in MARQUEE * 2)
MES = ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez']
def dt(d): y, m, dd = d.split('-'); return f'{int(dd):02d} {MES[int(m)-1]} {y}'
def crit_row(c):
    d, f, cat, t, u, co = c
    co_html = f' <span class="crit-co">com {E(co)}</span>' if co else ''
    return (f'<li class="crit-row" data-f="{f}" data-c="{E(cat)}" data-y="{d[:4]}"><a href="{E(u)}" target="_blank" rel="noopener">'
            f'<span class="crit-meta"><time datetime="{d}">{dt(d)}</time><span>{E(FONTES[f])}</span><span>{E(cat)}</span></span>'
            f'<span class="crit-title">{E(t)}{co_html}</span><span class="crit-arrow" aria-hidden="true">↗</span></a></li>')
crit_destaque = ''.join(crit_row(c) for c in CRITICAS[:6])
crit_todas = ''.join(crit_row(c) for c in CRITICAS)
cats = sorted({c[2] for c in CRITICAS}); anos = sorted({c[0][:4] for c in CRITICAS}, reverse=True)
chips_cat = '<button class="chip on" data-cat="">Tudo</button>' + ''.join(f'<button class="chip" data-cat="{E(c)}">{E(c)}</button>' for c in cats)
opt_anos = '<option value="">Todos os anos</option>' + ''.join(f'<option>{a}</option>' for a in anos)
opt_fontes = '<option value="">Todos os veículos</option>' + ''.join(f'<option value="{k}">{E(v)}</option>' for k, v in FONTES.items())
exp_html = ''.join(
    f'<div class="experience-entry"><div class="experience-header"><div class="experience-header-left"><div class="experience-icon" aria-hidden="true">{E(c[0][:1])}</div>'
    f'<div><p class="experience-role">{E(c)}</p><p class="experience-company">{E(r)}</p></div></div><span class="experience-dates">{E(dts)}</span></div>'
    f'<div class="experience-desc"><p>{E(desc)}</p>{f"<a class=section-link href=#projeto/{pid}>Ver projeto</a>" if pid else ""}</div></div>'
    for c, r, dts, desc, pid in EXPERIENCIA)
form_html = ''.join(f'<div class="experience-entry"><div class="experience-header"><div><p class="experience-role">{E(a)}</p><p class="experience-company">{E(b)}</p></div><span class="experience-dates">{E(c)}</span></div></div>' for a, b, c in FORMACAO)
ferr_html = ''.join(f'<div class="tool-group"><p class="pm-block-label">{E(k)}</p><div class="pm-pills">{"".join(f"<span>{E(x)}</span>" for x in v)}</div></div>' for k, v in FERRAMENTAS.items())
mosaic = [('classic-tattoo', 'vertical'), ('basement', 'post-08'), ('nupe', 'oun-v'), ('proec', 'board8')]
mosaic_html = ''.join(f'<a href="#projeto/{pid}" class="mosaic-item"><img src="{IMG(pid, n)}" alt="" width="{size(pid, n)[0]}" height="{size(pid, n)[1]}" loading="eager" decoding="async"></a>' for pid, n in mosaic)

jsonld = {'@context': 'https://schema.org', '@type': 'Person', 'name': SITE['nome'], 'url': SITE['url'], 'email': 'mailto:' + SITE['email'],
          'jobTitle': 'Designer e comunicador', 'alumniOf': {'@type': 'CollegeOrUniversity', 'name': 'Universidade Estadual Paulista (Unesp)'},
          'sameAs': [SITE['linkedin'], SITE['instagram'], SITE['github'], SITE['letterboxd']],
          'knowsAbout': ['Identidade visual', 'Web design', 'Social media', 'Crítica cultural', 'Relações Públicas']}

CSS = open(os.path.join(ROOT, 'build', 'style.css')).read()
JS = open(os.path.join(ROOT, 'build', 'app.js')).read()
icon_svg = lambda d: f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="{d}"/></svg>'
X = icon_svg('M18 6L6 18M6 6l12 12'); L = icon_svg('M15 18l-6-6 6-6'); R = icon_svg('M9 18l6-6-6-6')

NAV = '''<a href="#inicio" data-nav="inicio" class="current">Início</a><a href="#trabalhos" data-nav="trabalhos" data-module="trabalhos">Trabalhos</a><a href="#critica" data-nav="critica" data-module="critica">Crítica</a><a href="#sobre" data-nav="sobre" data-module="sobre">Sobre</a><a href="#contato" data-nav="contato">Contato</a>'''

page = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{E(SITE["titulo"])}</title>
<meta name="description" content="{E(SITE["descricao"])}">
<link rel="canonical" href="{SITE["url"]}">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website"><meta property="og:locale" content="pt_BR">
<meta property="og:title" content="{E(SITE["titulo"])}"><meta property="og:description" content="{E(SITE["descricao"])}">
<meta property="og:url" content="{SITE["url"]}"><meta property="og:image" content="{SITE["url"]}assets/og.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23111'/%3E%3Ctext x='16' y='22' font-family='Georgia' font-style='italic' font-size='18' fill='%23fff' text-anchor='middle'%3Ehm%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<script>/* tema e cor antes da pintura (evita flash) */(function(){{try{{var t=localStorage.getItem('theme-pref');var h=new Date().getHours();if((t||((h>=6&&h<18)?'day':'night'))==='night')document.documentElement.setAttribute('data-theme','night');var c=new URLSearchParams(location.search).get('cor')||localStorage.getItem('accent');if(c&&/^[0-9a-f]{{6}}$/i.test(c))document.documentElement.style.setProperty('--accent','#'+c);}}catch(e){{}}}})();</script>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="top-header">
  <div class="header-inner">
    <div class="header-left"><a href="#inicio" class="brand"><span class="brand-name">Henrique Marinhos</span><span class="brand-location">— São Paulo, Brasil</span></a></div>
    <nav class="main-nav" aria-label="Navegação principal">{NAV}</nav>
    <div class="header-right theme-toggle"><button class="toggle-track theme-toggle-btn" type="button" role="switch" aria-checked="false" aria-label="Alternar modo claro/escuro"><span class="toggle-thumb"><svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg><svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 1110 3.5a7 7 0 0010 11z"/></svg></span></button></div>
  </div>
</header>
<header class="floating-header" id="floating-header" aria-hidden="true"><div class="header-inner"><div class="header-left"></div><nav class="main-nav" aria-label="Navegação (fixa)">{NAV}</nav><div class="header-right"></div></div></header>

<main id="conteudo">
 <div id="view-inicio" class="view">
  <section class="hero">
   <div class="hero-grid">
    <div class="hero-text">
     <h1 class="hero-headline"><span class="dim">Henrique Marinhos.</span> Design, comunicação e <em>crítica cultural</em>, do símbolo ao texto.</h1>
     <p class="hero-sub">Relações-públicas pela Unesp. Construo identidades visuais, sites e campanhas para redes, e escrevo sobre cinema, música e TV no Tesoura com Ponta e no Persona.</p>
     <div class="cta-row"><a class="btn" href="#trabalhos" data-module="trabalhos">Ver trabalhos</a><a class="btn ghost" href="#critica" data-module="critica">Ler críticas</a><a class="btn ghost" href="{SITE["cv"]}" target="_blank" rel="noopener">Currículo (PDF)</a></div>
    </div>
    <div class="hero-mosaic" data-module="trabalhos">{mosaic_html}</div>
   </div>
  </section>

  <section class="section-block" data-module="sobre">
   <div class="section-grid">
    <h2 class="section-label">Sobre</h2>
    <div class="section-body">
     <p>Trabalho entre design gráfico, web e comunicação. Fui estagiário de comunicação na Unesp, onde desenhei marcas e eventos para a Pró-Reitoria de Extensão e Cultura e para a Coordenadoria de Saúde, e hoje atendo como freelancer marcas como o Basement. Em paralelo, coordenei o Grupo de Pesquisa em Estética e Crítica Cultural Persona e publico crítica no portal Tesoura com Ponta.</p>
     <a href="#sobre" class="section-link">Saiba mais</a>
    </div>
   </div>
  </section>

  <section class="section-block" data-module="servicos">
   <div class="max-w">
    <h2 class="services-title">Serviços</h2>
    <div class="services-grid">{servicos_html}</div>
   </div>
  </section>

  <section class="marquee-section" aria-label="Clientes e veículos"><div class="marquee-mask"><div class="marquee-track">{marquee_html}</div></div></section>

  <section class="section-block" id="sec-trabalhos" data-module="trabalhos">
   <div class="max-w">
    <div class="work-intro"><h2 class="section-label">Trabalhos</h2><p class="intro-p">Identidades visuais, sites e campanhas, em ordem do mais recente.</p></div>
    <div class="work-grid" id="work-grid">{cards_home}</div>
   </div>
  </section>

  <section class="section-block" data-module="critica">
   <div class="max-w">
    <div class="work-intro"><h2 class="section-label">Crítica cultural</h2><p class="intro-p">{len(CRITICAS)} textos sobre cinema, música, séries e literatura. Os mais recentes:</p></div>
    <ul class="crit-list" id="crit-home">{crit_destaque}</ul>
    <a href="#critica" class="section-link">Ver o acervo completo</a>
   </div>
  </section>

  <section class="section-block" data-module="livro">
   <div class="section-grid book">
    <h2 class="section-label">Livro</h2>
    <div class="section-body"><p class="book-title"><em>{E(LIVRO["titulo"])}</em></p><p>{E(LIVRO["texto"])}</p></div>
   </div>
  </section>
 </div>

 <div id="view-trabalhos" class="view" hidden>
  <section class="work-page-hero"><div class="max-w"><h1 class="work-page-title"><span class="dim">Uma coleção de</span> marcas, sites e campanhas contadas do começo ao fim.</h1></div></section>
  <section class="section-block" style="padding-top:0"><div class="max-w"><h2 class="section-label" style="margin-bottom:24px">Estudos de caso</h2><div class="work-grid" id="work-case-grid"></div></div></section>
  <section class="section-block"><div class="max-w"><h2 class="section-label" style="margin-bottom:24px">Detalhes</h2><div class="explorations-grid" id="explorations-grid"></div></div></section>
 </div>

 <div id="view-critica" class="view" hidden>
  <section class="work-page-hero"><div class="max-w"><h1 class="work-page-title"><span class="dim">Acervo de crítica.</span> Cinema, música, séries e o que mais couber numa sala escura.</h1></div></section>
  <section class="section-block" style="padding-top:0"><div class="max-w">
   <div class="crit-filters">
    <div class="chips" id="crit-cats">{chips_cat}</div>
    <div class="crit-selects"><select id="crit-fonte" aria-label="Veículo">{opt_fontes}</select><select id="crit-ano" aria-label="Ano">{opt_anos}</select><input id="crit-busca" type="search" placeholder="Buscar título" aria-label="Buscar título"></div>
   </div>
   <p class="crit-count" id="crit-count" aria-live="polite"></p>
   <ul class="crit-list" id="crit-all">{crit_todas}</ul>
  </div></section>
 </div>

 <div id="view-sobre" class="view" hidden>
  <section class="work-page-hero"><div class="max-w"><h1 class="work-page-title"><span class="dim">Henrique Marinhos,</span> relações-públicas, designer e crítico cultural.</h1></div></section>
  <section class="section-block" style="padding-top:0"><div class="section-grid"><h2 class="section-label">Info</h2><div class="about-info-text">
   <p>Sou bacharel em Relações Públicas pela Unesp. Meu trabalho mistura estratégia de comunicação, design e escrita.</p>
   <p>No design, faço identidades visuais, sites e peças para redes sociais. Na escrita, publico crítica de cinema, música e TV, cubro festivais (48ª e 49ª Mostra SP, 15º Olhar de Cinema) e participei da coletiva de imprensa de <em>O Agente Secreto</em> com elenco e direção.</p>
   <p>Idiomas: português (nativo), inglês (avançado) e espanhol (em andamento).</p>
   <div class="cta-row"><a class="btn" href="{SITE["cv"]}" target="_blank" rel="noopener">Ver currículo</a><a class="btn ghost" href="{SITE["cv"]}" download>Baixar PDF</a></div>
  </div></div></section>
  <section class="section-block"><div class="section-grid"><h2 class="section-label">Experiência</h2><div>{exp_html}</div></div></section>
  <section class="section-block"><div class="section-grid"><h2 class="section-label">Formação</h2><div>{form_html}</div></div></section>
  <section class="section-block"><div class="section-grid"><h2 class="section-label">Ferramentas</h2><div class="tools">{ferr_html}</div></div></section>
 </div>
</main>

<footer class="contact-footer" id="contato">
 <div class="footer-inner">
  <div><h2 class="footer-headline">Vamos conversar?</h2><a href="mailto:{SITE["email"]}" class="footer-email">{SITE["email"]}</a></div>
  <div class="footer-links">
   <a href="{SITE["linkedin"]}" class="footer-social" target="_blank" rel="noopener">LinkedIn</a>
   <a href="{SITE["instagram"]}" class="footer-social" target="_blank" rel="noopener">Instagram</a>
   <a href="{SITE["cv"]}" class="footer-social" target="_blank" rel="noopener">Currículo</a>
   <a href="{SITE["github"]}" class="footer-social" target="_blank" rel="noopener">GitHub</a>
   <a href="{SITE["letterboxd"]}" class="footer-social" target="_blank" rel="noopener">Letterboxd</a>
  </div>
  <p class="footer-note">© 2026 Henrique Marinhos</p>
 </div>
</footer>

<div class="project-modal-overlay" id="pm-overlay" hidden>
 <div class="project-modal" role="dialog" aria-modal="true" aria-labelledby="pm-title">
  <div class="pm-topbar"><button class="pm-close" id="pm-close" aria-label="Fechar">{X}</button><div class="pm-nav-arrows"><button class="pm-nav-btn" id="pm-prev" aria-label="Projeto anterior">{L}</button><button class="pm-nav-btn" id="pm-next" aria-label="Próximo projeto">{R}</button></div></div>
  <div class="pm-scroll" id="pm-scroll">
   <div class="pm-gallery"><div class="pm-gallery-track" id="pm-track"></div><button class="pm-gallery-arrow pm-gallery-prev" id="pm-gprev" aria-label="Imagem anterior">{L}</button><button class="pm-gallery-arrow pm-gallery-next" id="pm-gnext" aria-label="Próxima imagem">{R}</button><div class="pm-gallery-dots" id="pm-dots"></div></div>
   <div class="pm-content max-w">
    <div class="pm-tags" id="pm-tags"></div><h2 class="pm-title" id="pm-title"></h2><p class="pm-subtitle" id="pm-subtitle"></p>
    <div class="pm-meta"><span id="pm-cliente"></span><span id="pm-ano"></span><a href="#" id="pm-link" class="pm-external-link" target="_blank" rel="noopener"></a></div>
    <div class="pm-block" id="pm-b-contexto"><p class="pm-block-label">Contexto</p><p class="pm-block-text" id="pm-contexto"></p></div>
    <div class="pm-block" id="pm-b-solucao"><p class="pm-block-label">Solução</p><p class="pm-block-text" id="pm-solucao"></p></div>
    <div class="pm-block" id="pm-b-resp"><p class="pm-block-label">O que fiz</p><ul class="pm-list" id="pm-resp"></ul></div>
    <div class="pm-block" id="pm-b-ferr"><p class="pm-block-label">Ferramentas</p><div class="pm-pills" id="pm-ferr"></div></div>
   </div>
  </div>
 </div>
</div>

<div class="project-modal-overlay" id="sm-overlay" hidden>
 <div class="project-modal service-modal" role="dialog" aria-modal="true" aria-labelledby="sm-title">
  <div class="pm-topbar"><button class="pm-close" id="sm-close" aria-label="Fechar">{X}</button></div>
  <div class="pm-scroll"><div class="pm-content max-w" style="padding-top:40px">
   <p class="pm-block-label">Serviço</p><h2 class="pm-title" id="sm-title"></h2><p class="sm-desc" id="sm-desc"></p>
   <div class="pm-block"><p class="pm-block-label">O que está incluso</p><ul class="pm-list" id="sm-incluso"></ul></div>
   <div class="pm-block"><p class="pm-block-label">Como trabalho</p><ol class="pm-list pm-list-numbered" id="sm-processo"></ol></div>
   <div class="pm-block" id="sm-b-rel"><p class="pm-block-label">Projetos relacionados</p><div class="work-grid" id="sm-rel"></div></div>
   <div class="sm-cta-wrap"><a href="mailto:{SITE["email"]}" class="sm-cta-btn">Pedir orçamento</a></div>
  </div></div>
 </div>
</div>

<div class="lightbox-overlay" id="lb-overlay" hidden>
 <button class="lightbox-close" id="lb-close" aria-label="Fechar visualização">{X}</button>
 <div class="lightbox-zoom-hint" id="lb-hint">Role ou pince para dar zoom · arraste para mover</div>
 <div class="lightbox-stage" id="lb-stage"><img class="lightbox-img" id="lb-img" src="" alt=""></div>
</div>

<div class="panel-overlay" id="panel" hidden>
 <div class="panel" role="dialog" aria-modal="true" aria-labelledby="panel-title">
  <div class="pm-topbar"><h2 id="panel-title" class="panel-h">Visualizações</h2><button class="pm-close" id="panel-close" aria-label="Fechar">{X}</button></div>
  <form id="panel-lock" class="panel-body"><label for="panel-pass">Senha</label><input id="panel-pass" type="password" autocomplete="off"><button class="btn" type="submit">Entrar</button><p id="panel-err" class="panel-err" hidden>Senha incorreta.</p></form>
  <div id="panel-main" class="panel-body" hidden>
   <p class="pm-block-label">Atalhos fixos</p><div class="pm-pills" id="panel-presets"></div>
   <p class="pm-block-label">Módulos</p><div class="panel-checks" id="panel-mods"></div>
   <p class="pm-block-label">Projetos</p><div class="panel-checks" id="panel-projs"></div>
   <p class="pm-block-label">Crítica: veículos</p><div class="panel-checks" id="panel-fontes"></div>
   <p class="pm-block-label">Cor de destaque</p><div class="panel-color"><input type="color" id="panel-cor" value="#ff4f1f"><button type="button" class="btn ghost" id="panel-cor-reset">Padrão</button></div>
   <p class="pm-block-label">Link gerado</p><input id="panel-url" readonly><div class="cta-row"><button type="button" class="btn" id="panel-copy">Copiar</button><a class="btn ghost" id="panel-open" target="_blank" rel="noopener">Abrir</a></div>
  </div>
 </div>
</div>

<noscript><style>.view[hidden]{{display:block!important}}</style></noscript>
<script>window.PORTFOLIO={json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))};</script>
<script>{JS}</script>
</body>
</html>'''

open(os.path.join(ROOT, 'index.html'), 'w').write(page)

# atalhos fixos /<preset>/ → ?ver=<preset>
for k in PRESETS:
    d = os.path.join(ROOT, k); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w').write(f'<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><meta name="robots" content="noindex"><title>Henrique Marinhos</title><meta http-equiv="refresh" content="0; url=../?ver={k}"><link rel="canonical" href="{SITE["url"]}"></head><body><a href="../?ver={k}">Abrir portfólio</a><script>location.replace("../?ver={k}"+location.hash)</script></body></html>')
open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE["url"]}sitemap.xml\n')
open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE["url"]}</loc><changefreq>monthly</changefreq></url></urlset>\n')
print('ok', len(page) // 1024, 'KB')
