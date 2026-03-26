from typing import TypedDict
from langgraph.graph import StateGraph, END

# Import the refactored async agents
from src.agents.entity_extractor import extract_entities
from src.agents.graph_query_agent import query_graph
from src.agents.reasoning_agent import reason_over_facts
from src.utils.constants import MESSAGES

class AgentState(TypedDict):
    question: str
    entities: list[str]
    graph_facts: list[dict]
    answer: str

async def entity_extraction_node(state: AgentState) -> AgentState:
    print(MESSAGES["EXTRACTING"])
    entities = await extract_entities(state["question"])
    print(MESSAGES["FOUND_ENTITIES"].format(entities=entities))
    return {**state, "entities": entities}

async def graph_query_node(state: AgentState) -> AgentState:
    print(MESSAGES["QUERYING"])
    facts = await query_graph(state["question"], state["entities"])
    print(MESSAGES["RETRIEVED_FACTS"].format(count=len(facts)))
    return {**state, "graph_facts": facts}

async def reasoning_node(state: AgentState) -> AgentState:
    print(MESSAGES["REASONING"])
    answer = await reason_over_facts(state["question"], state["graph_facts"])
    return {**state, "answer": answer}

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("extract_entities", entity_extraction_node)
    graph.add_node("query_graph", graph_query_node)
    graph.add_node("reasoning", reasoning_node)
    graph.set_entry_point("extract_entities")
    graph.add_edge("extract_entities", "query_graph")
    graph.add_edge("query_graph", "reasoning")
    graph.add_edge("reasoning", END)
    return graph.compile()