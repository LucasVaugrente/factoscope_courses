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
      <div class="header-row">
        <div>
          <p class="eyebrow">Catalogue</p>
          <h2>Liste des cours</h2>
          <p class="subtitle">Cours issus de la base MariaDB</p>
        </div>
        <div class="actions">
          <div class="view-toggle" role="group" aria-label="Mode d'affichage des cours">
            <button class="ghost" :class="{ active: displayMode === 'cards' }" @click="displayMode = 'cards'">Boîtes</button>
            <button class="ghost" :class="{ active: displayMode === 'table' }" @click="displayMode = 'table'">Tableau</button>
          </div>
          <button class="primary" @click="showUpload = true">Ajouter cours</button>
          <button class="ghost" @click="fetchCourses" :disabled="isLoading">Actualiser</button>
        </div>
      </div>

      <div v-if="showUpload" class="modal-backdrop">
        <div class="modal">
          <h3>Ajouter un cours via CSV</h3>
          <div class="form-grid">
            <label>
              <span>Titre (optionnel si 3ème colonne)</span>
              <input class="input" v-model="formTitre" placeholder="Titre du cours" />
            </label>
            <label>
              <span>Description (optionnel)</span>
              <textarea class="textarea" rows="3" v-model="formDescription" placeholder="Description du cours"></textarea>
            </label>
            <label>
              <span>Thématique associée (optionnel)</span>
              <input class="input" v-model="formThematique" placeholder="Nom de la thématique" />
            </label>
            <label>
              <span>Fichier CSV</span>
              <input class="input" type="file" accept=".csv,text/csv" @change="onFileChange" />
            </label>
          </div>
          <div v-if="uploadError" class="error-bar" style="margin-top:10px;">{{ uploadError }}</div>
          <div class="card-actions" style="margin-top:16px;">
            <button class="ghost" @click="closeUpload" :disabled="uploading">Annuler</button>
            <button class="primary" @click="submitUpload" :disabled="!selectedFile || uploading">
              {{ uploading ? 'Import en cours...' : 'Importer' }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="error" class="error-bar">{{ error }}</div>

      <div v-if="isLoading" class="dashboard-grid">
        <div v-for="n in 4" :key="n" class="card skeleton">
          <div class="skeleton-line title"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
      </div>

      <div v-else-if="displayMode === 'cards'" class="dashboard-grid">
        <div v-for="course in courses" :key="course.id" class="card">
          <div class="card-icon">📘</div>
          <h3>{{ course.titre }}</h3>
          <p class="description">{{ course.description }}</p>
          <p class="meta">Contenu : {{ course.contenu }}</p>
          <p class="meta" v-if="course.id_module">Module lié : #{{ course.id_module }}</p>
          <div class="card-actions">
            <button class="primary" @click="viewCours(course.id)">Éditer</button>
            <button class="danger" @click="deleteCours(course.id)">Supprimer</button>
          </div>
        </div>
      </div>

      <div v-else class="table-wrapper">
        <table class="courses-table">
          <thead>
            <tr>
              <th>Titre du cours</th>
              <th>Description</th>
              <th>Contenu</th>
              <th>Raccourci</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!courses.length">
              <td colspan="4" class="empty-row">Aucun cours disponible.</td>
            </tr>
            <tr v-for="course in courses" :key="course.id">
              <td>{{ course.titre || '-' }}</td>
              <td>{{ course.description || '-' }}</td>
              <td>{{ course.contenu || '-' }}</td>
              <td>
                <button class="primary small" @click="viewCours(course.id)">Éditer</button>
                <button class="danger small" @click="deleteCours(course.id)">Supprimer</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userName = ref('')
const courses = ref([])
const isLoading = ref(false)
const error = ref('')
const showUpload = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const displayMode = ref('cards')
const selectedFile = ref(null)
const formTitre = ref('')
const formDescription = ref('')
const formThematique = ref('')

const apiBase = 'http://localhost:8000'

const fetchCourses = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const res = await fetch(`${apiBase}/api/cours`)
    if (!res.ok) throw new Error('Impossible de récupérer les cours')
    const data = await res.json()
    courses.value = data
  } catch (err) {
    error.value = err.message || 'Erreur lors du chargement des cours'
  } finally {
    isLoading.value = false
  }
}

const viewCours = (courseId) => {
  router.push(`/cours/${courseId}`)
}

const deleteCours = async (courseId) => {
  const confirmed = window.confirm('Supprimer ce cours ? Cette action est irréversible.')
  if (!confirmed) return

  try {
    const res = await fetch(`${apiBase}/api/cours/${courseId}`, {
      method: 'DELETE'
    })
    if (!res.ok) throw new Error('Impossible de supprimer le cours')
    await fetchCourses()
  } catch (err) {
    error.value = err.message || 'Erreur lors de la suppression du cours'
  }
}

const onFileChange = (e) => {
  const files = e.target.files
  selectedFile.value = files && files[0] ? files[0] : null
}

const closeUpload = () => {
  showUpload.value = false
  uploadError.value = ''
  uploading.value = false
  selectedFile.value = null
  formTitre.value = ''
  formDescription.value = ''
  formThematique.value = ''
}

const submitUpload = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  uploadError.value = ''
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    if (formTitre.value) fd.append('titre', formTitre.value)
    if (formDescription.value) fd.append('description', formDescription.value)
    if (formThematique.value) fd.append('thematique', formThematique.value)

    const res = await fetch(`${apiBase}/api/cours/upload`, {
      method: 'POST',
      body: fd
    })
    if (!res.ok) {
      const msg = await res.json().catch(() => null)
      throw new Error((msg && (msg.detail || msg.message)) || 'Échec de l\'import du cours')
    }
    await res.json()
    closeUpload()
    await fetchCourses()
  } catch (err) {
    uploadError.value = err.message || 'Erreur lors de l\'import'
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  const token = localStorage.getItem('token')
  const storedName = localStorage.getItem('userName')

  if (!token) {
    router.push('/login')
    return
  }

  userName.value = storedName || 'Utilisateur'
  fetchCourses()
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
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.view-toggle {
  display: inline-flex;
  gap: 8px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 50;
}

.modal {
  width: 100%;
  max-width: 640px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  padding: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-top: 10px;
}

.table-wrapper {
  margin-top: 10px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  overflow: auto;
}

.courses-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}

.courses-table th,
.courses-table td {
  text-align: left;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: top;
}

.courses-table thead th {
  background: #fafbff;
  font-size: 0.95rem;
  color: #333;
}

.courses-table tbody tr:hover {
  background: #fafcff;
}

.empty-row {
  text-align: center !important;
  color: #666;
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
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  min-height: 40px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.ghost.active {
  background: #eef1ff;
  border-color: #b7c0f9;
}

.primary.small,
.danger.small {
  padding: 8px 12px;
  font-size: 0.9rem;
  min-height: 36px;
}

.danger {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  min-height: 40px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: 600;
}

.courses-table td .small + .small {
  margin-left: 10px;
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


</style>
