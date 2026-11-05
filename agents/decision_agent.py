import json


def make_decision(
    comparison_result: dict,
    requirements: dict
) -> dict:
    """
    Decision-Making Agent.

    Evaluates ranked products and selects the
    best overall option according to user priorities.
    """

    print("\n[Decision Agent] Evaluating product rankings...")

    products = comparison_result.get("ranked_products", [])

    if not products:
        return {
            "agent": "Decision-Making Agent",
            "decision": "no_recommendation",
            "reason": "No matching products were available."
        }

    # Highest-scoring product is the overall winner.
    best_product = products[0]

    priorities = [
        str(p).lower()
        for p in requirements.get("priorities", [])
    ]

    use_cases = [
        str(u).lower()
        for u in requirements.get("use_cases", [])
    ]

    # Identify a gaming-focused alternative.
    gaming_alternative = None

    if any("gaming" in use_case for use_case in use_cases):

        gaming_alternative = max(
            products,
            key=lambda p: p.get("score_breakdown", {}).get(
                "gaming", 0
            )
        )

        if (
            gaming_alternative["product_id"]
            == best_product["product_id"]
        ):
            gaming_alternative = None

    # Build an explanation from available evidence.
    breakdown = best_product.get("score_breakdown", {})

    reasons = []

    for priority in priorities:

        if priority == "performance":
            reasons.append(
                f"Performance score: {breakdown.get('performance', 'N/A')}"
            )

        elif priority in ["battery", "battery life"]:
            reasons.append(
                f"Battery score: {breakdown.get('battery', 'N/A')}"
            )

        elif priority in ["build", "build quality"]:
            reasons.append(
                f"Build score: {breakdown.get('build', 'N/A')}"
            )

    # Identify the product's limitations.
    limitations = best_product.get("limitations", [])

    decision = {
        "agent": "Decision-Making Agent",
        "decision": "recommend",
        "overall_winner": {
            "product_id": best_product["product_id"],
            "brand": best_product["brand"],
            "model": best_product["model"],
            "price_inr": best_product["price_inr"],
            "final_score": best_product["final_score"]
        },
        "decision_reasons": reasons,
        "advantages": best_product.get("research_findings", []),
        "limitations": limitations,
        "alternative_for_gaming": None,
        "decision_explanation": (
            "The selected product has the highest weighted "
            "score according to the user's stated priorities."
        )
    }

    if gaming_alternative:
        decision["alternative_for_gaming"] = {
            "product_id": gaming_alternative["product_id"],
            "brand": gaming_alternative["brand"],
            "model": gaming_alternative["model"],
            "price_inr": gaming_alternative["price_inr"],
            "gaming_score": gaming_alternative.get(
                "score_breakdown", {}
            ).get("gaming", 0),
            "reason": (
                "This alternative has a higher gaming score "
                "than the overall winner."
            )
        }

    print(
        f"[Decision Agent] Selected "
        f"{best_product['brand']} "
        f"{best_product['model']}."
    )

    return decision


if __name__ == "__main__":

    sample_comparison = {
        "ranked_products": [
            {
                "product_id": "P001",
                "brand": "DemoTech",
                "model": "CreatorBook 14",
                "price_inr": 58999,
                "final_score": 85.50,
                "score_breakdown": {
                    "performance": 95,
                    "battery": 87.5,
                    "build": 90,
                    "gaming": 35
                },
                "research_findings": [
                    "Lightweight design",
                    "Aluminium construction"
                ],
                "limitations": [
                    "Actual battery runtime not verified",
                    "Integrated graphics limit gaming capability"
                ]
            },
            {
                "product_id": "P006",
                "brand": "SampleWorks",
                "model": "PerformanceBook 16",
                "price_inr": 63999,
                "final_score": 82.88,
                "score_breakdown": {
                    "performance": 95,
                    "battery": 81.25,
                    "build": 65,
                    "gaming": 90
                },
                "research_findings": [
                    "Dedicated RTX 3050 graphics"
                ],
                "limitations": [
                    "Relatively heavy",
                    "Actual battery runtime not verified"
                ]
            }
        ]
    }

    sample_requirements = {
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

    result = make_decision(
        sample_comparison,
        sample_requirements
    )

    print("\nDECISION AGENT OUTPUT:")
    print(json.dumps(result, indent=4))