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
        # Ensure tables exist
        models.Base.metadata.create_all(bind=db.get_bind())

        # ── CLEAN SLATE ──────────────────────────────────────────────────────────
        print("Suppression des données existantes…")
        db.query(models.QCM).delete()
        db.query(models.Page).delete()
        db.query(models.Cours).delete()
        db.query(models.Module).delete()
        db.commit()
        print("Tables vidées.")

        print("\n✅ Seed terminé avec succès.")

    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors du seed : {e}")
        raise
    finally:
        with suppress(Exception):
            db.close()


if __name__ == "__main__":
    seed_cours()