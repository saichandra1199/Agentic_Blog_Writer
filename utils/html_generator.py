"""Convert a blog markdown file → beautiful Medium-style HTML page."""
import re
from datetime import datetime
from pathlib import Path

import markdown


_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --serif: Georgia, 'Times New Roman', serif;
  --sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --mono: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  --text: #292929;
  --muted: #757575;
  --accent: #1a8917;
  --border: #e6e6e6;
  --bg-code: #f8f8f8;
  --max-w: 740px;
}
body {
  font-family: var(--serif);
  color: var(--text);
  background: #fff;
  font-size: 20px;
  line-height: 1.8;
  -webkit-font-smoothing: antialiased;
}
.post { max-width: var(--max-w); margin: 0 auto; padding: 56px 24px 100px; }
h1 { font-size: 2.6rem; line-height: 1.2; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 14px; }
h2 { font-size: 1.7rem; font-weight: 700; margin: 2.8rem 0 1rem; }
h3 { font-size: 1.3rem; font-weight: 700; margin: 2rem 0 0.75rem; }
h4 { font-size: 1.1rem; font-weight: 700; margin: 1.5rem 0 0.5rem; }
p { margin-bottom: 1.5rem; }
a { color: var(--accent); }
ul, ol { margin: 0 0 1.5rem 1.5rem; }
li { margin-bottom: 0.4rem; }
blockquote {
  border-left: 3px solid #ccc;
  margin: 2rem 0;
  padding: 0.4rem 0 0.4rem 1.5rem;
  color: var(--muted);
  font-style: italic;
}
hr { border: none; border-top: 1px solid var(--border); margin: 3rem 0; }
.meta {
  font-family: var(--sans);
  color: var(--muted);
  font-size: 0.85rem;
  margin-bottom: 3rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
/* Images */
.post img {
  max-width: 100%;
  border-radius: 8px;
  margin: 2rem auto;
  display: block;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  cursor: zoom-in;
  transition: transform 0.2s, box-shadow 0.2s;
}
.post img:hover { transform: scale(1.015); box-shadow: 0 8px 40px rgba(0,0,0,0.15); }
.post img[src*="giphy"] { border-radius: 8px; }
em { font-style: italic; }
/* Image captions (em after img) */
p > img + br + em,
p > img ~ em { display: block; text-align: center; color: var(--muted); font-size: 0.82rem; margin-top: -1.2rem; margin-bottom: 1.5rem; }
/* Code */
pre {
  background: var(--bg-code);
  border-radius: 6px;
  padding: 1.5rem;
  margin: 1.5rem 0;
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.6;
  border: 1px solid var(--border);
}
code { font-family: var(--mono); font-size: 0.875em; background: var(--bg-code); padding: 2px 5px; border-radius: 3px; }
pre code { background: none; padding: 0; font-size: inherit; }
/* Tables */
table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-family: var(--sans); font-size: 0.88rem; }
th { background: var(--bg-code); font-weight: 700; text-align: left; padding: 10px 14px; border: 1px solid var(--border); }
td { padding: 10px 14px; border: 1px solid var(--border); }
tr:nth-child(even) td { background: #fafafa; }
/* Lightbox */
.lb {
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,0.92); z-index: 9999;
  align-items: center; justify-content: center; cursor: zoom-out;
}
.lb.open { display: flex; }
.lb img { max-width: 90vw; max-height: 90vh; border-radius: 4px; object-fit: contain; cursor: default; box-shadow: none; transform: none; }
.lb-close { position: absolute; top: 20px; right: 28px; color: #fff; font-size: 2.4rem; cursor: pointer; line-height: 1; user-select: none; }
/* GIF badge */
.gif-frame { position: relative; display: block; margin: 2rem auto; width: fit-content; }
.gif-frame img { margin: 0; display: block; }
.gif-badge {
  position: absolute; top: 10px; left: 10px;
  background: rgba(0,0,0,0.65); color: #fff;
  font-family: var(--sans); font-size: 0.65rem; font-weight: 800;
  letter-spacing: 0.12em; padding: 3px 7px; border-radius: 3px;
  pointer-events: none;
}
/* Responsive */
@media (max-width: 600px) {
  body { font-size: 17px; }
  h1 { font-size: 1.9rem; }
  h2 { font-size: 1.4rem; }
  .post { padding: 28px 16px 60px; }
}
"""

_JS = """
(function () {
  // Lightbox
  const lb = document.getElementById('lb');
  const lbImg = document.getElementById('lb-img');
  document.querySelectorAll('.post img').forEach(img => {
    if (img.closest('.lb')) return;
    img.addEventListener('click', () => {
      lbImg.src = img.src;
      lb.classList.add('open');
    });
  });
  lb.addEventListener('click', e => {
    if (e.target !== lbImg) lb.classList.remove('open');
  });
  document.querySelector('.lb-close').addEventListener('click', () => lb.classList.remove('open'));

  // Wrap giphy images in gif-frame badge
  document.querySelectorAll('.post img').forEach(img => {
    if (img.src.includes('giphy') || img.src.includes('tenor') || img.src.includes('.gif')) {
      const wrap = document.createElement('div');
      wrap.className = 'gif-frame';
      img.parentNode.insertBefore(wrap, img);
      wrap.appendChild(img);
      const badge = document.createElement('span');
      badge.className = 'gif-badge';
      badge.textContent = 'GIF';
      wrap.appendChild(badge);
    }
  });

  // highlight.js
  if (window.hljs) hljs.highlightAll();

  // Mermaid fallback (renders any leftover mermaid blocks)
  if (window.mermaid) mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
})();
"""

_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>{css}</style>
</head>
<body>
  <article class="post">
    <h1>{title}</h1>
    <p class="meta">Generated {date}</p>
    {content}
  </article>
  <div class="lb" id="lb">
    <span class="lb-close">&times;</span>
    <img id="lb-img" src="" alt="">
  </div>
  <script>{js}</script>
</body>
</html>"""


def _fix_image_paths(html: str, md_path: str) -> str:
    """Replace local paths with absolute file:// URLs."""
    cwd = Path.cwd().resolve()
    def abs_src(m):
        raw = m.group(1)
        if raw.startswith(("http://", "https://", "file://")):
            return m.group(0)
        if raw.startswith("/"):
            return f'src="file://{raw}"'
        # Paths like output/visuals/... are relative to CWD, not the md file
        abs_path = (cwd / raw).resolve()
        return f'src="file://{abs_path}"'
    return re.sub(r'src="([^"]+)"', abs_src, html)


def generate_html(title: str, md_content: str, md_path: str) -> str:
    """Render blog markdown to HTML. Returns path of the saved .html file."""
    extensions = [
        "tables",
        "fenced_code",
        "toc",
        "attr_list",
        "md_in_html",
    ]
    html_body = markdown.markdown(md_content, extensions=extensions)
    html_body = _fix_image_paths(html_body, md_path)

    html = _TEMPLATE.format(
        title=title,
        date=datetime.now().strftime("%B %d, %Y"),
        content=html_body,
        css=_CSS,
        js=_JS,
    )

    html_path = Path(md_path).with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    return str(html_path)
