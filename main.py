import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()


def validate_env():
    missing = []
    if not os.getenv("OPENAI_API_KEY"):
        missing.append("OPENAI_API_KEY")
    if not os.getenv("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if missing:
        print(f"❌ Missing env vars: {', '.join(missing)}")
        print("   Copy .env.example → .env and fill in your keys.")
        sys.exit(1)


def get_input() -> tuple[str, str]:
    if len(sys.argv) >= 3:
        title = sys.argv[1]
        context = sys.argv[2]
        return title, context

    print("\n🖊️  Agentic Blog Writer")
    print("=" * 40)
    title = input("Blog Title: ").strip()
    if not title:
        print("❌ Title cannot be empty.")
        sys.exit(1)
    print("\nContext (what you want covered, tone, audience, key points):")
    print("(Press Enter thrice when done)\n")
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    context = "\n".join(lines).strip()
    return title, context


def main():
    validate_env()

    from graph import build_graph

    title, context = get_input()

    from config import get_blog_config
    blog_config = get_blog_config()

    print(f"\n🚀 Starting blog generation pipeline...")
    print(f"   Title: {title}")
    print(f"   ⏱  Estimated time: ~3–5 min\n")

    app = build_graph()

    steps = [
        "context_enhancer",
        "researcher",
        "trend_analyst",
        "outline_generator",
        "writer",
        "editor",
        "seo_analyzer",
        "enhancer",
        "save_output",
    ]
    step_labels = {
        "context_enhancer": "🧠 Enhancing context",
        "researcher":        "🔍 Researching          ◀ parallel",
        "trend_analyst":     "📈 Analyzing trends     ◀ parallel",
        "outline_generator": "📋 Generating outline",
        "writer":            "✍️  Writing draft",
        "editor":            "✏️  Editing              ◀ parallel",
        "seo_analyzer":      "🔖 Analyzing SEO        ◀ parallel",
        "enhancer":          "🎨 Adding visuals & GIFs",
        "save_output":       "💾 Saving",
    }

    def _fmt(seconds: float) -> str:
        s = int(seconds)
        return f"{s // 60}m {s % 60:02d}s" if s >= 60 else f"{s}s"

    pipeline_start = time.time()
    step_start = pipeline_start
    final_state = None

    for event in app.stream({"title": title, "context": context, "blog_config": blog_config}):
        for node_name in steps:
            if node_name in event:
                elapsed_step = time.time() - step_start
                elapsed_total = time.time() - pipeline_start
                label = step_labels.get(node_name, node_name)
                print(f"  ✅ {label:<30} {_fmt(elapsed_step):>6}   [total {_fmt(elapsed_total)}]")
                step_start = time.time()
                final_state = event[node_name]

    total_time = time.time() - pipeline_start
    print(f"\n⏱  Completed in {_fmt(total_time)}")

    if final_state and final_state.get("final_blog"):
        print("\n" + "=" * 60)
        print("📄 FINAL BLOG PREVIEW (first 500 chars)")
        print("=" * 60)
        print(final_state["final_blog"][:500] + "...")
        print(f"\n📁 Full blog saved to: {final_state.get('output_file', 'output/')}")

        if final_state.get("seo_data"):
            seo = final_state["seo_data"]
            print("\n🏷️  SEO Tags:", ", ".join(seo.get("tags", [])))

        suggestions = final_state.get("next_blog_suggestions")
        if suggestions:
            print("\n" + "=" * 60)
            print("💡 NEXT BLOG IDEAS (trending now)")
            print("=" * 60)
            for i, idea in enumerate(suggestions, 1):
                print(f"  {i}. {idea}")

        print("\n" + "=" * 60)
        publish = input("🚀 Publish to Medium? (y/N): ").strip().lower()
        if publish == "y":
            from nodes.publisher import publish_to_medium
            publish_to_medium(final_state)


if __name__ == "__main__":
    main()
