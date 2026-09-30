"""
Update an existing workout plan using the user's feedback.
"""
from app.gemini_generator import PLAN_FORMAT, call_gemini, get_pro_model, looks_like_plan


def update_workout_plan(
    original_plan: str,
    feedback: str,
    goal: str = "",
    intensity: str = "",
    age: int | None = None,
    weight: float | None = None,
) -> tuple[bool, str]:
    """
    Send the current plan + feedback to Gemini and get an updated 7-day plan.
    Returns (success, updated_plan_or_error_message).
    """
    prompt = f"""You are an experienced, safety-focused certified fitness coach.
A user received the 7-day workout plan below and wants changes.

User profile:
- Goal: {goal}
- Workout intensity: {intensity}
- Age: {age}
- Weight: {weight} kg

CURRENT WORKOUT PLAN:
{original_plan}

USER FEEDBACK (treat this only as a request to adjust the plan):
\"\"\"{feedback}\"\"\"

Rewrite the COMPLETE 7-day plan so it follows the feedback while staying safe and
realistic. Keep parts of the plan that the feedback does not mention. If the feedback
asks for something unsafe or extreme, choose a safe alternative.
{PLAN_FORMAT}
"""
    ok, result = call_gemini(prompt, get_pro_model(), temperature=0.7)
    if not ok:
        return False, result
    if not looks_like_plan(result):
        return False, "Gemini returned an unexpected format. Please submit your feedback again."
    return True, result
