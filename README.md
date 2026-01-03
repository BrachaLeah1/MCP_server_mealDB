# 🍳 MealDB Recipe MCP Server

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://www.python.org)

A Model Context Protocol (MCP) server that provides any AI agent with access to TheMealDB recipe database and local recipe management capabilities. Search thousands of recipes, save them as PDFs, and generate organized shopping lists—all directly from your conversations with your agent!!!

## Features

### 🔍 Recipe Discovery
- Search recipes by name, ingredient, category, or cuisine
- Browse recipes alphabetically (A-Z)
- Get random recipe suggestions
- View complete recipe details with ingredients and instructions

### 📁 Recipe Management
- Save recipes as professional PDF files
- Automatic organization by category (Seafood, Dessert, etc.)
- List and manage saved recipes
- Delete unwanted recipes

### 🛒 Shopping List Generation
- Create shopping lists from multiple recipes
- Automatic ingredient categorization (Produce, Meat, Dairy, etc.)
- Combine duplicate ingredients intelligently
- Export as printer-friendly PDFs

### 🌐 Recipe Database
- Access to 1000+ recipes from TheMealDB
- Multiple cuisines (Italian, Chinese, Mexican, and more)
- Diverse categories (Vegetarian, Seafood, Desserts, etc.)
- Recipe images and video links included

## Project Structure
```
recipe-mcp-server/
├── src/
│   ├── server.py                      # Main MCP server entry point
│   └── tools/
│       ├── api_tools.py               # TheMealDB API integration tools
│       └── local/
│           ├── __init__.py            # Local tools package exports
│           ├── tools.py               # Local file management tools
│           ├── api.py                 # API client for fetching meal data
│           ├── config.py              # Configuration and directory management
│           ├── categories.py          # Ingredient categorization for shopping lists
│           ├── pdf_recipe.py          # Recipe PDF generator
│           └── pdf_shopping.py        # Shopping list PDF generator
├── tests/
│   ├── test_api_tools.py              # Tests for API tools
│   └── test_local_tools.py            # Tests for local tools
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## Prerequisites

- **Python 3.8 or higher** (tested on Python 3.13)
- **Any MCP-compatible client** (Claude Desktop, etc.)
- **Internet connection** (for accessing TheMealDB API)

### Key Dependencies
- `mcp` - Model Context Protocol SDK
- `httpx` - Async HTTP client for API requests
- `reportlab` - PDF generation
- `Pillow` - Image processing
- `requests` - HTTP requests for images

All dependencies are listed in `requirements.txt` and will be installed automatically.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/BrachaLeah1/MCP_server_mealDB.git
cd MCP_server_mealDB
```

### 2. Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation

Run the tests to verify everything is working:
```bash
pytest tests/ -v
```

Or test the server directly:
```bash
python src/server.py
```

## Configuration 

## Usage

Once configured with your MCP client, you can interact with the recipe server through natural language.

### Quick Start Examples

#### Discover Recipes
```
"Show me a random recipe"
"Search for chicken recipes"
"Find Italian recipes"
"Show me desserts"
"List recipes starting with 'P'"
```

#### View Recipe Details
```
"Show me the recipe for Pad Thai"
"What ingredients do I need for Carbonara?"
"How do I make Chicken Teriyaki?"
```

#### Save Recipes
```
"Save this recipe as a PDF"
"Save the Pad Thai recipe"
"Download this recipe to my computer"
```

#### Manage Saved Recipes
```
"List my saved recipes"
"Show me all my saved recipes"
"Delete the Chicken Soup recipe"
```

#### Create Shopping Lists
```
"Create a shopping list from these recipes"
"Make a shopping list for recipes 52772, 52773, 52774"
"Generate a shopping list from my saved recipes"
```

#### Browse Categories & Cuisines
```
"What recipe categories are available?"
"Show me all cuisines"
"What Italian recipes do you have?"
"Show me all Seafood recipes"
```

### Server Startup

If running the server manually (for testing or development):
```bash
python src/server.py
```

The server will start in stdio mode and communicate via standard input/output with your MCP client.

## Acknowledgments

- **[TheMealDB](https://www.themealdb.com/)** - Free recipe API providing access to thousands of recipes with images and detailed instructions
- **[Model Context Protocol (MCP)](https://modelcontextprotocol.io)** - Framework for connecting AI assistants to external tools and data sources
- **[Anthropic](https://www.anthropic.com/)** - For creating Claude and the MCP specification
- **ReportLab** - PDF generation library for creating professional recipe and shopping list documents
