"""
Nutrition tool functions using official MCP pattern
"""

import asyncio
import requests
from typing import Dict, List, Any
from utils import (
    parse_amount_and_get_multiplier,
    format_nutrition_data,
    format_search_results,
)

# Global API key (set by main.py)
API_KEY = None


async def get_food_search(query: str, limit: int = 10) -> str:
    """Search for food items and return formatted results"""
    if not API_KEY:
        raise Exception("USDA API key not configured")

    url = f"https://api.nal.usda.gov/fdc/v1/foods/search"

    payload = {
        "query": query,
        "pageSize": limit,
        "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)", "Branded"],
        "sortBy": "dataType.keyword",
        "sortOrder": "asc",
    }

    params = {"api_key": API_KEY}

    # Use asyncio to run blocking request in thread pool
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, lambda: requests.post(url, json=payload, params=params, timeout=10)
    )

    if not response.ok:
        raise Exception(f"USDA API error {response.status_code}: {response.text}")

    data = response.json()

    if not data.get("foods"):
        raise Exception(f"No food items found for '{query}'")

    results = [
        {
            "fdcId": food["fdcId"],
            "description": food["description"],
            "dataType": food["dataType"],
            "brandOwner": food.get("brandOwner"),
            "ingredients": food.get("ingredients"),
        }
        for food in data["foods"]
    ]

    return format_search_results(results, query)


async def get_nutrition_by_id(fdc_id: int, amount: str = "100g") -> str:
    """Get detailed nutrition data for a specific food ID"""
    if not API_KEY:
        raise Exception("USDA API key not configured")

    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {"api_key": API_KEY}

    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, lambda: requests.get(url, params=params, timeout=10)
    )

    if not response.ok:
        raise Exception(f"USDA API error {response.status_code}: {response.text}")

    data = response.json()

    # Extract nutrients and food portions
    nutrients = data.get("foodNutrients", [])
    food_portions = data.get("foodPortions", [])

    def get_nutrient_value(nutrient_name: str) -> float:
        for nutrient in nutrients:
            if (
                nutrient_name.lower()
                in nutrient.get("nutrient", {}).get("name", "").lower()
            ):
                return nutrient.get("amount", 0)
        return 0

    # Parse amount using USDA portion data
    multiplier, portion_note = parse_amount_and_get_multiplier(amount, food_portions)

    # Get base values (per 100g) and apply multiplier
    nutrition_data = {
        "name": data.get("description", f"Food Item {fdc_id}"),
        "calories": get_nutrient_value("Energy") * multiplier,
        "protein": get_nutrient_value("Protein") * multiplier,
        "carbs": get_nutrient_value("Carbohydrate") * multiplier,
        "fat": get_nutrient_value("Total lipid") * multiplier,
        "fiber": get_nutrient_value("Fiber") * multiplier,
        "sugar": get_nutrient_value("Sugars") * multiplier,
        "serving_size": amount,
        "portion_note": portion_note,
    }

    return format_nutrition_data(nutrition_data)


async def search_nutrition_quick(ingredient: str, amount: str = "100g") -> str:
    """Quick search and get nutrition data for best match"""
    # Search for the ingredient
    search_results = await get_food_search(ingredient, limit=1)

    # Extract FDC ID from search results (simple parsing)
    import re

    match = re.search(r"ID: (\d+)", search_results)
    if not match:
        raise Exception(f"No food items found for '{ingredient}'")

    fdc_id = int(match.group(1))

    # Get nutrition for the first result
    return await get_nutrition_by_id(fdc_id, amount)
