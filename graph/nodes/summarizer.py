from graph.state import ResearchState
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model("groq:llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

def summarize(state: ResearchState) -> dict:
    """Generate a 3-sentence news-style summary for each paper."""
    summaries = []
    for paper in state["ranked_papers"]:
        prompt =prompt = f"""You are a science journalist writing for a general audience.
                            Summarize this paper in exactly 3 sentences using ONLY information explicitly stated in the abstract below.

                            Rules:
                            - Each sentence must be under 20 words
                            - No jargon — if you must use a technical term, define it inline
                            - Lead with the real-world impact, not the methodology
                            - Do NOT infer, extrapolate, or add context not present in the abstract
                            - If the abstract does not mention real-world impact, describe what the paper does instead

                    
                    Abstract (your only source of truth):
                    {paper['abstract']}


                    Other metadata (for context):
                    Title: {paper['title']}
                    Authors: {paper['authors']} ({paper['year']})
 
                    Strictly output only the 3-sentence summary."""
        try:
            result = llm.invoke(prompt)
            summaries.append({
                "title": paper["title"],
                "summary": result.content,
                "url": paper["url"],
                "year": paper["year"],
                "source": paper["source"],
                "citations": paper.get("citations", 0),
            })
        except Exception as e:
            print(f"Summarization failed for '{paper['title']}': {e}")
 
    return {"summaries": summaries}
 
 
def synthesize_trends(state: ResearchState) -> dict:
    """
    Single LLM call that reads across all summaries and writes a 
    'State of the Field' briefing — the hero section in the UI.
    """
    if not state.get("summaries"):
        return {"trend_synthesis": None}
 
    bullet_list = "\n".join([
        f"- {s['title']} ({s['year']}): {s['summary']}"
        for s in state["summaries"]
    ])
 
    prompt = f"""You are a senior research analyst writing a briefing for a smart generalist audience.
                
                Based on these recent papers on "{state['query']}", write a "State of the Field" briefing 
                in exactly 2 paragraphs:
                - Paragraph 1: The dominant themes and what the field is converging on.
                - Paragraph 2: Emerging directions, open problems, or tensions worth watching.
                
                Be specific — mention paper titles or techniques by name where relevant. 
                Write for someone who is intelligent but not a specialist in this field.
                
                Papers:
                {bullet_list}
                
                Output only the 2 paragraphs, no headings or preamble."""
    
 
    try:
        result = llm.invoke(prompt)
        return {"trend_synthesis": result.content}
    except Exception as e:
        print(f"Trend synthesis failed: {e}")
        return {"trend_synthesis": None}
 