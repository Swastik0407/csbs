import json

from tools.product_research import research_product


def research_products(discovery_result: dict) -> dict:
    """
    Product Research Agent.

    Receives discovered products and analyses
    their specifications individually.
    """

    print("\n[Research Agent] Starting product research...")

    products = discovery_result.get("products", [])

    research_results = []

    for product in products:

        print(
            f"[Research Agent] Researching "
            f"{product.get('brand')} {product.get('model')}..."
        )

        research = research_product(product)

        research_results.append(research)

    result = {
        "agent": "Product Research Agent",
        "products_researched": len(research_results),
        "research_results": research_results
    }

    print(
        f"[Research Agent] Completed research on "
        f"{len(research_results)} products."
    )

    return result


if __name__ == "__main__":

    # Temporary sample input for independent testing.
    sample_discovery_result = {
        "products": [
            {
                "product_id": "P001",
                "brand": "DemoTech",
                "model": "CreatorBook 14",
                "price_inr": 58999,
                "processor": "Ryzen 7",
                "ram_gb": 16,
                "gpu": "Integrated Graphics",
                "battery_wh": 70,
                "weight_kg": 1.45,
                "build": "Aluminium"
            },
            {
                "product_id": "P006",
                "brand": "SampleWorks",
                "model": "PerformanceBook 16",
                "price_inr": 63999,
                "processor": "Ryzen 7",
                "ram_gb": 16,
                "gpu": "RTX 3050",
                "battery_wh": 65,
                "weight_kg": 2.3,
                "build": "Plastic"
            }
        ]
    }

    output = research_products(sample_discovery_result)

    print("\nRESEARCH AGENT OUTPUT:")
    print(json.dumps(output, indent=4))