from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import pymysql
pymysql.install_as_MySQLdb() 
import time
from sqlalchemy.exc import OperationalError
# Charger les variables d'environnement
load_dotenv()

# URL de connexion à la base de données
DATABASE_URL = os.getenv("DATABASE_URL")

# Créer le moteur SQLAlchemy avec retry pour attendre MySQL
engine = None
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL n'est pas défini dans les variables d'environnement")

for attempt in range(30):
    try:
        engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
        # Test d'une connexion immédiate pour valider la disponibilité
        with engine.connect() as conn:
            pass
        break
    except Exception as e:
        time.sleep(2)
else:
    # Si aucune connexion n'a réussi après les tentatives, lever l'erreur
    raise OperationalError(f"Impossible de se connecter à la base de données après plusieurs tentatives: {DATABASE_URL}", None, None)

# Créer une session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Fonction pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
