# Agentic Blog Writer

**Turn a title and a few notes into a publication-ready blog post — automatically.**

Give it a topic and some context. A chain of specialized AI agents researches the web, builds a structured outline, writes a full draft, edits it for clarity and SEO, then enriches it with diagrams, tables, and callout blocks. Output lands as a clean Markdown file ready to paste into Medium.

> **Deep dive:** For full system design, architecture, script-by-script breakdown, benefits/drawbacks, and beginner guide — see **[PROJECT.md](PROJECT.md)**.

---

## What It Does (Quick Summary)

| Step | What happens | Runs |
|------|-------------|------|
| You provide | Blog title + a few sentences of context | — |
| Agent 1 | Expands your context into a detailed content brief | sequential |
| Agent 2 | Searches the web for research (Tavily) | **parallel** with Agent 3 |
| Agent 3 | Identifies viral trends and suggests 5 follow-up blog ideas | **parallel** with Agent 2 |
| Agent 4 | Builds a structured outline (H1/H2/H3) — waits for both above | sequential |
| Agent 5 | Writes a full 800–6000 word draft | sequential |
| Agent 6 | Edits the draft for clarity and flow | **parallel** with Agent 7 |
| Agent 7 | Generates SEO metadata (tags, keywords, meta description) | **parallel** with Agent 6 |
| Agent 8 | Adds diagrams, images, GIFs, tables, callout blocks — waits for both above | sequential |
| Output | `.md` + `.html` files saved to `output/` | — |
| Optional | Publishes directly to Medium via browser automation | — |

---

## Full Pipeline

The graph uses a **double-diamond topology** — two fan-out/fan-in points where independent agents run in parallel, saving ~35–40 seconds per run.

```
User Input (title + context)
              │
              ▼
    [ Context Enhancer ]      → Expands raw context into a detailed creative brief
              │
         ┌────┴────┐           ← FAN-OUT: both start at the same time
         ▼         ▼
  [Researcher]  [Trend Analyst]
  Tavily web    Viral formats,
  search →      hooks, and 5
  research      next blog ideas
  notes
         │         │
         └────┬────┘           ← FAN-IN: Outline waits for both to finish
              ▼
    [ Outline Generator ]      → H1/H2/H3 skeleton with section descriptions
              │
              ▼
          [ Writer ]           → Full 800–6000 word draft
              │
         ┌────┴────┐           ← FAN-OUT: both start at the same time
         ▼         ▼
     [Editor]  [SEO Analyzer]
     Polished   Tags, keywords,
     draft      meta description
         │         │
         └────┬────┘           ← FAN-IN: Enhancer waits for both to finish
              ▼
          [ Enhancer ]         → Mermaid diagrams, stock images, GIFs, tables, callouts
              │
              ▼
        [ Save Output ]        → output/<title>_<timestamp>.md  +  .html preview
              │
              ▼
    [ Publisher ] (optional)   → Opens Medium in browser, pastes formatted content
```

**How LangGraph makes this work:** Adding two edges from one node causes LangGraph to run both downstream nodes concurrently. Adding two edges *into* one node makes LangGraph automatically hold that node until all predecessors complete — no extra code needed.

---

## Features in Detail

### 9-Node LangGraph Pipeline — Double-Diamond Topology
Each agent has exactly one job. The graph has two parallel fan-out/fan-in points (the "double diamond"). LangGraph handles concurrency automatically — you just wire the edges and it figures out what can run at the same time. Easy to debug: if something goes wrong, you know exactly which node failed.

**Why not just sequential?** `researcher` and `trend_analyst` don't depend on each other — they both only need the enhanced context. Making one wait for the other wastes time. Same for `editor` and `seo_analyzer` — both only need the raw draft. Running them concurrently cuts ~35–40 seconds off every run.

### Context Enhancer
Takes your raw title and a few bullet points and expands them into a complete creative brief covering target audience, tone, key angles, unique value proposition, and common misconceptions to address. The richer this gets, the better the final blog.

### Web Research (Tavily)
Searches the web for up-to-date information on your topic. Not just pulling Wikipedia — it finds recent articles, technical docs, and discussion threads to ground the blog in current knowledge.

### Trend Analysis
Searches for what blog formats and hooks are performing best right now on that topic. Identifies whether a listicle, hot take, deep dive, or personal story would perform best. Also generates **5 follow-up blog ideas** shown at the end of the run.

