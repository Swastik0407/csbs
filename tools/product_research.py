def research_product(product: dict) -> dict:
    """
    Analyse available product specifications.
    Does not invent missing specifications or reviews.
    """

    findings = []
    limitations = []

    # Processor analysis
    processor = str(product.get("processor", "")).lower()

    if "ryzen 7" in processor or "core i7" in processor:
        findings.append("Higher-tier processor family")
    elif "ryzen 5" in processor or "core i5" in processor:
        findings.append("Mid-range processor family")
    else:
        limitations.append("Exact processor model and generation unknown")

    # RAM analysis
    ram = int(product.get("ram_gb", 0))

    if ram >= 16:
        findings.append("16GB or more RAM: suitable for multitasking")
    else:
        findings.append("Less than 16GB RAM: may limit heavy multitasking")

    # GPU analysis
    gpu = str(product.get("gpu", "")).lower()

    if "rtx" in gpu:
        findings.append(f"Dedicated graphics available: {product['gpu']}")
        findings.append("Potentially better suited for occasional gaming")
    else:
        findings.append("Integrated graphics: limited gaming capability")

    # Battery analysis
    battery = float(product.get("battery_wh", 0))

    if battery >= 70:
        findings.append("Large battery capacity on paper")
    else:
        findings.append("Battery capacity is below 70Wh")

    limitations.append(
        "Actual battery runtime has not been verified"
    )

    # Weight analysis
    weight = float(product.get("weight_kg", 0))

    if weight <= 1.5:
        findings.append("Lightweight design: good portability")
    elif weight <= 2.0:
        findings.append("Moderate weight")
    else:
        findings.append("Relatively heavy: less convenient to carry")

    # Build analysis
    build = str(product.get("build", "")).lower()

    if "aluminium" in build:
        findings.append("Aluminium construction listed")
    else:
        findings.append("Plastic construction listed")

    # Missing information
    limitations.extend([
        "Exact CPU model and generation",
        "Display resolution and refresh rate",
        "GPU power limit (TGP), if applicable",
        "Verified customer ratings and reviews",
        "Warranty and after-sales information",
        "Independent benchmark results"
    ])

    return {
        "product_id": product.get("product_id"),
        "product_name": (
            f"{product.get('brand')} {product.get('model')}"
        ),
        "price_inr": product.get("price_inr"),
        "research_findings": findings,
        "limitations": limitations
    }