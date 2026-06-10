import streamlit as st
import pandas as pd
from graph.graph import build_graph

st.set_page_config(page_title="Research Radar", layout="wide")

## Header
st.title("Research Radar")
st.caption("Enter a topic. Get the latest papers as readable news briefs — plus a field overview.")

## sidebar controls 
with st.sidebar:
    st.header("Settings")
    sources = st.multiselect(
        "Sources",
        ["arxiv", "semantic", "scholar"],
        default=["arxiv", "semantic"],
        help="Select which databases to scrape. Scholar can be slow or blocked."
    )
    st.divider()
    st.caption("Results are cached for 1 hour per query to save Apify credits.")


# cached graph runner
@st.cache_data(ttl=3600, show_spinner=False)
def run_research(query: str, sources: tuple) -> dict:
    """
    Cache by (query, sources) so re-runs within an hour don't hit Apify again.
    sources must be a tuple (hashable) for st.cache_data to work.
    """
    graph = build_graph(list(sources))
    return graph.invoke({
        "query": query,
        "sources": list(sources),
        "raw_papers": [],
        "ranked_papers": [],
        "summaries": [],
        "trend_synthesis": None,
        "error": None,
    })


## Search Bar
query = st.text_input(
    "Topic / keyword",
    placeholder="e.g. multimodal LLMs, CRISPR gene editing, reinforcement learning from human feedback"
)

search_clicked = st.button("🔍 Search", type="primary", disabled=not query)

if search_clicked and query:
    if not sources:
        st.warning("Please select at least one source in the sidebar.")
        st.stop()

    with st.spinner(f"Scraping {', '.join(sources)} and summarizing..."):
        result = run_research(query, tuple(sorted(sources)))

    if result.get("error"):
        st.error(f"One or more scrapers had issues: {result['error']}")

    summaries = result.get("summaries", [])
    if not summaries:
        st.warning("No relevant papers found. Try a different query or add more sources.")
        st.stop()

    ## trend synthesis box
    synthesis = result.get("trend_synthesis")
    if synthesis:
        st.subheader("State of the Field")
        st.info(synthesis)
        st.divider()

    ## summary statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Papers found", len(summaries))
    col2.metric("Sources searched", len(sources))

    years = [s["year"] for s in summaries if s.get("year") and str(s["year"]).isdigit()]
    if years:
        col3.metric("Most recent year", max(years))

    ## publication year chart
    if years:
        with st.expander("Papers by publication year"):
            year_counts = pd.Series(years).value_counts().sort_index()
            st.bar_chart(year_counts)

    st.divider()

    ## source labels 
    source_labels = {
        "arxiv":    ("🔴", "ArXiv"),
        "semantic": ("🔵", "Semantic Scholar"),
        "scholar":  ("🟢", "Google Scholar"),
    }

    ## paper summary cards
    st.subheader(f"{len(summaries)} papers")

    for item in summaries:
        with st.container(border=True):
            emoji, label = source_labels.get(item["source"], ("⚪", item["source"].upper()))

            # title row
            title_col, badge_col = st.columns([5, 1])
            with title_col:
                st.markdown(f"#### {item['title']}")
            with badge_col:
                st.caption(f"{emoji} {label}")

            # meta row
            meta_parts = [f"{item['year']}"]
            if item.get("citations"):
                meta_parts.append(f"{item['citations']:,} citations")
            st.caption("  ·  ".join(meta_parts))

            # summary
            st.write(item["summary"])

            # link
            st.markdown(f"[Read paper →]({item['url']})")