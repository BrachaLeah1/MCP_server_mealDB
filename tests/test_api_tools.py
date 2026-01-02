"""
Unit tests for api_tools.py
Tests all API tool functions including HTTP requests, response formatting, and error handling.
"""

import unittest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.api_tools import (
    handle_api_tool,
    get_api_tool_definitions,
    format_full_meal,
    format_meal_summary,
    format_category,
)


class TestFormatters(unittest.TestCase):
    """Test formatting functions."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_meal = {
            "idMeal": "52772",
            "strMeal": "Teriyaki Chicken",
            "strCategory": "Chicken",
            "strArea": "Japanese",
            "strTags": "Meat,Casserole",
            "strIngredient1": "soy sauce",
            "strMeasure1": "3 tbs",
            "strIngredient2": "water",
            "strMeasure2": "3 tbs",
            "strIngredient3": "brown sugar",
            "strMeasure3": "2 tbs",
            "strIngredient4": "",
            "strMeasure4": "",
            "strInstructions": "Mix ingredients and cook.",
            "strMealThumb": "https://example.com/image.jpg",
            "strYoutube": "https://youtube.com/watch?v=test",
        }
        
        self.sample_category = {
            "strCategory": "Seafood",
            "strCategoryThumb": "https://example.com/seafood.jpg",
            "strCategoryDescription": "Fish, shellfish, and other seafood dishes from around the world.",
        }
    
    def test_format_full_meal(self):
        """Test formatting a full meal."""
        result = format_full_meal(self.sample_meal)
        
        self.assertIn("Teriyaki Chicken", result)
        self.assertIn("52772", result)
        self.assertIn("Chicken", result)
        self.assertIn("Japanese", result)
        self.assertIn("soy sauce", result)
        self.assertIn("3 tbs", result)
        self.assertIn("Mix ingredients and cook.", result)
        self.assertIn("https://example.com/image.jpg", result)
        self.assertIn("https://youtube.com/watch?v=test", result)
    
    def test_format_full_meal_no_ingredients(self):
        """Test formatting a meal with no ingredients."""
        meal = {
            "strMeal": "Test Meal",
            "idMeal": "123",
            "strInstructions": "Test instructions",
        }
        
        result = format_full_meal(meal)
        self.assertIn("Test Meal", result)
        self.assertIn("No ingredients listed", result)
    
    def test_format_full_meal_no_video(self):
        """Test formatting a meal without YouTube video."""
        meal = self.sample_meal.copy()
        meal["strYoutube"] = None
        
        result = format_full_meal(meal)
        self.assertIn("Teriyaki Chicken", result)
        self.assertNotIn("Video:", result)
    
    def test_format_meal_summary(self):
        """Test formatting a meal summary."""
        result = format_meal_summary(self.sample_meal)
        
        self.assertIn("Teriyaki Chicken", result)
        self.assertIn("52772", result)
        self.assertIn("**", result)  # Check for bold formatting
    
    def test_format_category(self):
        """Test formatting a category."""
        result = format_category(self.sample_category)
        
        self.assertIn("Seafood", result)
        self.assertIn("Fish, shellfish", result)
        self.assertIn("https://example.com/seafood.jpg", result)
    
    def test_format_category_long_description(self):
        """Test category with long description gets truncated."""
        long_desc = "A" * 300
        category = {
            "strCategory": "Test",
            "strCategoryDescription": long_desc,
            "strCategoryThumb": "test.jpg",
        }
        
        result = format_category(category)
        self.assertIn("...", result)
        self.assertLess(len(result), len(long_desc) + 100)


class TestToolDefinitions(unittest.TestCase):
    """Test tool definitions."""
    
    def test_get_tool_definitions(self):
        """Test that all tools are defined correctly."""
        tools = get_api_tool_definitions()
        
        # Should have 11 tools
        self.assertEqual(len(tools), 11)
        
        # Check tool names
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "search_meal_by_name",
            "list_meals_by_first_letter",
            "lookup_meal_by_id",
            "get_random_meal",
            "list_all_categories",
            "list_category_names",
            "list_area_names",
            "list_all_ingredients",
            "filter_by_ingredient",
            "filter_by_category",
            "filter_by_area",
        ]
        self.assertEqual(tool_names, expected_names)
    
    def test_tool_schemas(self):
        """Test that each tool has proper input schema."""
        tools = get_api_tool_definitions()
        
        for tool in tools:
            self.assertIsNotNone(tool.inputSchema)
            self.assertEqual(tool.inputSchema["type"], "object")


class TestAPIToolHandlers(unittest.IsolatedAsyncioTestCase):
    """Test API tool handlers using async tests."""
    
    def setUp(self):
        """Set up test data."""
        self.mock_meal = {
            "idMeal": "52772",
            "strMeal": "Teriyaki Chicken",
            "strCategory": "Chicken",
            "strArea": "Japanese",
            "strTags": "Meat",
            "strIngredient1": "soy sauce",
            "strMeasure1": "3 tbs",
            "strIngredient2": "",
            "strMeasure2": "",
            "strInstructions": "Cook it.",
            "strMealThumb": "https://example.com/image.jpg",
        }
        
        self.mock_category = {
            "strCategory": "Seafood",
            "strCategoryThumb": "https://example.com/seafood.jpg",
            "strCategoryDescription": "Seafood dishes",
        }
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_search_meal_by_name(self, mock_client):
        """Test searching for a meal by name."""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": [self.mock_meal]}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("search_meal_by_name", {"name": "chicken"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Teriyaki Chicken", result[0].text)
        self.assertIn("52772", result[0].text)
        mock_get.assert_called_once()
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_search_meal_by_name_no_results(self, mock_client):
        """Test searching with no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("search_meal_by_name", {"name": "nonexistent"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("No meals found", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_list_meals_by_first_letter(self, mock_client):
        """Test listing meals by first letter."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": [self.mock_meal]}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("list_meals_by_first_letter", {"letter": "t"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Teriyaki Chicken", result[0].text)
        self.assertIn("Found 1 meal(s)", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_lookup_meal_by_id(self, mock_client):
        """Test looking up a meal by ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": [self.mock_meal]}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("lookup_meal_by_id", {"meal_id": "52772"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Teriyaki Chicken", result[0].text)
        self.assertIn("52772", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_lookup_meal_by_id_not_found(self, mock_client):
        """Test looking up a non-existent meal ID."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("lookup_meal_by_id", {"meal_id": "99999"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("No meal found", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_get_random_meal(self, mock_client):
        """Test getting a random meal."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": [self.mock_meal]}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("get_random_meal", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("random meal", result[0].text)
        self.assertIn("Teriyaki Chicken", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_list_all_categories(self, mock_client):
        """Test listing all categories."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"categories": [self.mock_category]}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("list_all_categories", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Seafood", result[0].text)
        self.assertIn("Found 1 categories", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_list_category_names(self, mock_client):
        """Test listing category names."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "meals": [
                {"strCategory": "Beef"},
                {"strCategory": "Chicken"},
                {"strCategory": "Dessert"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("list_category_names", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Beef", result[0].text)
        self.assertIn("Chicken", result[0].text)
        self.assertIn("Dessert", result[0].text)
        self.assertIn("(3)", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_list_area_names(self, mock_client):
        """Test listing area/cuisine names."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "meals": [
                {"strArea": "Italian"},
                {"strArea": "Chinese"},
                {"strArea": "Mexican"},
            ]
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("list_area_names", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Italian", result[0].text)
        self.assertIn("Chinese", result[0].text)
        self.assertIn("(3)", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_list_all_ingredients(self, mock_client):
        """Test listing all ingredients."""
        mock_ingredients = [
            {"strIngredient": "Chicken", "strDescription": "Poultry meat"},
            {"strIngredient": "Salt", "strDescription": ""},
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": mock_ingredients}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("list_all_ingredients", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Chicken", result[0].text)
        self.assertIn("Poultry meat", result[0].text)
        self.assertIn("Salt", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_list_all_ingredients_truncation(self, mock_client):
        """Test that ingredients list shows truncation message."""
        # Create 150 ingredients
        mock_ingredients = [
            {"strIngredient": f"Ingredient{i}", "strDescription": ""}
            for i in range(150)
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": mock_ingredients}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("list_all_ingredients", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("and 50 more ingredients", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_filter_by_ingredient(self, mock_client):
        """Test filtering meals by ingredient."""
        mock_meals = [
            {"strMeal": "Chicken Soup", "idMeal": "123", "strMealThumb": "img1.jpg"},
            {"strMeal": "Chicken Curry", "idMeal": "456", "strMealThumb": "img2.jpg"},
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": mock_meals}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("filter_by_ingredient", {"ingredient": "chicken"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Found 2 meal(s)", result[0].text)
        self.assertIn("Chicken Soup", result[0].text)
        self.assertIn("Chicken Curry", result[0].text)
        self.assertIn("lookup_meal_by_id", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_filter_by_category(self, mock_client):
        """Test filtering meals by category."""
        mock_meals = [
            {"strMeal": "Salmon Fillet", "idMeal": "789", "strMealThumb": "salmon.jpg"},
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": mock_meals}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("filter_by_category", {"category": "Seafood"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Seafood", result[0].text)
        self.assertIn("Salmon Fillet", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_filter_by_area(self, mock_client):
        """Test filtering meals by area/cuisine."""
        mock_meals = [
            {"strMeal": "Spaghetti Carbonara", "idMeal": "999", "strMealThumb": "pasta.jpg"},
        ]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": mock_meals}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("filter_by_area", {"area": "Italian"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Italian", result[0].text)
        self.assertIn("Spaghetti Carbonara", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_filter_no_results(self, mock_client):
        """Test filter returning no results."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("filter_by_ingredient", {"ingredient": "unicorn"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("No meals found", result[0].text)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_unknown_tool(self, mock_client):
        """Test handling unknown tool name."""
        result = await handle_api_tool("unknown_tool", {})
        
        self.assertIsNone(result)
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_api_error_handling(self, mock_client):
        """Test error handling when API call fails."""
        mock_get = AsyncMock(side_effect=Exception("Network error"))
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("search_meal_by_name", {"name": "chicken"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("API Error", result[0].text)
        self.assertIn("Network error", result[0].text)


class TestEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Test edge cases and error conditions."""
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_empty_meal_name(self, mock_client):
        """Test searching with empty meal name."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"meals": None}
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("search_meal_by_name", {"name": ""})
        
        self.assertEqual(len(result), 1)
        # Should handle gracefully
    
    @patch('src.tools.api_tools.httpx.AsyncClient')
    async def test_malformed_response(self, mock_client):
        """Test handling malformed API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}  # Missing 'meals' key
        mock_response.raise_for_status = MagicMock()
        
        mock_get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value.get = mock_get
        
        result = await handle_api_tool("search_meal_by_name", {"name": "test"})
        
        self.assertEqual(len(result), 1)
        self.assertIn("No meals found", result[0].text)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFormatters))
    suite.addTests(loader.loadTestsFromTestCase(TestToolDefinitions))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIToolHandlers))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    result = run_tests()
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)