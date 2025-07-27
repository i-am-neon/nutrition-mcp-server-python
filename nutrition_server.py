"""
Nutrition MCP Server - Main server implementation
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
from usda_api import USDAApi
from utils import (
    parse_amount_and_get_multiplier,
    format_nutrition_data,
    format_search_results,
)


class NutritionServer:
    def __init__(self, api_key: str):
        self.api = USDAApi(api_key)
        self.server = Server("nutrition-server")
        self._setup_tools()

    def _setup_tools(self):
        """Register all available tools"""

        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
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
                Tool(
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
                Tool(
                    name="search_nutrition",
                    description="Quick nutrition lookup using best match. Use search_food_items first for better accuracy when ingredient names might be ambiguous",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "ingredient": {
                                "type": "string",
                                "description": "The ingredient or food item to search for (e.g., 'chicken breast', 'banana', 'olive oil')",
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

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            try:
                if name == "search_food_items":
                    query = arguments["query"]
                    limit = min(arguments.get("limit", 10), 20)
                    results = await self.api.search_food_items(query, limit)
                    return [
                        TextContent(
                            type="text", text=format_search_results(results, query)
                        )
                    ]

                elif name == "get_nutrition_by_id":
                    fdc_id = arguments["fdcId"]
                    amount = arguments.get("amount", "100g")
                    nutrition_data = await self.api.get_nutrition_by_id(fdc_id, amount)
                    return [
                        TextContent(
                            type="text", text=format_nutrition_data(nutrition_data)
                        )
                    ]

                elif name == "search_nutrition":
                    ingredient = arguments["ingredient"]
                    amount = arguments.get("amount", "100g")
                    nutrition_data = await self.api.search_nutrition(ingredient, amount)
                    return [
                        TextContent(
                            type="text", text=format_nutrition_data(nutrition_data)
                        )
                    ]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def run(self, read_stream, write_stream):
        """Run the server"""
        await self.server.run(read_stream, write_stream, {})
