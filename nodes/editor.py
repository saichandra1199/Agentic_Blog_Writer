from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import BlogState


SYSTEM_PROMPT = """You are a senior editor for a top-tier publication.

Your editing tasks:
1. **Clarity**: Simplify complex sentences. Remove redundancy. Tighten every paragraph.
2. **Flow**: Ensure smooth transitions. Check logical progression of ideas.
3. **Tone**: Conversational yet authoritative. Not salesy. Not academic.
4. **Accuracy**: Flag any factual claims that seem unsupported (add [?] marker).
5. **Engagement**: Strengthen the hook. Punch up the conclusion.

Output the full edited blog in Markdown. Nothing else."""


def editor_node(state: BlogState) -> BlogState:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.3)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Edit the following blog post:\n\n{state['draft']}"),
    ]

    response = llm.invoke(messages)
    return {"edited_draft": response.content.strip()}
