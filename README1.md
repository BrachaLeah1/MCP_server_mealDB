# MealDB MCP Server

A well-organized MCP server for TheMealDB recipe API with clean separation of concerns.

## Project Structure

```
recipes/
├── README.md
├── requirements.txt
├── src/
│   ├── server.py              # Main entry point - routes and coordinates
│   └── tools/
│       ├── api_tools.py       # API tools - fetches data from TheMealDB
│       ├── local_tools.py     # Local tools - saves recipes, creates shopping lists
│       └── __pycache__/
├── tests/
└── docs/
```

## Tools Available

### API Tools (11 tools) - from `src/tools/api_tools.py`
Fetch data from TheMealDB:

1. **search_meal_by_name** - Search recipes by name
2. **list_meals_by_first_letter** - Browse alphabetically
3. **lookup_meal_by_id** - Get full recipe details
4. **get_random_meal** - Random recipe inspiration
5. **list_all_categories** - All categories with details
6. **list_category_names** - Just category names
7. **list_area_names** - All cuisines
8. **list_all_ingredients** - All ingredients
9. **filter_by_ingredient** - Find by ingredient
10. **filter_by_category** - Find by category
11. **filter_by_area** - Find by cuisine

### Local Tools (5 tools) - from `src/tools/local_tools.py`
Manage recipes on your computer:

1. **save_recipe_to_file** - Save recipe as text file
2. **list_saved_recipes** - View all saved recipes
3. **delete_saved_recipe** - Remove a saved recipe
4. **create_shopping_list** - Generate shopping list from recipe IDs
5. **email_recipe** - Create email draft with recipe

## Installation

```bash
# Install dependencies
pip install mcp httpx

# Run the server (from project root)
python src/server.py
```

## Configuration

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mealdb": {
      "command": "python",
      "args": ["/full/path/to/recipes/src/server.py"]
    }
  }
}
```

## Local Storage

Recipes are saved to: `~/mealdb_recipes/`

This directory is created automatically on first use.

## Usage Examples

**Finding and saving a recipe:**
1. "Search for pasta recipes" → Uses `search_meal_by_name`
2. "Save recipe ID 52772" → Uses `save_recipe_to_file`

**Creating a shopping list:**
1. "Find Italian recipes" → Uses `filter_by_area`
2. "Create shopping list for IDs 52772, 52773" → Uses `create_shopping_list`

**Managing saved recipes:**
- "List my saved recipes" → Uses `list_saved_recipes`
- "Delete Arrabiata.txt" → Uses `delete_saved_recipe`

## Architecture

### Why This Structure?

**src/server.py** - Main coordinator
- Registers all tools from both modules
- Routes tool calls to appropriate handlers
- Single entry point for the MCP server

**src/tools/api_tools.py** - External API interactions
- All TheMealDB API calls
- Data fetching and formatting
- No local file operations

**src/tools/local_tools.py** - Local file operations
- Save/delete recipes to local files
- Create shopping lists
- Email draft generation
- No external API calls

### Benefits:
- Separation of concerns - Each file has one job
- Easy to maintain - Changes to API don't affect local tools
- Easy to extend - Add new tools to the right file
- Easy to test - Test API and local tools separately
- Clear organization - Know where everything is

## Extending the Server

**Adding a new API tool:**
1. Add tool definition to `get_api_tool_definitions()` in `src/tools/api_tools.py`
2. Add handler logic to `handle_api_tool()` in `src/tools/api_tools.py`

**Adding a new local tool:**
1. Add tool definition to `get_local_tool_definitions()` in `src/tools/local_tools.py`
2. Add handler logic to `handle_local_tool()` in `src/tools/local_tools.py`

No changes needed to `src/server.py` - it automatically picks up new tools!

## Troubleshooting

**SSL Certificate Error:**
- Already handled with `verify=False` in httpx clients

**Import Errors:**
- Ensure all files are in the correct subdirectories (`src/server.py` and `src/tools/*.py`)
- Run the server from the project root: `python src/server.py`

**UnicodeEncodeError (Windows):**
- Remove emoji characters from print statements
- Use ASCII characters instead for console output

**Permission Errors:**
- Check that `~/mealdb_recipes/` directory is writable

## License

MIT License - Free to use and modify!