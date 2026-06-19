import json
from graph.state import ResearchState
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

load_dotenv()

llm = init_chat_model("groq:llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))


def filter_relevant(state: ResearchState) -> dict:
    """
    Score each paper for relevance to the user query.
    Drops papers scoring below 6/10 and papers with stub abstracts.
    """
    papers = state["ranked_papers"]
    if not papers:
        return {"ranked_papers": []}

    paper_list = "\n".join([
        f"{i}. Title: {p['title']}\n   Abstract: {p['abstract'][:300]}"
        for i, p in enumerate(papers)
    ])

    prompt = f"""You are a research librarian. The user is interested in: "{state['query']}"

                For each paper below, score its relevance 1-10 (10 = directly on topic, 1 = unrelated).
                Return ONLY a valid JSON array of integers, one score per paper, in the same order.
                Example for 3 papers: [8, 3, 9]

                Papers:
                {paper_list}

                Return only the JSON array, nothing else."""

    try:
        result = llm.invoke(prompt)
        scores = json.loads(result.content.strip())
        filtered = [p for p, score in zip(papers, scores) if score >= 6]
        if not filtered:
            # fallback: keep all if filter is too aggressive
            filtered = papers
        print(f"Relevance filter: {len(papers)} → {len(filtered)} papers kept")
        return {"ranked_papers": filtered}
    except Exception as e:
        print(f"Relevance filter failed ({e}), keeping all papers")
        return {"ranked_papers": papers}