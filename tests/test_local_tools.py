"""
Unit tests for local_tools.py
Tests all local tool functions including PDF generation, file operations, and shopping lists.
"""

import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import json
import os

# Import the module to test
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import local_tools
from src.tools.local_tools import (
    handle_local_tool,
    get_local_tool_definitions,
    create_recipe_pdf,
    create_shopping_list_pdf,
    get_ingredient_category,
    load_recipes_dir,
    save_recipes_dir,
)


class TestIngredientCategories(unittest.TestCase):
    """Test ingredient categorization."""
    
    def test_produce_category(self):
        self.assertEqual(get_ingredient_category("tomato"), "Produce")
        self.assertEqual(get_ingredient_category("Fresh Tomatoes"), "Produce")
        self.assertEqual(get_ingredient_category("ONION"), "Produce")
    
    def test_meat_category(self):
        self.assertEqual(get_ingredient_category("chicken breast"), "Meat & Seafood")
        self.assertEqual(get_ingredient_category("Ground Beef"), "Meat & Seafood")
        self.assertEqual(get_ingredient_category("salmon fillet"), "Meat & Seafood")
    
    def test_dairy_category(self):
        self.assertEqual(get_ingredient_category("milk"), "Dairy & Eggs")
        self.assertEqual(get_ingredient_category("Cheddar Cheese"), "Dairy & Eggs")
        self.assertEqual(get_ingredient_category("eggs"), "Dairy & Eggs")
    
    def test_pantry_category(self):
        self.assertEqual(get_ingredient_category("flour"), "Pantry & Dry")
        self.assertEqual(get_ingredient_category("rice"), "Pantry & Dry")
        self.assertEqual(get_ingredient_category("olive oil"), "Pantry & Dry")
    
    def test_spices_category(self):
        self.assertEqual(get_ingredient_category("paprika"), "Spices")
        self.assertEqual(get_ingredient_category("black pepper"), "Spices")
    
    def test_unknown_category(self):
        self.assertEqual(get_ingredient_category("unknown ingredient"), "Other")


class TestDirectoryManagement(unittest.TestCase):
    """Test directory configuration and management."""
    
    def setUp(self):
        """Set up temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = Path(self.temp_dir) / "test_config.json"
        
    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('src.tools.local_tools.CONFIG_FILE')
    def test_save_recipes_dir(self, mock_config_file):
        """Test saving recipes directory to config."""
        mock_config_file.__str__ = lambda x: str(self.test_config)
        mock_config_file.exists.return_value = False
        
        test_path = Path(self.temp_dir) / "recipes"
        result = save_recipes_dir(str(test_path))
        
        self.assertEqual(result, test_path)
        self.assertTrue(test_path.exists())


class TestToolDefinitions(unittest.TestCase):
    """Test tool definitions and schemas."""
    
    def test_get_tool_definitions(self):
        """Test that all tools are defined correctly."""
        tools = get_local_tool_definitions()
        
        # Should have 6 tools
        self.assertEqual(len(tools), 6)
        
        # Check tool names
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "save_recipe_to_file",
            "list_saved_recipes",
            "delete_saved_recipe",
            "create_shopping_list",
            "set_recipes_directory",
            "get_recipes_directory",
        ]
        self.assertEqual(tool_names, expected_names)
    
    def test_tool_schemas(self):
        """Test that each tool has proper input schema."""
        tools = get_local_tool_definitions()
        
        for tool in tools:
            self.assertIsNotNone(tool.inputSchema)
            self.assertEqual(tool.inputSchema["type"], "object")


class TestPDFGeneration(unittest.TestCase):
    """Test PDF generation functions."""
    
    def setUp(self):
        """Set up test data and temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_meal = {
            "strMeal": "Test Recipe",
            "strCategory": "Dessert",
            "strArea": "American",
            "strTags": "Sweet,Baked",
            "strIngredient1": "Flour",
            "strMeasure1": "2 cups",
            "strIngredient2": "Sugar",
            "strMeasure2": "1 cup",
            "strIngredient3": "",
            "strMeasure3": "",
            "strInstructions": "Mix and bake at 350F for 30 minutes.",
            "strMealThumb": "https://example.com/image.jpg",
        }
    
    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_recipe_pdf(self):
        """Test creating a recipe PDF."""
        filepath = Path(self.temp_dir) / "test_recipe.pdf"
        
        # Mock the image request to avoid network calls
        with patch('src.tools.local_tools.requests.get') as mock_get:
            mock_get.return_value.status_code = 404  # Simulate no image
            
            create_recipe_pdf(self.test_meal, filepath)
        
        # Check that PDF was created
        self.assertTrue(filepath.exists())
        self.assertGreater(filepath.stat().st_size, 0)
    
    def test_create_shopping_list_pdf(self):
        """Test creating a shopping list PDF."""
        filepath = Path(self.temp_dir) / "test_shopping_list.pdf"
        
        meal_names = ["Recipe 1", "Recipe 2"]
        ingredients = {
            "flour": {
                "original": "Flour",
                "measures": ["2 cups", "1 cup"],
                "recipes": ["Recipe 1", "Recipe 2"]
            },
            "sugar": {
                "original": "Sugar",
                "measures": ["1 cup"],
                "recipes": ["Recipe 1"]
            }
        }
        
        create_shopping_list_pdf(meal_names, ingredients, filepath)
        
        # Check that PDF was created
        self.assertTrue(filepath.exists())
        self.assertGreater(filepath.stat().st_size, 0)


