from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from .. import models
from ..database import get_db
import csv
import io
import logging
from typing import List, Dict, Any, Optional

from .. import models, schemas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/jeu-classement",
    tags=["Jeu à Classement"]
)

def _clean_cell(x: Optional[str]) -> str:
    return (x or "").strip()

def _is_header_line(row: List[str]) -> bool:
    # Format: "Titre_cours_relie_au_jeu;"
    # => souvent une seule colonne non vide
    cleaned = [c for c in map(_clean_cell, row) if c]
    return len(cleaned) == 1

def _validate_ordre_solution(ordre: str) -> bool:
    """Valide le format de l'ordre solution: ex: '2<1<4<3'"""
    if not ordre:
        return False
    parts = ordre.split('<')
    if len(parts) != 4:
        return False
    try:
        nums = [int(p.strip()) for p in parts]
        return all(1 <= n <= 4 for n in nums) and len(set(nums)) == 4
    except ValueError:
        return False

@router.post("/upload/{cours_id}", status_code=status.HTTP_201_CREATED)
async def upload_jeu_classement(
    cours_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload CSV Jeu à Classement pour un cours.
    Format attendu (après éventuelle première ligne titre) :
      question;element1;element2;element3;element4;ordre_solution;type_elements
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être au format CSV")

    # Vérifier cours
    db_cours = db.query(models.Cours).filter(models.Cours.id == cours_id).first()
    if not db_cours:
        raise HTTPException(status_code=404, detail=f"Cours avec l'ID {cours_id} non trouvé")

    try:
        content = await file.read()
        try:
            content_str = content.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Le fichier doit être encodé en UTF-8")

        reader = csv.reader(io.StringIO(content_str), delimiter=";", skipinitialspace=True)

        rows = []
        for r in reader:
            # ignorer lignes vides / commentaires
            if not r:
                continue
            if "".join(r).strip() == "":
                continue
            if _clean_cell(r[0]).startswith("#"):
                continue
            rows.append(r)

        if not rows:
            raise HTTPException(status_code=400, detail="Le fichier est vide")

        # Si première ligne = titre, on la saute
        start_idx = 1 if _is_header_line(rows[0]) else 0
        data_rows = rows[start_idx:]

        valid = []
        invalid_count = 0

        for i, row in enumerate(data_rows, start=start_idx + 1):
            cleaned = [_clean_cell(c) for c in row]
            # On veut 7 colonnes
            cleaned = cleaned[:7]

            # Vérif colonnes
            if len(cleaned) < 7:
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: moins de 7 colonnes")
                continue

            question, e1, e2, e3, e4, ordre, type_elem = cleaned

            if not question or not e1 or not e2 or not e3 or not e4 or not ordre or not type_elem:
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: champs manquants")
                continue

            # Valider le type d'éléments
            if type_elem.lower() not in ["texte", "images"]:
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: type_elements doit être 'texte' ou 'images': {type_elem}")
                continue

            # Valider l'ordre solution
            if not _validate_ordre_solution(ordre):
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: ordre_solution invalide: {ordre}")
                continue

            valid.append((question, e1, e2, e3, e4, ordre, type_elem.lower()))

        if not valid:
            raise HTTPException(status_code=400, detail="Aucune ligne valide trouvée dans le fichier")

        added = 0
        for (question, e1, e2, e3, e4, ordre, type_elem) in valid:
            q = models.JeuClassement(
                question=question,
                element1=e1,
                element2=e2,
                element3=e3,
                element4=e4,
                ordre_solution=ordre,
                type_elements=type_elem,
                id_cours=cours_id
            )
            db.add(q)
            added += 1

        db.commit()

        return {
            "status": "success",
            "message": f"{added} questions de classement ont été ajoutées avec succès",
            "details": {
                "total_rows": len(rows),
                "data_rows": len(data_rows),
                "valid_rows": len(valid),
                "questions_added": added,
                "invalid_rows": invalid_count
            }
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Erreur upload CSV Jeu à Classement", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur inattendue: {str(e)}")


@router.get("/{cours_id}")
def get_jeu_classement_par_cours(cours_id: int, db: Session = Depends(get_db)):
    qs = db.query(models.JeuClassement).filter(models.JeuClassement.id_cours == cours_id).all()
    return [
        {
            "id": q.id,
            "question": q.question,
            "element1": q.element1,
            "element2": q.element2,
            "element3": q.element3,
            "element4": q.element4,
            "ordre_solution": q.ordre_solution,
            "type_elements": q.type_elements,
            "id_cours": q.id_cours,
        }
        for q in qs
    ]

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_jeu_classement(question_id: int, db: Session = Depends(get_db)):
    q = db.query(models.JeuClassement).filter(models.JeuClassement.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question de classement introuvable")

    db.delete(q)
    db.commit()
    return None

# Schémas pour Jeu à Classement
from pydantic import BaseModel, Field
from typing import Optional

class JeuClassementUpdate(BaseModel):
    question: Optional[str] = None
    element1: Optional[str] = None
    element2: Optional[str] = None
    element3: Optional[str] = None
    element4: Optional[str] = None
    ordre_solution: Optional[str] = None
    type_elements: Optional[str] = None

@router.put("/{question_id}")
def update_jeu_classement(question_id: int, payload: JeuClassementUpdate, db: Session = Depends(get_db)):
    q = db.query(models.JeuClassement).filter(models.JeuClassement.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question de classement introuvable")

    data = payload.dict(exclude_unset=True)

    # Validation de l'ordre solution si fourni
    if "ordre_solution" in data and data["ordre_solution"] is not None:
        if not _validate_ordre_solution(data["ordre_solution"]):
            raise HTTPException(status_code=400, detail="ordre_solution invalide")

    # Validation du type_elements si fourni
    if "type_elements" in data and data["type_elements"] is not None:
        if data["type_elements"].lower() not in ["texte", "images"]:
            raise HTTPException(status_code=400, detail="type_elements doit être 'texte' ou 'images'")

    for k, v in data.items():
        setattr(q, k, v)

    db.commit()
    db.refresh(q)

    return {
        "id": q.id,
        "question": q.question,
        "element1": q.element1,
        "element2": q.element2,
        "element3": q.element3,
        "element4": q.element4,
        "ordre_solution": q.ordre_solution,
        "type_elements": q.type_elements,
        "id_cours": q.id_cours,
    }
