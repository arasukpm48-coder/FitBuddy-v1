"""
Gemini workout generator (main "Pro" model).

Also contains the shared helper call_gemini() used by the other
Gemini files, so the API-key and error handling is written only once.

Uses the CURRENT official SDK:  pip install google-genai
    from google import genai
    client = genai.Client(api_key=...)
    client.models.generate_content(model=..., contents=...)
"""
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger("fitbuddy")

# "-latest" aliases always point to Google's newest model of that type.
# You can override them in .env with GEMINI_PRO_MODEL / GEMINI_FLASH_MODEL.
DEFAULT_PRO_MODEL = "gemini-pro-latest"


def get_pro_model() -> str:
    return os.getenv("GEMINI_PRO_MODEL", "").strip() or DEFAULT_PRO_MODEL


def clean_text(text: str) -> str:
    """Remove markdown symbols so the text looks clean in HTML."""
    text = text.replace("**", "").replace("__", "").replace("`", "")
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*)[*•]\s+", r"\1- ", text, flags=re.MULTILINE)
    return text.strip()


def looks_like_plan(text: str) -> bool:
    """True if the text contains Day 1 ... Day 7 headings."""
    return all(
        re.search(rf"(?im)^\W*day\s*{n}\b", text) for n in range(1, 8)
    )


def _friendly_error(exc: Exception) -> str:
    message = str(exc).lower()
    if "429" in message or "quota" in message or "resource_exhausted" in message:
        return (
            "The Gemini API limit was reached. Please wait a minute and try again. "
            "(Tip: a free API key has usage limits.)"
        )
    if "api key" in message or "api_key" in message or "permission" in message or "401" in message or "403" in message:
        return "The Gemini API key was rejected. Please check GOOGLE_API_KEY in your .env file."
    if "404" in message or "not found" in message:
        return (
            "The Gemini model name was not found. Check the model names on "
            "https://ai.google.dev/gemini-api/docs/models and set GEMINI_PRO_MODEL / "
            "GEMINI_FLASH_MODEL in your .env file."
        )
    if "connect" in message or "timeout" in message or "network" in message:
        return "Could not reach the Gemini service. Please check your internet connection."
    return "The AI service had a problem. Please try again in a moment."


def call_gemini(prompt: str, model: str, temperature: float = 0.7) -> tuple[bool, str]:
    """
    Send a prompt to Gemini.
    Returns (True, text) on success or (False, friendly_error_message) on failure.
    It never raises an exception, so the website never crashes.
    """
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key or api_key == "your_api_key_here":
        return False, (
            "Gemini API key is missing. Create a .env file and add: "
            "GOOGLE_API_KEY=your_real_key"
        )

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=temperature),
        )
        text = response.text
    except Exception as exc:  # any API/network problem ends up here
        logger.exception("Gemini request failed")
        print(f"[FitBuddy] Gemini error: {exc}")
        return False, _friendly_error(exc)

    if not text or not text.strip():
        return False, "Gemini returned an empty answer. Please try again."

    return True, clean_text(text)


PLAN_FORMAT = """
FORMAT RULES (very important):
- Write plain text only. Do NOT use markdown symbols such as **, #, or backticks.
- Write exactly 7 sections, one per day, starting with a line like:
  DAY 1: <workout focus>
  ...
  DAY 7: <workout focus>
- Inside every day, use exactly these lines:
  Warm-up: <short warm-up, 5-10 minutes>
  Exercises:
  - <Exercise name> | <number of sets> sets | <reps or duration> | Rest: <rest time>
  - (3 to 6 exercises per training day)
  Cooldown/Recovery: <stretching or recovery advice>
- For a rest day, still write "DAY N: Rest / Active Recovery" and suggest light activity
  (walking, stretching, mobility) with sets/reps/duration where relevant.
- Do NOT write any introduction or conclusion outside the 7 days.
"""


def generate_workout_gemini(
    name: str, age: int, weight: float, goal: str, intensity: str
) -> tuple[bool, str]:
    """
    Generate a personalized 7-day workout plan.
    Returns (success, plan_text_or_error_message).
    """
    prompt = f"""You are an experienced, safety-focused certified fitness coach.
Create a personalized 7-day workout plan.

User profile:
- Name: {name}
- Age: {age}
- Weight: {weight} kg
- Fitness goal: {goal}
- Workout intensity: {intensity}

Requirements:
- Safe, realistic and suitable for the age, goal and intensity.
- Include at least 1-2 rest or active-recovery days.
- Match the intensity: Low = gentle and beginner friendly, Medium = moderate,
  High = challenging but still safe.
- Do not make medical claims. Do not recommend extreme or dangerous training.
{PLAN_FORMAT}
"""
    ok, result = call_gemini(prompt, get_pro_model(), temperature=0.7)
    if not ok:
        return False, result
    if not looks_like_plan(result):
        return False, "Gemini returned an unexpected format. Please click the button again."
    return True, result
