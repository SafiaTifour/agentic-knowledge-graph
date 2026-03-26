import yaml
from pathlib import Path

PROMPTS_PATH = Path(__file__).parent.parent / "prompts" / "prompts.yaml"

def load_prompts() -> dict:
    with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

PROMPTS = load_prompts()
