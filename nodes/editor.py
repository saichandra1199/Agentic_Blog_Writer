import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import BlogState


SYSTEM_PROMPT = """You are a senior editor and SEO specialist for a top-tier publication.

Your editing tasks:
1. **Clarity**: Simplify complex sentences. Remove redundancy. Tighten every paragraph.
2. **Flow**: Ensure smooth transitions. Check logical progression of ideas.
3. **Tone**: Conversational yet authoritative. Not salesy. Not academic.
4. **Accuracy**: Flag any factual claims that seem unsupported (add [?] marker).
5. **Engagement**: Strengthen the hook. Punch up the conclusion.

Your SEO tasks — extract and return as JSON at the END of your response:
- meta_description: 150-160 char summary for search engines
- tags: 5-8 relevant Medium tags (lowercase, hyphenated)
- focus_keyword: primary keyword phrase
- secondary_keywords: 3-5 supporting keyword phrases

Output format — return the full edited blog first, then on a new line:
---SEO_DATA---
{"meta_description": "...", "tags": [...], "focus_keyword": "...", "secondary_keywords": [...]}"""


def editor_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Edit the following blog post and provide SEO data:

{state['draft']}"""),
    ]

    response = llm.invoke(messages)
    content = response.content

    seo_data = {}
    edited_draft = content

    if "---SEO_DATA---" in content:
        parts = content.split("---SEO_DATA---", 1)
        edited_draft = parts[0].strip()
        try:
            seo_data = json.loads(parts[1].strip())
        except json.JSONDecodeError:
            seo_data = {"raw": parts[1].strip()}

    return {**state, "edited_draft": edited_draft, "seo_data": seo_data}
