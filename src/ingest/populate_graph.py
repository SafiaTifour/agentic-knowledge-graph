import asyncio
from src.ingest.extract_triples import extract_triples
from src.graph.neo4j_client import Neo4jClient
from src.ingest.github_fetcher import GitHubFetcher
from src.utils.config import CONFIG

async def ingest_corpus():
    client = Neo4jClient()

    if not client.verify_connection():
        raise ConnectionError("Cannot connect to Neo4j Aura. Check your .env credentials.")

    repo = CONFIG["ingest"]["github_repo"]
    branch = CONFIG["ingest"]["github_branch"]
    path = CONFIG["ingest"]["github_path"]
    exts = CONFIG["ingest"]["file_extensions"]
    
    fetcher = GitHubFetcher(repo=repo, branch=branch, base_path=path, extensions=exts)
    
    print(f"Fetching from {repo} at {path}...")
    files = await fetcher.fetch_files()
    
    if not files:
        print("No files found!")
        client.close()
        return

    print(f"Found {len(files)} files to consider.")

    for file_info in files:
        uri = file_info["uri"]
        content = file_info["content"]
        current_hash = file_info["hash"]
        
        db_hash = await asyncio.to_thread(client.get_document_hash, uri)
        
        if db_hash == current_hash:
            print(f"Skipping {uri} (Unchanged)")
            continue
            
        print(f"Processing {uri}...")
        
        if db_hash is not None:
            await asyncio.to_thread(client.invalidate_triples_by_source, uri)
            
        triples = await extract_triples(content)
        print(f"  Extracted {len(triples)} triples")

        for triple in triples:
            await asyncio.to_thread(
                client.create_triple,
                subject=triple["subject"],
                relation=triple["relation"],
                obj=triple["object"],
                source_uri=uri
            )
            
        await asyncio.to_thread(client.upsert_document_hash, uri, current_hash)
        
        await asyncio.sleep(2)

    client.close()
    print("Ingestion complete!")