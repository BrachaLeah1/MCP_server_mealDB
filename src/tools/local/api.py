"""
API client for TheMealDB.
Handles fetching meal data from the external API.
"""

import httpx


async def fetch_meal_data(meal_id: str) -> dict:
    """
    Fetch meal data from TheMealDB API.
    
    Args:
        meal_id: The meal ID to fetch
        
    Returns:
        Dictionary containing meal data
        
    Raises:
        ValueError: If meal ID is not found
        httpx.HTTPError: If API request fails
    """
    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        response = await client.get(
            f"https://www.themealdb.com/api/json/v1/1/lookup.php",
            params={"i": meal_id}
        )
        response.raise_for_status()
        data = response.json()
        meals = data.get("meals")
        if not meals:
            raise ValueError(f"Meal ID {meal_id} not found")
        return meals[0]