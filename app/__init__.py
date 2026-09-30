# This file makes "app" a Python package.
#
# It also exposes the FastAPI object as "app", so BOTH commands work:
#     uvicorn app.main:app --reload
#     uvicorn app:app --reload
from app.main import app  # noqa: F401
