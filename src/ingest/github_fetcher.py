import aiohttp
import asyncio
import hashlib
from typing import List, Dict

class GitHubFetcher:
    """
    Fetches raw file contents and computes SHA-256 state hashes from a public GitHub repository.
    """
    def __init__(self, repo: str, branch: str = "main", base_path: str = "", extensions: list = [".md", ".txt"]):
        self.repo = repo
        self.branch = branch
        self.base_path = base_path
        self.extensions = extensions
        # public api, rate limited to 60/hr unauthenticated, you can attach GH Token to headers in a real setting
        self.api_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"

    async def fetch_files(self) -> List[Dict[str, str]]:
        """
        Retrieves files matching criteria. Returns a list of dicts:
        [{'uri': '...', 'content': '...', 'hash': '...'}]
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url) as resp:
                if resp.status != 200:
                    text_resp = await resp.text()
                    raise Exception(f"Failed to fetch repo tree from {self.api_url}: {text_resp}")
                data = await resp.json()

            tree = data.get("tree", [])
            valid_files = [
                item for item in tree
                if item["type"] == "blob"
                and item["path"].startswith(self.base_path)
                and any(item["path"].endswith(ext) for ext in self.extensions)
            ]

            results = []
            for item in valid_files:
                uri = f"github://{self.repo}/{self.branch}/{item['path']}"
                raw_url = f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{item['path']}"
                
                async with session.get(raw_url) as file_resp:
                    if file_resp.status == 200:
                        content = await file_resp.text()
                        sha_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                        results.append({
                            "uri": uri,
                            "content": content,
                            "hash": sha_hash
                        })
                    else:
                        print(f"  Warning: failed to download raw file at {raw_url}")
                        
                # sleep slightly to respect github rate limits for raw unauth
                await asyncio.sleep(0.5)

            return results
