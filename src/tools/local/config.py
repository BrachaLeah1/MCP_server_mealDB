"""
Configuration management for local tools.
Handles recipes directory configuration and user preferences.
"""

import json
from pathlib import Path


# Config file for storing user preferences
CONFIG_FILE = Path.home() / ".mealdb_recipes_config"


def load_recipes_dir() -> Path:
    """Load recipes directory from config or return default."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                recipes_path = config.get("recipes_dir")
                if recipes_path:
                    path = Path(recipes_path).expanduser()
                    path.mkdir(parents=True, exist_ok=True)
                    return path
        except Exception:
            pass
    
    # Default: Try /mnt/user-data/outputs first (for Claude.ai), fallback to Documents
    outputs_path = Path("/mnt/user-data/outputs")
    if outputs_path.exists() and outputs_path.is_dir():
        default_path = outputs_path / "recipes"
        default_path.mkdir(parents=True, exist_ok=True)
        return default_path
    
    # Fallback to Documents
    default_path = Path.home() / "Documents" / "mealdb_recipes"
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path


def save_recipes_dir(directory: str) -> Path:
    """Save recipes directory to config."""
    path = Path(directory).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    
    config = {"recipes_dir": str(path)}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return path


# Initialize recipes directory
RECIPES_DIR = load_recipes_dir()