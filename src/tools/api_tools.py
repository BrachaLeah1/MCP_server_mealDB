"""
API Tools - Fetching data from TheMealDB API
All tools that interact with the external TheMealDB API.
"""

import httpx
from mcp.types import Tool, TextContent
from typing import Any


API_BASE = "https://www.themealdb.com/api/json/v1/1"


def format_full_meal(meal: dict) -> str:
    """Format a full meal with all details."""
    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}", "")
        measure = meal.get(f"strMeasure{i}", "")
        if ingredient and ingredient.strip():
            ingredients.append(f"  - {measure.strip()} {ingredient.strip()}")
    
    ingredients_text = "\n".join(ingredients) if ingredients else "No ingredients listed"
    
    image_url = meal.get('strMealThumb', '')
    image_section = f"\n🖼️ [View Recipe Image]({image_url})" if image_url else ""
    
    return f"""# {meal.get('strMeal', 'Unknown')}{image_section}

**ID:** {meal.get('idMeal', 'N/A')}
**Category:** {meal.get('strCategory', 'N/A')}
**Cuisine:** {meal.get('strArea', 'N/A')}
**Tags:** {meal.get('strTags', 'N/A')}

## Ingredients:
{ingredients_text}

## Instructions:
{meal.get('strInstructions', 'No instructions available')}

{f"**Video:** {meal.get('strYoutube')}" if meal.get('strYoutube') else ""}
"""


def format_meal_summary(meal: dict) -> str:
    """Format a brief meal summary with image link."""
    meal_name = meal.get('strMeal', 'Unknown')
    meal_id = meal.get('idMeal', 'N/A')
    image_url = meal.get('strMealThumb', '')
    
    if image_url:
        summary = f"- **[{meal_name}]({image_url})** (ID: {meal_id})"
    else:
        summary = f"- **{meal_name}** (ID: {meal_id})"
    
    return summary


def format_category(cat: dict) -> str:
    """Format a category with details."""
    desc = cat.get('strCategoryDescription', 'No description')
    if len(desc) > 200:
        desc = desc[:200] + "..."
    
    thumb_url = cat.get('strCategoryThumb', '')
    thumb_section = f"\n🖼️ [View Category Image]({thumb_url})" if thumb_url else ""
    
    return f"""## {cat.get('strCategory', 'Unknown')}{thumb_section}
{desc}
"""


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

def get_api_tool_definitions() -> list[Tool]:
    """Return all API tool definitions."""
    return [
        # Search & Lookup Tools
        Tool(
            name="search_meal_by_name",
            description="Search for meals by name (e.g., 'Arrabiata', 'chicken', 'pasta') with urls for picture of each recipe.  After showing results, ask user if they want to: 1.see any specific recipe 2.to see all categories / all areas 3.recipes by ingredient/specific letter (a-z).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Meal name to search for"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="list_meals_by_first_letter",
            description="List all meals starting with a specific letter (A-Z) with urls for picture of each recipe. After showing results, ask user if they want to: 1.see any specific recipe 2.to see all categories / all areas 3.recipes by ingredient/name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "letter": {
                        "type": "string",
                        "description": "Single letter (A-Z)",
                        "minLength": 1,
                        "maxLength": 1
                    }
                },
                "required": ["letter"]
            },
        ),
        Tool(
            name="lookup_meal_by_id",
            description="Get full meal details by ID with url for picture of recipe. Use this to VIEW a recipe. After showing the recipe, ask if user wants to save it as a PDF and prepare shopping list.",
            inputSchema={
                "type": "object",
                "properties": {
                    "meal_id": {"type": "string", "description": "Meal ID (e.g., '52772')"}
                },
                "required": ["meal_id"]
            },
        ),
        Tool(
            name="get_random_meal",
            description="Get a single random meal for inspiration with url for picture recipe. After showing the recipe, ask if user wants 1.to save it as a PDF. 2.to create a shopping list. 3.to see another random meal. 4.to see all categories / all areas. 5.recipes by ingredient/specific letter (a-z).",
            inputSchema={"type": "object", "properties": {}},
        ),
        
        # Category & List Tools
        Tool(
            name="list_all_categories",
            description="Get all meal categories with descriptions and images, after showing categories, ask user if they want to: see recipes in any specific category",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_category_names",
            description="Get just the category names (e.g., Seafood, Dessert, Vegetarian)",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_area_names",
            description="Get all cuisine/area names (e.g., Italian, Chinese, Mexican)",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="list_all_ingredients",
            description="Get all available ingredients in the database",
            inputSchema={"type": "object", "properties": {}},
        ),
        
        # Filter Tools
        Tool(
            name="filter_by_ingredient",
            description="Find all meals that contain a specific ingredient with urls for picture of each recipe. After showing results, ask user if they want to: see any specific recipe ",
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredient": {
                        "type": "string",
                        "description": "Ingredient name (e.g., 'chicken_breast', 'garlic')"
                    }
                },
                "required": ["ingredient"]
            },
        ),
        Tool(
            name="filter_by_category",
            description="Find all meals in a specific category with urls for picture of each recipe. After showing results, ask user if they want to: see any specific recipe.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category name (e.g., 'Seafood', 'Dessert')"
                    }
                },
                "required": ["category"]
            },
        ),
        Tool(
            name="filter_by_area",
            description="Find all meals from a specific cuisine/area with urls for picture of each recipe. After showing results, ask user if they want to: see any specific recipe.",
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Area/cuisine name (e.g., 'Italian', 'Canadian')"
                    }
                },
                "required": ["area"]
            },
        ),
    ]


