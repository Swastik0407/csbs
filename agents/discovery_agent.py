import json

from tools.product_search import search_products


def discover_products(requirements: dict, top_k: int = 10) -> dict:
    """
    Product Discovery Agent.

    Receives structured requirements and discovers
    relevant products from the product catalogue.
    """

    print("\n[Discovery Agent] Starting product discovery...")

    print(
        f"[Discovery Agent] Category: "
        f"{requirements.get('category')}"
    )

    print(
        f"[Discovery Agent] Budget: "
        f"{requirements.get('budget_max')}"
    )

    products = search_products(
        requirements=requirements,
        top_k=top_k
    )

    result = {
        "agent": "Product Discovery Agent",
        "products_found": len(products),
        "products": products
    }

    print(
        f"[Discovery Agent] Found "
        f"{len(products)} matching products."
    )

    return result


if __name__ == "__main__":

    # Temporary test input.
    # This represents the output received from Agent 1.
    sample_requirements = {
        "category": "laptop",
        "budget_max": 65000,
        "currency": "INR",
        "use_cases": [
            "programming",
            "occasional gaming",
            "college work"
        ],
        "priorities": [
            "performance",
            "battery life",
            "build quality"
        ],
        "required_features": [],
        "excluded_features": [],
        "missing_information": [
            "screen size preference",
            "operating system preference",
            "weight and portability preferences"
        ],
        "clarification_question": None
    }

    print("\nUSER REQUIREMENTS:")
    print(json.dumps(sample_requirements, indent=4))

    discovery_result = discover_products(
        sample_requirements
    )

    print("\nDISCOVERY AGENT OUTPUT:")
    print(json.dumps(discovery_result, indent=4))