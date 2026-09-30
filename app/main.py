"""
FitBuddy - application entry point.

This file creates the FastAPI application, connects the static files
(CSS), connects the routes from routes.py, and creates the database
tables when the server starts.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# Folder that contains app/, templates/, static/ ...
BASE_DIR = Path(__file__).resolve().parent.parent

# Load the secret values (GOOGLE_API_KEY) from the .env file.
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from app.database import init_db  # noqa: E402
from app.routes import router  # noqa: E402


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Runs once when the server starts: create fitbuddy.db and its tables.
    init_db()
    yield


app = FastAPI(
    title="FitBuddy – AI Fitness Plan Generator",
    description=(
        "FitBuddy generates personalized 7-day workout plans using Google Gemini, "
        "updates them from user feedback, and stores everything in SQLite."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Serve files from the /static folder at the URL /static/...
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Add all routes defined in routes.py
app.include_router(router)
