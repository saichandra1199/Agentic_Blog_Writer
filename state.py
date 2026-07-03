from typing import TypedDict, Optional


class BlogState(TypedDict):
    title: str
    context: str
    blog_config: Optional[dict]
    research: Optional[str]
    trend_insights: Optional[str]
    next_blog_suggestions: Optional[list]
    outline: Optional[str]
    draft: Optional[str]
    edited_draft: Optional[str]
    seo_data: Optional[dict]
    final_blog: Optional[str]
    output_file: Optional[str]
    medium_url: Optional[str]
