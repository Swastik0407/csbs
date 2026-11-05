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
        "Warranty and after-sales information",
        "Independent benchmark results"
    ])

    # Specs the catalogue source did not provide (API sources only).
    missing_specs = product.get("missing_specs") or []
    if missing_specs:
        limitations.append(
            "Not provided by the source: " + ", ".join(missing_specs)
        )

    # Reviews: report what exists, and say clearly when it does not.
    review_status = product.get("review_status", "missing")
    rating = product.get("rating")
    review_count = product.get("review_count")

    if review_status == "verified":
        findings.append(
            f"Verified rating {rating}/5 from {review_count} reviews "
            f"(source: {product.get('source_name')})"
        )
    elif review_status == "unverified":
        limitations.append(
            f"A rating of {rating}/5 is listed but could not be verified "
            "(no review count or checkable source link)"
        )
    else:
        limitations.append("Customer reviews: not available from this source")

    # Provenance.
    if product.get("source_type") == "synthetic":
        limitations.append(
            "Synthetic demo record: not taken from a real listing"
        )

    return {
        "product_id": product.get("product_id"),
        "product_name": (
            f"{product.get('brand')} {product.get('model')}"
        ),
        "price_inr": product.get("price_inr"),
        "review_status": review_status,
        "research_findings": findings,
        "limitations": limitations
    }