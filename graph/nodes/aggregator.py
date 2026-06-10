from graph.state import ResearchState


def score_paper(p: dict) -> float:
    """Combined score: citation weight + recency boost."""
    try:
        year = int(p.get("year") or 0)
    except ValueError:
        year = 0
    citations = int(p.get("citations") or 0)
    recency = max(0, year - 2019)       # papers from 2020+ get a boost
    return citations * 0.6 + recency * 10


def aggregate(state: ResearchState) -> dict:
    papers = state["raw_papers"]

    # deduplicate by lowercased title
    seen, unique = set(), []
    for p in papers:
        key = p["title"].lower().strip()
        if key not in seen and p["title"] and p["abstract"]:
            seen.add(key)
            unique.append(p)

    # rank by combined citation + recency score
    ranked = sorted(unique, key=score_paper, reverse=True)

    return {"ranked_papers": ranked[:10]}