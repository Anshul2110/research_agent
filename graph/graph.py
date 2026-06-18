from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from graph.state import ResearchState
from graph.nodes.scrapers import scrape_arxiv, scrape_semantic, scrape_scholar
from graph.nodes.aggregator import aggregate
from graph.nodes.filter import filter_relevant
from graph.nodes.summarizer import summarize, synthesize_trends


SCRAPER_MAP = {
    "arxiv": scrape_arxiv,
    "semantic": scrape_semantic,
    "scholar": scrape_scholar,
}


def route_to_scrapers(state: ResearchState):
    """Fan out to all selected scrapers in parallel using Send API."""
    return [Send(src, state) for src in state["sources"] if src in SCRAPER_MAP]


def build_graph(sources: list[str]):
    g = StateGraph(ResearchState)

    # register only the selected scraper nodes
    for src in sources:
        if src in SCRAPER_MAP:
            g.add_node(src, SCRAPER_MAP[src])

    g.add_node("aggregate", aggregate)
    g.add_node("filter", filter_relevant)
    g.add_node("summarize", summarize)
    g.add_node("synthesize", synthesize_trends)

    # START → parallel scrapers (true fan-out)
    g.add_conditional_edges(START, route_to_scrapers)

    # all scrapers → aggregator
    for src in sources:
        if src in SCRAPER_MAP:
            g.add_edge(src, "aggregate")

    # linear pipeline after aggregation
    g.add_edge("aggregate", "filter")
    g.add_edge("filter", "summarize")
    g.add_edge("summarize", "synthesize")
    g.add_edge("synthesize", END)

    return g.compile()