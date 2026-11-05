
import json
import time

from google import genai
from google.genai import types
from google.genai import errors
from pydantic import BaseModel
from typing import Optional

from config.settings import GEMINI_API_KEY, GEMINI_MODEL


# 1. Define structured shopping requirements

class ShoppingRequirements(BaseModel):
    category: str
    budget_max: Optional[float] = None
    currency: str = "INR"

    use_cases: list[str]
    priorities: list[str]

    required_features: list[str]
    excluded_features: list[str]

    missing_information: list[str]
    clarification_question: Optional[str] = None


# 2. Initialize Gemini

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# 3. Requirement Understanding Agent

def understand_requirements(user_input: str):

    prompt = f"""
    You are the Requirement Understanding Agent
    of ShopMind AI, an autonomous shopping assistant.

    Understand the user's shopping requirements.

    Extract:
    1. Product category
    2. Maximum budget
    3. Currency
    4. Intended use cases
    5. User priorities
    6. Required features
    7. Excluded features
    8. Missing information

    RULES:
    - Never invent user requirements.
    - Never assume a budget.
    - Convert Indian currency into numeric INR.
    - Separate mandatory requirements from preferences.
    - Identify missing information.
    - Ask a clarification question when essential
      information is missing.

    USER REQUEST:
    {user_input}
    """

    response = None

    # Retry if Gemini temporarily becomes unavailable
    for attempt in range(3):

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ShoppingRequirements
                )
            )

            break

        except errors.ServerError:

            if attempt == 2:
                raise

            print("Gemini temporarily unavailable. Retrying...")

            time.sleep(2 ** (attempt + 1))

    if response is None or not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = ShoppingRequirements.model_validate_json(
        response.text
    )

    return result


# 4. Test the agent independently

if __name__ == "__main__":

    user_input = (
        "I need a laptop under 65000 rupees "
        "for programming, occasional gaming "
        "and college work. Prioritize performance, "
        "battery life and build quality."
    )

    print("\nUSER REQUEST:")
    print(user_input)

    result = understand_requirements(user_input)

    print("\nREQUIREMENT AGENT OUTPUT:")

    print(
        json.dumps(
            result.model_dump(),
            indent=4
        )
    )
