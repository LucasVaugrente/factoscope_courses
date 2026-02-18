# Factoscope Courses

Application web pour gérer les cours utilisée par l'application Factoscope.

## Prérequis

- **Docker** et/ou **Docker Compose** installés sur votre machine.
- Python 3.9+ si vous souhaitez exécuter le backend localement sans Docker.

## Configuration minimale

Copier le fichier `.env.example` (à la racine du projet) :

```env
cp .env.example .env
```

Cette URL indique à l'API de se connecter au service MySQL défini dans le `docker-compose.yml`. Le port `3307` est mappé vers `3306` dans le conteneur.

## Exécution avec Docker

Dans le dossier racine du projet (`factoscope_courses`) :

### Démarrer (build + run)

```sh
docker compose up --build
```

Les services exposés par défaut :

- Frontend : http://localhost:5173/
- Backend (API) : http://localhost:8000/
- MySQL (depuis l’hôte) : localhost:3307

### Démarrer en arrière-plan

```sh
docker compose up -d --build
```

### Arrêter

```sh
docker compose down
```

### Réinitialisation complète (efface les données MySQL)

```sh
docker compose down -v
```

## Peupler la base de test

Le script de seed se trouve dans `backend/test.py`. Il insère quelques cours de test et est idempotent.

Pour l'exécuter une fois les services démarrés :

```sh
docker compose exec backend python /app/test.py
```