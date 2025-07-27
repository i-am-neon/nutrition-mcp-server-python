"""
USDA FoodData Central API client
"""

import asyncio
import requests
from typing import Dict, List, Optional, Any
from utils import parse_amount_and_get_multiplier


class USDAApi:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.nal.usda.gov/fdc/v1"

    async def search_food_items(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for food items and return basic info"""
        url = f"{self.base_url}/foods/search"

        payload = {
            "query": query,
            "pageSize": limit,
            "dataType": ["Foundation", "SR Legacy", "Survey (FNDDS)", "Branded"],
            "sortBy": "dataType.keyword",
            "sortOrder": "asc",
        }

        params = {"api_key": self.api_key}

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

        return [
            {
                "fdcId": food["fdcId"],
                "description": food["description"],
                "dataType": food["dataType"],
                "brandOwner": food.get("brandOwner"),
                "ingredients": food.get("ingredients"),
            }
            for food in data["foods"]
        ]

    async def get_nutrition_by_id(
        self, fdc_id: int, amount: str = "100g"
    ) -> Dict[str, Any]:
        """Get detailed nutrition data for a specific food ID"""
        url = f"{self.base_url}/food/{fdc_id}"
        params = {"api_key": self.api_key}

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
        multiplier, portion_note = parse_amount_and_get_multiplier(
            amount, food_portions
        )

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

        return nutrition_data

    async def search_nutrition(
        self, ingredient: str, amount: str = "100g"
    ) -> Dict[str, Any]:
        """Search and get nutrition data for best match"""
        # Search for the ingredient
        results = await self.search_food_items(ingredient, limit=1)

        # Get nutrition for the first result
        return await self.get_nutrition_by_id(results[0]["fdcId"], amount)
