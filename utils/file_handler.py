import os
from datetime import datetime
from pathlib import Path


def save_blog(title: str, content: str, output_dir: str = "output") -> str:
    os.makedirs(output_dir, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title)
    safe_title = safe_title.replace(" ", "_")[:60]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_title}_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Also generate HTML for browser preview
    try:
        from utils.html_generator import generate_html
        html_path = generate_html(title=title, md_content=content, md_path=filepath)
        print(f"🌐 HTML preview: {html_path}")
    except Exception as e:
        print(f"⚠️  HTML generation failed: {e}")

    return filepath
