# Portfólio — Henrique Marinhos

Site estático (GitHub Pages): https://henrictrl.github.io/portfolio/

## Como editar
1. Textos, projetos, críticas e atalhos ficam em `build/data.py`.
2. Estilo em `build/style.css`, comportamento em `build/app.js`.
3. Gere o site: `pip install pillow && python3 build/build.py` (gera `index.html`, `/design`, `/redacao`, `/social`, `/web`, `sitemap.xml`).
4. Imagens: `assets/img/<projeto>/<nome>.webp` (até 1600 px).

## Visualizações customizadas
- Atalhos fixos: `/design/`, `/redacao/`, `/social/`, `/web/` (definidos em `PRESETS`).
- Links na hora: `?ver=m:trabalhos,sobre|p:basement,papelaria|f:tcp` (m = módulos, p = projetos, f = veículos de crítica) e `&cor=ff4f1f` para a cor de destaque.
- Painel gerador: abra `#painel` no fim da URL. Senha em `PAINEL_SENHA` (`build/data.py`), só para afastar visitantes.
