import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(
                os.getenv("NEO4J_USERNAME", "neo4j"),
                os.getenv("NEO4J_PASSWORD")
            ),
            connection_timeout=10
        )

    def close(self):
        self.driver.close()

    def run_query(self, query, params=None):
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]

    def get_document_hash(self, uri: str) -> str:
        query = "MATCH (d:Document {uri: $uri}) RETURN d.content_hash AS hash"
        res = self.run_query(query, {"uri": uri})
        return res[0]["hash"] if res else None

    def upsert_document_hash(self, uri: str, content_hash: str):
        query = """
        MERGE (d:Document {uri: $uri})
        SET d.content_hash = $content_hash
        """
        self.run_query(query, {"uri": uri, "content_hash": content_hash})

    def invalidate_triples_by_source(self, uri: str):
        query = """
        MATCH ()-[r:RELATION {source_uri: $uri}]->()
        SET r.valid = false
        """
        self.run_query(query, {"uri": uri})

    def create_triple(self, subject, relation, obj, source_uri=""):
        query = """
        MERGE (a:Entity {name: $subject})
        MERGE (b:Entity {name: $obj})
        MERGE (a)-[r:RELATION {type: $relation, source_uri: $source_uri}]->(b)
        ON CREATE SET r.valid = true
        ON MATCH SET r.valid = true
        """
        self.run_query(query, {
            "subject": subject,
            "relation": relation,
            "obj": obj,
            "source_uri": source_uri
        })

    def verify_connection(self):
        result = self.run_query("RETURN 1 AS ok")
        return result[0]["ok"] == 1