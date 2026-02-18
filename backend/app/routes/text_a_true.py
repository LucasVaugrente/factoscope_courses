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
    prefix="/api/text-a-true",
    tags=["Text à True"]
)

def _clean_cell(x: Optional[str]) -> str:
    return (x or "").strip()

def _is_header_line(row: List[str]) -> bool:
    # Ta première ligne exemple: "Titre_cours_relie_au_jeu;"
    # => souvent une seule colonne non vide
    cleaned = [c for c in map(_clean_cell, row) if c]
    return len(cleaned) == 1

@router.post("/upload/{cours_id}", status_code=status.HTTP_201_CREATED)
async def upload_text_a_true(
    cours_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload CSV questions pour un cours.
    Format attendu (après éventuelle première ligne titre) :
      texte;reponse1;reponse2;reponse3;reponse4;numero_reponse_correcte(1..4)
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
            # On garde les colonnes même si certaines sont vides (mais on veut 6 colonnes)
            # Certains CSV ont un ; final -> ça crée une colonne vide en plus, donc on tronque à 6.
            cleaned = cleaned[:6]

            # Vérif colonnes
            if len(cleaned) < 6:
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: moins de 6 colonnes")
                continue

            texte, r1, r2, r3, r4, correct = cleaned

            if not texte or not r1 or not r2 or not r3 or not r4 or not correct:
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: champs manquants")
                continue

            try:
                correct_int = int(correct)
            except ValueError:
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: numero_reponse_correcte non numérique: {correct}")
                continue

            if correct_int not in (1, 2, 3, 4):
                invalid_count += 1
                logger.warning(f"Ligne {i} invalide: numero_reponse_correcte hors 1..4: {correct_int}")
                continue

            valid.append((texte, r1, r2, r3, r4, correct_int))

        if not valid:
            raise HTTPException(status_code=400, detail="Aucune ligne valide trouvée dans le fichier")

        added = 0
        for (texte, r1, r2, r3, r4, correct_int) in valid:
            q = models.TextATrue(
                texte=texte,
                reponse1=r1,
                reponse2=r2,
                reponse3=r3,
                reponse4=r4,
                numero_reponse_correcte=correct_int,
                explication=None,
                id_cours=cours_id
            )
            db.add(q)
            added += 1

        db.commit()

        return {
            "status": "success",
            "message": f"{added} questions ont été ajoutées avec succès",
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
        logger.error("Erreur upload CSV", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur inattendue: {str(e)}")


@router.get("/{cours_id}")
def get_text_a_true_par_cours(cours_id: int, db: Session = Depends(get_db)):
    qs = db.query(models.TextATrue).filter(models.TextATrue.id_cours == cours_id).all()
    return [
        {
            "id": q.id,
            "texte": q.texte,
            "reponse1": q.reponse1,
            "reponse2": q.reponse2,
            "reponse3": q.reponse3,
            "reponse4": q.reponse4,
            "numero_reponse_correcte": q.numero_reponse_correcte,
            "explication": q.explication,
            "id_cours": q.id_cours,
        }
        for q in qs
    ]

@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_text_a_true(question_id: int, db: Session = Depends(get_db)):
    q = db.query(models.TextATrue).filter(models.TextATrue.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question introuvable")

    db.delete(q)
    db.commit()
    return None
# Schémas pour Text à True
from pydantic import BaseModel, Field
from typing import Optional

class TextATrueUpdate(BaseModel):
    texte: Optional[str] = None
    reponse1: Optional[str] = None
    reponse2: Optional[str] = None
    reponse3: Optional[str] = None
    reponse4: Optional[str] = None
    numero_reponse_correcte: Optional[int] = Field(default=None, ge=1, le=4)
    explication: Optional[str] = None
@router.put("/{question_id}")
def update_text_a_true(question_id: int, payload: TextATrueUpdate, db: Session = Depends(get_db)):
    q = db.query(models.TextATrue).filter(models.TextATrue.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question introuvable")

    data = payload.dict(exclude_unset=True)

    # petite validation
    if "numero_reponse_correcte" in data and data["numero_reponse_correcte"] is not None:
        n = data["numero_reponse_correcte"]
        if n < 1 or n > 4:
            raise HTTPException(status_code=400, detail="numero_reponse_correcte doit être entre 1 et 4")

    for k, v in data.items():
        setattr(q, k, v)

    db.commit()
    db.refresh(q)

    return {
        "id": q.id,
        "texte": q.texte,
        "reponse1": q.reponse1,
        "reponse2": q.reponse2,
        "reponse3": q.reponse3,
        "reponse4": q.reponse4,
        "numero_reponse_correcte": q.numero_reponse_correcte,
        "explication": q.explication,
        "id_cours": q.id_cours,
    }
