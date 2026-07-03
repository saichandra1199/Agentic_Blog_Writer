import os
from langchain_tavily import TavilySearch


def get_search_tool(max_results: int = 5) -> TavilySearch:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not set in environment")
    return TavilySearch(max_results=max_results)
