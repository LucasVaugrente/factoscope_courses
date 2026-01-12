# Backend FastAPI

## Installation

1. Créer un environnement virtuel :
   
```bash
python -m venv venv
```
2. Activer l'environnement :
```bash
Windows : venv\Scripts\activate
macOS/Linux : source venv/bin/activate
```
3. Installer les dépendances :
```bash
pip install -r requirements.txt
```
4. Lancer le serveur :
```bash
uvicorn app.main:app --reload
```

Le serveur sera accessible à http://127.0.0.1:8000
