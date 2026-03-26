import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.config import CONFIG
from src.utils.prompts import PROMPTS
from src.schemas.agent_schemas import TripleExtractionResponse
from src.utils.decorators import async_retry_with_fallback
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=CONFIG["llm"]["model"],
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=CONFIG["llm"]["temperature"]
)
structured_llm = llm.with_structured_output(TripleExtractionResponse)

@async_retry_with_fallback(max_retries=3, fallback_value=TripleExtractionResponse(triples=[]))
async def extract_triples(text: str) -> list[dict]:
    """
    Extract factual knowledge triples from the text asynchronously.
    Returns a list of dictionaries to maintain compatibility with the graph populator.
    """
    prompt = PROMPTS["triple_extraction"].format(text=text)
    response = await structured_llm.ainvoke(prompt)
    
    # Check if the fallback hit (which returns the Pydantic model directly)
    if isinstance(response, TripleExtractionResponse):
        return [{"subject": t.subject, "relation": t.relation, "object": t.object} for t in response.triples]
    return []