from graph.state import ResearchState
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model("groq:llama-3.3-70b-versatile", api_key=os.getenv("grok_api_key"))

def summarize(state: ResearchState) -> dict:
    summaries = []
    for paper in state["ranked_papers"]:
        prompt = f"""You are a science journalist. Given this research paper, write a 3-sentence 
news-style summary a non-expert can understand. Lead with the key innovation.

Title: {paper['title']}
Abstract: {paper['abstract']}
Authors: {paper['authors']} ({paper['year']})

Output only the 3-sentence summary, no preamble."""
        result = llm.invoke(prompt)
        summaries.append({
            "title": paper["title"],
            "summary": result.content,
            "url": paper["url"],
            "year": paper["year"],
            "source": paper["source"],
        })
    return {"summaries": summaries}