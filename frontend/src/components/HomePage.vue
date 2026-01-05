<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-content">
        <h1>Factoscope</h1>
        <div class="user-info">
          <span>Bienvenue, {{ userName }}</span>
          <button @click="handleLogout" class="logout-btn">Déconnexion</button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <div class="welcome-section">
        <h2>🎉 Connexion réussie !</h2>
        <p>Vous êtes maintenant connecté à votre espace Factoscope.</p>
      </div>

      <div class="dashboard-grid">
        <div class="card">
          <div class="card-icon">📝</div>
          <h3>Créer</h3>
          <p>Ajouter de nouveaux éléments</p>
        </div>

        <div class="card">
          <div class="card-icon">📋</div>
          <h3>Lire</h3>
          <p>Consulter vos données</p>
        </div>

        <div class="card">
          <div class="card-icon">✏️</div>
          <h3>Modifier</h3>
          <p>Mettre à jour les informations</p>
        </div>

        <div class="card">
          <div class="card-icon">🗑️</div>
          <h3>Supprimer</h3>
          <p>Effacer des éléments</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userName = ref('')

onMounted(() => {
  const token = localStorage.getItem('token')
  const storedName = localStorage.getItem('userName')
  
  if (!token) {
    router.push('/login')
  } else {
    userName.value = storedName || 'Utilisateur'
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  router.push('/login')
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar h1 {
  margin: 0;
  font-size: 1.8rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-section h2 {
  font-size: 2.5rem;
  color: #333;
  margin-bottom: 10px;
}

.welcome-section p {
  color: #666;
  font-size: 1.2rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.card {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.card h3 {
  color: #333;
  margin-bottom: 10px;
  font-size: 1.5rem;
}

.card p {
  color: #666;
  font-size: 0.95rem;
}
</style>
