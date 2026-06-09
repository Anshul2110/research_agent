import streamlit as st
from graph.graph import build_graph

st.set_page_config(page_title="Research Radar", layout="wide")
st.title("Research Radar")
st.caption("Enter a topic. Get the latest papers as readable news briefs.")

query = st.text_input("Topic / keyword", placeholder="e.g. multimodal LLMs")
sources = st.multiselect("Sources", ["arxiv", "semantic", "scholar"],
                          default=["arxiv", "semantic"])

if st.button("Search") and query:
    with st.spinner("Scraping and summarizing..."):
        graph = build_graph(sources)
        result = graph.invoke({"query": query, "sources": sources, "raw_papers": []})

    st.subheader(f"{len(result['summaries'])} papers found")
    for item in result["summaries"]:
        with st.container(border=True):
            st.markdown(f"### {item['title']}")
            st.caption(f"{item['year']}  ·  {item['source'].upper()}")
            st.write(item["summary"])
            st.markdown(f"[Read paper →]({item['url']})")