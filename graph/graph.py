from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from graph.nodes.scarpers import scrape_arxiv, scrape_semantic, scrape_scholar
from graph.nodes.aggregator import aggregate
from graph.nodes.summarizer import summarize

def build_graph(sources: list[str]):
    g = StateGraph(ResearchState)

    # add nodes conditionally based on selected sources
    if "arxiv" in sources:
        g.add_node("arxiv", scrape_arxiv)
    if "semantic" in sources:
        g.add_node("semantic", scrape_semantic)
    if "scholar" in sources:
        g.add_node("scholar", scrape_scholar)

    g.add_node("aggregate", aggregate)
    g.add_node("summarize", summarize)

    # set entry: all selected scrapers run in parallel (LangGraph handles fan-out)
    g.set_entry_point("arxiv" if "arxiv" in sources else "semantic")

    # scrapers → aggregator
    for src in sources:
        g.add_edge(src, "aggregate")

    g.add_edge("aggregate", "summarize")
    g.add_edge("summarize", END)

    return g.compile()