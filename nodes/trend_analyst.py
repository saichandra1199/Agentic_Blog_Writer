import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.search import get_search_tool
from state import BlogState


SYSTEM_PROMPT = """You are a top-tier content strategist and social media influencer coach.
You deeply understand what makes blog content go viral — on Medium, LinkedIn, Substack, and beyond.

Your job has two parts:

PART 1 — TREND ANALYSIS:
Search results in hand, identify:
- What angles/hooks on this topic are currently performing best
- What format is winning right now (personal story, listicle, hot take, deep dive, how-to, myth-busting)
- What emotional triggers are resonating (fear of missing out, inspiration, controversy, curiosity gap)
- What language patterns top influencers use (power words, sentence rhythm, opening styles)
- What unique perspective would make this post stand out from the 100 others on this topic

PART 2 — NEXT BLOG IDEAS:
Based on the trending signals, suggest exactly 5 follow-up blog ideas that would perform well.
Each idea should ride current trends and logically follow from this topic.

Output format — return PART 1 first, then on a new line:
---NEXT_BLOG_IDEAS---
["Idea 1 title — one sentence why it's trending", "Idea 2 title — one sentence why it's trending", ...]

Be specific and tactical. Think like a creator with 100k followers who lives and dies by engagement metrics."""


def trend_analyst_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.6)
    search_tool = get_search_tool(max_results=5)

    trend_query = f"trending blog topics {state['title']} 2025 viral content influencer"
    format_query = f"best performing blog formats Medium viral {state['title'].split()[0]} niche 2025"

    trend_results = search_tool.invoke(trend_query)
    format_results = search_tool.invoke(format_query)

    def fmt(results):
        if isinstance(results, str):
            return results
        return "\n\n".join(
            r if isinstance(r, str) else f"**Source:** {r.get('url', 'N/A')}\n{r.get('content', '')}"
            for r in results
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Blog Topic: {state['title']}
User Context: {state['context']}

Trend Search Results:
{fmt(trend_results)}

Format/Style Search Results:
{fmt(format_results)}

Analyze trends and provide influencer-style writing insights + 5 next blog ideas."""),
    ]

    response = llm.invoke(messages)
    content = response.content

    trend_insights = content
    next_blog_suggestions = []

    if "---NEXT_BLOG_IDEAS---" in content:
        parts = content.split("---NEXT_BLOG_IDEAS---", 1)
        trend_insights = parts[0].strip()
        try:
            next_blog_suggestions = json.loads(parts[1].strip())
        except json.JSONDecodeError:
            raw = parts[1].strip()
            next_blog_suggestions = [
                line.lstrip("0123456789.-) ").strip()
                for line in raw.splitlines()
                if line.strip()
            ]

    return {
        **state,
        "trend_insights": trend_insights,
        "next_blog_suggestions": next_blog_suggestions,
    }
