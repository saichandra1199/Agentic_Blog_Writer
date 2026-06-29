import os
from langchain_community.tools.tavily_search import TavilySearchResults


def get_search_tool(max_results: int = 5) -> TavilySearchResults:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not set in environment")
    return TavilySearchResults(max_results=max_results)
