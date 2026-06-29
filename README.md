# Agentic Blog Writer

**Turn a title and a few notes into a publication-ready blog post — automatically.**

Give it a topic and some context. A chain of specialized AI agents researches the web, builds a structured outline, writes a full draft, edits it for clarity and SEO, then enriches it with diagrams, tables, and callout blocks. Output lands as a clean Markdown file ready to paste into Medium.

---

## Problem

- Writing a quality blog post takes 3–6 hours of research, drafting, editing, and formatting.
- Maintaining consistency across posts (tone, structure, SEO) is hard without a defined process.
- Adding visual elements (diagrams, tables) is time-consuming and often skipped.
- SEO metadata — tags, meta descriptions, keywords — is an afterthought, not baked into the writing process.

---

## Solution

A LangGraph pipeline where each agent has exactly one job:

```
User Input (title + context)
         │
         ▼
  [ Researcher ]        → Tavily web search → structured research notes
         │
         ▼
  [ Outline Generator ] → H1/H2/H3 blog skeleton with section descriptions
         │
         ▼
  [ Writer ]            → Full 1500–2500 word draft
         │
         ▼
  [ Editor ]            → Edited draft + SEO metadata (tags, keywords, meta description)
         │
         ▼
  [ Enhancer ]          → Mermaid diagrams, comparison tables, callout blocks, image hints
         │
         ▼
  output/<title>_<timestamp>.md
```

---

## Architecture

```
Agentic_Blog_writer/
├── main.py                    # CLI entry point
├── graph.py                   # LangGraph StateGraph — wires all nodes
├── state.py                   # BlogState TypedDict — shared pipeline state
├── nodes/
│   ├── researcher.py          # Tavily search → research notes
│   ├── outline_generator.py   # Research → structured outline
│   ├── writer.py              # Outline → full draft
│   ├── editor.py              # Draft → edited draft + SEO JSON
│   └── enhancer.py            # Draft → visual elements injected
├── tools/
│   └── search.py              # Tavily search tool factory
├── utils/
│   └── file_handler.py        # Timestamped .md file save
├── output/                    # Generated blogs saved here
├── .env.example               # API key template
├── requirements.txt
└── plan.md
```

---

## Requirements

- Python 3.10+
- OpenAI API key with GPT-4o access
- Tavily API key (free tier: 1,000 searches/month — [sign up here](https://tavily.com))

---

## Installation

```bash
# 1. Clone or navigate to the project directory
cd Agentic_Blog_writer

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
```

Edit `.env`:
```env
OPENAI_API_KEY=sk-your-openai-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here
```

---

## Configuration

| Variable | Where to get it | Notes |
|----------|----------------|-------|
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | GPT-4o access required |
| `TAVILY_API_KEY` | [app.tavily.com](https://app.tavily.com) | Free tier: 1000 req/month |

---

## Running

**Interactive mode (prompts for input):**
```bash
python main.py
```

**Direct mode (pass args inline):**
```bash
python main.py "Blog Title Here" "Context: target audience, key points, tone, etc."
```

**Expected output:**
```
🚀 Starting blog generation pipeline...
   Title: The Future of AI Agents

🔍 Researching...
📋 Generating outline...
✍️  Writing draft...
✏️  Editing & SEO...
🎨 Adding visualizations...
💾 Saving...

✅ Blog saved: output/The_Future_of_AI_Agents_20250115_143022.md

============================================================
📄 FINAL BLOG PREVIEW (first 500 chars)
============================================================
# The Future of AI Agents: How Multi-Agent Systems Are Reshaping Software

AI agents aren't a future concept anymore — they're already running in production...

📁 Full blog saved to: output/The_Future_of_AI_Agents_20250115_143022.md

🏷️  SEO Tags: ai-agents, langgraph, multi-agent-systems, llm, software-engineering
```

---

## Usage Examples

### Example 1 — Technical tutorial
```bash
python main.py \
  "Building Your First RAG Pipeline with LangChain" \
  "Audience: Python developers new to LLMs. Cover vector stores, embeddings, retrieval. Use practical code examples. Tone: friendly and educational."
```

### Example 2 — Thought leadership
```bash
python main.py \
  "Why Most AI Projects Fail Before They Start" \
  "Focus on data quality, unclear business goals, and team skill gaps. Target: tech leads and CTOs. Tone: direct, slightly provocative."
```

### Example 3 — Explainer post
```bash
python main.py \
  "Transformers Explained Without the Math" \
  "Audience: non-technical product managers. No equations. Use analogies. Cover attention mechanism, training, real-world uses."
```

---

## Testing the Pipeline

| Scenario | What to do | What to expect |
|----------|-----------|----------------|
| Smoke test | Run with any title + 1 sentence context | Full .md generated in `output/` |
| Rich context | Provide 5+ bullet points of context | More focused, accurate content |
| Niche topic | Use a very specific technical topic | Researcher pulls relevant sources |
| Missing Tavily key | Remove `TAVILY_API_KEY` from `.env` | Clear error message on startup, no crash |
| Missing OpenAI key | Remove `OPENAI_API_KEY` from `.env` | Clear error message on startup, no crash |

---

## Key Design Decisions

| Decision | Reason |
|----------|--------|
| Sequential graph (no cycles) | Each stage fully completes before the next — simpler to debug and reason about |
| GPT-4o for all nodes | Consistent output quality; temperature varied per node role |
| `---SEO_DATA---` delimiter | Avoids JSON parsing fragility from fenced code blocks in editor output |
| Tavily over SerpAPI | Native LangChain integration, better structured results, generous free tier |
| Mermaid in Markdown | GitHub, Notion, and many blog platforms render Mermaid natively |
| Timestamped filenames | Prevents overwriting when running on same topic multiple times |

---

## Limitations

- Requires active internet connection (Tavily search)
- GPT-4o API costs apply (~$0.10–0.30 per full blog run depending on length)
- Mermaid diagrams are AI-generated suggestions — verify syntax before publishing
- Does not auto-publish to Medium (copy-paste the generated `.md`)
- Output quality depends on context quality — better input = better output

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `langgraph` | Agent orchestration via StateGraph |
| `langchain-openai` | GPT-4o calls |
| `langchain-community` | TavilySearchResults tool |
| `tavily-python` | Web search API |
| `python-dotenv` | Load `.env` into environment |

---

## Project Context

Built as part of an Agentic Generative AI Projects course. Demonstrates a practical multi-agent LangGraph pipeline for a real content creation use case — from raw idea to polished, SEO-ready blog post.
