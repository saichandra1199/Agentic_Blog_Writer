"""
Visual content tools for blog enhancement.
Used by both the MCP server (Claude Code) and the LangGraph enhancer node.
"""
import base64
import os
import re
import zlib
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

VISUALS_DIR = Path("output/visuals")

# ponytail: fallback GIF dict — works without any API key
# Curated Giphy CDN URLs for common blog emotional moments
_FALLBACK_GIFS: dict[str, str] = {
    "mind blown":       "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif",
    "excited":          "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "waiting":          "https://media.giphy.com/media/l46Cy1rHbQ92uuLXa/giphy.gif",
    "confused":         "https://media.giphy.com/media/5wWf7H0qoWaNnkZBucM/giphy.gif",
    "this is fine":     "https://media.giphy.com/media/QMHoU66sBXqqLqYvGO/giphy.gif",
    "celebrate":        "https://media.giphy.com/media/g9582DNuQppxC/giphy.gif",
    "sarcastic":        "https://media.giphy.com/media/3oEjI5VtIhHvK37WYo/giphy.gif",
    "thinking":         "https://media.giphy.com/media/d3mlE7uhX8KFgEmY/giphy.gif",
    "coding":           "https://media.giphy.com/media/ZVik7pIo9ZS1o/giphy.gif",
    "ai":               "https://media.giphy.com/media/077i6AULCXc0FKTj9s/giphy.gif",
    "facepalm":         "https://media.giphy.com/media/XsUtdIeJ0MWMo/giphy.gif",
    "wow":              "https://media.giphy.com/media/ToMjGpjpXZ5TlxCHm3e/giphy.gif",
    "challenge":        "https://media.giphy.com/media/3o7btNa0RUYa5E7iiQ/giphy.gif",
    "nailed it":        "https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/giphy.gif",
    "mic drop":         "https://media.giphy.com/media/l3V0sNZ0NGomEniJ2/giphy.gif",
}
_DEFAULT_FALLBACK_GIF = "https://media.giphy.com/media/SVs6DmVQXMNISTdOp9/giphy.gif"


def _ensure_dir():
    VISUALS_DIR.mkdir(parents=True, exist_ok=True)


def _fallback_gif_url(query: str) -> str:
    """Pick closest fallback GIF from curated dict by keyword match."""
    q = query.lower()
    for keyword, url in _FALLBACK_GIFS.items():
        if any(word in q for word in keyword.split()):
            return url
    return _DEFAULT_FALLBACK_GIF


def render_mermaid(diagram_code: str, filename: str = "diagram") -> dict:
    """Render Mermaid diagram to PNG via mermaid.ink (no auth required)."""
    _ensure_dir()
    clean_code = diagram_code.strip()
    encoded = base64.urlsafe_b64encode(clean_code.encode()).decode()
    url = f"https://mermaid.ink/img/{encoded}"

    with httpx.Client(follow_redirects=True, timeout=30) as client:
        resp = client.get(url)
        resp.raise_for_status()

    path = VISUALS_DIR / f"{filename}.png"
    path.write_bytes(resp.content)
    return {"path": str(path), "markdown": f"![{filename}]({path})"}


def fetch_stock_image(query: str, filename: str = "image") -> dict:
    """Fetch contextual stock photo. Priority: Unsplash → Pexels → Lorem Picsum."""
    _ensure_dir()

    # 1. Unsplash (50 req/hour free, most contextually accurate)
    unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY", "")
    if unsplash_key:
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                "https://api.unsplash.com/photos/random",
                params={"query": query, "orientation": "landscape", "client_id": unsplash_key},
            )
            if resp.status_code == 200:
                data = resp.json()
                img_url = data["urls"]["regular"]
                photographer = data.get("user", {}).get("name", "")
                alt = data.get("alt_description") or query
                img_resp = client.get(img_url, follow_redirects=True, timeout=60)
                img_resp.raise_for_status()
                path = VISUALS_DIR / f"{filename}.jpg"
                path.write_bytes(img_resp.content)
                caption = f"\n*Photo by {photographer} on Unsplash*" if photographer else ""
                return {"path": str(path), "markdown": f"![{alt}]({path}){caption}"}

    # 2. Pexels
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if pexels_key:
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": pexels_key},
                params={"query": query, "per_page": 1, "orientation": "landscape", "size": "large"},
            )
            if resp.status_code == 200:
                photos = resp.json().get("photos", [])
                if photos:
                    img_url = photos[0]["src"]["large2x"]
                    alt = photos[0].get("alt", query)
                    photographer = photos[0].get("photographer", "")
                    img_resp = client.get(img_url, follow_redirects=True, timeout=60)
                    img_resp.raise_for_status()
                    path = VISUALS_DIR / f"{filename}.jpg"
                    path.write_bytes(img_resp.content)
                    caption = f"\n*Photo by {photographer} on Pexels*" if photographer else ""
                    return {"path": str(path), "markdown": f"![{alt}]({path}){caption}"}

    # 3. Lorem Picsum fallback — deterministic seed from query, no auth needed
    seed = abs(hash(query)) % 1000
    url = f"https://picsum.photos/seed/{seed}/1200/630"
    with httpx.Client(follow_redirects=True, timeout=30) as client:
        resp = client.get(url)
        resp.raise_for_status()
    path = VISUALS_DIR / f"{filename}.jpg"
    path.write_bytes(resp.content)
    return {"path": str(path), "markdown": f"![{query}]({path})"}


