import pandas as pd
from pathlib import Path


# Locate the CSV relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data" / "products.csv"


def search_products(requirements: dict, top_k: int = 10) -> list[dict]:
    """
    Find products matching the user's requirements.

    Args:
        requirements: Structured output from Requirement Agent.
        top_k: Maximum number of products to return.

    Returns:
        A list of matching product dictionaries.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Product dataset not found: {DATA_FILE}"
        )

    df = pd.read_csv(DATA_FILE)

    # Filter by product category.
    category = str(requirements.get("category", "")).lower().strip()

    if category:
        df = df[
            df["category"].str.lower() == category
        ]

    # Filter by maximum budget.
    budget = requirements.get("budget_max")

    if budget is not None:
        df = df[df["price_inr"] <= float(budget)]

    if df.empty:
        return []

    # Extract preferences from Agent 1.
    use_cases = requirements.get("use_cases", [])
    priorities = requirements.get("priorities", [])
    required_features = requirements.get("required_features", [])
    excluded_features = requirements.get("excluded_features", [])

    # Normalize values.
    use_cases = [str(x).lower() for x in use_cases]
    priorities = [str(x).lower() for x in priorities]
    required_features = [str(x).lower() for x in required_features]
    excluded_features = [str(x).lower() for x in excluded_features]

    # Convert each product into searchable text.
    def product_text(row):
        return " ".join(
            str(row[column]).lower()
            for column in [
                "brand", "model", "processor", "ram_gb",
                "storage", "gpu", "display", "build", "tags"
            ]
        )

    # Exclude products containing explicitly excluded features.
    if excluded_features:
        df = df[
            ~df.apply(
                lambda row: any(
                    feature in product_text(row)
                    for feature in excluded_features
                ),
                axis=1
            )
        ]

    # If mandatory features were specified, require all of them.
    if required_features:
        df = df[
            df.apply(
                lambda row: all(
                    feature in product_text(row)
                    for feature in required_features
                ),
                axis=1
            )
        ]

    if df.empty:
        return []

    # Score products according to relevance.
    def calculate_score(row):
        searchable_text = product_text(row)
        score = 0

        # Match intended use cases.
        for use_case in use_cases:
            if any(
                word in searchable_text
                for word in use_case.split()
                if len(word) > 2
            ):
                score += 3

        # Match user priorities.
        for priority in priorities:
            if priority in ["performance"]:
                if any(
                    term in searchable_text
                    for term in ["ryzen 7", "core i7", "rtx"]
                ):
                    score += 3

                if int(row["ram_gb"]) >= 16:
                    score += 2

            elif priority in ["battery life", "battery"]:
                if float(row["battery_wh"]) >= 70:
                    score += 3

            elif priority in ["build quality", "build"]:
                if "aluminium" in str(row["build"]).lower():
                    score += 3

        return score

    df = df.copy()
    df["relevance_score"] = df.apply(calculate_score, axis=1)

    # Highest relevance first, then lower price.
    df = df.sort_values(
        by=["relevance_score", "price_inr"],
        ascending=[False, True]
    )

    # Return only the requested number of products.
    results = df.head(top_k)

    return results.to_dict(orient="records")