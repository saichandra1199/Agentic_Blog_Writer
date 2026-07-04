from langgraph.graph import StateGraph, START, END
from state import BlogState
from nodes.context_enhancer import context_enhancer_node
from nodes.researcher import researcher_node
from nodes.trend_analyst import trend_analyst_node
from nodes.outline_generator import outline_generator_node
from nodes.writer import writer_node
from nodes.editor import editor_node
from nodes.seo_analyzer import seo_analyzer_node
from nodes.enhancer import enhancer_node
from utils.file_handler import save_blog


def save_output_node(state: BlogState) -> BlogState:
    filepath = save_blog(
        title=state["title"],
        content=state["final_blog"],
        output_dir="output",
    )
    print(f"\n✅ Blog saved: {filepath}")
    return {**state, "output_file": filepath}


def build_graph() -> StateGraph:
    """
    Double-diamond parallel topology:

        context_enhancer
              ↓ (fan-out)
        researcher ────────┐
        trend_analyst ─────┤
                           ↓ (fan-in)
                   outline_generator
                           ↓
                         writer
                           ↓ (fan-out)
        editor ────────────┐
        seo_analyzer ──────┤
                           ↓ (fan-in)
                        enhancer
                           ↓
                      save_output
    """
    graph = StateGraph(BlogState)

    graph.add_node("context_enhancer", context_enhancer_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("trend_analyst", trend_analyst_node)
    graph.add_node("outline_generator", outline_generator_node)
    graph.add_node("writer", writer_node)
    graph.add_node("editor", editor_node)
    graph.add_node("seo_analyzer", seo_analyzer_node)
    graph.add_node("enhancer", enhancer_node)
    graph.add_node("save_output", save_output_node)

    graph.add_edge(START, "context_enhancer")

    # First diamond — research and trend analysis run in parallel
    graph.add_edge("context_enhancer", "researcher")
    graph.add_edge("context_enhancer", "trend_analyst")

    # Fan-in — outline waits for both branches
    graph.add_edge("researcher", "outline_generator")
    graph.add_edge("trend_analyst", "outline_generator")

    graph.add_edge("outline_generator", "writer")

    # Second diamond — editing and SEO analysis run in parallel
    graph.add_edge("writer", "editor")
    graph.add_edge("writer", "seo_analyzer")

    # Fan-in — enhancer waits for both branches
    graph.add_edge("editor", "enhancer")
    graph.add_edge("seo_analyzer", "enhancer")

    graph.add_edge("enhancer", "save_output")
    graph.add_edge("save_output", END)

    return graph.compile()
