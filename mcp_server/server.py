"""
MCP server exposing visual content tools for blog enhancement.
Run: python mcp_server/server.py  (from project root)
"""
import sys
from pathlib import Path

# Add project root so visual_tools resolves imports correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

from mcp_server.visual_tools import (
    fetch_gif,
    fetch_stock_image,
    generate_ai_image,
    process_blog_visuals,
    render_diagram,
    render_mermaid,
)

mcp = FastMCP(
    "blog-visual-tools",
    instructions=(
        "Visual content tools for blog enhancement. "
        "Render Mermaid diagrams, fetch stock photos, generate AI images, "
        "find GIFs, render PlantUML/Graphviz diagrams, or process an entire blog at once."
    ),
)


@mcp.tool()
def mermaid_to_image(diagram_code: str, filename: str = "diagram") -> str:
    """Render a Mermaid diagram to PNG and return a markdown image tag.
    Saves to output/visuals/{filename}.png. No auth required."""
    return render_mermaid(diagram_code, filename)["markdown"]


@mcp.tool()
def stock_image(query: str, filename: str = "image") -> str:
    """Fetch a relevant stock photo for a topic. Uses Pexels (set PEXELS_API_KEY)
    or falls back to Lorem Picsum placeholder. Returns markdown image tag."""
    return fetch_stock_image(query, filename)["markdown"]


@mcp.tool()
def ai_image(prompt: str, filename: str = "ai_image") -> str:
    """Generate an image via DALL-E 3. Requires OPENAI_API_KEY.
    Returns markdown image tag saved to output/visuals/{filename}.png."""
    return generate_ai_image(prompt, filename)["markdown"]


@mcp.tool()
def animated_gif(query: str) -> str:
    """Search Giphy for a relevant animated GIF. Requires GIPHY_API_KEY.
    Returns markdown image tag (remote URL, not downloaded) or empty string."""
    result = fetch_gif(query)
    return result["markdown"]


@mcp.tool()
def kroki_diagram(code: str, diagram_type: str = "plantuml", filename: str = "diagram") -> str:
    """Render a diagram via kroki.io (no auth required). Returns markdown image tag.
    diagram_type options: plantuml, graphviz, d2, blockdiag, seqdiag, actdiag, nwdiag, c4plantuml."""
    return render_diagram(code, diagram_type, filename)["markdown"]


@mcp.tool()
def enhance_blog_visuals(blog_markdown: str) -> str:
    """Process an entire blog post: render mermaid blocks, replace Image and GIF tags.
    Returns the enhanced markdown."""
    return process_blog_visuals(blog_markdown)


@mcp.tool()
def html_preview(md_path: str) -> str:
    """Convert a saved blog .md file to a beautiful HTML page for browser preview.
    Pass the path to the .md file. Returns the path of the generated .html file."""
    from pathlib import Path as P
    from utils.html_generator import generate_html
    md_path_obj = P(md_path)
    content = md_path_obj.read_text(encoding="utf-8")
    title = md_path_obj.stem.replace("_", " ")
    return generate_html(title=title, md_content=content, md_path=str(md_path_obj))


if __name__ == "__main__":
    mcp.run()
