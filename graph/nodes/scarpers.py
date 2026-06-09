from apify_client import ApifyClient
from graph.state import ResearchState
import os
from dotenv import load_dotenv

load_dotenv()

client = ApifyClient(os.getenv("APIFY_KEY"))

## arxiv scraper
def scrape_arxiv(state: ResearchState) -> dict:
    run = client.actor("fatihai-tools/arxiv-scraper").call(run_input={
        "searchQuery": state["query"],
        "maxItems": 10
    })
    papers = []
    for item in client.dataset(run.default_dataset_id).iterate_items():
        papers.append({
            "title": item["title"],
            "abstract": item.get("abstract", ""),
            "authors": ", ".join(item.get("authors", [])),
            "year": str(item.get("published", ""))[:4],
            "url": item["url"],
            "source": "arxiv"
        })
    return {"raw_papers": state.get("raw_papers", []) + papers}

## scholar scraper
def scrape_scholar(state: ResearchState) -> dict:
    run = client.actor("primeparse/google-scholar-scraper").call(run_input={
        "query": state["query"],
        "maxPages": 2,
        "startYear": 2022,
        "proxyConfiguration": {
        "useApifyProxy": True
  }
    })
    papers = []
    for item in client.dataset(run.default_dataset_id).iterate_items():
        papers.append({
            "title": item["title"],
            "abstract": item.get("abstract", ""),
            "authors": ", ".join(item.get("authors", [])),
            "year": str(item.get("year", "")),
            "url": item["url"],
            "source": "scholar"
        })
    return {"raw_papers": state.get("raw_papers", []) + papers}

## semantic scholar scraper
def scrape_semantic(state: ResearchState) -> dict:
    run = client.actor("agenscrape/semantic-scholar-paper-scraper").call(run_input={
        "keyword": state["query"],
        "maxResult": 10
    })
    papers = []
    for item in client.dataset(run.default_dataset_id).iterate_items():
        papers.append({
            "title": item["title"],
            "abstract": item.get("abstract", ""),
            "authors": ", ".join(item.get("authors", [])),
            "year": str(item.get("year", "")),
            "url": item["url"],
            "source": "semantic"
        })
    return {"raw_papers": state.get("raw_papers", []) + papers}