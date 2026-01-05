from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
