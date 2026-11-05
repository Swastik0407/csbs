from agents.requirement_agent import understand_requirements
from agents.discovery_agent import discover_products
from agents.research_agent import research_products
from agents.comparison_agent import compare_products
from agents.decision_agent import make_decision
from agents.recommendation_agent import generate_recommendation


def run_shopping_workflow(user_input: str) -> dict:
    """
    Main ShopMind AI orchestrator.

    Executes all six agents in sequence and passes
    each agent's output to the next agent.
    """

    print("\n===================================")
    print("       SHOPMIND AI STARTED")
    print("===================================")

    # AGENT 1: Understand requirements
    print("\nSTEP 1: REQUIREMENT UNDERSTANDING")

    requirements_model = understand_requirements(user_input)

    # Convert Pydantic model into a dictionary.
    requirements = requirements_model.model_dump()

    print("Requirements extracted successfully.")

    # AGENT 2: Discover products
    print("\nSTEP 2: PRODUCT DISCOVERY")

    discovery_result = discover_products(
        requirements
    )

    if not discovery_result.get("products"):
        return {
            "status": "no_products_found",
            "requirements": requirements,
            "message": "No products matched the supplied requirements."
        }

    # AGENT 3: Research products
    print("\nSTEP 3: PRODUCT RESEARCH")

    research_result = research_products(
        discovery_result
    )

    # AGENT 4: Compare products
    print("\nSTEP 4: PRODUCT COMPARISON")

    comparison_result = compare_products(
        discovery_result,
        research_result,
        requirements
    )

    # AGENT 5: Make decision
    print("\nSTEP 5: DECISION MAKING")

    decision_result = make_decision(
        comparison_result,
        requirements
    )

    # AGENT 6: Generate recommendation
    print("\nSTEP 6: FINAL RECOMMENDATION")

    recommendation_result = generate_recommendation(
        decision_result,
        comparison_result,
        requirements
    )

    # Collect all agent outputs.
    workflow_result = {
        "status": "success",
        "user_input": user_input,
        "agents": {
            "requirement_agent": requirements,
            "discovery_agent": discovery_result,
            "research_agent": research_result,
            "comparison_agent": comparison_result,
            "decision_agent": decision_result,
            "recommendation_agent": recommendation_result
        }
    }

    print("\n===================================")
    print("      SHOPMIND AI COMPLETED")
    print("===================================")

    return workflow_result


if __name__ == "__main__":

    user_request = (
        "I need a laptop under 65000 rupees "
        "for programming, occasional gaming "
        "and college work. Prioritize performance, "
        "battery life and build quality."
    )

    result = run_shopping_workflow(user_request)

    import json

    print("\nCOMPLETE WORKFLOW OUTPUT:")
    print(json.dumps(result, indent=4))