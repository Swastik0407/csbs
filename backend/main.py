
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.orchestrator import run_shopping_workflow

from google.genai.errors import ServerError
from agents.discovery_agent import discover_products
from agents.research_agent import research_products
from agents.comparison_agent import compare_products
from agents.decision_agent import make_decision
from agents.recommendation_agent import generate_recommendation


# Initialize FastAPI
app = FastAPI(
    title="ShopMind AI",
    description="Autonomous Multi-Agent Shopping Assistant",
    version="1.0.0"
)


# Allow frontend communication during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5501",
        "http://127.0.0.1:5501"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request model
class ShoppingRequest(BaseModel):
    user_input: str = Field(
        min_length=5,
        description="User's natural-language shopping requirements"
    )


# Health-check endpoint
@app.get("/")
def home():
    return {
        "project": "ShopMind AI",
        "message": "Shopping assistant API is running.",
        "status": "online"
    }


# Shopping recommendation endpoint
@app.post("/api/recommend")
def get_recommendation(request: ShoppingRequest):

    try:
        result = run_shopping_workflow(request.user_input)
        return result

    except ServerError:
        raise HTTPException(
            status_code=503,
            detail="Gemini is temporarily unavailable. Please try again later."
        )

    except Exception as error:
        print(f"Backend Error: {error}")

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing your request."
        )
@app.post("/api/demo-recommend")
def demo_recommendation(request: ShoppingRequest):

    # Temporary structured requirements.
    # This bypasses Gemini for frontend testing.
    requirements = {
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
        "missing_information": [],
        "clarification_question": None
    }

    discovery = discover_products(requirements)

    research = research_products(discovery)

    comparison = compare_products(
        discovery,
        research,
        requirements
    )

    decision = make_decision(
        comparison,
        requirements
    )

    recommendation = generate_recommendation(
        decision,
        comparison,
        requirements
    )

    return {
        "status": "success",
        "user_input": request.user_input,
        "demo_mode": True,
        "agents": {
            "requirement_agent": requirements,
            "discovery_agent": discovery,
            "research_agent": research,
            "comparison_agent": comparison,
            "decision_agent": decision,
            "recommendation_agent": recommendation
        }
    }