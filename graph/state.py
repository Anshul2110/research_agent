from typing import TypedDict, List, Optional

class Paper(TypedDict):
    title: str
    abstract: str
    authors: str
    year: str
    url: str
    # "arxiv" | "scholar" | "semantic"
    source: str 

class ResearchState(TypedDict):
    query: str
     # which scrapers to run    sources: List[str]   
    raw_papers: List[Paper]
    ranked_papers: List[Paper]
    # {title, summary, url, year}
    summaries: List[dict]  
    error: Optional[str]