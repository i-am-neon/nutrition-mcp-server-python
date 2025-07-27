"""
Utility functions for nutrition calculations and formatting
"""

import re
from typing import Dict, List, Any, Tuple


def parse_amount_and_get_multiplier(
    amount: str, food_portions: List[Dict] = None
) -> Tuple[float, str]:
    """
    Parse amount and return multiplier + explanation
    Uses USDA portion data when available, falls back to estimates
    """
    amount = amount.lower().strip()

    # If we have USDA portion data, use it
    if food_portions:
        for portion in food_portions:
            portion_desc = portion.get("portionDescription", "").lower()
            if any(term in amount for term in portion_desc.split()):
                gram_weight = portion.get("gramWeight", 100)
                multiplier = gram_weight / 100
                return (
                    multiplier,
                    f"USDA portion: {portion['portionDescription']} = {gram_weight}g",
                )

    # Extract numeric value
    match = re.search(r"(\d+(?:\.\d+)?)", amount)
    if not match:
        return 1.0, "No amount specified, using 100g"

    value = float(match.group(1))

    # Handle grams directly
    if "g" in amount and "kg" not in amount:
        multiplier = value / 100
        return multiplier, f"{value}g"

    # Handle common units with standard estimates
    unit_estimates = {
        "cup": 240,  # grams per cup (varies by food)
        "medium": 150,  # medium fruit/vegetable
        "large": 200,  # large fruit/vegetable
        "small": 100,  # small fruit/vegetable
        "slice": 30,  # bread slice
        "piece": 100,  # generic piece
        "tbsp": 15,  # tablespoon
        "tsp": 5,  # teaspoon
    }

    for unit, grams_per_unit in unit_estimates.items():
        if unit in amount:
            total_grams = value * grams_per_unit
            multiplier = total_grams / 100
            return multiplier, f"{value} {unit} ≈ {total_grams}g (estimate)"

    # Default: assume grams
    multiplier = value / 100
    return multiplier, f"{value}g (assumed)"


def format_nutrition_data(data: Dict[str, Any]) -> str:
    """Format nutrition data for display"""
    result = f"🥗 **{data['name']}** ({data['serving_size']})\n"

    if data.get("portion_note"):
        result += f"*{data['portion_note']}*\n"

    result += "\n**Macronutrients:**\n"
    result += f"• Calories: {round(data['calories'])} kcal\n"
    result += f"• Protein: {data['protein']:.1f}g\n"
    result += f"• Carbohydrates: {data['carbs']:.1f}g\n"
    result += f"• Fat: {data['fat']:.1f}g\n"

    if data.get("fiber", 0) > 0:
        result += f"• Fiber: {data['fiber']:.1f}g\n"

    if data.get("sugar", 0) > 0:
        result += f"• Sugar: {data['sugar']:.1f}g\n"

    # Calculate macro percentages
    total_macro_calories = (
        (data["protein"] * 4) + (data["carbs"] * 4) + (data["fat"] * 9)
    )
    if total_macro_calories > 0:
        result += "\n**Macro Distribution:**\n"
        result += (
            f"• Protein: {round((data['protein'] * 4 / total_macro_calories) * 100)}%\n"
        )
        result += (
            f"• Carbs: {round((data['carbs'] * 4 / total_macro_calories) * 100)}%\n"
        )
        result += f"• Fat: {round((data['fat'] * 9 / total_macro_calories) * 100)}%\n"

    return result


def format_search_results(results: List[Dict[str, Any]], query: str) -> str:
    """Format search results for display"""
    output = f'🔍 **Search Results for "{query}"**\n\n'
    output += f"Found {len(results)} food items:\n\n"

    for i, item in enumerate(results, 1):
        output += f"**{i}. {item['description']}**\n"
        output += f"   • ID: {item['fdcId']}\n"
        output += f"   • Data Type: {item['dataType']}\n"
        if item.get("brandOwner"):
            output += f"   • Brand: {item['brandOwner']}\n"
        output += "\n"

    output += "\n💡 **Next Steps:**\n"
    output += "Use the `get_nutrition_by_id` tool with one of the FDC IDs above to get detailed nutrition information.\n"
    if results:
        first_result = results[0]
        output += f"Example: Get nutrition for ID {first_result['fdcId']} ({first_result['description'][:40]}...)"

    return output
