# Research Radar

An agentic research tool that scrapes the latest papers from ArXiv, Semantic Scholar, and Google Scholar based on a user query, then summarizes and ranks them into a readable news-style feed — plus a "State of the Field" trend briefing.

Built with **LangGraph**, **Groq (Llama 3.3 70B)**, **Apify**, and **Streamlit**.

## System architecture

<img width="1763" height="860" alt="Research Radar architecture diagram" src="https://github.com/user-attachments/assets/2c3ce20d-832d-4d46-ac81-2e7561113a81" />

The pipeline runs as a LangGraph state machine:

1. **Supervisor node** fans out to selected scrapers in parallel using the `Send` API
2. **Scraper nodes** (ArXiv, Semantic Scholar, Google Scholar) hit Apify actors concurrently
3. **Aggregator node** deduplicates by title and ranks by a combined citation + recency score
4. **Relevance filter node** uses an LLM to score and drop off-topic papers
5. **Summarizer node** generates a 3-sentence, faithful, news-style brief per paper
6. **Trend synthesis node** writes a 2-paragraph "State of the Field" overview across all papers

## Features

- **Parallel scraping** across 3 academic sources via LangGraph's `Send` API fan-out
- **Deduplication + ranking** combining citation count and publication recency
- **LLM-based relevance filtering** to remove off-topic results before summarization
- **Faithful summarization** — prompted and evaluated to stay grounded in the source abstract
- **Trend synthesis** — a field-level briefing generated across all retrieved papers
- **Query-level caching** (1 hour TTL) to minimize redundant Apify calls
- **Containerized with Docker** for consistent, portable deployment

## Evaluation

The pipeline is evaluated across 5 benchmark queries (`eval/evaluate.py`) on:

| Metric | Description |
|---|---|
| Source coverage | % of selected sources that returned results |
| Deduplication rate | % of raw papers removed as duplicates |
| Filter retention rate | % of papers kept after relevance filtering |
| Compression ratio | abstract length ÷ summary length |
| Readability gain | Flesch Reading Ease score, summary vs. abstract |
| Faithfulness | LLM-as-judge score (1–10) for groundedness in the source abstract |
| Synthesis coverage | % of paper titles referenced in the trend synthesis |
| Latency | end-to-end wall time per query |

**Before → after prompt iteration** (tightening the summarization prompt for faithfulness):

| Metric | Before | After |
|---|---|---|
| Avg compression ratio | 2.2× | 13.1× |
| Avg readability gain | -16.7 pts | +7.6 pts |
| Avg faithfulness | 6.3/10 | 6.4/10 |

Full reports: [`eval/eval_report.json`](eval/eval_report.json), [`eval/eval_report_2.json`](eval/eval_report_2.json)

## Getting started

### Prerequisites

- An [Apify](https://apify.com) account and API key
- A [Groq](https://console.groq.com) account and API key

### Run with Docker (recommended)

```bash
git clone https://github.com/Anshul2110/research_agent.git
cd research_agent

docker build -t research-radar .

docker run -p 8501:8501 \
  -e APIFY_KEY="your_apify_key" \
  -e GROQ_API_KEY="your_groq_key" \
  research-radar
```

Open `http://localhost:8501`.


### Run the evaluation suite

```bash
python -m eval.evaluate
```

Results are saved to `eval/eval_report.json`.

## Project structure

```
research_agent/
├── Dockerfile
├── .dockerignore
├── .env.example
├── requirements.txt
├── app.py                      # Streamlit UI
├── graph/
│   ├── state.py                # LangGraph state schema
│   ├── graph.py                # graph construction + parallel fan-out
│   └── nodes/
│       ├── scrapers.py         # ArXiv / Semantic Scholar / Google Scholar
│       ├── aggregator.py       # dedup + citation-recency ranking
│       ├── filter.py           # LLM relevance filter
│       └── summarizer.py       # paper summaries + trend synthesis
└── eval/
    ├── evaluate.py             # evaluation harness
    └── eval_report*.json       # evaluation results
```

## Tech stack

- **Orchestration:** LangGraph (parallel fan-out via `Send` API)
- **LLM:** Groq — Llama 3.3 70B Versatile
- **Data sources:** Apify actors (ArXiv, Semantic Scholar, Google Scholar scrapers)
- **UI:** Streamlit
- **Deployment:** Docker







