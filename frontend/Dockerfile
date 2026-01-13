# Utiliser l'image officielle Node.js version 20
FROM node:20

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier package.json et installer les dépendances
COPY package.json /app/
COPY package-lock.json /app/
RUN npm install

# Copier le reste du projet
COPY . /app/

# Construire l'application pour la production
RUN npm run build

# Exposer le port sur lequel l'application sera disponible
EXPOSE 8080

# Lancer l'application en mode développement
CMD ["npm", "run", "dev"]
