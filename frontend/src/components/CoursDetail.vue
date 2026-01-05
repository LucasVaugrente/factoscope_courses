<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-content">
        <h1>Factoscope</h1>
        <div class="user-info">
          <span>{{ userName }}</span>
          <button @click="handleLogout" class="logout-btn">Déconnexion</button>
        </div>
      </div>
    </nav>

    <main class="main-content">
      <div class="header-row">
        <div>
          <p class="eyebrow">Cours</p>
          <h2>{{ cours?.titre || 'Chargement...' }}</h2>
          <p class="subtitle">{{ cours?.description }}</p>
        </div>
        <div class="actions">
          <button class="ghost" @click="goBack">← Retour</button>
          <button class="ghost" @click="fetchPages" :disabled="isLoading">Actualiser</button>
        </div>
      </div>

      <div v-if="error" class="error-bar">{{ error }}</div>

      <div v-if="isLoading" class="dashboard-grid">
        <div v-for="n in 3" :key="n" class="card skeleton">
          <div class="skeleton-line title"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
      </div>

      <div v-else class="dashboard-grid">
        <div v-for="page in pages" :key="page.id" class="card">
          <template v-if="editingPageId === page.id">
            <textarea v-model="editingForm.description" class="textarea" rows="4" placeholder="Description"></textarea>
            <input v-model="editingForm.medias" class="input" placeholder="Médias (URLs, séparées par virgule)" />
            <div class="card-actions">
              <button class="ghost" @click="cancelEdit">Annuler</button>
              <button class="danger-outline" @click="deletePage(page.id)">Supprimer</button>
              <button class="primary" @click="savePage(page.id)" :disabled="isSaving">{{ isSaving ? 'Enregistrement...' : 'Enregistrer' }}</button>
            </div>
          </template>
          <template v-else>
            <div class="card-icon">📄</div>
            <p class="description">{{ page.description || 'Aucune description' }}</p>
            <p class="meta" v-if="page.medias">Médias : {{ page.medias }}</p>
            <div class="card-actions">
              <button class="primary" @click="startEdit(page)">Éditer</button>
            </div>
          </template>
        </div>

        <!-- Bloc pour ajouter une page -->
        <div class="card add-card" @click="startAddPage">
          <div class="add-icon">➕</div>
          <h3>Ajouter une page</h3>
        </div>
      </div>

      <!-- Modal d'ajout de page -->
      <div v-if="showAddModal" class="modal-overlay" @click="closeAddModal">
        <div class="modal-card" @click.stop>
          <h3>Nouvelle page</h3>
          <textarea v-model="newPageForm.description" class="textarea" rows="4" placeholder="Description"></textarea>
          <input v-model="newPageForm.medias" class="input" placeholder="Médias (URLs, séparées par virgule)" />
          <div class="modal-actions">
            <button class="ghost" @click="closeAddModal">Annuler</button>
            <button class="primary" @click="createPage" :disabled="isSaving">{{ isSaving ? 'Création...' : 'Créer' }}</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const userName = ref('')
const cours = ref(null)
const pages = ref([])
const isLoading = ref(false)
const isSaving = ref(false)
const error = ref('')
const editingPageId = ref(null)
const editingForm = ref({ description: '', medias: '' })
const showAddModal = ref(false)
const newPageForm = ref({ description: '', medias: '' })

const apiBase = 'http://localhost:8000'
const coursId = route.params.id

const fetchCours = async () => {
  try {
    const res = await fetch(`${apiBase}/api/cours/${coursId}`)
    if (!res.ok) throw new Error('Impossible de récupérer le cours')
    cours.value = await res.json()
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement du cours'
  }
}

