#!/usr/bin/env python3
"""
Nutrition MCP Server - Official MCP pattern
Run with: python main.py
"""

import asyncio
import os
import sys
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from nutrition_tools import get_food_search, get_nutrition_by_id, search_nutrition_quick

# Create MCP server instance
server = Server("nutrition-server")


# Register our tools
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_food_items",
            description="ALWAYS use this first to search for food items by name. Returns multiple options to choose from since ingredient names vary widely (e.g., 'firm tofu' vs 'soft tofu')",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The food item to search for (e.g., 'tofu', 'chicken', 'apple')",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10, max: 20)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 20,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_nutrition_by_id",
            description="Get detailed nutrition information for a specific food item using its ID from search results",
            inputSchema={
                "type": "object",
                "properties": {
                    "fdcId": {
                        "type": "number",
                        "description": "The FDC ID of the food item from search results",
                    },
                    "amount": {
                        "type": "string",
                        "description": "Optional: specify amount (e.g., '100g', '1 cup', '1 medium'). Defaults to per 100g",
                        "default": "100g",
                    },
                },
                "required": ["fdcId"],
            },
        ),
        types.Tool(
            name="search_nutrition",
            description="Quick nutrition lookup using best match. Use search_food_items first for better accuracy when ingredient names might be ambiguous",
            inputSchema={
                "type": "object",
                "properties": {
                    "ingredient": {
                        "type": "string",
                        "description": "The ingredient or food item to search for",
                    },
                    "amount": {
                        "type": "string",
                        "description": "Optional: specify amount (e.g., '100g', '1 cup', '1 medium'). Defaults to per 100g",
                        "default": "100g",
                    },
                },
                "required": ["ingredient"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    if not arguments:
        arguments = {}

    try:
        if name == "search_food_items":
            query = arguments["query"]
            limit = min(arguments.get("limit", 10), 20)
            result = await get_food_search(query, limit)
            return [types.TextContent(type="text", text=result)]

        elif name == "get_nutrition_by_id":
            fdc_id = arguments["fdcId"]
            amount = arguments.get("amount", "100g")
            result = await get_nutrition_by_id(fdc_id, amount)
            return [types.TextContent(type="text", text=result)]

        elif name == "search_nutrition":
            ingredient = arguments["ingredient"]
            amount = arguments.get("amount", "100g")
            result = await search_nutrition_quick(ingredient, amount)
            return [types.TextContent(type="text", text=result)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    # Check for API key
    api_key = os.getenv("USDA_API_KEY")
    if not api_key:
        print("ERROR: USDA_API_KEY environment variable required", file=sys.stderr)
        print(
            "Get a free key at: https://fdc.nal.usda.gov/api-guide.html",
            file=sys.stderr,
        )
        sys.exit(1)

    print("✅ Nutrition MCP Server starting...", file=sys.stderr)
    print("✅ API key found", file=sys.stderr)
    print("✅ Ready! Add to Claude Desktop config and restart Claude.", file=sys.stderr)
    print("Press Ctrl+C to stop this test.", file=sys.stderr)

    # Store API key globally for tools to use
    import nutrition_tools

    nutrition_tools.API_KEY = api_key

    # Run the server using stdin/stdout
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nutrition-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
