Exécution avec Docker 


Dans le dossier racine du projet (factoscope_courses):

docker compose up --build
Frontend: http://localhost:5173/
Backend (API): http://localhost:8000/
MySQL (depuis l’hôte): localhost:3307 (mappé vers 3306 dans le conteneur)

Arrêt:
docker compose down

Réinitialisation complète (efface les données MySQL):

docker compose down -v

2-Peupler la base de test (insérer 2 cours);

Le script de seed se trouve dans backend/test.py. Il est idempotent (pas de doublons si déjà présents).

Démarrer en arrière-plan:

docker compose up -d



Exécuter le seed:

docker compose exec backend python /app/test.py


