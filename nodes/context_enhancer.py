from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import BlogState


SYSTEM_PROMPT = """You are a blog strategy expert. A user has provided a blog title and brief context.
Your job is to expand that context into a rich, actionable brief that will guide research and writing.

Given the title and raw context, produce an enhanced brief that includes:
1. **Target Audience** — who will read this, their knowledge level, what they care about
2. **Core Intent** — what the reader should learn, feel, or do after reading
3. **Key Angles to Cover** — specific sub-topics, questions to answer, perspectives to include
4. **Tone & Style** — formal/casual, technical depth, narrative approach
5. **Gaps to Fill** — common misconceptions to address, questions the audience typically has
6. **Unique Value** — what makes this post worth reading over existing content

If the user context is already detailed, preserve their intent exactly — only add what's missing.
Output the enhanced brief in structured Markdown. Do NOT write the blog itself."""


def context_enhancer_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Blog Title: {state['title']}

User Context:
{state['context'] or '(none provided)'}

Expand this into a comprehensive blog brief."""),
    ]

    response = llm.invoke(messages)
    return {**state, "context": response.content}
