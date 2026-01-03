"""
Unit tests for local tools
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

# Fixed imports
from src.tools.local.tools import (
    handle_local_tool,
    get_local_tool_definitions,
)
from src.tools.local.pdf_recipe import create_recipe_pdf
from src.tools.local.pdf_shopping import create_shopping_list_pdf
from src.tools.local.categories import get_ingredient_category
from src.tools.local.config import load_recipes_dir, save_recipes_dir, RECIPES_DIR, CONFIG_FILE
from src.tools.local import api as local_api
import src.tools.local.tools as local_tools
import src.tools.local.config as config


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
    
    @patch('src.tools.local.config.CONFIG_FILE')
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
        
        # Should have 11 tools
        self.assertEqual(len(tools), 11)
        
        # Check tool names
        tool_names = [tool.name for tool in tools]
        expected_names = [
            "save_recipe_to_file",
            "save_recipe_by_name",
            "list_saved_recipes",
            "delete_saved_recipe",
            "list_shopping_lists",
            "delete_shopping_list",
            "delete_all_shopping_lists",
            "create_shopping_list",
            "create_shopping_list_from_saved",
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
        with patch('src.tools.local.pdf_recipe.requests.get') as mock_get:
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
    
    @patch('src.tools.local.tools.fetch_meal_data')
    @patch('src.tools.local.pdf_recipe.requests.get')
    async def test_save_recipe_to_file(self, mock_requests, mock_fetch):
        """Test saving a recipe to file."""
        mock_fetch.return_value = self.mock_meal
        mock_requests.return_value.status_code = 404  # No image
        
        # Temporarily override the RECIPES_DIR in the config module
        original_dir = config.RECIPES_DIR
        config.RECIPES_DIR = Path(self.temp_dir)
        
        try:
            result = await handle_local_tool(
                "save_recipe_to_file",
                {"meal_id": "12345"}
            )
            
            self.assertEqual(len(result), 1)
            self.assertIn("Recipe saved successfully", result[0].text)
            self.assertIn("Spaghetti Carbonara", result[0].text)
        finally:
            # Restore original directory
            config.RECIPES_DIR = original_dir
    
    async def test_unknown_tool(self):
        """Test handling unknown tool name."""
        result = await handle_local_tool("unknown_tool", {})
        
        self.assertIsNone(result)


class TestEdgeCases(unittest.IsolatedAsyncioTestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


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