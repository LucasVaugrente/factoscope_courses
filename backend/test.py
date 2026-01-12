import os
import sys
from contextlib import suppress

# Ensure we can import the app package when run from project root or container
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from app.database import SessionLocal  # type: ignore
from app import models  # type: ignore


def seed_cours():
    db = SessionLocal()
    try:
        # Create table metadata if not already created (safe/no-op if exists)
        models.Base.metadata.create_all(bind=db.get_bind())

        # Insert two demo cours if they don't already exist (by title)
        titles = {"Cours 1", "Cours 2"}
        existing_titles = {
            c.titre for c in db.query(models.Cours).filter(models.Cours.titre.in_(titles)).all()
        }
        to_create = []
        if "Cours 1" not in existing_titles:
            to_create.append(
                models.Cours(
                    titre="Cours 1",
                    description="Description cours 1",
                    contenu="Contenu cours 1",
                )
            )
        if "Cours 2" not in existing_titles:
            to_create.append(
                models.Cours(
                    titre="Cours 2",
                    description="Description cours 2",
                    contenu="Contenu cours 2",
                )
            )
        if to_create:
            db.add_all(to_create)
            db.commit()
            print(f"Inserted {len(to_create)} cours")
        else:
            print("No cours inserted (already present)")
    finally:
        with suppress(Exception):
            db.close()


if __name__ == "__main__":
    seed_cours()
