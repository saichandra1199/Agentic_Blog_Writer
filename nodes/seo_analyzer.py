import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import BlogState


SYSTEM_PROMPT = """You are an SEO specialist for a top-tier publication.

Given a blog title and draft, return ONLY a valid JSON object with these fields:
- meta_description: 150-160 char summary for search engines
- tags: 5-8 relevant Medium tags (lowercase, hyphenated)
- focus_keyword: primary keyword phrase
- secondary_keywords: 3-5 supporting keyword phrases

Return ONLY the JSON object. No explanation. No markdown fences."""


def seo_analyzer_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Blog title: {state['title']}\n\nDraft:\n{state['draft']}"),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        seo_data = json.loads(raw)
    except json.JSONDecodeError:
        seo_data = {"raw": raw}

    return {"seo_data": seo_data}
