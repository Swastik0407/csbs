import json

from tools.scoring_engine import calculate_product_score


def compare_products(
    discovery_result: dict,
    research_result: dict,
    requirements: dict
) -> dict:
    """
    Comparison Agent.

    Combines discovered product specifications and research findings,
    calculates scores, and ranks products.
    """

    print("\n[Comparison Agent] Starting product comparison...")

    products = discovery_result.get("products", [])

    research_by_id = {
        item["product_id"]: item
        for item in research_result.get("research_results", [])
    }

    comparisons = []

    for product in products:

        score_data = calculate_product_score(
            product,
            requirements
        )

        research = research_by_id.get(
            product["product_id"], {}
        )

        comparison = {
            "product_id": product["product_id"],
            "brand": product["brand"],
            "model": product["model"],
            "price_inr": product["price_inr"],
            "processor": product["processor"],
            "ram_gb": product["ram_gb"],
            "gpu": product["gpu"],
            "battery_wh": product["battery_wh"],
            "weight_kg": product["weight_kg"],
            "build": product["build"],
            "source_name": product.get("source_name"),
            "source_type": product.get("source_type"),
            "source_url": product.get("source_url"),
            "fetched_at": product.get("fetched_at"),
            "review_status": product.get("review_status", "missing"),
            "rating": product.get("rating"),
            "review_count": product.get("review_count"),
            "review_source_url": product.get("review_source_url"),
            "final_score": score_data["final_score"],
            "score_breakdown": score_data["score_breakdown"],
            "weights_used": score_data["weights_used"],
            "research_findings": research.get(
                "research_findings", []
            ),
            "limitations": research.get("limitations", [])
        }

        comparisons.append(comparison)

    # Rank products by score, then by price.
    comparisons.sort(
        key=lambda x: (
            -x["final_score"],
            x["price_inr"]
        )
    )

    for rank, product in enumerate(comparisons, start=1):
        product["rank"] = rank

    result = {
        "agent": "Comparison Agent",
        "products_compared": len(comparisons),
        "ranking_method": (
            "Weighted heuristic scoring based on user priorities."
        ),
        "ranked_products": comparisons
    }

    print(
        f"[Comparison Agent] Compared "
        f"{len(comparisons)} products."
    )

    return result


if __name__ == "__main__":

    # Sample input for independent testing.
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
        ]
    }

    sample_discovery = {
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

    sample_research = {
        "research_results": [
            {
                "product_id": "P001",
                "research_findings": [
                    "Lightweight design",
                    "Aluminium construction"
                ],
                "limitations": [
                    "Actual battery runtime not verified"
                ]
            },
            {
                "product_id": "P006",
                "research_findings": [
                    "Dedicated RTX 3050 graphics"
                ],
                "limitations": [
                    "Actual battery runtime not verified"
                ]
            }
        ]
    }

    output = compare_products(
        sample_discovery,
        sample_research,
        sample_requirements
    )

    print("\nCOMPARISON AGENT OUTPUT:")
    print(json.dumps(output, indent=4))