const fetchPages = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiBase}/api/pages`)
    if (!res.ok) throw new Error('Impossible de récupérer les pages')
    const allPages = await res.json()
    pages.value = allPages.filter(p => p.id_cours === parseInt(coursId))
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement des pages'
  } finally {
    isLoading.value = false
  }
}

const startEdit = (page) => {
  editingPageId.value = page.id
  editingForm.value = {
    description: page.description || '',
    medias: page.medias || '',
  }
}

const cancelEdit = () => {
  editingPageId.value = null
}

const savePage = async (pageId) => {
  isSaving.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiBase}/api/pages/${pageId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...editingForm.value,
        id_cours: parseInt(coursId),
      }),
    })
    if (!res.ok) throw new Error('Échec de la mise à jour de la page')
    const updated = await res.json()
    pages.value = pages.value.map((p) => (p.id === pageId ? updated : p))
    editingPageId.value = null
  } catch (err) {
    error.value = err.message || 'Erreur lors de la sauvegarde'
  } finally {
    isSaving.value = false
  }
}

const deletePage = async (pageId) => {
  if (!confirm('Êtes-vous sûr de vouloir supprimer cette page ?')) return
  
  error.value = ''
  try {
    const res = await fetch(`${apiBase}/api/pages/${pageId}`, {
      method: 'DELETE',
    })
    if (!res.ok) throw new Error('Échec de la suppression')
    pages.value = pages.value.filter((p) => p.id !== pageId)
    editingPageId.value = null
  } catch (err) {
    error.value = err.message || 'Erreur lors de la suppression'
  }
}

const startAddPage = () => {
  showAddModal.value = true
  newPageForm.value = { description: '', medias: '' }
}

const closeAddModal = () => {
  showAddModal.value = false
}

const createPage = async () => {
  isSaving.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiBase}/api/pages`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...newPageForm.value,
        id_cours: parseInt(coursId),
      }),
    })
    if (!res.ok) throw new Error('Échec de la création de la page')
    const created = await res.json()
    pages.value.push(created)
    showAddModal.value = false
  } catch (err) {
    error.value = err.message || 'Erreur lors de la création'
  } finally {
    isSaving.value = false
  }
}

const goBack = () => {
  router.push('/home')
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  router.push('/login')
}

onMounted(() => {
  const token = localStorage.getItem('token')
  const storedName = localStorage.getItem('userName')

  if (!token) {
    router.push('/login')
    return
  }

  userName.value = storedName || 'Utilisateur'
  fetchCours()
  fetchPages()
})
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

.back-btn,
.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.back-btn:hover,
.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 12px;
  color: #667eea;
  margin: 0 0 6px;
  font-weight: 700;
}

h2 {
  margin: 0;
  font-size: 2rem;
  color: #1f1f1f;
}

.subtitle {
  margin: 6px 0 0;
  color: #555;
}

.actions {
  display: flex;
  gap: 10px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-top: 10px;
}

.card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.add-card {
  border: 2px dashed #d0d0d0;
  cursor: pointer;
  justify-content: center;
  align-items: center;
  transition: border-color 0.3s, background 0.3s;
}

.add-card:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.add-icon {
  font-size: 3rem;
  color: #667eea;
}

.card-icon {
  font-size: 2.4rem;
}

h3 {
  margin: 0;
  color: #222;
}

.description {
  color: #555;
  margin: 0;
}

.meta {
  color: #777;
  font-size: 0.9rem;
  margin: 0;
}

.card-actions {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
  font-weight: 600;
}

.ghost {
  background: transparent;
  color: #667eea;
  border: 1px solid #d8ddff;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 600;
}

.danger-outline {
  background: transparent;
  color: #d32f2f;
  border: 1px solid #ffcdd2;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 600;
}

.input,
.textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  background: #fafafa;
}

.textarea {
  resize: vertical;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #555;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
}

.error-bar {
  background: #ffe3e3;
  color: #b00020;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 12px;
  border: 1px solid #ffb3b3;
}

.skeleton {
  position: relative;
  overflow: hidden;
}

.skeleton::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
  animation: shimmer 1.5s infinite;
}

.skeleton-line {
  height: 14px;
  background: #ececec;
  border-radius: 6px;
  margin: 8px 0;
}

.skeleton-line.title {
  width: 70%;
  height: 18px;
}

.skeleton-line.short {
  width: 40%;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
</style>
