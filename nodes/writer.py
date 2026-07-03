from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import BlogState


BASE_PROMPT = """You are a top influencer-style blog writer for Medium — think Ali Abdaal, Lenny Rachitsky,
or Sahil Bloom. You write content that gets shared, saved, and remembered.

Core influencer writing principles to apply:
- **Open with a punch** — first line creates instant curiosity or hits a pain point hard
- **Write like you talk** — short sentences, contractions, direct address ("you", "your")
- **Use the "1 idea per paragraph" rule** — never bury the lead in a wall of text
- **Personal credibility drops** — weave in "I've seen...", "When I tried...", "Most people miss..."
- **Provocative subheadings** — make each H2 a mini-hook, not a label
- **Concrete > abstract** — replace vague claims with numbers, names, specific examples
- **The scroll-stopper pattern** — every 300 words, add something visually distinct (a stat, quote, list, bold claim)
- **End sections with a "so what"** — never leave a section without the implication for the reader

Use the Trend Insights to match the format, angle, and emotional tone that's currently winning.
Full Markdown. # H1, ## H2, ### H3. No placeholders. Write everything completely."""


def writer_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    cfg = state.get("blog_config") or {}
    word_range    = cfg.get("word_range", "1500–2500")
    tone          = cfg.get("tone", "Conversational / Influencer style")
    audience      = cfg.get("audience", "Intermediate")
    fmt           = cfg.get("format", "Deep Dive")
    diagrams      = cfg.get("diagrams", True)

    diagram_note = (
        "Include Mermaid diagrams (```mermaid blocks) where they add clarity."
        if diagrams else
        "Do NOT include any Mermaid diagrams."
    )

    SYSTEM_PROMPT = f"""{BASE_PROMPT}

Target word count: {word_range} words.
Tone: {tone}.
Target audience: {audience}.
Blog format: {fmt}.
{diagram_note}"""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Blog Title: {state['title']}

User Context: {state['context']}

Research Notes:
{state['research']}

Trend Insights (match this angle, tone, and format):
{state.get('trend_insights', 'No trend data available.')}

Blog Outline:
{state['outline']}

Write the complete, publication-ready influencer-style blog post following the outline above."""),
    ]

    response = llm.invoke(messages)
    return {**state, "draft": response.content}
