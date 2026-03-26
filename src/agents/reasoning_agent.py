import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.config import CONFIG
from src.utils.prompts import PROMPTS
from src.schemas.agent_schemas import ReasoningResponse
from dotenv import load_dotenv

from src.utils.decorators import async_retry_with_fallback

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=CONFIG["llm"]["model"],
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=CONFIG["llm"]["temperature"]
)
structured_llm = llm.with_structured_output(ReasoningResponse)

@async_retry_with_fallback(max_retries=3, fallback_value="I apologize, but I am currently unable to provide an answer. Please try again later.")
async def reason_over_facts(question: str, graph_facts: list[dict]) -> str:
    """
    Generates an answer based ONLY on the retrieved facts from the graph.
    If facts are insufficient, the LLM will reply indicating the inability to answer.
    """
    if not graph_facts:
        return "I could not find relevant facts in the knowledge graph to answer this question."

    facts_str = "\n".join(
        f"- {row.get('n.name', '?')} --[{row.get('r.type', '?')}]--> {row.get('m.name', '?')}"
        for row in graph_facts
    )

    prompt = PROMPTS["reasoning"].format(question=question, facts_str=facts_str)
    response = await structured_llm.ainvoke(prompt)
    return response.answer.strip()