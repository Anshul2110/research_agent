from typing import TypedDict, List, Optional, Annotated
import operator

class Paper(TypedDict):
    title: str
    abstract: str
    authors: str
    year: str
    url: str
    # "arxiv" | "scholar" | "semantic"
    source: str 
    citations: int

class ResearchState(TypedDict):
    query: str
     # which scrapers to run    
    sources: List[str]   
    raw_papers: Annotated[List[Paper], operator.add]  
    ranked_papers: List[Paper]
    # {title, summary, url, year}
    summaries: List[dict]  
    error: Optional[str]
    trend_synthesis: Optional[str]