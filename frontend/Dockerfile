FROM node:20
WORKDIR /app

# Copier d'abord les fichiers de dépendances
COPY package*.json ./

# Installer les dépendances avec des versions spécifiques
RUN npm install \
    pinia@2.1.7 \
    postcss-import@15.1.0 \
    postcss-nested@6.0.1 \
    tailwindcss@3.3.0 \
    --legacy-peer-deps

# Installer les autres dépendances
RUN npm install --legacy-peer-deps

# Copier le reste des fichiers
COPY . .

# Construire l'application
RUN npm run build

# Exposer le port de développement
EXPOSE 5173

# Démarrer l'application en mode développement
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]