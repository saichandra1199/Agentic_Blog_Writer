"""Interactive blog config collector. Called once before pipeline start."""


LENGTH_OPTIONS = {
    "1": {"label": "Short",  "words": "800–1200",  "sections": "3–5"},
    "2": {"label": "Medium", "words": "1500–2500", "sections": "5–8"},
    "3": {"label": "Long",   "words": "2500–4000", "sections": "7–10"},
    "4": {"label": "Pillar", "words": "4000–6000", "sections": "10–14"},
}

TONE_OPTIONS = {
    "1": "Conversational / Influencer style",
    "2": "Professional / Formal",
    "3": "Technical / Developer-focused",
    "4": "Inspirational / Motivational",
}

AUDIENCE_OPTIONS = {
    "1": "Beginners",
    "2": "Intermediate",
    "3": "Advanced / Expert",
    "4": "Mixed / General",
}

FORMAT_OPTIONS = {
    "1": "Deep Dive",
    "2": "How-To / Tutorial",
    "3": "Listicle (Top N)",
    "4": "Hot Take / Opinion",
    "5": "Myth-Busting",
    "6": "Personal Story / Case Study",
}


def _pick(prompt: str, options: dict, default: str) -> str:
    print(f"\n{prompt}")
    for k, v in options.items():
        marker = " [default]" if k == default else ""
        label = v["label"] if isinstance(v, dict) else v
        print(f"  {k}. {label}{marker}")
    choice = input(f"Choice (default {default}): ").strip() or default
    return choice if choice in options else default


def get_blog_config() -> dict:
    print("\n" + "─" * 40)
    print("📝  Blog Configuration")
    print("─" * 40)

    length_key = _pick("Blog Length:", LENGTH_OPTIONS, "2")
    length = LENGTH_OPTIONS[length_key]

    tone_key = _pick("Writing Tone:", TONE_OPTIONS, "1")
    tone = TONE_OPTIONS[tone_key]

    audience_key = _pick("Target Audience:", AUDIENCE_OPTIONS, "2")
    audience = AUDIENCE_OPTIONS[audience_key]

    format_key = _pick("Blog Format:", FORMAT_OPTIONS, "1")
    fmt = FORMAT_OPTIONS[format_key]

    print("\nNumber of GIFs (0–2, default 2):")
    raw_gifs = input("GIFs: ").strip()
    max_gifs = int(raw_gifs) if raw_gifs in ("0", "1", "2") else 2

    print("\nInclude Mermaid diagrams? (Y/n, default Y):")
    diagrams = input("Diagrams: ").strip().lower() not in ("n", "no")

    print("─" * 40)
    return {
        "word_range": length["words"],
        "section_range": length["sections"],
        "tone": tone,
        "audience": audience,
        "format": fmt,
        "max_gifs": max_gifs,
        "diagrams": diagrams,
    }