### Configurable Blog Parameters
Before generation starts, you choose:
- **Length**: Short (800–1200 words) / Medium (1500–2500) / Long (2500–4000) / Pillar (4000–6000)
- **Tone**: Conversational, Professional, Technical, or Inspirational
- **Audience**: Beginners, Intermediate, Advanced, or Mixed
- **Format**: Deep Dive, How-To, Listicle, Hot Take, Myth-Busting, or Case Study
- **GIFs**: 0, 1, or 2 animated GIFs
- **Diagrams**: Mermaid diagrams on/off

### Visual Enrichment
The enhancer node injects:
- **Mermaid diagrams** — flowcharts, sequence diagrams, mind maps rendered to PNG via [mermaid.ink](https://mermaid.ink)
- **Stock photos** — from Unsplash or Pexels (with photographer credit), falls back to Lorem Picsum if no API key
- **Animated GIFs** — via Giphy API, or a curated 15-GIF fallback set if no API key
- **Comparison tables** — prose with 3+ items automatically turned into clean Markdown tables
- **Callout blocks** — `💡 Key Insight`, `⚠️ Watch Out`, `🔥 Hot Take`, `😂 Real Talk`

### SEO Analyzer (dedicated parallel node)
Runs concurrently with the editor — both work on the raw draft at the same time. Generates:
- **Meta description** — 150–160 character summary for search engines
- **Focus keyword** — primary keyword the post targets
- **Secondary keywords** — 3–5 supporting keywords
- **Tags** — 5–8 relevant blog tags

> Previously SEO was bundled inside the editor, forcing it sequential. Splitting it into its own node enables the second parallel diamond and gives each agent a cleaner single responsibility.

### HTML Preview
Every run generates both a `.md` and a beautiful `.html` file you can open in any browser. The HTML has:
- Medium-style serif typography
- Click-to-zoom lightbox on images
- GIF badge overlay
- Syntax highlighting for code blocks (highlight.js)
- Mermaid diagram rendering fallback
- Fully responsive (mobile-friendly)

### Medium Publisher (Browser Automation)
After generation, you're asked `Publish to Medium? (y/N)`. If yes:
1. Opens Chrome with a persistent profile (login once, never again)
2. Navigates to `medium.com/new-story`
3. Pastes title and rich HTML content directly into the Medium editor via clipboard simulation
4. You review, add tags, and click publish manually

> Medium disabled its API for new integrations — this is the only way to automate publishing without copy-pasting.

---

## Project Structure

```
Agentic_Blog_writer/
├── main.py                         # CLI entry point — validates env, collects input, runs pipeline
├── graph.py                        # LangGraph StateGraph — double-diamond parallel topology (9 nodes)
├── state.py                        # BlogState TypedDict — shared data passed between all nodes
├── config.py                       # Interactive config collector (length, tone, audience, format)
│
├── nodes/
│   ├── context_enhancer.py         # Expands raw context → detailed brief            [sequential]
│   ├── researcher.py               # Tavily search → research notes                  [parallel ◀]
│   ├── trend_analyst.py            # Trend analysis + 5 next blog ideas              [parallel ◀]
│   ├── outline_generator.py        # Research + trends → H1/H2/H3 outline           [fan-in]
│   ├── writer.py                   # Outline → full draft                            [sequential]
│   ├── editor.py                   # Draft → polished edited draft                   [parallel ◀]
│   ├── seo_analyzer.py             # Draft → SEO tags, keywords, meta description    [parallel ◀]
│   ├── enhancer.py                 # Edited draft + SEO → visuals injected           [fan-in]
│   └── publisher.py                # Browser automation for Medium publishing
│
├── tools/
│   └── search.py                   # Tavily search tool factory
│
├── utils/
│   ├── file_handler.py             # Saves timestamped .md file to output/
│   └── html_generator.py           # Converts .md → beautiful Medium-style .html
│
├── mcp_server/
│   ├── server.py                   # MCP server (for Claude Code integration)
│   └── visual_tools.py             # Image/GIF/diagram fetching — used by enhancer node
│
├── output/                         # Generated blogs saved here (auto-created)
├── .env.example                    # Copy this to .env and fill in your keys
├── pyproject.toml                  # uv/pip project config + dependencies
└── requirements.txt                # pip-compatible dependency list
```

---

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- OpenAI API key with **GPT-4o** access
- Tavily API key (free tier: 1,000 searches/month)
- Chrome browser installed (only needed for Medium publishing)

Optional (for better visuals — all have free tiers):
- Unsplash Access Key
- Pexels API Key
- Giphy API Key

---

## Installation

### Using uv (recommended)

```bash
# 1. Clone the repo
git clone <repo-url>
cd Agentic_Blog_writer

# 2. Install dependencies
uv sync

# 3. Set up environment variables
cp .env.example .env
```

### Using pip

```bash
git clone <repo-url>
cd Agentic_Blog_writer
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

---

## Configuration

Open `.env` and fill in your API keys:

```env
# Required
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# Optional — images (priority: Unsplash > Pexels > Lorem Picsum fallback)
UNSPLASH_ACCESS_KEY=...
PEXELS_API_KEY=...

# Optional — GIFs (falls back to curated set if not set)
GIPHY_API_KEY=...
```

### Where to get each key

| Key | Where | Free Tier |
|-----|-------|-----------|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | Pay-per-use (~$0.10–0.30/run) |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | 1,000 req/month |
| `UNSPLASH_ACCESS_KEY` | [unsplash.com/developers](https://unsplash.com/developers) → New Application | 50 req/hour |
| `PEXELS_API_KEY` | [pexels.com/api](https://www.pexels.com/api) → Get Started | 200 req/hour |
| `GIPHY_API_KEY` | [developers.giphy.com](https://developers.giphy.com) → Create an App | Free dev key |

> **No Unsplash/Pexels key?** Falls back to Lorem Picsum placeholder images automatically.
>
> **No Giphy key?** Falls back to a curated set of 15 GIFs covering common blog emotions (mind blown, this is fine, celebrate, etc.).

---

## Running

### Interactive mode

```bash
uv run python main.py
# or if using pip/venv:
python main.py
```

You'll be prompted for:
1. Blog title
2. Context (audience, key points, tone — press Enter three times when done)
3. Configuration (length, tone, audience, format, GIFs, diagrams)

### Command-line mode (skip title/context prompts)

```bash
uv run python main.py "Your Blog Title" "Context: target audience, key points, tone"
```

> You'll still see the interactive config prompts for length/tone/format. Press Enter to accept defaults.

---

## Example Run

```
🖊️  Agentic Blog Writer
════════════════════════
Blog Title: Why Most AI Projects Fail Before They Start

Context: Focus on data quality, unclear business goals, and team skill gaps.
Target audience is tech leads and CTOs. Tone: direct and slightly provocative.


────────────────────────
📝  Blog Configuration
────────────────────────
Blog Length:
  1. Short  (800–1200 words)
  2. Medium (1500–2500 words)  [default]
  3. Long   (2500–4000 words)
  4. Pillar (4000–6000 words)
Choice (default 2): 2

...

🚀 Starting blog generation pipeline...
   Title: Why Most AI Projects Fail Before They Start
   ⏱  Estimated time: ~3–5 min

  ✅ 🧠 Enhancing context              8s   [total 8s]
  ✅ 🔍 Researching          ◀ parallel   22s   [total 30s]
  ✅ 📈 Analyzing trends     ◀ parallel    4s   [total 34s]  ← finished ~same time, not 48s
  ✅ 📋 Generating outline              12s   [total 46s]
  ✅ ✍️  Writing draft                  35s   [total 1m 21s]
  ✅ ✏️  Editing              ◀ parallel   20s   [total 1m 41s]
  ✅ 🔖 Analyzing SEO        ◀ parallel    3s   [total 1m 44s]  ← finished ~same time
  ✅ 🎨 Adding visuals & GIFs           30s   [total 2m 14s]
  ✅ 💾 Saving                           1s   [total 2m 15s]

⏱  Completed in 2m 15s   (was ~2m 50s sequential — ~35s saved)

============================================================
📄 FINAL BLOG PREVIEW (first 500 chars)
============================================================
# Why Most AI Projects Fail Before They Start

Everyone's building AI. Most are failing quietly...

📁 Full blog saved to: output/Why_Most_AI_Projects_Fail_20250115_143022.md

🏷️  SEO Tags: ai-projects, machine-learning, data-quality, product-strategy, ai-failure

============================================================
💡 NEXT BLOG IDEAS (trending now)
============================================================
  1. The $1M AI Mistake — why data labeling is everyone's blind spot
  2. How to build an AI business case your CFO will approve
  ...

🚀 Publish to Medium? (y/N):
```

---

## Output Files

Every run creates two files in `output/`:

```
output/
├── Why_Most_AI_Projects_Fail_20250115_143022.md    ← Full blog in Markdown
└── Why_Most_AI_Projects_Fail_20250115_143022.html  ← Beautiful browser preview
```

Open the `.html` in any browser to see the final styled version with images, diagrams, and GIFs rendered.

---

## Publishing to Medium

Medium's public API no longer accepts new integrations. The publisher uses browser automation instead:

1. Run the pipeline as normal
2. At the prompt, type `y` and press Enter
3. A Chrome window opens — **first time only**: log into Medium in the browser, then press Enter in the terminal
4. The blog title and full formatted content are pasted into the editor automatically
5. Review in the browser, add tags, then click **Publish**

The Chrome session is saved at `~/.medium_uc_profile` — you only need to log in once ever.

---

## Example Usage Scenarios

### Technical tutorial
```bash
python main.py \
  "Building Your First RAG Pipeline with LangChain" \
  "Audience: Python developers new to LLMs. Cover vector stores, embeddings, retrieval. Use practical code examples. Tone: friendly and educational."
```

### Thought leadership
```bash
python main.py \
  "Why Most AI Projects Fail Before They Start" \
  "Focus on data quality, unclear business goals, team skill gaps. Target: tech leads and CTOs. Tone: direct, slightly provocative."
```

### Non-technical explainer
```bash
python main.py \
  "Transformers Explained Without the Math" \
  "Audience: non-technical product managers. No equations. Use analogies. Cover attention mechanism, training, real-world uses."
```

---

## Common Issues

| Problem | Fix |
|---------|-----|
| `Missing env vars: OPENAI_API_KEY` | Copy `.env.example` → `.env` and fill in your keys |
| Images not showing in HTML preview | Run from the project root directory — image paths are CWD-relative |
| Medium CAPTCHA on first run | Complete the verification in the browser once; subsequent runs skip it |
| Chrome not found for publishing | Install Chrome: `sudo apt install google-chrome-stable` (Linux) or download from [google.com/chrome](https://google.com/chrome) |
| Mermaid diagram looks broken | AI-generated Mermaid occasionally has syntax errors — edit the `.md` file manually if needed |

---

## Cost Estimate

A typical Medium-length blog (1500–2500 words):

| Model call | ~Tokens | ~Cost | Runs |
|------------|---------|-------|------|
| Context enhancer | 1K | $0.003 | sequential |
| Researcher | 2K | $0.006 | parallel |
| Trend analyst | 3K | $0.009 | parallel |
| Outline generator | 2K | $0.006 | sequential |
| Writer | 6K | $0.018 | sequential |
| Editor | 5K | $0.015 | parallel |
| SEO analyzer | 2K | $0.006 | parallel |
| Enhancer | 8K | $0.024 | sequential |
| **Total** | ~29K | **~$0.09–0.16** | |

All calls use GPT-4o. Actual costs vary with blog length.

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| Double-diamond parallel topology | `researcher` + `trend_analyst` are independent; `editor` + `seo_analyzer` are independent — no reason to serialize them |
| SEO extracted from editor into its own node | Single responsibility + enables the second parallel diamond; editor focuses on prose, SEO node focuses on metadata |
| Fan-in handled by LangGraph automatically | No polling or locks needed — LangGraph holds a node until all its predecessors complete |
| GPT-4o for all nodes | Consistent quality; temperature tuned per role (0.2–0.7) |
| Tavily over SerpAPI | Native LangChain integration, better structured results, generous free tier |
| Mermaid via mermaid.ink | No local install needed; PNG renders server-side |
| Remote CDN URLs for images | Works in both HTML preview and Medium editor (local `file://` paths don't load in browsers) |
| `undetected-chromedriver` for Medium | Bypasses Cloudflare bot detection |
| Persistent Chrome profile | Log into Medium once; session reused on every subsequent run |
| Curated GIF fallback set | Works without a Giphy API key; 15 GIFs cover common blog emotional moments |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | Agent orchestration via StateGraph |
| `langchain-openai` | GPT-4o LLM calls |
| `langchain-tavily` | Tavily web search tool |
| `tavily-python` | Tavily API client |
| `python-dotenv` | Load `.env` into environment |
| `markdown` | Convert Markdown to HTML |
| `httpx` | HTTP client for image/GIF fetching |
| `undetected-chromedriver` | Bot-detection-resistant Chrome for Medium publishing |
| `selenium` | Browser automation (used by publisher) |

---

## Project Context

Built as part of an Agentic Generative AI Projects course. Demonstrates a practical 9-node multi-agent LangGraph pipeline with a double-diamond parallel topology — two fan-out/fan-in points where independent agents run concurrently. Goes from a raw idea to a polished, SEO-ready, visually rich blog post with one-click Medium publishing.
