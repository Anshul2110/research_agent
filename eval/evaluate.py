# eval/evaluate.py
import time
import json
import re
from typing import List
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os

load_dotenv()

llm = init_chat_model("groq:llama-3.3-70b-versatile", api_key=os.getenv("grok_api_key"))


## benchmark queries
TEST_QUERIES = [
    "retrieval augmented generation",
    "protein structure prediction",
    "federated learning privacy",
    "reinforcement learning from human feedback",
    "diffusion models image generation",
]


## individual metric functions
def retrieval_metrics(result: dict, sources: list) -> dict:
    raw = result.get("raw_papers", [])
    ranked = result.get("ranked_papers", [])
    summaries = result.get("summaries", [])

    sources_returned = set(p["source"] for p in raw)
    source_coverage = len(sources_returned) / len(sources) if sources else 0

    dedup_rate = (len(raw) - len(ranked)) / len(raw) if raw else 0

    filter_retention = len(summaries) / len(ranked) if ranked else 0

    return {
        "total_raw_papers": len(raw),
        "papers_after_dedup": len(ranked),
        "papers_after_filter": len(summaries),
        "source_coverage": round(source_coverage, 2),
        "deduplication_rate": round(dedup_rate, 2),
        "filter_retention_rate": round(filter_retention, 2),
        "sources_returned": list(sources_returned),
    }


def readability_score(text: str) -> float:
    """Flesch Reading Ease — higher = easier to read (target: summaries > abstracts)."""
    sentences = max(1, text.count('.') + text.count('!') + text.count('?'))
    words = max(1, len(text.split()))
    syllables = max(1, sum(
        len(re.findall(r'[aeiouAEIOU]', w)) for w in text.split()
    ))
    return round(206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words), 1)


def summarization_metrics(summaries: list, ranked_papers: list) -> dict:
    if not summaries:
        return {}

    compression_ratios = []
    readability_gains = []

    for summary, paper in zip(summaries, ranked_papers):
        abstract = paper.get("abstract", "")
        s_text = summary.get("summary", "")

        if abstract and s_text:
            compression_ratios.append(len(abstract) / max(1, len(s_text)))
            readability_gains.append(
                readability_score(s_text) - readability_score(abstract)
            )

    return {
        "avg_compression_ratio": round(sum(compression_ratios) / len(compression_ratios), 2) if compression_ratios else 0,
        "avg_readability_gain": round(sum(readability_gains) / len(readability_gains), 1) if readability_gains else 0,
    }


def faithfulness_score(summary: str, abstract: str) -> dict:
    """LLM-as-judge: checks if summary contradicts the abstract."""
    prompt = f"""You are evaluating an AI-generated summary of a research paper.

Abstract: {abstract[:600]}

Summary: {summary}

Rate the summary on two dimensions, responding ONLY with valid JSON:
{{
  "faithfulness": <1-10, where 10 = no contradictions, 1 = major hallucinations>,
  "reason": "<one sentence>"
}}"""
    try:
        result = llm.invoke(prompt)
        return json.loads(result.content.strip())
    except Exception:
        return {"faithfulness": -1, "reason": "eval failed"}


def synthesis_coverage(synthesis: str, summaries: list) -> float:
    """What fraction of paper titles are referenced in the synthesis."""
    if not synthesis or not summaries:
        return 0.0
    mentioned = sum(
        1 for s in summaries
        if any(word.lower() in synthesis.lower()
               for word in s["title"].split() if len(word) > 5)
    )
    return round(mentioned / len(summaries), 2)


def latency_breakdown(query: str, sources: list) -> dict:
    """Time each node by running the graph with manual checkpoints."""
    from graph.graph import build_graph

    timings = {}
    t0 = time.time()
    result = build_graph(sources).invoke({
        "query": query,
        "sources": sources,
        "raw_papers": [],
        "ranked_papers": [],
        "summaries": [],
        "trend_synthesis": None,
        "error": None,
    })
    timings["total_seconds"] = round(time.time() - t0, 2)
    return timings, result


## full evaluation run function
def evaluate(queries: List[str] = TEST_QUERIES, sources: list = ["arxiv", "semantic"]):
    all_results = []

    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)

        timings, result = latency_breakdown(query, sources)
        summaries = result.get("summaries", [])
        ranked = result.get("ranked_papers", [])

        r_metrics = retrieval_metrics(result, sources)
        s_metrics = summarization_metrics(summaries, ranked)

        # faithfulness on first 3 papers only (saves LLM calls)
        faith_scores = []
        for summary, paper in zip(summaries[:3], ranked[:3]):
            score = faithfulness_score(summary["summary"], paper["abstract"])
            faith_scores.append(score["faithfulness"])
            print(f"  Faithfulness [{summary['title'][:40]}...]: {score['faithfulness']}/10 — {score['reason']}")

        avg_faithfulness = round(sum(f for f in faith_scores if f > 0) / max(1, len([f for f in faith_scores if f > 0])), 1)

        cov = synthesis_coverage(result.get("trend_synthesis", ""), summaries)

        report = {
            "query": query,
            "latency": timings,
            **r_metrics,
            **s_metrics,
            "avg_faithfulness_score": avg_faithfulness,
            "synthesis_coverage": cov,
        }

        all_results.append(report)

        print(f"  Source coverage:      {r_metrics['source_coverage']} ({r_metrics['sources_returned']})")
        print(f"  Raw → dedup → filter: {r_metrics['total_raw_papers']} → {r_metrics['papers_after_dedup']} → {r_metrics['papers_after_filter']}")
        print(f"  Dedup rate:           {r_metrics['deduplication_rate']}")
        print(f"  Filter retention:     {r_metrics['filter_retention_rate']}")
        print(f"  Avg compression:      {s_metrics.get('avg_compression_ratio')}×")
        print(f"  Avg readability gain: +{s_metrics.get('avg_readability_gain')} Flesch points")
        print(f"  Avg faithfulness:     {avg_faithfulness}/10")
        print(f"  Synthesis coverage:   {cov}")
        print(f"  Total latency:        {timings['total_seconds']}s")

    ## saving final report as json
    with open("eval/eval_report_2.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nReport saved to eval/eval_report.json")

    return all_results


if __name__ == "__main__":
    evaluate()