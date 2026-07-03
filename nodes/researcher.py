from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from tools.search import get_search_tool
from state import BlogState


SYSTEM_PROMPT = """You are an expert research assistant. Your job is to gather relevant,
up-to-date information to support writing a high-quality blog post.

Given a blog title and user-provided context, search the web for:
- Recent statistics, data, and trends
- Real-world examples and case studies
- Expert opinions and notable perspectives
- Common misconceptions to address

Return structured research notes in Markdown format with clear sections.
Be factual, concise, and focus only on what's directly relevant to the blog topic."""


def researcher_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
    search_tool = get_search_tool(max_results=5)

    search_query = f"{state['title']} latest trends examples statistics 2024 2025"
    raw_results = search_tool.invoke(search_query)

    if isinstance(raw_results, str):
        search_text = raw_results
    else:
        search_text = "\n\n".join(
            f"**Source:** {r.get('url', 'N/A')}\n{r.get('content', '')}"
            if isinstance(r, dict) else str(r)
            for r in raw_results
        )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Blog Title: {state['title']}

User Context: {state['context']}

Web Search Results:
{search_text}

Synthesize the above into structured research notes to support writing this blog."""),
    ]

    response = llm.invoke(messages)
    return {**state, "research": response.content}
