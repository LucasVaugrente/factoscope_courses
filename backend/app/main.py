from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

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
    "admin": {"password": "admin123", "name": "Administrateur"},
    "user": {"password": "user123", "name": "Utilisateur"}
}

@app.get("/")
def read_root():
    return {"message": "API Factoscope"}

@app.post("/api/login")
def login(credentials: LoginRequest):
    user = users_db.get(credentials.username)
    
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    
    # Dans un vrai projet, générer un vrai token JWT
    token = f"token_{credentials.username}"
    
    return {
        "token": token,
        "username": credentials.username,
        "name": user["name"],
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
def update_page(page_id: int, page: schemas.PageCreate, db: Session = Depends(get_db)):
    """Modifier une page existante"""
    db_page = db.query(models.Page).filter(models.Page.id == page_id).first()
    if not db_page:
        raise HTTPException(status_code=404, detail="Page non trouvée")
    
    for key, value in page.dict().items():
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

# ==================== ROUTES QCM ====================

@app.get("/api/qcm", response_model=List[schemas.QCM])
def get_qcm(db: Session = Depends(get_db)):
    """Récupérer tous les QCM"""
    return db.query(models.QCM).all()

@app.get("/api/qcm/{qcm_id}", response_model=schemas.QCM)
def get_qcm_by_id(qcm_id: int, db: Session = Depends(get_db)):
    """Récupérer un QCM par son ID"""
    qcm = db.query(models.QCM).filter(models.QCM.id == qcm_id).first()
    if not qcm:
        raise HTTPException(status_code=404, detail="QCM non trouvé")
    return qcm

@app.post("/api/qcm", response_model=schemas.QCM)
def create_qcm(qcm: schemas.QCMCreate, db: Session = Depends(get_db)):
    """Créer un nouveau QCM"""
    db_qcm = models.QCM(**qcm.dict())
    db.add(db_qcm)
    db.commit()
    db.refresh(db_qcm)
    return db_qcm

@app.put("/api/qcm/{qcm_id}", response_model=schemas.QCM)
def update_qcm(qcm_id: int, qcm: schemas.QCMCreate, db: Session = Depends(get_db)):
    """Modifier un QCM existant"""
    db_qcm = db.query(models.QCM).filter(models.QCM.id == qcm_id).first()
    if not db_qcm:
        raise HTTPException(status_code=404, detail="QCM non trouvé")
    
    for key, value in qcm.dict().items():
        setattr(db_qcm, key, value)
    
    db.commit()
    db.refresh(db_qcm)
    return db_qcm

@app.delete("/api/qcm/{qcm_id}")
def delete_qcm(qcm_id: int, db: Session = Depends(get_db)):
    """Supprimer un QCM"""
    db_qcm = db.query(models.QCM).filter(models.QCM.id == qcm_id).first()
    if not db_qcm:
        raise HTTPException(status_code=404, detail="QCM non trouvé")
    
    db.delete(db_qcm)
    db.commit()
    return {"message": "QCM supprimé avec succès"}

