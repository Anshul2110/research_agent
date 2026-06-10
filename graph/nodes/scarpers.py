from apify_client import ApifyClient
from graph.state import ResearchState
import os
from dotenv import load_dotenv

load_dotenv()

client = ApifyClient(os.getenv("APIFY_KEY"))

def scrape_arxiv(state: ResearchState) -> dict:
    try:
        run = client.actor("fatihai-tools/arxiv-scraper").call(run_input={
            "searchQuery": state["query"],
            "maxItems": 10
        })
        papers = []
        for item in client.dataset(run.default_dataset_id).iterate_items():
            papers.append({
                "title": item.get("title", ""),
                "abstract": item.get("abstract", ""),
                "authors": ", ".join(item.get("authors", [])) if isinstance(item.get("authors"), list) else item.get("authors", ""),
                "year": str(item.get("published", ""))[:4],
                "url": item.get("url", ""),
                "source": "arxiv",
                "citations": 0
            })
        if not papers:
            print("ArXiv returned 0 results")
        return {"raw_papers": state.get("raw_papers", []) + papers}
    except Exception as e:
        print(f"ArXiv scraper failed: {e}")
        return {"raw_papers": state.get("raw_papers", []), "error": f"arxiv: {str(e)}"}
 
 
def scrape_scholar(state: ResearchState) -> dict:
    try:
        run = client.actor("primeparse/google-scholar-scraper").call(run_input={
            "query": state["query"],
            "maxPages": 2,
            "startYear": 2022,
            "proxyConfiguration": {"useApifyProxy": True}
        })
        papers = []
        for item in client.dataset(run.default_dataset_id).iterate_items():
            authors = item.get("authors", [])
            if isinstance(authors, list):
                authors = ", ".join(authors)
            abstract = item.get("abstract", "")
            # skip stub abstracts from Scholar (just ellipsis snippets)
            if len(abstract) < 80:
                continue
            papers.append({
                "title": item.get("title", ""),
                "abstract": abstract,
                "authors": authors,
                "year": str(item.get("year", "")),
                "url": item.get("scholarLink") or item.get("url", ""),
                "source": "scholar",
                "citations": int(item.get("citations", 0) or 0)
            })
        if not papers:
            print("Google Scholar returned 0 results — proxy may have been blocked")
        return {"raw_papers": state.get("raw_papers", []) + papers}
    except Exception as e:
        print(f"❌ Google Scholar scraper failed: {e}")
        return {"raw_papers": state.get("raw_papers", []), "error": f"scholar: {str(e)}"}
 
 
def scrape_semantic(state: ResearchState) -> dict:
    try:
        run = client.actor("agenscrape/semantic-scholar-paper-scraper").call(run_input={
            "keyword": state["query"],
            "maxResults": 10
        })
        papers = []
        for item in client.dataset(run.default_dataset_id).iterate_items():
            papers.append({
                "title": item.get("title", ""),
                "abstract": item.get("abstract", ""),
                "authors": item.get("authors", ""),
                "year": str(item.get("year", "")),
                "url": item.get("url", ""),
                "source": "semantic",
                "citations": int(item.get("citationCount", 0) or 0)
            })
        if not papers:
            print("Semantic Scholar returned 0 results")
        return {"raw_papers": state.get("raw_papers", []) + papers}
    except Exception as e:
        print(f"Semantic Scholar scraper failed: {e}")
        return {"raw_papers": state.get("raw_papers", []), "error": f"semantic: {str(e)}"}
 