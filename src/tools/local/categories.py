"""
Ingredient categorization for shopping lists.
Maps ingredients to grocery store categories.
"""


INGREDIENT_CATEGORIES = {
    # Produce
    'tomato': 'Produce', 'lettuce': 'Produce', 'onion': 'Produce', 'garlic': 'Produce',
    'carrot': 'Produce', 'potato': 'Produce', 'broccoli': 'Produce', 'spinach': 'Produce',
    'pepper': 'Produce', 'cucumber': 'Produce', 'mushroom': 'Produce', 'apple': 'Produce',
    'banana': 'Produce', 'lemon': 'Produce', 'lime': 'Produce', 'orange': 'Produce',
    'celery': 'Produce', 'zucchini': 'Produce', 'pumpkin': 'Produce', 'bean': 'Produce',
    
    # Meat & Seafood
    'chicken': 'Meat & Seafood', 'beef': 'Meat & Seafood', 'pork': 'Meat & Seafood',
    'fish': 'Meat & Seafood', 'salmon': 'Meat & Seafood', 'tuna': 'Meat & Seafood',
    'shrimp': 'Meat & Seafood', 'cod': 'Meat & Seafood', 'turkey': 'Meat & Seafood',
    'lamb': 'Meat & Seafood', 'bacon': 'Meat & Seafood', 'sausage': 'Meat & Seafood',
    
    # Dairy & Eggs
    'milk': 'Dairy & Eggs', 'cheese': 'Dairy & Eggs', 'yogurt': 'Dairy & Eggs',
    'butter': 'Dairy & Eggs', 'cream': 'Dairy & Eggs', 'egg': 'Dairy & Eggs',
    'mozzarella': 'Dairy & Eggs', 'cheddar': 'Dairy & Eggs', 'parmesan': 'Dairy & Eggs',
    
    # Pantry & Dry Goods
    'flour': 'Pantry & Dry', 'rice': 'Pantry & Dry', 'pasta': 'Pantry & Dry',
    'bread': 'Pantry & Dry', 'sugar': 'Pantry & Dry', 'salt': 'Pantry & Dry',
    'oil': 'Pantry & Dry', 'vinegar': 'Pantry & Dry', 'sauce': 'Pantry & Dry',
    'honey': 'Pantry & Dry', 'jam': 'Pantry & Dry', 'cereal': 'Pantry & Dry',
    'bean': 'Pantry & Dry', 'lentil': 'Pantry & Dry',
    
    # Spices & Seasonings
    'salt': 'Spices', 'pepper': 'Spices', 'paprika': 'Spices', 'cumin': 'Spices',
    'cinnamon': 'Spices', 'ginger': 'Spices', 'turmeric': 'Spices', 'basil': 'Spices',
    'oregano': 'Spices', 'thyme': 'Spices', 'chili': 'Spices', 'mustard': 'Spices',
}


def get_ingredient_category(ingredient: str) -> str:
    """
    Determine the category of an ingredient.
    
    Args:
        ingredient: The ingredient name to categorize
        
    Returns:
        Category name (e.g., 'Produce', 'Meat & Seafood', 'Other')
    """
    ingredient_lower = ingredient.lower()
    
    # Check for exact or partial matches
    for key, category in INGREDIENT_CATEGORIES.items():
        if key in ingredient_lower:
            return category
    
    return 'Other'  # Default category