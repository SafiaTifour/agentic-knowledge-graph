import os
import yaml
from pathlib import Path

# Provide a robust path to config.yaml
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.yaml"

def load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# Singleton-like configuration accessible by just importing it
CONFIG = load_config()