def generate_ai_image(prompt: str, filename: str = "ai_image") -> dict:
    """Generate image via DALL-E 3. Requires OPENAI_API_KEY."""
    _ensure_dir()
    from openai import OpenAI

    client = OpenAI()
    resp = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="standard",
        n=1,
    )
    img_url = resp.data[0].url
    short_alt = prompt[:80].rstrip()

    with httpx.Client(follow_redirects=True, timeout=60) as http:
        img_resp = http.get(img_url)
        img_resp.raise_for_status()

    path = VISUALS_DIR / f"{filename}.png"
    path.write_bytes(img_resp.content)
    return {"path": str(path), "markdown": f"![{short_alt}]({path})"}


def fetch_gif(query: str) -> dict:
    """Search Giphy for GIF. Falls back to curated dict if GIPHY_API_KEY not set."""
    api_key = os.environ.get("GIPHY_API_KEY", "")

    if api_key:
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                "https://api.giphy.com/v1/gifs/search",
                params={"api_key": api_key, "q": query, "limit": 3, "rating": "g"},
            )
            if resp.status_code == 200:
                data = resp.json().get("data", [])
                if data:
                    gif_url = data[0]["images"]["original"]["url"]
                    return {"markdown": f"![{query}]({gif_url})", "url": gif_url}

    # Fallback: curated dict — no API key required
    url = _fallback_gif_url(query)
    return {"markdown": f"![{query}]({url})", "url": url, "fallback": True}


def render_diagram(code: str, diagram_type: str = "plantuml", filename: str = "diagram") -> dict:
    """Render diagram via kroki.io. Supports plantuml, graphviz, d2, blockdiag, seqdiag."""
    _ensure_dir()
    compressed = zlib.compress(code.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode()
    url = f"https://kroki.io/{diagram_type}/png/{encoded}"

    with httpx.Client(follow_redirects=True, timeout=30) as client:
        resp = client.get(url)
        resp.raise_for_status()

    path = VISUALS_DIR / f"{filename}.png"
    path.write_bytes(resp.content)
    return {"path": str(path), "markdown": f"![{filename}]({path})"}


def process_blog_visuals(blog_content: str) -> str:
    """Post-process blog markdown:
    - Render ```mermaid blocks → PNG via mermaid.ink
    - Replace <!-- 📸 Image: ... --> → contextual stock photo
    - Replace <!-- 🎭 GIF: ... --> → animated GIF (Giphy or curated fallback)
    All failures keep original text silently.
    """
    # ── Mermaid diagrams ──────────────────────────────────────────────────────
    mermaid_pattern = re.compile(r"```mermaid\n(.*?)```", re.DOTALL)
    counter = [0]

    def replace_mermaid(match):
        counter[0] += 1
        code = match.group(1).strip()
        try:
            return f"\n{render_mermaid(code, f'diagram_{counter[0]}')['markdown']}\n"
        except Exception:
            return match.group(0)

    content = mermaid_pattern.sub(replace_mermaid, blog_content)

    # ── Stock images (both old and new tag formats) ───────────────────────────
    img_pattern = re.compile(
        r"<!--\s*📸\s*Image(?:\s+suggestion)?:\s*(.*?)\s*-->",
        re.IGNORECASE,
    )
    img_counter = [0]

    def replace_image(match):
        img_counter[0] += 1
        description = match.group(1).strip()
        try:
            return fetch_stock_image(description, f"image_{img_counter[0]}")["markdown"]
        except Exception:
            return match.group(0)

    content = img_pattern.sub(replace_image, content)

    # ── GIFs ──────────────────────────────────────────────────────────────────
    gif_pattern = re.compile(r"<!--\s*🎭\s*GIF:\s*(.*?)\s*-->", re.IGNORECASE)
    gif_counter = [0]

    def replace_gif(match):
        gif_counter[0] += 1
        query = match.group(1).strip()
        try:
            return fetch_gif(query)["markdown"]
        except Exception:
            return match.group(0)

    content = gif_pattern.sub(replace_gif, content)
    return content
