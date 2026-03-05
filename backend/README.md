## Project Setup (local)

1. Créez et activez un environnement virtuel (optionnel mais recommandé) :

```sh
python -m venv .venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Installez les dépendances :

```sh
pip install -r requirements.txt
```

3. Copier le fichier `.env.example` (à la racine du projet) :

```env
cp .env.example .env
```

4. Lancer l'API en local (rechargement automatique) :

```sh
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

L'API sera disponible sur `http://localhost:8000/`.

## Exécution avec Docker

Dans le dossier racine du projet (`factoscope_courses`) utilisez `docker compose` pour construire et démarrer les services :

```sh
docker compose up --build
```

- Frontend: http://localhost:5173/
- Backend (API): http://localhost:8000/
- MySQL (depuis l’hôte): localhost:3307 (mappé vers 3306 dans le conteneur)

Pour lancer en arrière-plan :

```sh
docker compose up -d --build
```

Arrêter les services :

```sh
docker compose down
```

Réinitialisation complète (supprime aussi les volumes de données MySQL) :

```sh
docker compose down -v
```

## Peupler la base de test

Le script de seed se trouve dans `backend/test.py`. Il est idempotent (n'insère pas de doublons si les données existent déjà).

Exécuter le seed depuis le conteneur backend :

```sh
docker compose exec backend python /app/test.py
```

## Notes utiles

- Le `Dockerfile` du backend démarre l'application avec `uvicorn` sur le port `8000`.
- Assurez-vous que le `.env` contient `DATABASE_URL` correct et que le service MySQL du compose est démarré.
