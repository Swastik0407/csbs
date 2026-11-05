
import json


def _source_info(product: dict) -> dict:
    """Where this record came from and when it was fetched."""
    return {
        "name": product.get("source_name"),
        "type": product.get("source_type"),
        "url": product.get("source_url"),
        "fetched_at": product.get("fetched_at")
    }


def _review_info(product: dict) -> dict:
    """Review data, with an explicit status so missing != zero."""
    return {
        "status": product.get("review_status", "missing"),
        "rating": product.get("rating"),
        "count": product.get("review_count"),
        "source_url": product.get("review_source_url")
    }


def _disclaimer(winner: dict) -> str:
    if winner.get("source_type") == "synthetic":
        return (
            "This recommendation is based on a demo product "
            "dataset and heuristic scoring. Prices and product "
            "specifications are illustrative, not verified live "
            "marketplace information."
        )
    return (
        "Scores are heuristic and based on catalogue data fetched "
        "at the time shown. Prices and availability can change; "
        "check the source link before buying."
    )


def _verification_needed(winner: dict) -> list:
    items = [
        "Verify current price and availability.",
        "Check exact processor model and generation.",
        "Verify battery runtime through independent tests.",
        "Check display quality and refresh rate."
    ]
    if winner.get("review_status") == "verified":
        items.append("Check warranty details.")
    else:
        items.append("Check customer reviews and warranty.")
    return items


def generate_recommendation(
    decision_result: dict,
    comparison_result: dict,
    requirements: dict
) -> dict:
    """
    Recommendation Agent.

    Converts decision and comparison results
    into a clear, personalized shopping recommendation.
    """

    print("\n[Recommendation Agent] Preparing final recommendation...")

    if decision_result.get("decision") != "recommend":
        return {
            "agent": "Recommendation Agent",
            "status": "no_recommendation",
            "message": decision_result.get(
                "reason",
                "No suitable product was found."
            )
        }

    winner = decision_result["overall_winner"]
    ranked_products = comparison_result.get("ranked_products", [])

    # Find the winner's full comparison record.
    winner_details = next(
        (
            product for product in ranked_products
            if product["product_id"] == winner["product_id"]
        ),
        None
    )

    if winner_details is None:
        raise ValueError(
            "Winner details were not found in comparison results."
        )

    # Get the gaming alternative.
    gaming_alternative = decision_result.get(
        "alternative_for_gaming"
    )

    # Track product IDs already included in the recommendation.
    excluded_ids = {winner["product_id"]}

    if gaming_alternative:
        excluded_ids.add(gaming_alternative["product_id"])

    # Build final recommendation.
    recommendation = {
        "agent": "Recommendation Agent",
        "status": "success",

        "user_requirements": {
            "category": requirements.get("category"),
            "budget_max": requirements.get("budget_max"),
            "priorities": requirements.get("priorities", []),
            "use_cases": requirements.get("use_cases", [])
        },

        "best_overall_recommendation": {
            "product_id": winner["product_id"],
            "product_name": (
                f"{winner['brand']} {winner['model']}"
            ),
            "price_inr": winner["price_inr"],
            "overall_score": winner["final_score"],
            "why_recommended": decision_result.get(
                "decision_reasons", []
            ),
            "advantages": decision_result.get(
                "advantages", []
            ),
            "limitations": decision_result.get(
                "limitations", []
            ),
            "source": _source_info(winner_details),
            "reviews": _review_info(winner_details)
        },

        "gaming_alternative": gaming_alternative,

        "other_alternatives": [],

        "important_disclaimer": _disclaimer(winner_details),

        "verification_needed": _verification_needed(winner_details)
    }

    # Add remaining products without duplicating the winner
    # or the gaming alternative.
    for product in ranked_products:

        if product["product_id"] in excluded_ids:
            continue

        recommendation["other_alternatives"].append({
            "product_id": product["product_id"],
            "product_name": (
                f"{product['brand']} {product['model']}"
            ),
            "price_inr": product["price_inr"],
            "overall_score": product["final_score"],
            "source": _source_info(product),
            "reviews": _review_info(product)
        })

    print("[Recommendation Agent] Recommendation generated.")

    return recommendation


if __name__ == "__main__":

    sample_requirements = {
        "category": "laptop",
        "budget_max": 65000,
        "priorities": [
            "performance",
            "battery life",
            "build quality"
        ],
        "use_cases": [
            "programming",
            "occasional gaming",
            "college work"
        ]
    }

    sample_decision = {
        "decision": "recommend",
        "overall_winner": {
            "product_id": "P001",
            "brand": "DemoTech",
            "model": "CreatorBook 14",
            "price_inr": 58999,
            "final_score": 85.5
        },
        "decision_reasons": [
            "Performance score: 95",
            "Battery score: 87.5",
            "Build score: 90"
        ],
        "advantages": [
            "Lightweight design",
            "Aluminium construction"
        ],
        "limitations": [
            "Actual battery runtime not verified",
            "Integrated graphics limit gaming capability"
        ],
        "alternative_for_gaming": {
            "product_id": "P006",
            "brand": "SampleWorks",
            "model": "PerformanceBook 16",
            "price_inr": 63999,
            "gaming_score": 90,
            "reason": "Higher gaming score than the overall winner."
        }
    }

    sample_comparison = {
        "ranked_products": [
            {
                "product_id": "P001",
                "brand": "DemoTech",
                "model": "CreatorBook 14",
                "price_inr": 58999,
                "final_score": 85.5
            },
            {
                "product_id": "P006",
                "brand": "SampleWorks",
                "model": "PerformanceBook 16",
                "price_inr": 63999,
                "final_score": 82.88
            }
        ]
    }

    result = generate_recommendation(
        sample_decision,
        sample_comparison,
        sample_requirements
    )

    print("\nFINAL RECOMMENDATION:")
    print(json.dumps(result, indent=4))
