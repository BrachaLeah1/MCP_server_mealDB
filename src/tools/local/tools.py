"""
MCP tool definitions and handlers for local recipe management.
Provides tools for saving recipes, creating shopping lists, and managing files.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.types import Tool, TextContent

from .api import fetch_meal_data
from . import config
from .pdf_recipe import create_recipe_pdf
from .pdf_shopping import create_shopping_list_pdf


def get_local_tool_definitions() -> list[Tool]:
    """Return all local tool definitions."""
    return [
        Tool(
            name="save_recipe_to_file",
            description="Save a recipe to a PDF file. Use this ONLY when user explicitly asks to save/download a recipe. For viewing recipes, use lookup_meal_by_id from API tools instead.",
            inputSchema={
                "type": "object",
                "properties": {
                    "meal_id": {
                        "type": "string",
                        "description": "Meal ID to save (e.g., '52772')"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional custom filename (without extension). If not provided, uses meal name."
                    },
                    "directory": {
                        "type": "string",
                        "description": "Optional directory path where to save the file. If not provided, uses default recipes directory."
                    }
                },
                "required": ["meal_id"]
            },
        ),
        Tool(
            name="save_recipe_by_name",
            description="Save a recipe by searching for its name first, then saving it. More convenient than needing to know the meal ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipe_name": {
                        "type": "string",
                        "description": "Name of the recipe to search for and save (e.g., 'Arrabiata', 'Pad Thai')"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional custom filename (without extension). If not provided, uses meal name."
                    },
                    "directory": {
                        "type": "string",
                        "description": "Optional directory path where to save the file. If not provided, uses default recipes directory."
                    }
                },
                "required": ["recipe_name"]
            },
        ),
        Tool(
            name="list_saved_recipes",
            description="List all recipes saved on your computer",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="delete_saved_recipe",
            description="Delete a saved recipe file from your computer",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to delete (with or without .pdf extension)"
                    }
                },
                "required": ["filename"]
            },
        ),
        Tool(
            name="list_shopping_lists",
            description="List all existing shopping lists to check if any exist before creating a new one",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="delete_shopping_list",
            description="Delete a specific shopping list file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Name of the shopping list file to delete (with or without .pdf extension)"
                    }
                },
                "required": ["filename"]
            },
        ),
        Tool(
            name="delete_all_shopping_lists",
            description="Delete all shopping list files at once",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="create_shopping_list",
            description="Create a shopping list PDF from recipe IDs. IMPORTANT: Always call list_shopping_lists first to check for existing lists, then ask user if they want to replace or keep old ones.",
            inputSchema={
                "type": "object",
                "properties": {
                    "meal_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of meal IDs to create shopping list from"
                    },
                    "replace_existing": {
                        "type": "boolean",
                        "description": "If true, deletes old shopping lists (keeping max 3). If false, keeps all existing lists.",
                        "default": False
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional custom filename (without extension). If not provided, uses timestamped name."
                    },
                    "directory": {
                        "type": "string",
                        "description": "Optional directory path where to save the list. If not provided, uses default recipes directory."
                    }
                },
                "required": ["meal_ids"]
            },
        ),
        Tool(
            name="create_shopping_list_from_saved",
            description="Create a shopping list from all saved recipes automatically. No need to specify meal IDs manually.",
            inputSchema={
                "type": "object",
                "properties": {
                    "replace_existing": {
                        "type": "boolean",
                        "description": "If true, deletes old shopping lists (keeping max 3). If false, keeps all existing lists.",
                        "default": False
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional custom filename (without extension). If not provided, uses timestamped name."
                    }
                },
            },
        ),
        Tool(
            name="set_recipes_directory",
            description="Set where recipes should be saved on your computer",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Full path where recipes should be saved (e.g., '/home/user/recipes' or '~/Documents/recipes')"
                    }
                },
                "required": ["directory"]
            },
        ),
        Tool(
            name="get_recipes_directory",
            description="Get the current directory where recipes are being saved",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


async def handle_local_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Handle all local tool calls.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        List of TextContent responses, or None if tool not found
    """
    try:
        # Tool 1: Save recipe to file
        if name == "save_recipe_to_file":
            meal_id = arguments.get("meal_id", "")
            custom_filename = arguments.get("filename")
            custom_directory = arguments.get("directory")
            
            # Fetch meal data
            meal = await fetch_meal_data(meal_id)
            
            # Determine save directory
            if custom_directory:
                save_dir = Path(custom_directory).expanduser()
                save_dir.mkdir(parents=True, exist_ok=True)
            else:
                save_dir = config.RECIPES_DIR
            
            # Get category and create subdirectory
            category = meal.get('strCategory', 'Uncategorized').strip()
            category_dir = save_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            if custom_filename:
                filename = f"{custom_filename}.pdf"
            else:
                meal_name = meal.get('strMeal', 'recipe').replace('/', '-').replace('\\', '-')
                filename = f"{meal_name}.pdf"
            
            filepath = category_dir / filename
            
            # Check if file exists
            file_exists = filepath.exists()
            
            # Create PDF
            try:
                create_recipe_pdf(meal, filepath)
                
                response_text = f"Recipe saved successfully"
                if file_exists:
                    response_text += " (replaced existing file)"
                response_text += f"!\n\nFile: {filepath}\nRecipe: {meal.get('strMeal', 'Unknown')}\nCategory: {category}"
                
                return [TextContent(type="text", text=response_text)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Failed to create PDF: {str(e)}"
                )]
        
        # Tool 2: Save recipe by name
        elif name == "save_recipe_by_name":
            import httpx
            
            recipe_name = arguments.get("recipe_name", "")
            custom_filename = arguments.get("filename")
            custom_directory = arguments.get("directory")
            
            # Search for the recipe
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://www.themealdb.com/api/json/v1/1/search.php",
                    params={"s": recipe_name}
                )
                response.raise_for_status()
                data = response.json()
                
                meals = data.get("meals")
                if not meals:
                    return [TextContent(
                        type="text",
                        text=f"No recipe found with name '{recipe_name}'. Try a different search term."
                    )]
                
                # If multiple results, use the first one (most relevant)
                meal = meals[0]
                meal_id = meal.get("idMeal")
                
                # Now save using the meal_id
                result_msg = ""
                if len(meals) > 1:
                    result_msg = f"Found {len(meals)} recipes. Saving the first match: {meal.get('strMeal')}\n\n"
                
                # Determine save directory
                if custom_directory:
                    save_dir = Path(custom_directory).expanduser()
                    save_dir.mkdir(parents=True, exist_ok=True)
                else:
                    save_dir = config.RECIPES_DIR
                
                # Get category and create subdirectory
                category = meal.get('strCategory', 'Uncategorized').strip()
                category_dir = save_dir / category
                category_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate filename
                if custom_filename:
                    filename = f"{custom_filename}.pdf"
                else:
                    meal_name = meal.get('strMeal', 'recipe').replace('/', '-').replace('\\', '-')
                    filename = f"{meal_name}.pdf"
                
                filepath = category_dir / filename
                
                # Check if file exists
                file_exists = filepath.exists()
                
                # Create PDF
                try:
                    create_recipe_pdf(meal, filepath)
                    
                    result_msg += f"Recipe saved successfully"
                    if file_exists:
                        result_msg += " (replaced existing file)"
                    result_msg += f"!\n\nFile: {filepath}\nRecipe: {meal.get('strMeal', 'Unknown')}\nCategory: {category}"
                    
                    return [TextContent(type="text", text=result_msg)]
                except Exception as e:
                    return [TextContent(
                        type="text",
                        text=f"Failed to create PDF: {str(e)}"
                    )]
        
        # Tool 3: List saved recipes
        elif name == "list_saved_recipes":
            result = "Saved recipes by category:\n\n"
            total_files = 0
            
            # Get all category directories
            if not config.RECIPES_DIR.exists():
                return [TextContent(type="text", text=f"No recipes directory found.\n\nDirectory: {config.RECIPES_DIR}")]
            
            for category_dir in sorted(config.RECIPES_DIR.iterdir()):
                if category_dir.is_dir() and not category_dir.name.startswith('.'):
                    files = sorted(category_dir.glob("*.pdf"))
                    if files:
                        result += f"{category_dir.name} ({len(files)})\n"
                        for i, filepath in enumerate(files, 1):
                            size = filepath.stat().st_size / 1024  # Convert to KB
                            modified = datetime.fromtimestamp(filepath.stat().st_mtime)
                            result += f"   {i}. {filepath.stem}\n"
                            result += f"      Size: {size:.1f} KB | Modified: {modified.strftime('%Y-%m-%d %H:%M')}\n"
                        result += "\n"
                        total_files += len(files)
            
            if total_files == 0:
                return [TextContent(type="text", text=f"No saved recipes found.\n\nDirectory: {config.RECIPES_DIR}")]
            
            result += f"Total recipes: {total_files}\nDirectory: {config.RECIPES_DIR}"
            return [TextContent(type="text", text=result)]
        
        # Tool 4: Delete saved recipe
        elif name == "delete_saved_recipe":
            filename = arguments.get("filename", "")
            
            # Add .pdf if not present
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            # Search for the file in all category directories
            found = False
            filepath = None
            
            for category_dir in config.RECIPES_DIR.iterdir():
                if category_dir.is_dir():
                    potential_path = category_dir / filename
                    if potential_path.exists():
                        filepath = potential_path
                        found = True
                        break
            
            if not found:
                return [TextContent(
                    type="text",
                    text=f"Recipe not found: {filename}\n\nTip: Use 'list_saved_recipes' to see available recipes."
                )]
            
            filepath.unlink()
            
            return [TextContent(
                type="text",
                text=f"Recipe deleted successfully!\n\nDeleted: {filename}"
            )]
        
        # Tool 5: List shopping lists
        elif name == "list_shopping_lists":
            shopping_lists = sorted(config.RECIPES_DIR.glob("shopping_list_*.pdf"))
            
            if not shopping_lists:
                return [TextContent(
                    type="text",
                    text=f"No shopping lists found.\n\nDirectory: {config.RECIPES_DIR}"
                )]
            
            result = f"Found {len(shopping_lists)} shopping list(s):\n\n"
            for i, filepath in enumerate(shopping_lists, 1):
                size = filepath.stat().st_size / 1024
                modified = datetime.fromtimestamp(filepath.stat().st_mtime)
                result += f"{i}. {filepath.name}\n"
                result += f"   Size: {size:.1f} KB | Modified: {modified.strftime('%Y-%m-%d at %H:%M')}\n\n"
            
            result += f"Directory: {config.RECIPES_DIR}"
            return [TextContent(type="text", text=result)]
        
        # Tool 6: Delete shopping list
        elif name == "delete_shopping_list":
            filename = arguments.get("filename", "")
            
            # Add .pdf if not present
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            filepath = config.RECIPES_DIR / filename
            
            if not filepath.exists():
                return [TextContent(
                    type="text",
                    text=f"Shopping list not found: {filename}\n\nTip: Use 'list_shopping_lists' to see available lists."
                )]
            
            filepath.unlink()
            
            return [TextContent(
                type="text",
                text=f"Shopping list deleted successfully!\n\nDeleted: {filename}"
            )]
        
        # Tool 7: Delete all shopping lists
        elif name == "delete_all_shopping_lists":
            shopping_lists = list(config.RECIPES_DIR.glob("shopping_list_*.pdf"))
            
            if not shopping_lists:
                return [TextContent(
                    type="text",
                    text=f"No shopping lists found to delete.\n\nDirectory: {config.RECIPES_DIR}"
                )]
            
            count = len(shopping_lists)
            for filepath in shopping_lists:
                filepath.unlink()
            
            return [TextContent(
                type="text",
                text=f"Successfully deleted {count} shopping list(s)!"
            )]
        
        # Tool 8: Create shopping list
        elif name == "create_shopping_list":
            meal_ids = arguments.get("meal_ids", [])
            replace_existing = arguments.get("replace_existing", False)
            custom_filename = arguments.get("filename")
            custom_directory = arguments.get("directory")
            
            if not meal_ids:
                return [TextContent(type="text", text="No meal IDs provided")]
            
            # Determine save directory
            if custom_directory:
                save_dir = Path(custom_directory).expanduser()
                save_dir.mkdir(parents=True, exist_ok=True)
            else:
                save_dir = config.RECIPES_DIR
            
            # Handle existing shopping lists
            existing_lists = sorted(save_dir.glob("shopping_list_*.pdf"))
            
            if replace_existing and existing_lists:
                # Keep only the 2 most recent (so we can add 1 new one = max 3)
                lists_to_delete = existing_lists[:-2] if len(existing_lists) > 2 else []
                for old_list in lists_to_delete:
                    old_list.unlink()
                
                deleted_count = len(lists_to_delete)
            else:
                deleted_count = 0
            
            # Structure: {ingredient_lower: {'original': name, 'measures': [measures], 'recipes': [recipe_names]}}
            all_ingredients = {}
            meal_names = []
            
            # Fetch all meals
            for meal_id in meal_ids:
                meal = await fetch_meal_data(meal_id)
                meal_name = meal.get('strMeal', 'Unknown')
                meal_names.append(meal_name)
                
                # Collect ingredients
                for i in range(1, 21):
                    ingredient = meal.get(f"strIngredient{i}", "")
                    measure = meal.get(f"strMeasure{i}", "")
                    if ingredient and ingredient.strip():
                        ing_key = ingredient.strip().lower()
                        if ing_key not in all_ingredients:
                            all_ingredients[ing_key] = {
                                'original': ingredient.strip(),
                                'measures': [],
                                'recipes': []
                            }
                        if measure.strip():
                            all_ingredients[ing_key]['measures'].append(measure.strip())
                        all_ingredients[ing_key]['recipes'].append(meal_name)
            
            # Generate filename
            if custom_filename:
                filename = f"{custom_filename}.pdf"
            else:
                filename = f"shopping_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            filepath = save_dir / filename
            
            try:
                create_shopping_list_pdf(meal_names, all_ingredients, filepath)
                
                # Build response
                summary = f"Shopping list created successfully!\n\n"
                summary += f"File: {filepath}\n"
                summary += f"Recipes ({len(meal_names)}):\n"
                for i, name in enumerate(meal_names, 1):
                    summary += f"   {i}. {name}\n"
                summary += f"\nTotal ingredients: {len(all_ingredients)}\n"
                
                if deleted_count > 0:
                    summary += f"Deleted {deleted_count} old shopping list(s) to keep max 3\n"
                
                # Check current count
                current_lists = list(save_dir.glob("shopping_list_*.pdf"))
                summary += f"Total shopping lists: {len(current_lists)}"
                
                return [TextContent(type="text", text=summary)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Failed to create shopping list PDF: {str(e)}"
                )]
        
        # Tool 9: Create shopping list from saved recipes
        elif name == "create_shopping_list_from_saved":
            replace_existing = arguments.get("replace_existing", False)
            custom_filename = arguments.get("filename")
            
            # Get all saved recipe PDFs and extract meal IDs from them
            meal_ids = []
            meal_names_from_files = []
            
            # We need to parse the PDFs or maintain a mapping
            # For now, let's return an error message guiding the user
            return [TextContent(
                type="text",
                text="This feature requires recipe metadata storage which isn't implemented yet.\n\nWorkaround:\n1. List your saved recipes with 'list_saved_recipes'\n2. Look up each recipe by name to get its ID\n3. Use 'create_shopping_list' with those IDs\n\nOr, I can help you create a shopping list if you tell me which saved recipes you want to include!"
            )]
        
        # Tool 10: Set recipes directory
        elif name == "set_recipes_directory":
            directory = arguments.get("directory", "")
            
            if not directory:
                return [TextContent(type="text", text="Directory path is required")]
            
            try:
                new_dir = config.save_recipes_dir(directory)
                # Update the module-level variable
                config.RECIPES_DIR = new_dir
                
                return [TextContent(
                    type="text",
                    text=f"Recipes directory updated!\n\nNew location: {new_dir}"
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Failed to set directory: {str(e)}")]
        
        # Tool 11: Get recipes directory
        elif name == "get_recipes_directory":
            return [TextContent(
                type="text",
                text=f"Current recipes directory:\n{config.RECIPES_DIR}"
            )]
        
        else:
            return None  # Not a local tool
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]