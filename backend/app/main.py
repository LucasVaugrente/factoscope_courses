from fastapi import FastAPI, HTTPException, Depends
from fastapi import UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io

# Import des routeurs
from .routes import text_a_trou, qcm, jeu_classement

from . import models, schemas
from .database import engine, get_db

# Créer les tables si elles n'existent pas déjà (ne modifie pas les données existantes)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle pour les données de connexion
class LoginRequest(BaseModel):
    username: str
    password: str

# Données temporaires (à remplacer par une vraie base de données)
users_db = {
    "password": "admin123", "name": "Administrateur"
}

@app.get("/")
def read_root():
    return {"message": "API Factoscope"}

@app.post("/api/login")
def login(credentials: LoginRequest):
    if credentials.username != users_db["name"] or credentials.password != users_db["password"]:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    # Dans un vrai projet, générer un vrai token JWT
    token = f"token_{credentials.username}"
    
    return {
        "token": token,
        "username": credentials.username,
        "name": credentials.username,
        "message": "Connexion réussie"
    }

# ==================== ROUTES COURS ====================

@app.get("/api/cours", response_model=List[schemas.Cours])
def get_cours(db: Session = Depends(get_db)):
    """Récupérer tous les cours"""
    return db.query(models.Cours).all()

@app.get("/api/cours/{cours_id}", response_model=schemas.Cours)
def get_cours_by_id(cours_id: int, db: Session = Depends(get_db)):
    """Récupérer un cours par son ID"""
    cours = db.query(models.Cours).filter(models.Cours.id == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    return cours

@app.post("/api/cours", response_model=schemas.Cours)
def create_cours(cours: schemas.CoursCreate, db: Session = Depends(get_db)):
    """Créer un nouveau cours"""
    db_cours = models.Cours(**cours.dict())
    db.add(db_cours)
    db.commit()
    db.refresh(db_cours)
    return db_cours

from fastapi import UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
import csv, io

@app.post("/api/cours/upload", response_model=schemas.Cours)
async def upload_cours_csv(
    file: UploadFile = File(...),
    titre: str = Form(None),
    description: str = Form(None),
    thematique: str = Form(None),
    db: Session = Depends(get_db),
):
    def clean(x):
        return (x or "").strip()

    raw = await file.read()

    for encoding in ['utf-8-sig', 'utf-8', 'windows-1252', 'latin-1']:
        try:
            text = raw.decode(encoding)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        raise HTTPException(400, "Impossible de décoder le fichier CSV. Sauvegardez-le en UTF-8 et réessayez.")

    reader = csv.reader(io.StringIO(text), delimiter=';')
    rows = [row for row in reader if any(clean(c) for c in row)]

    if not rows:
        raise HTTPException(400, "CSV vide")

    is_form_mode = any([clean(titre), clean(description), clean(thematique)])

    first = [clean(c) for c in rows[0]]
    csv_has_header = len(first) >= 3 and first[0] and first[2]
    
    if is_form_mode:
        course_title = clean(titre)
        course_description = clean(description)
        module_name = clean(thematique)
        module_description = None 
        data_rows = rows[1:]
    else:
        if not csv_has_header:
            raise HTTPException(
                400,
                "CSV invalide : l'en-tête doit contenir au moins 3 colonnes (titre; description; module)"
            )
        course_title = first[0]
        course_description = first[1] if len(first) >= 2 else ""
        module_name = first[2]
        module_description = first[3] if len(first) >= 4 else None
        data_rows = rows[1:]

    # Résolution ou création du module
    id_module = None
    if module_name:
        db_module = db.query(models.Module).filter(
            models.Module.titre == module_name
        ).first()

        if db_module:
            id_module = db_module.id

        elif module_description:
            db_module = models.Module(
                titre=module_name,
                description=module_description,
            )
            db.add(db_module)
            db.commit()
            db.refresh(db_module)
            id_module = db_module.id

        else:
            raise HTTPException(
                400,
                f"Le module \"{module_name}\" n'existe pas en base de données. "
                f"Pour le créer automatiquement, ajoutez sa description en 4ème colonne de l'en-tête de votre CSV : "
                f"titre; description_cours; {module_name}; description_du_module"
            )

    db_cours = models.Cours(
        titre=course_title,
        description=course_description,
        contenu=course_description,
        id_module=id_module
    )
    db.add(db_cours)
    db.commit()
    db.refresh(db_cours)

    created_pages = 0

    for row in data_rows:
        row = [clean(c) for c in row]
        description = row[0] if len(row) >= 1 else ""
        content = row[1] if len(row) >= 2 else ""
        medias = row[2] if len(row) >= 3 else ""

        if not description and not content and not medias:
            continue

        page = models.Page(
            description=description,
            content=content,
            medias=medias,
            est_vue=0,
            id_cours=db_cours.id
        )
        db.add(page)
        created_pages += 1

    if created_pages == 0:
        db.rollback()
        raise HTTPException(400, "Aucune page valide trouvée dans le CSV")

    db.commit()
    return db_cours
@app.put("/api/cours/{cours_id}", response_model=schemas.Cours)
def update_cours(cours_id: int, cours: schemas.CoursCreate, db: Session = Depends(get_db)):
    """Modifier un cours existant"""
    db_cours = db.query(models.Cours).filter(models.Cours.id == cours_id).first()
    if not db_cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    
    for key, value in cours.dict().items():
        setattr(db_cours, key, value)
    
    db.commit()
    db.refresh(db_cours)
    return db_cours

@app.delete("/api/cours/{cours_id}")
def delete_cours(cours_id: int, db: Session = Depends(get_db)):
    """Supprimer un cours"""
    db_cours = db.query(models.Cours).filter(models.Cours.id == cours_id).first()
    if not db_cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    
    db.delete(db_cours)
    db.commit()
    return {"message": "Cours supprimé avec succès"}

# ==================== ROUTES MODULE ====================

@app.get("/api/modules", response_model=List[schemas.Module])
def get_modules(db: Session = Depends(get_db)):
    """Récupérer tous les modules"""
    return db.query(models.Module).all()

@app.get("/api/modules/{module_id}", response_model=schemas.Module)
def get_module_by_id(module_id: int, db: Session = Depends(get_db)):
    """Récupérer un module par son ID"""
    module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module non trouvé")
    return module

@app.post("/api/modules", response_model=schemas.Module)
def create_module(module: schemas.ModuleCreate, db: Session = Depends(get_db)):
    """Créer un nouveau module"""
    db_module = models.Module(**module.dict())
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

@app.put("/api/modules/{module_id}", response_model=schemas.Module)
def update_module(module_id: int, module: schemas.ModuleCreate, db: Session = Depends(get_db)):
    """Modifier un module existant"""
    db_module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module non trouvé")
    
    for key, value in module.dict().items():
        setattr(db_module, key, value)
    
    db.commit()
    db.refresh(db_module)
    return db_module

@app.delete("/api/modules/{module_id}")
def delete_module(module_id: int, db: Session = Depends(get_db)):
    """Supprimer un module"""
    db_module = db.query(models.Module).filter(models.Module.id == module_id).first()
    if not db_module:
        raise HTTPException(status_code=404, detail="Module non trouvé")
    
    db.delete(db_module)
    db.commit()
    return {"message": "Module supprimé avec succès"}

# ==================== ROUTES PAGE ====================

@app.get("/api/pages", response_model=List[schemas.Page])
def get_pages(db: Session = Depends(get_db)):
    """Récupérer toutes les pages"""
    return db.query(models.Page).all()

@app.get("/api/pages/{page_id}", response_model=schemas.Page)
def get_page_by_id(page_id: int, db: Session = Depends(get_db)):
    """Récupérer une page par son ID"""
    page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    return page

@app.post("/api/pages", response_model=schemas.Page)
def create_page(page: schemas.PageCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle page"""
    db_page = models.Page(**page.dict())
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

@app.put("/api/pages/{page_id}", response_model=schemas.Page)
def update_page(page_id: int, page: schemas.PageUpdate, db: Session = Depends(get_db)):
    """Modifier une page existante"""
    db_page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not db_page:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    
    update_data = page.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_page, key, value)
    
    db.commit()
    db.refresh(db_page)
    return db_page

@app.delete("/api/pages/{page_id}")
def delete_page(page_id: int, db: Session = Depends(get_db)):
    """Supprimer une page"""
    db_page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not db_page:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    
    db.delete(db_page)
    db.commit()
    return {"message": "Page supprimée avec succès"}

# Inclure les routeurs
app.include_router(text_a_trou.router)
app.include_router(qcm.router)
app.include_router(jeu_classement.router)

