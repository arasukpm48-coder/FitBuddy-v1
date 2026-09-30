"""
Gemini "Flash" generator: fast model used for the short nutrition/recovery tip.
"""
import os

from app.gemini_generator import call_gemini

DEFAULT_FLASH_MODEL = "gemini-flash-latest"


def get_flash_model() -> str:
    return os.getenv("GEMINI_FLASH_MODEL", "").strip() or DEFAULT_FLASH_MODEL


def generate_nutrition_tip_with_flash(
    goal: str, intensity: str, age: int | None = None, weight: float | None = None
) -> tuple[bool, str]:
    """
    Generate a short nutrition / recovery tip.
    Returns (success, tip_text_or_error_message).
    """
    profile = f"Goal: {goal}. Workout intensity: {intensity}."
    if age:
        profile += f" Age: {age}."
    if weight:
        profile += f" Weight: {weight} kg."

    prompt = f"""You are a friendly, safety-focused fitness and wellness coach.
{profile}

Write ONE concise nutrition or recovery tip (2 to 3 sentences) that fits this goal.
Rules: plain text only (no markdown, no lists), general wellness advice only,
no medical claims, no extreme diets, no supplement or medicine recommendations."""

    return call_gemini(prompt, get_flash_model(), temperature=0.6)
