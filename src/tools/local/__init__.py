"""
Local tools package for recipe management.

This package provides MCP tools for saving recipes, creating shopping lists,
and managing local recipe files.
"""

from .tools import get_local_tool_definitions, handle_local_tool
from .config import RECIPES_DIR, load_recipes_dir, save_recipes_dir
from .categories import get_ingredient_category
from .api import fetch_meal_data
from .pdf_recipe import create_recipe_pdf
from .pdf_shopping import create_shopping_list_pdf


__all__ = [
    # Main tool functions
    'get_local_tool_definitions',
    'handle_local_tool',
    
    # Configuration
    'RECIPES_DIR',
    'load_recipes_dir',
    'save_recipes_dir',
    
    # Utilities
    'get_ingredient_category',
    'fetch_meal_data',
    
    # PDF generators
    'create_recipe_pdf',
    'create_shopping_list_pdf',
]