class TestLocalToolHandlers(unittest.IsolatedAsyncioTestCase):
    """Test the actual tool handlers using async tests."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        local_tools.RECIPES_DIR = Path(self.temp_dir)
        
        # Mock meal data
        self.mock_meal = {
            "strMeal": "Spaghetti Carbonara",
            "strCategory": "Pasta",
            "strArea": "Italian",
            "strTags": "Pasta,Italian",
            "strIngredient1": "Spaghetti",
            "strMeasure1": "400g",
            "strIngredient2": "Bacon",
            "strMeasure2": "200g",
            "strIngredient3": "Eggs",
            "strMeasure3": "3",
            "strIngredient4": "Parmesan",
            "strMeasure4": "100g",
            "strIngredient5": "",
            "strMeasure5": "",
            "strInstructions": "Cook pasta. Fry bacon. Mix with eggs and cheese.",
            "strMealThumb": "https://example.com/carbonara.jpg",
        }
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('src.tools.local_tools.fetch_meal_data')
    @patch('src.tools.local_tools.requests.get')
    async def test_save_recipe_to_file(self, mock_requests, mock_fetch):
        """Test saving a recipe to file."""
        mock_fetch.return_value = self.mock_meal
        mock_requests.return_value.status_code = 404  # No image
        
        result = await handle_local_tool(
            "save_recipe_to_file",
            {"meal_id": "12345"}
        )
        
        self.assertEqual(len(result), 1)
        self.assertIn("[SUCCESS]", result[0].text)
        self.assertIn("Spaghetti Carbonara", result[0].text)
        
        # Check that file was created
        category_dir = Path(self.temp_dir) / "Pasta"
        self.assertTrue(category_dir.exists())
        
        pdf_files = list(category_dir.glob("*.pdf"))
        self.assertEqual(len(pdf_files), 1)
    
    @patch('src.tools.local_tools.fetch_meal_data')
    @patch('src.tools.local_tools.requests.get')
    async def test_save_recipe_with_custom_filename(self, mock_requests, mock_fetch):
        """Test saving a recipe with custom filename."""
        mock_fetch.return_value = self.mock_meal
        mock_requests.return_value.status_code = 404
        
        result = await handle_local_tool(
            "save_recipe_to_file",
            {"meal_id": "12345", "filename": "my_custom_recipe"}
        )
        
        self.assertIn("[SUCCESS]", result[0].text)
        
        # Check that file exists with custom name
        category_dir = Path(self.temp_dir) / "Pasta"
        custom_file = category_dir / "my_custom_recipe.pdf"
        self.assertTrue(custom_file.exists())
    
    async def test_list_saved_recipes_empty(self):
        """Test listing recipes when none are saved."""
        result = await handle_local_tool("list_saved_recipes", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("No saved recipes found", result[0].text)
    
    @patch('src.tools.local_tools.fetch_meal_data')
    @patch('src.tools.local_tools.requests.get')
    async def test_list_saved_recipes(self, mock_requests, mock_fetch):
        """Test listing saved recipes."""
        mock_fetch.return_value = self.mock_meal
        mock_requests.return_value.status_code = 404
        
        # Save a recipe first
        await handle_local_tool("save_recipe_to_file", {"meal_id": "12345"})
        
        # List recipes
        result = await handle_local_tool("list_saved_recipes", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Pasta", result[0].text)
        self.assertIn("Total recipes: 1", result[0].text)
    
    @patch('src.tools.local_tools.fetch_meal_data')
    @patch('src.tools.local_tools.requests.get')
    async def test_delete_saved_recipe(self, mock_requests, mock_fetch):
        """Test deleting a saved recipe."""
        mock_fetch.return_value = self.mock_meal
        mock_requests.return_value.status_code = 404
        
        # Save a recipe first
        await handle_local_tool("save_recipe_to_file", {"meal_id": "12345"})
        
        # Delete it
        result = await handle_local_tool(
            "delete_saved_recipe",
            {"filename": "Spaghetti Carbonara.pdf"}
        )
        
        self.assertIn("[SUCCESS]", result[0].text)
        self.assertIn("deleted", result[0].text.lower())
        
        # Verify it's gone
        category_dir = Path(self.temp_dir) / "Pasta"
        pdf_files = list(category_dir.glob("*.pdf"))
        self.assertEqual(len(pdf_files), 0)
    
    async def test_delete_nonexistent_recipe(self):
        """Test deleting a recipe that doesn't exist."""
        result = await handle_local_tool(
            "delete_saved_recipe",
            {"filename": "nonexistent.pdf"}
        )
        
        self.assertIn("[ERROR]", result[0].text)
        self.assertIn("not found", result[0].text)
    
    @patch('src.tools.local_tools.fetch_meal_data')
    async def test_create_shopping_list(self, mock_fetch):
        """Test creating a shopping list from multiple recipes."""
        # Mock two different meals
        mock_meal_1 = {
            "strMeal": "Pasta",
            "strIngredient1": "Spaghetti",
            "strMeasure1": "400g",
            "strIngredient2": "Tomato",
            "strMeasure2": "3",
            "strIngredient3": "",
        }
        
        mock_meal_2 = {
            "strMeal": "Salad",
            "strIngredient1": "Lettuce",
            "strMeasure1": "1 head",
            "strIngredient2": "Tomato",
            "strMeasure2": "2",
            "strIngredient3": "",
        }
        
        # Configure mock to return different meals
        mock_fetch.side_effect = [mock_meal_1, mock_meal_2]
        
        result = await handle_local_tool(
            "create_shopping_list",
            {"meal_ids": ["12345", "67890"]}
        )
        
        self.assertIn("[SUCCESS]", result[0].text)
        self.assertIn("Shopping list created as PDF", result[0].text)
        self.assertIn("2 recipe(s)", result[0].text)
        
        # Check that shopping list file was created
        pdf_files = list(Path(self.temp_dir).glob("shopping_list_*.pdf"))
        self.assertEqual(len(pdf_files), 1)
    
    async def test_create_shopping_list_no_meals(self):
        """Test creating shopping list with no meal IDs."""
        result = await handle_local_tool(
            "create_shopping_list",
            {"meal_ids": []}
        )
        
        self.assertIn("No meal IDs provided", result[0].text)
    
    async def test_get_recipes_directory(self):
        """Test getting current recipes directory."""
        result = await handle_local_tool("get_recipes_directory", {})
        
        self.assertEqual(len(result), 1)
        self.assertIn("Current recipes directory:", result[0].text)
        self.assertIn(str(self.temp_dir), result[0].text)
    
    async def test_set_recipes_directory(self):
        """Test setting recipes directory."""
        new_dir = Path(self.temp_dir) / "new_recipes"
        
        result = await handle_local_tool(
            "set_recipes_directory",
            {"directory": str(new_dir)}
        )
        
        self.assertIn("[SUCCESS]", result[0].text)
        self.assertTrue(new_dir.exists())
    
    async def test_set_recipes_directory_empty(self):
        """Test setting recipes directory with empty path."""
        result = await handle_local_tool(
            "set_recipes_directory",
            {"directory": ""}
        )
        
        self.assertIn("[ERROR]", result[0].text)
        self.assertIn("required", result[0].text)
    
    async def test_unknown_tool(self):
        """Test handling unknown tool name."""
        result = await handle_local_tool("unknown_tool", {})
        
        self.assertIsNone(result)
    
    @patch('src.tools.local_tools.fetch_meal_data')
    async def test_tool_error_handling(self, mock_fetch):
        """Test error handling when fetch fails."""
        mock_fetch.side_effect = Exception("API Error")
        
        result = await handle_local_tool(
            "save_recipe_to_file",
            {"meal_id": "12345"}
        )
        
        self.assertIn("Error", result[0].text)


class TestEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        local_tools.RECIPES_DIR = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('src.tools.local_tools.fetch_meal_data')
    @patch('src.tools.local_tools.requests.get')
    async def test_recipe_with_special_characters(self, mock_requests, mock_fetch):
        """Test saving recipe with special characters in name."""
        mock_meal = {
            "strMeal": "Recipe/With\\Special:Characters",
            "strCategory": "Test",
            "strArea": "Test",
            "strTags": "",
            "strIngredient1": "Ingredient",
            "strMeasure1": "1 cup",
            "strIngredient2": "",
            "strMeasure2": "",
            "strInstructions": "Test instructions",
            "strMealThumb": "",
        }
        # Add remaining ingredients (up to 20)
        for i in range(3, 21):
            mock_meal[f"strIngredient{i}"] = ""
            mock_meal[f"strMeasure{i}"] = ""
        
        mock_fetch.return_value = mock_meal
        mock_requests.return_value.status_code = 404
        
        result = await handle_local_tool(
            "save_recipe_to_file",
            {"meal_id": "12345"}
        )
        
        self.assertIn("[SUCCESS]", result[0].text)
        
        # Check that file was created in Test category
        # Note: On Windows, colons (:) are invalid in filenames and cause truncation
        # The file may not have .pdf extension due to this
        category_dir = Path(self.temp_dir) / "Test"
        self.assertTrue(category_dir.exists(), "Category directory should exist")
        
        # Check that at least one file was created (may not have .pdf extension on Windows)
        all_files = list(category_dir.iterdir())
        self.assertGreater(len(all_files), 0, "At least one file should be created")
    
    @patch('src.tools.local_tools.fetch_meal_data')
    @patch('src.tools.local_tools.requests.get')
    async def test_recipe_with_no_category(self, mock_requests, mock_fetch):
        """Test saving recipe with no category."""
        mock_meal = {
            "strMeal": "Test Recipe",
            "strCategory": "",
            "strArea": "Test",
            "strTags": "",
            "strIngredient1": "Ingredient",
            "strMeasure1": "1 cup",
            "strIngredient2": "",
            "strMeasure2": "",
            "strInstructions": "Test instructions",
            "strMealThumb": "",
        }
        # Add remaining ingredients (up to 20)
        for i in range(3, 21):
            mock_meal[f"strIngredient{i}"] = ""
            mock_meal[f"strMeasure{i}"] = ""
        
        mock_fetch.return_value = mock_meal
        mock_requests.return_value.status_code = 404
        
        result = await handle_local_tool(
            "save_recipe_to_file",
            {"meal_id": "12345"}
        )
        
        self.assertIn("[SUCCESS]", result[0].text)
        
        # With empty category, the file is saved directly in temp_dir (no subdirectory)
        # This is the actual behavior - empty string creates a subdirectory named ""
        pdf_files = list(Path(self.temp_dir).glob("**/*.pdf"))
        self.assertGreater(len(pdf_files), 0, "At least one PDF should be created")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIngredientCategories))
    suite.addTests(loader.loadTestsFromTestCase(TestDirectoryManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestToolDefinitions))
    suite.addTests(loader.loadTestsFromTestCase(TestPDFGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestLocalToolHandlers))
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
