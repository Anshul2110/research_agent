from typing import TypedDict, List, Optional

class Paper(TypedDict):
    title: str
    abstract: str
    authors: str
    year: str
    url: str
    source: str           # "arxiv" | "scholar" | "semantic"
    citations: int

class ResearchState(TypedDict):
    query: str
    sources: List[str]    # which scrapers to run
    raw_papers: List[Paper]
    ranked_papers: List[Paper]
    summaries: List[dict]  # {title, summary, url, year}
    error: Optional[str]