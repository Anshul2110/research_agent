from graph.state import ResearchState

## aggregator node: deduplicate and rank papers
def aggregate(state: ResearchState) -> dict:
    papers = state["raw_papers"]
    # deduplicate by lowercased title
    seen, unique = set(), []
    for p in papers:
        key = p["title"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    # rank: sort by recency of publication (year)
    ranked = sorted(unique, key=lambda p: (p["year"]), reverse=True) ## might add citations in later iterations
    return {"ranked_papers": ranked[:10]}