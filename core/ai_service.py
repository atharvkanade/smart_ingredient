import os
from openai import OpenAI, OpenAIError, RateLimitError


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def generate_ai_explanation(user_profile, ingredients, warnings):
    # Safe fallback if AI is not configured
    client = get_client()
    if not client:
        return (
            "Some ingredients may pose health risks. "
            "AI explanation is not configured yet."
        )

    # No warnings → simple message
    if not warnings:
        return (
            "Based on your profile and the provided ingredients, no known health risks were detected. "
            "Continue to check labels and consume in moderation."
        )

    prompt = f"""
You are a food safety and health assistant.

User profile:
{user_profile}

Ingredients:
{ingredients}

Warnings:
{warnings}

Explain clearly:
- Why these ingredients may be harmful
- Possible health risks
- Safer alternatives
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return response.choices[0].message.content

    except RateLimitError:
        return (
            "Some ingredients may pose health risks. "
            "AI explanation is temporarily unavailable. Please try again later."
        )

    except OpenAIError:
        return (
            "We detected ingredients that may not be ideal for your health profile. "
            "Consider safer alternatives and consult a professional if needed."
        )

    except Exception:
        return (
            "Ingredient analysis completed, but detailed AI guidance is unavailable at the moment."
        )
