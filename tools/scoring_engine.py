def calculate_product_score(product: dict, requirements: dict) -> dict:
    """
    Calculate a transparent heuristic score out of 100.

    Scores are based only on available catalogue specifications.
    They are not independent benchmark or review scores.
    """

    # Performance score
    processor = str(product.get("processor", "")).lower()

    if "ryzen 7" in processor or "core i7" in processor:
        cpu_score = 90
    elif "ryzen 5" in processor or "core i5" in processor:
        cpu_score = 75
    else:
        cpu_score = 55

    ram = int(product.get("ram_gb", 0))

    if ram >= 16:
        ram_score = 100
    elif ram >= 8:
        ram_score = 60
    else:
        ram_score = 30

    performance_score = (cpu_score + ram_score) / 2

    # Gaming score
    gpu = str(product.get("gpu", "")).lower()

    if "rtx" in gpu:
        gaming_score = 90
    elif "gtx" in gpu:
        gaming_score = 75
    else:
        gaming_score = 35

    # Battery capacity proxy, NOT actual runtime.
    battery_wh = float(product.get("battery_wh", 0))
    battery_score = min((battery_wh / 80) * 100, 100)

    # Construction material proxy, NOT a verified durability test.
    build = str(product.get("build", "")).lower()

    if "aluminium" in build:
        build_score = 90
    elif "plastic" in build:
        build_score = 65
    else:
        build_score = 50

    # Criteria weights.
    weights = {}

    priorities = [
        str(p).lower() for p in requirements.get("priorities", [])
    ]

    for priority in priorities:

        if priority == "performance":
            weights["performance"] = 35

        elif priority in ["battery", "battery life"]:
            weights["battery"] = 30

        elif priority in ["build", "build quality"]:
            weights["build"] = 25

    use_cases = [
        str(x).lower()
        for x in requirements.get("use_cases", [])
    ]

    if any("gaming" in x for x in use_cases):
        weights["gaming"] = 10

    # Normalize weights if some priorities are absent.
    total_weight = sum(weights.values())

    if total_weight == 0:
        weights = {"performance": 100}
        total_weight = 100

    score_components = {
        "performance": performance_score,
        "gaming": gaming_score,
        "battery": battery_score,
        "build": build_score
    }

    final_score = sum(
        score_components[key] * weight
        for key, weight in weights.items()
    ) / total_weight

    return {
        "final_score": round(final_score, 2),
        "score_breakdown": {
            key: round(score_components[key], 2)
            for key in weights
        },
        "weights_used": weights,
        "scoring_note": (
            "Heuristic scores based on available specifications; "
            "not verified benchmarks or review scores."
        )
    }