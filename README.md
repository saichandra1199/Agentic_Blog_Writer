# Agentic Blog Writer

**Turn a title and a few notes into a publication-ready blog post — automatically.**

Give it a topic and some context. A chain of specialized AI agents researches the web, analyzes trends, builds a structured outline, writes a full draft, edits it for clarity and SEO, enriches it with diagrams, images, and GIFs, saves it as Markdown + HTML, and optionally publishes it directly to Medium — all in 3–5 minutes.

---

## What It Does (Quick Summary)

| Step | What happens |
|------|-------------|
| You provide | Blog title + a few sentences of context |
| Agent 1 | Expands your context into a detailed content brief |
| Agent 2 | Searches the web for research (Tavily) |
| Agent 3 | Identifies viral trends and suggests 5 follow-up blog ideas |
| Agent 4 | Builds a structured outline (H1/H2/H3) |
| Agent 5 | Writes a full 800–6000 word draft |
| Agent 6 | Edits the draft and generates SEO metadata |
| Agent 7 | Adds diagrams, images, GIFs, tables, and callout blocks |
| Output | `.md` + `.html` files saved to `output/` |
| Optional | Publishes directly to Medium via browser automation |

---

## Full Pipeline

```
User Input (title + context)
         │
         ▼
  [ Context Enhancer ]   → Expands raw context into a detailed creative brief
         │
         ▼
  [ Researcher ]         → Tavily web search → structured research notes
         │
         ▼
  [ Trend Analyst ]      → Identifies viral formats, hooks, and 5 next blog ideas
         │
         ▼
  [ Outline Generator ]  → H1/H2/H3 skeleton with section descriptions
         │
         ▼
  [ Writer ]             → Full 800–6000 word draft
         │
         ▼
  [ Editor ]             → Polished draft + SEO (tags, keywords, meta description)
         │
         ▼
  [ Enhancer ]           → Mermaid diagrams, stock images, GIFs, tables, callout blocks
         │
         ▼
  output/<title>_<timestamp>.md   (+ .html preview file)
         │
         ▼
  [ Publisher ] (optional)  → Opens Medium in browser, pastes formatted content
```

---

## Features in Detail

### 8-Node LangGraph Pipeline
Each agent has exactly one job. Sequential pipeline — each stage fully completes before the next starts. Easy to debug: if something goes wrong, you know exactly which node failed.

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

### SEO Metadata
The editor node generates and appends:
- **Meta description** — 150–160 character summary for search engines
- **Focus keyword** — primary keyword the post targets
- **Secondary keywords** — 3–5 supporting keywords
- **Tags** — 5–8 relevant blog tags

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
├── graph.py                        # LangGraph StateGraph — wires all 8 nodes together
├── state.py                        # BlogState TypedDict — shared data passed between all nodes
├── config.py                       # Interactive config collector (length, tone, audience, format)
│
├── nodes/
│   ├── context_enhancer.py         # Expands raw context → detailed brief
│   ├── researcher.py               # Tavily search → research notes
│   ├── trend_analyst.py            # Trend analysis + 5 next blog ideas
│   ├── outline_generator.py        # Research → H1/H2/H3 outline
│   ├── writer.py                   # Outline → full draft
│   ├── editor.py                   # Draft → edited draft + SEO JSON
│   ├── enhancer.py                 # Draft → visuals injected (diagrams, images, GIFs)
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
  ✅ 🔍 Researching                   22s   [total 30s]
  ✅ 📈 Analyzing trends              18s   [total 48s]
  ✅ 📋 Generating outline            12s   [total 1m 00s]
  ✅ ✍️  Writing draft                35s   [total 1m 35s]
  ✅ ✏️  Editing & SEO                20s   [total 1m 55s]
  ✅ 🎨 Adding visuals & GIFs         30s   [total 2m 25s]
  ✅ 💾 Saving                         1s   [total 2m 26s]

⏱  Completed in 2m 26s

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

| Model call | ~Tokens | ~Cost |
|------------|---------|-------|
| Context enhancer | 1K | $0.003 |
| Researcher (summary) | 2K | $0.006 |
| Trend analyst | 3K | $0.009 |
| Outline generator | 2K | $0.006 |
| Writer | 6K | $0.018 |
| Editor | 5K | $0.015 |
| Enhancer | 8K | $0.024 |
| **Total** | ~27K | **~$0.08–0.15** |

All calls use GPT-4o. Actual costs vary with blog length.

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| Sequential graph, no cycles | Simpler to debug; each stage fully commits before the next begins |
| GPT-4o for all nodes | Consistent quality; temperature tuned per role (0.3–0.6) |
| `---SEO_DATA---` delimiter in editor output | Avoids JSON-inside-markdown parsing fragility |
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

Built as part of an Agentic Generative AI Projects course. Demonstrates a practical 8-node multi-agent LangGraph pipeline for a real content creation use case — from a raw idea to a polished, SEO-ready, visually rich blog post with one-click Medium publishing.
