import os
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from src.graph.neo4j_client import Neo4jClient
from src.utils.config import CONFIG
from src.utils.prompts import PROMPTS
from src.schemas.agent_schemas import CypherQueryResponse
from dotenv import load_dotenv

from src.utils.decorators import async_retry_with_fallback

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=CONFIG["llm"]["model"],
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=CONFIG["llm"]["temperature"]
)
structured_llm = llm.with_structured_output(CypherQueryResponse)

@async_retry_with_fallback(max_retries=3, fallback_value=[])
async def query_graph(question: str, entities: list[str]) -> list[dict]:
    """
    Generates a Cypher query from a question and a list of extracted entities, 
    and executes it against the Neo4j knowledge graph.
    Returns a list of dictionary facts representing the matched graph structure.
    """
    if not entities:
        return []

    client = Neo4jClient()
    entity_list = ", ".join(f'"{e}"' for e in entities)

    prompt = PROMPTS["cypher_generation"].format(entity_list=entity_list, question=question)
    response = await structured_llm.ainvoke(prompt)
    cypher = response.query.strip()
    
    if cypher.startswith("```"):
        cypher = cypher.split("```")[1]
        if cypher.startswith("cypher") or cypher.startswith("sql"):
            cypher = cypher[cypher.index("\n"):]
    cypher = cypher.strip()

    try:
        # Offload sync client run_query call to thread pool
        results = await asyncio.to_thread(client.run_query, cypher)
    except Exception as e:
        print(f"  Cypher error: {e}")
        print(f"  Query was: {cypher}")
        results = []
    finally:
        client.close()
        
    return results