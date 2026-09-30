"""
Database setup (SQLite + SQLAlchemy).

The database file "fitbuddy.db" is created automatically in the
FitBuddy folder the first time the application starts.
"""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{(BASE_DIR / 'fitbuddy.db').as_posix()}"

# check_same_thread=False is needed for SQLite when used with FastAPI.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# All database models inherit from this Base class.
Base = declarative_base()


def init_db() -> None:
    """Create all tables if they do not exist yet."""
    # Importing models registers the tables with Base.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency: gives each request its own database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