# ============================================================================
# TOOL HANDLERS
# ============================================================================

async def handle_api_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle all API tool calls."""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Tool 1: Search meal by name
            if name == "search_meal_by_name":
                meal_name = arguments.get("name", "")
                response = await client.get(f"{API_BASE}/search.php", params={"s": meal_name})
                response.raise_for_status()
                data = response.json()
                
                meals = data.get("meals")
                if not meals:
                    return [TextContent(type="text", text=f"No meals found for '{meal_name}'")]
                
                result = f"Found {len(meals)} meal(s) for '{meal_name}':\n\n"
                result += "\n---\n\n".join([format_full_meal(meal) for meal in meals])
                
                # Add proactive suggestions
                result += f"\n\n **What would you like to do?**\n"
                result += "- See any specific recipe?\n"
                result += "- See all categories or areas?\n"
                result += "- Search recipes by ingredient or specific letter (a-z)?"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 2: List meals by first letter
            elif name == "list_meals_by_first_letter":
                letter = arguments.get("letter", "a").upper()
                
                # Validate letter input
                if not letter.isalpha() or len(letter) != 1:
                    return [TextContent(type="text", text=f"Invalid input. Please provide a single letter (A-Z).")]
                
                response = await client.get(f"{API_BASE}/search.php", params={"f": letter})
                response.raise_for_status()
                data = response.json()
                
                meals = data.get("meals")
                if not meals:
                    return [TextContent(type="text", text=f"No meals found starting with '{letter}'")]
                
                result = f"Found {len(meals)} meal(s) starting with '{letter}':\n\n"
                result += "\n".join([format_meal_summary(meal) for meal in meals])
                result += f"\n\n **What would you like to do?**\n"
                result += "- See any specific recipe?\n"
                result += "- See all categories or areas?\n"
                result += "- Search by ingredient or name?"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 3: Lookup meal by ID
            elif name == "lookup_meal_by_id":
                meal_id = arguments.get("meal_id", "")
                
                # Validate meal_id format
                if not meal_id.isdigit():
                    return [TextContent(type="text", text=f"Invalid meal ID. Please provide a numeric ID.")]
                
                response = await client.get(f"{API_BASE}/lookup.php", params={"i": meal_id})
                response.raise_for_status()
                data = response.json()
                
                meals = data.get("meals")
                if not meals:
                    return [TextContent(type="text", text=f"No meal found with ID '{meal_id}'")]
                
                result = format_full_meal(meals[0])
                result += "\n\n **What would you like to do?**\n"
                result += "- Save this recipe as a PDF?\n"
                result += "- Create a shopping list?\n"
                result += "- See another recipe?"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 4: Get random meal
            elif name == "get_random_meal":
                response = await client.get(f"{API_BASE}/random.php")
                response.raise_for_status()
                data = response.json()
                
                meal = data.get("meals", [{}])[0]
                result = "Here's a random meal:\n\n" + format_full_meal(meal)
                result += "\n\n **What would you like to do?**\n"
                result += "- Save this recipe as a PDF?\n"
                result += "- Create a shopping list?\n"
                result += "- See another random meal?\n"
                result += "- See all categories or areas?\n"
                result += "- Search by ingredient or specific letter (a-z)?"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 5: List all categories
            elif name == "list_all_categories":
                response = await client.get(f"{API_BASE}/categories.php")
                response.raise_for_status()
                data = response.json()
                
                categories = data.get("categories", [])
                result = f"Found {len(categories)} categories:\n\n"
                result += "\n".join([format_category(cat) for cat in categories])
                result += "\n\n **What would you like to do?**\n"
                result += "- See recipes in any specific category?"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 6: List category names
            elif name == "list_category_names":
                response = await client.get(f"{API_BASE}/list.php", params={"c": "list"})
                response.raise_for_status()
                data = response.json()
                
                categories = data.get("meals", [])
                names = [cat.get("strCategory", "") for cat in categories]
                result = f"Available categories ({len(names)}):\n\n"
                result += ", ".join(names)
                
                return [TextContent(type="text", text=result)]
            
            # Tool 7: List area names
            elif name == "list_area_names":
                response = await client.get(f"{API_BASE}/list.php", params={"a": "list"})
                response.raise_for_status()
                data = response.json()
                
                areas = data.get("meals", [])
                names = [area.get("strArea", "") for area in areas]
                result = f"Available cuisines/areas ({len(names)}):\n\n"
                result += ", ".join(sorted(names))
                
                return [TextContent(type="text", text=result)]
            
            # Tool 8: List all ingredients
            elif name == "list_all_ingredients":
                response = await client.get(f"{API_BASE}/list.php", params={"i": "list"})
                response.raise_for_status()
                data = response.json()
                
                ingredients = data.get("meals", [])
                result = f"Found {len(ingredients)} ingredients:\n\n"
                
                for ing in ingredients[:100]:
                    name = ing.get("strIngredient", "Unknown")
                    desc = ing.get("strDescription", "")
                    if desc:
                        desc = desc[:100] + "..." if len(desc) > 100 else desc
                        result += f"- **{name}** - {desc}\n"
                    else:
                        result += f"- **{name}**\n"
                
                if len(ingredients) > 100:
                    result += f"\n... and {len(ingredients) - 100} more ingredients (showing first 100)"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 9: Filter by ingredient
            elif name == "filter_by_ingredient":
                ingredient = arguments.get("ingredient", "")
                response = await client.get(f"{API_BASE}/filter.php", params={"i": ingredient})
                response.raise_for_status()
                data = response.json()
                
                meals = data.get("meals")
                if not meals:
                    return [TextContent(type="text", text=f"No meals found with ingredient '{ingredient}'")]
                
                result = f"Found {len(meals)} meal(s) with '{ingredient}':\n\n"
                result += "\n".join([format_meal_summary(meal) for meal in meals])
                
                result += "\n\n **What would you like to do?**\n"
                result += "- See any specific recipe?\n"
                result += "- Try another filter?"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 10: Filter by category
            elif name == "filter_by_category":
                category = arguments.get("category", "")
                response = await client.get(f"{API_BASE}/filter.php", params={"c": category})
                response.raise_for_status()
                data = response.json()
                
                meals = data.get("meals")
                if not meals:
                    return [TextContent(type="text", text=f"No meals found in category '{category}'")]
                
                result = f"Found {len(meals)} meal(s) in category '{category}':\n\n"
                result += "\n".join([format_meal_summary(meal) for meal in meals])
                
                result += "\n\n **What would you like to do?**\n"
                result += "- See any specific recipe?\n"
                result += "- Try another filter?"
                
                return [TextContent(type="text", text=result)]
            
            # Tool 11: Filter by area
            elif name == "filter_by_area":
                area = arguments.get("area", "")
                response = await client.get(f"{API_BASE}/filter.php", params={"a": area})
                response.raise_for_status()
                data = response.json()
                
                meals = data.get("meals")
                if not meals:
                    return [TextContent(type="text", text=f"No meals found from area '{area}'")]
                
                result = f"Found {len(meals)} meal(s) from '{area}' cuisine:\n\n"
                result += "\n".join([format_meal_summary(meal) for meal in meals])
                
                result += "\n\n **What would you like to do?**\n"
                result += "- See any specific recipe?\n"
                result += "- Try another filter?"
                
                return [TextContent(type="text", text=result)]
            
            else:
                return None  # Not an API tool
        
        except Exception as e:
            return [TextContent(type="text", text=f"API Error: {str(e)}")]