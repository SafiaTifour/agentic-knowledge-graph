import asyncio
from src.ingest.populate_graph import ingest_corpus

def main():
    try:
        asyncio.run(ingest_corpus())
    except Exception as e:
        print(f"Error during ingestion: {e}")

if __name__ == "__main__":
    main()