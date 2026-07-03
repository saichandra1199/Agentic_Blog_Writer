from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import BlogState


BASE_PROMPT = """You are an expert blog architect specializing in Medium-style long-form content.

Create a detailed, engaging blog outline that:
- Opens with a compelling hook or relatable problem — shaped by what's trending right now
- Flows logically from introduction to conclusion
- Includes H1 (title), H2 (main sections), H3 (subsections) structure
- Ends with clear takeaways or a call to action

Use the Trend Insights to pick the best angle, format, and hook style for maximum engagement.
For each section, provide a 1-2 sentence description of what it will cover.
Output in clean Markdown outline format."""


def outline_generator_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

    cfg = state.get("blog_config") or {}
    section_range = cfg.get("section_range", "5–8")
    fmt           = cfg.get("format", "Deep Dive")
    audience      = cfg.get("audience", "Intermediate")

    SYSTEM_PROMPT = f"""{BASE_PROMPT}

Sections: {section_range} main sections.
Blog format: {fmt}.
Target audience: {audience}."""

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Blog Title: {state['title']}

User Context: {state['context']}

Research Notes:
{state['research']}

Trend Insights (use these to shape the angle, hook, and format):
{state.get('trend_insights', 'No trend data available.')}

Generate a detailed blog outline for this topic."""),
    ]

    response = llm.invoke(messages)
    return {**state, "outline": response.content}
