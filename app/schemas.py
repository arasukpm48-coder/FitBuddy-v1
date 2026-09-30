"""
Pydantic schemas: they check (validate) the data users send us.
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

GOALS = ["Weight Loss", "Muscle Gain", "General Fitness", "Strength", "Wellness"]
INTENSITIES = ["Low", "Medium", "High"]


class UserInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Letters, numbers, - and _ only (3-30 characters)",
    )
    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=350, description="Weight in kg")
    goal: Literal["Weight Loss", "Muscle Gain", "General Fitness", "Strength", "Wellness"]
    intensity: Literal["Low", "Medium", "High"]


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(min_length=1, max_length=30)
    feedback: str = Field(min_length=3, max_length=500)
