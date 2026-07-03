"""
Copies the latest blog HTML to clipboard as rich text.
Then open medium.com/new-story and press Ctrl+V.

Usage:
    uv run copy_to_medium.py                  # auto-picks latest output
    uv run copy_to_medium.py output/blog.html # specific file
"""
import subprocess
import sys
import webbrowser
from pathlib import Path


def _latest_html() -> Path:
    files = sorted(Path("output").glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError("No HTML files found in output/")
    return files[0]


def _copy_html_to_clipboard(html: str) -> bool:
    """Set system clipboard to HTML MIME type. Returns True on success."""
    # xclip (Linux/WSL with display)
    try:
        r = subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "text/html"],
            input=html.encode("utf-8"),
            capture_output=True,
            timeout=5,
        )
        if r.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    # xsel fallback
    try:
        r = subprocess.run(
            ["xsel", "--clipboard", "--input"],
            input=html.encode("utf-8"),
            capture_output=True,
            timeout=5,
            env={"DISPLAY": ":0"},
        )
        if r.returncode == 0:
            return True
    except FileNotFoundError:
        pass

    return False


def main():
    html_path = Path(sys.argv[1]) if len(sys.argv) > 1 else _latest_html()
    print(f"📄 File: {html_path}")

    # Extract just the article body — skip <head>, CSS, JS
    raw = html_path.read_text(encoding="utf-8")
    # Grab content inside <article ...> ... </article>
    import re
    body_match = re.search(r"(<article.*?</article>)", raw, re.DOTALL)
    html_to_copy = body_match.group(1) if body_match else raw

    if _copy_html_to_clipboard(html_to_copy):
        print("✅ Rich HTML copied to clipboard!")
        print("\nNext steps:")
        print("  1. Go to  https://medium.com/new-story  (opening now...)")
        print("  2. Click in the BODY area (below the title field)")
        print("  3. Press  Ctrl+V")
        print("  4. Add title, tags, then publish\n")
        webbrowser.open("https://medium.com/new-story")
    else:
        print("⚠️  xclip/xsel not found. Install with:")
        print("    sudo apt install xclip")
        print("\nAlternative: manually open the HTML file in a browser,")
        print("select all (Ctrl+A), copy (Ctrl+C), paste into Medium.")
        print(f"\n  File path: {html_path.resolve()}")


if __name__ == "__main__":
    main()
