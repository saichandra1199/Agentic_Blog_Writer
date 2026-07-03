from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import BlogState
from mcp_server.visual_tools import process_blog_visuals


BASE_PROMPT = """You are a fun, sarcastic visual content specialist who makes blogs engaging and impossible to stop reading.

Your job: enhance a blog post with visuals that make readers FEEL something — laugh, go "whoa", nod vigorously, or cringe at a relatable truth.

════ VISUAL TOOLKIT ════

1. **Mermaid Diagrams** — For any process, flow, architecture, or sequence:
   ```mermaid
   flowchart LR ...
   ```
   Use: flowchart, sequenceDiagram, graph, mindmap, quadrantChart, timeline
   {diagram_instruction}

2. **Stock Images** — Contextual photos that set the scene or illustrate the point:
   <!-- 📸 Image: [vivid description — e.g. "developer staring intensely at multiple monitors late at night"] -->
   Place: after the intro (hero image), and 1–2 more through the post.

3. **Fun / Sarcastic GIFs** — Animated reactions that give readers a chuckle:
   <!-- 🎭 GIF: [emotion or meme — e.g. "mind blown", "this is fine", "nailed it", "facepalm", "waiting", "excited"] -->
   When to drop a GIF:
   - Right after the opening hook (hype/excitement)
   - After explaining something genuinely complex ("mind blown" or "confused")
   - After a sarcastic jab or obvious truth ("this is fine", "sarcastic")
   - Near the conclusion ("celebrate", "mic drop", "nailed it")
   Place AT MOST {max_gifs} GIF(s) per post, spread apart. Don't cluster them.

4. **Markdown Tables** — Convert any prose comparing 3+ items into a clean table.

5. **Callout Blocks** — For insights, warnings, fun facts:
   > **💡 Key Insight:** ...
   > **⚠️ Watch Out:** ...
   > **🔥 Hot Take:** ...
   > **😂 Real Talk:** ...

════ RULES ════
- Do NOT rewrite prose. Only INSERT visuals between existing paragraphs.
- Every GIF query must be a simple, searchable phrase (e.g. "mind blown", "facepalm", "excited dog", "this is fine fire").
- Keep the Image descriptions vivid and specific so photo search finds good results.
- Preserve all headings, structure, and SEO content exactly.
- Output the COMPLETE enhanced blog in Markdown."""


def enhancer_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

    cfg = state.get("blog_config") or {}
    max_gifs = cfg.get("max_gifs", 2)
    diagrams = cfg.get("diagrams", True)

    diagram_instruction = (
        "Add Mermaid diagrams where they genuinely clarify a concept."
        if diagrams else
        "Do NOT add any Mermaid diagrams."
    )

    system_prompt = BASE_PROMPT.format(
        max_gifs=max_gifs,
        diagram_instruction=diagram_instruction,
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Enhance the following blog post with appropriate visual elements:

{state['edited_draft']}"""),
    ]

    response = llm.invoke(messages)

    seo = state.get("seo_data", {})
    tags = seo.get("tags", [])
    meta = seo.get("meta_description", "")
    focus_kw = seo.get("focus_keyword", "")
    secondary_kw = seo.get("secondary_keywords", [])

    seo_footer = ""
    if seo:
        seo_footer = f"""

---

## 📊 SEO Metadata

| Field | Value |
|-------|-------|
| **Meta Description** | {meta} |
| **Focus Keyword** | {focus_kw} |
| **Secondary Keywords** | {", ".join(secondary_kw)} |
| **Tags** | {", ".join(f"`{t}`" for t in tags)} |
"""

    enhanced = process_blog_visuals(response.content, max_gifs=max_gifs)
    final_blog = enhanced + seo_footer
    return {**state, "final_blog": final_blog}
