from typing import List
from pydantic import BaseModel, Field

class EntityExtractorResponse(BaseModel):
    entities: List[str] = Field(
        description="List of extracted named entities that could be nodes in a knowledge graph."
    )

class CypherQueryResponse(BaseModel):
    query: str = Field(
        description="The generated Cypher query to run against Neo4j."
    )

class ReasoningResponse(BaseModel):
    answer: str = Field(
        description="The final answer reasoning over the retrieved facts."
    )

class Triple(BaseModel):
    subject: str = Field(description="Entity name acting as subject")
    relation: str = Field(description="Verb phrase in snake_case")
    object: str = Field(description="Entity name or short fact acting as object")

class TripleExtractionResponse(BaseModel):
    triples: List[Triple] = Field(description="List of extracted knowledge triples")
