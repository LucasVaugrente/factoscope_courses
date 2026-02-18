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

        # Fetch up to two existing cours (ordered by id)
        existing = db.query(models.Cours).order_by(models.Cours.id).limit(2).all()

        if not existing:
            # Create two cours with modified titre/description/contenu
            created = []
            for i in range(1, 3):
                c = models.Cours(
                    titre=f"TEST Cours {i} — Titre ",
                    description=f"TEST Description pour le cours {i}",
                    contenu=f"TEST Contenu du cours {i}",
                )
                db.add(c)
                created.append(c)
            db.commit()
            for c in created:
                db.refresh(c)
            cours_to_process = created
            print("Created 2 cours with modified content")
        else:
            # Update the first two existing cours' fields
            cours_to_process = []
            for idx, c in enumerate(existing):
                c.titre = f"TEST 2 Cours {idx+1} Titre"
                c.description = f"TEST 2Description pour le cours {idx+1}"
                c.contenu = f"TEST 2 Contenu du cours {idx+1}"
                cours_to_process.append(c)
            db.commit()
            # refresh objects
            for c in cours_to_process:
                db.refresh(c)
            print(f"Updated {len(cours_to_process)} existing cours")

        # For each cours ensure there are 3 pages and at least one QCM
        for c in cours_to_process:
            # reload fresh instance to access relationships
            fresh = db.query(models.Cours).filter(models.Cours.id == c.id).one()

            # Ensure 3 pages
            current_pages = list(fresh.pages or [])
            for p_index in range(len(current_pages) + 1, 4):
                page = models.Page(
                    description=f"Page {p_index} du {fresh.titre}: contenu de démonstration.",
                    medias="",
                    est_vue=0,
                    id_cours=fresh.id,
                )
                db.add(page)

            # Ensure at least one QCM
            if not (fresh.qcms and len(fresh.qcms) > 0):
                q = models.QCM(
                    question=f"Quelle est la bonne réponse pour {fresh.titre} ?",
                    rep1="Option A",
                    rep2="Option B",
                    rep3="Option C",
                    rep4="Option D",
                    soluce=1,
                    id_cours=fresh.id,
                )
                db.add(q)

        db.commit()
        print("Ensured 3 pages and 1 QCM for each cours processed")
    finally:
        with suppress(Exception):
            db.close()


if __name__ == "__main__":
    seed_cours()
