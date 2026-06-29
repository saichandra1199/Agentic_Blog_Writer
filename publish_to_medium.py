"""
Publish a blog post to Medium.

Setup:
  1. Go to medium.com/me/settings → Security and Apps → Integration tokens
  2. Generate a token and add to .env: MEDIUM_INTEGRATION_TOKEN=...
  3. Run: python publish_to_medium.py

Images: Local images (output/visuals/*) are uploaded to Medium's CDN automatically.
The script replaces local paths with Medium CDN URLs before publishing.
"""
import os
import re
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

MEDIUM_API = "https://api.medium.com/v1"


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def get_user_id(token: str) -> tuple[str, str]:
    """Return (userId, username)."""
    resp = httpx.get(f"{MEDIUM_API}/me", headers=_headers(token), timeout=15)
    resp.raise_for_status()
    data = resp.json()["data"]
    return data["id"], data["username"]


def upload_image(token: str, image_path: Path) -> str:
    """Upload a local image to Medium CDN. Returns the CDN URL."""
    suffix = image_path.suffix.lower()
    content_type_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif"}
    content_type = content_type_map.get(suffix, "image/jpeg")

    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{MEDIUM_API}/images",
            headers={"Authorization": f"Bearer {token}"},
            files={"image": (image_path.name, image_path.read_bytes(), content_type)},
        )
        resp.raise_for_status()
    return resp.json()["data"]["url"]


def replace_local_images(content: str, token: str) -> str:
    """Find local image paths in markdown, upload to Medium, replace with CDN URLs."""
    # Match ![alt](output/visuals/...) or similar local paths
    pattern = re.compile(r"!\[([^\]]*)\]\((output/[^)]+)\)")

    def upload_and_replace(match):
        alt = match.group(1)
        local_path = Path(match.group(2))
        if not local_path.exists():
            print(f"  ⚠️  Image not found, skipping: {local_path}")
            return match.group(0)
        try:
            cdn_url = upload_image(token, local_path)
            print(f"  ✅ Uploaded: {local_path.name} → {cdn_url[:60]}...")
            return f"![{alt}]({cdn_url})"
        except Exception as e:
            print(f"  ⚠️  Upload failed for {local_path.name}: {e}")
            return match.group(0)

    return pattern.sub(upload_and_replace, content)


def pick_blog(output_dir: str = "output") -> tuple[str, Path]:
    """List saved blogs and let user pick one. Returns (title, path)."""
    md_files = sorted(Path(output_dir).glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not md_files:
        print(f"❌ No .md files found in {output_dir}/")
        sys.exit(1)

    print("\n📚 Saved blogs:")
    for i, f in enumerate(md_files, 1):
        print(f"  {i}. {f.name}")

    choice = input("\nPick a blog (number, or press Enter for latest): ").strip()
    if not choice:
        chosen = md_files[0]
    else:
        try:
            chosen = md_files[int(choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid choice.")
            sys.exit(1)

    title = chosen.stem.replace("_", " ").rsplit(" 2", 1)[0]  # strip timestamp suffix
    title = " ".join(w.capitalize() for w in title.split())
    return title, chosen


def publish(token: str, user_id: str, title: str, content: str, tags: list[str], status: str) -> str:
    """Publish post and return the Medium URL."""
    payload = {
        "title": title,
        "contentFormat": "markdown",
        "content": content,
        "tags": tags[:5],  # Medium cap: 5 tags
        "publishStatus": status,
        "notifyFollowers": status == "public",
    }
    resp = httpx.post(
        f"{MEDIUM_API}/users/{user_id}/posts",
        headers=_headers(token),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]["url"]


def extract_tags(content: str) -> list[str]:
    """Pull tags from the SEO metadata table at the bottom of the blog."""
    match = re.search(r"\*\*Tags\*\*\s*\|\s*([^\n|]+)", content)
    if not match:
        return []
    raw = match.group(1)
    return [t.strip().strip("`") for t in raw.split(",") if t.strip()]


def main():
    token = os.environ.get("MEDIUM_INTEGRATION_TOKEN", "")
    if not token:
        print("❌ MEDIUM_INTEGRATION_TOKEN not set in .env")
        print("   Get yours at: medium.com/me/settings → Security and Apps → Integration tokens")
        sys.exit(1)

    print("\n📡 Connecting to Medium...")
    try:
        user_id, username = get_user_id(token)
        print(f"✅ Logged in as: @{username}")
    except httpx.HTTPStatusError as e:
        print(f"❌ Auth failed: {e.response.status_code} — check your MEDIUM_INTEGRATION_TOKEN")
        sys.exit(1)

    title, blog_path = pick_blog()
    content = blog_path.read_text(encoding="utf-8")
    tags = extract_tags(content)

    print(f"\n📄 Blog: {title}")
    print(f"🏷️  Tags: {', '.join(tags) or '(none found)'}")

    status = input("\nPublish as [d]raft (safe) or [p]ublic? [d]: ").strip().lower()
    publish_status = "public" if status == "p" else "draft"

    print(f"\n🖼️  Uploading local images to Medium CDN...")
    content_with_cdn = replace_local_images(content, token)

    print(f"\n🚀 Publishing as {publish_status}...")
    try:
        url = publish(token, user_id, title, content_with_cdn, tags, publish_status)
        print(f"\n✅ Published! View at: {url}")
    except httpx.HTTPStatusError as e:
        print(f"❌ Publish failed: {e.response.status_code}")
        print(f"   Response: {e.response.text[:300]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
