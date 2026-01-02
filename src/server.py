#!/usr/bin/env python3
"""
MealDB MCP Server - Main Entry Point
Coordinates API tools and local tools.

Installation:
    pip install mcp httpx

Usage:
    python src/server.py

Configuration Options:
    - None for now.
    
"""

import asyncio
from mcp.server import Server
from mcp.types import TextContent
from typing import Any

# Import our tool modules
from tools.api_tools import get_api_tool_definitions, handle_api_tool
from tools.local import get_local_tool_definitions, handle_local_tool


# Create server
app = Server("mealdb-server")


@app.list_tools()
async def list_tools():
    """List all available tools from both modules."""
    api_tools = get_api_tool_definitions()
    local_tools = get_local_tool_definitions()
    
    all_tools = api_tools + local_tools
    
    print(f"Registered {len(all_tools)} tools:")
    print(f"   - API tools: {len(api_tools)}")
    print(f"   - Local tools: {len(local_tools)}")
    
    return all_tools


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Route tool calls to the appropriate handler."""
    
    # Try API tools first
    result = await handle_api_tool(name, arguments)
    if result is not None:
        return result
    
    # Try local tools
    result = await handle_local_tool(name, arguments)
    if result is not None:
        return result
    
    # Unknown tool
    return [TextContent(type="text", text=f"ERROR: Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    print("Starting MealDB MCP Server...")
    print("=" * 50)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())