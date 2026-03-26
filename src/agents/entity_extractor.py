import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.config import CONFIG
from src.utils.prompts import PROMPTS
from src.schemas.agent_schemas import EntityExtractorResponse
from dotenv import load_dotenv

from src.utils.decorators import async_retry_with_fallback

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=CONFIG["llm"]["model"],
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=CONFIG["llm"]["temperature"]
)
structured_llm = llm.with_structured_output(EntityExtractorResponse)

@async_retry_with_fallback(max_retries=3, fallback_value=[])
async def extract_entities(question: str) -> list[str]:
    """
    Extracts named entities from a given question that could act as nodes in a knowledge graph.
    Returns a validated list of string entities.
    """
    prompt = PROMPTS["entity_extraction"].format(question=question)
    response = await structured_llm.ainvoke(prompt)
    return response.entities