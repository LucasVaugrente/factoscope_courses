<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-content">
        <h1>Factoscope - Éditeur de cours</h1>
        <div class="user-info">
          <span>Bienvenue, {{ userName }}</span>
          <button @click="handleLogout" class="logout-btn">Déconnexion</button>
        </div>
      </div>
    </nav>

    <!-- Toast notifications -->
    <Teleport to="body">
      <div class="toast-container">
        <div v-if="error" class="toast toast-error">
          <span>{{ error }}</span>
          <button class="close-x" @click="error = ''">×</button>
        </div>
        <div v-if="successMessage" class="toast toast-success">
          <span>{{ successMessage }}</span>
          <button class="close-x" @click="successMessage = ''">×</button>
        </div>
      </div>
    </Teleport>

    <main class="main-content">

      <!-- Breadcrumb -->
      <nav class="breadcrumb" aria-label="Navigation">
        <button class="crumb" :class="{ active: view === 'cours' }" @click="goToCours">
          Cours
        </button>
        <template v-if="view === 'chapitres' && selectedModule">
          <span class="crumb-sep">›</span>
          <span class="crumb active">{{ selectedModule.titre }}</span>
        </template>
      </nav>

      <!-- ═══════════════════════════════════ VUE COURS ═══════════════════════════════════ -->
      <Transition name="slide" mode="out-in">
        <div v-if="view === 'cours'" key="cours">
          <div class="header-row">
            <div>
              <p class="eyebrow">Catalogue</p>
              <h2>Liste des cours</h2>
              <p class="subtitle">{{ modules.length }} cours disponible(s)</p>
            </div>
            <div class="actions">
              <button class="ghost_csv" @click="downloadCoursTemplate">⬇ Template CSV Cours</button>
              <button class="primary" @click="showUpload = true">+ Ajouter un chapitre</button>
              <button class="ghost" @click="fetchModules" :disabled="isLoading">Actualiser</button>
            </div>
          </div>

          <!-- Modal upload cours -->
          <div v-if="showUpload" class="modal-backdrop" @click.self="closeUpload">
            <div class="modal">
              <h3>Ajouter un chapitre via CSV</h3>
              <p class="csv-hint">
                Format : <code>titre_chapitre;description_chapitre;titre_cours;description_cours</code><br>
                <span class="csv-hint-sub">La 4ème colonne est requise uniquement si le cours n'existe pas
                  encore.</span>
              </p>
              <label class="field">
                <span>Fichier CSV</span>
                <input class="input" type="file" accept=".csv,text/csv" @change="onFileChange" />
              </label>
              <div class="card-actions" style="margin-top:16px;">
                <button class="ghost" @click="closeUpload" :disabled="uploading">Annuler</button>
                <button class="primary" @click="submitUpload" :disabled="!selectedFile || uploading">
                  {{ uploading ? 'Import en cours...' : 'Importer' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Skeleton -->
          <div v-if="isLoading" class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Titre</th>
                  <th>Description</th>
                  <th>Chapitres</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="n in 4" :key="n" class="skeleton-row">
                  <td>
                    <div class="skeleton-line" style="width:60%"></div>
                  </td>
                  <td>
                    <div class="skeleton-line" style="width:80%"></div>
                  </td>
                  <td>
                    <div class="skeleton-line" style="width:30%"></div>
                  </td>
                  <td>
                    <div class="skeleton-line" style="width:50%"></div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Table des cours (= modules) -->
          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width:32px"></th>
                  <th>Titre du cours</th>
                  <th>Description</th>
                  <th style="width:120px; text-align:center;">Chapitres</th>
                  <th style="width:160px; text-align:right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!modules.length">
                  <td colspan="5" class="empty-row">Aucun cours disponible.</td>
                </tr>
                <tr v-for="mod in modules" :key="mod.id" class="clickable-row" @click="openModule(mod)">
                  <td class="icon-cell">📘</td>
                  <td class="title-cell">{{ mod.titre || '—' }}</td>
                  <td class="desc-cell">{{ mod.description || '—' }}</td>
                  <td class="center-cell">
                    <span class="badge">
                      {{ chapitreCountByModule[mod.id] ?? '…' }}
                    </span>
                  </td>
                  <td class="actions-cell" @click.stop>
                    <button class="danger small" @click="deleteModule(mod.id)">Supprimer</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ══════════════════════════════ VUE CHAPITRES ══════════════════════════════ -->
        <div v-else-if="view === 'chapitres'" key="chapitres">
          <div class="header-row">
            <div>
              <p class="eyebrow">{{ selectedModule?.titre }}</p>
              <h2>Chapitres</h2>
              <p class="subtitle">{{ chapitres.length }} chapitre(s)</p>
            </div>
            <div class="actions">
              <button class="ghost" @click="goToCours">← Retour</button>
              <button class="ghost" @click="fetchChapitres(selectedModule.id)" :disabled="isLoadingChapitres">
                Actualiser
              </button>
            </div>
          </div>

          <!-- Skeleton -->
          <div v-if="isLoadingChapitres" class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Titre</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="n in 3" :key="n" class="skeleton-row">
                  <td>
                    <div class="skeleton-line" style="width:55%"></div>
                  </td>
                  <td>
                    <div class="skeleton-line" style="width:75%"></div>
                  </td>
                  <td>
                    <div class="skeleton-line" style="width:40%"></div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Table des chapitres (= cours) -->
          <div v-else class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th style="width:32px"></th>
                  <th>Titre du chapitre</th>
                  <th>Description</th>
                  <th style="width:160px; text-align:right;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!chapitres.length">
                  <td colspan="4" class="empty-row">Aucun chapitre pour ce cours.</td>
                </tr>
                <tr v-for="chapitre in chapitres" :key="chapitre.id" class="clickable-row"
                  @click="viewChapitre(chapitre.id)">
                  <td class="icon-cell">📄</td>
                  <td class="title-cell">{{ chapitre.titre || '—' }}</td>
                  <td class="desc-cell">{{ chapitre.description || '—' }}</td>
                  <td class="actions-cell" @click.stop>
                    <button class="danger small" @click="deleteChapitre(chapitre.id)">Supprimer</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Transition>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const apiBase = import.meta.env.VITE_API_URL

const userName = ref(localStorage.getItem('userName') || 'Utilisateur')
const error = ref('')
const successMessage = ref('')

// ── Vue active : 'cours' | 'chapitres'
const view = ref('cours')

// ── Cours (= modules BDD)
const modules = ref([])
const isLoading = ref(false)
const chapitreCountByModule = ref({})

// ── Chapitres (= cours BDD)
const selectedModule = ref(null)
const chapitres = ref([])
const isLoadingChapitres = ref(false)

// ── Upload
const showUpload = ref(false)
const uploading = ref(false)
const selectedFile = ref(null)

const downloadCoursTemplate = () => {
  const content = [
    'titre_chapitre;description_chapitre;titre_cours;description_cours',
    'description_page1;contenu_page1;media1.png@media2.mp3@media3.mp4;titre_chapitre',
  ].join('\n')
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'template_cours.csv'
  a.click()
  URL.revokeObjectURL(url)
}

// ────────────────────────── helpers ──────────────────────────
const apiFetch = async (url, options = {}) => {
  const token = localStorage.getItem('token')
  if (!token) { router.push('/login'); throw new Error('Non authentifié') }

  const headers = { ...(options.headers || {}) }
  headers.Authorization = `Bearer ${token}`
  if (!(options.body instanceof FormData) && options.method && options.method !== 'GET') {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json'
  }

  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    const msg = await res.json().catch(() => ({}))
    throw new Error(msg.detail || msg.message || 'Erreur API')
  }
  if (res.status === 204) return null
  return res.json().catch(() => ({}))
}

// ────────────────────────── modules ──────────────────────────
const fetchModules = async () => {
  isLoading.value = true
  error.value = ''
  try {
    const data = await apiFetch(`${apiBase}/api/modules`)
    modules.value = Array.isArray(data) ? data : []
    // Charger le nombre de chapitres pour chaque module
    await fetchAllChapitreCounts()
  } catch (e) {
    error.value = e.message || 'Erreur chargement cours'
  } finally {
    isLoading.value = false
  }
}

const fetchAllChapitreCounts = async () => {
  const allCours = await apiFetch(`${apiBase}/api/cours`).catch(() => [])
  const counts = {}
  if (Array.isArray(allCours)) {
    for (const c of allCours) {
      if (c.id_module != null) {
        counts[c.id_module] = (counts[c.id_module] || 0) + 1
      }
    }
  }
  chapitreCountByModule.value = counts
}

const deleteModule = async (id) => {
  if (!confirm('Supprimer ce cours et tous ses chapitres ?')) return
  try {
    await apiFetch(`${apiBase}/api/modules/${id}`, { method: 'DELETE' })
    successMessage.value = 'Cours supprimé'
    await fetchModules()
  } catch (e) {
    error.value = e.message || 'Erreur suppression'
  }
}

// ────────────────────────── chapitres ──────────────────────────
const openModule = async (mod) => {
  selectedModule.value = mod
  view.value = 'chapitres'
  await fetchChapitres(mod.id)
}

const fetchChapitres = async (moduleId) => {
  isLoadingChapitres.value = true
  error.value = ''
  try {
    const allCours = await apiFetch(`${apiBase}/api/cours`)
    chapitres.value = Array.isArray(allCours)
      ? allCours.filter(c => c.id_module === moduleId)
      : []
  } catch (e) {
    error.value = e.message || 'Erreur chargement chapitres'
  } finally {
    isLoadingChapitres.value = false
  }
}

const deleteChapitre = async (id) => {
  if (!confirm('Supprimer ce chapitre et toutes ses pages ?')) return
  try {
    await apiFetch(`${apiBase}/api/cours/${id}`, { method: 'DELETE' })
    successMessage.value = 'Chapitre supprimé'
    chapitres.value = chapitres.value.filter(c => c.id !== id)
    if (selectedModule.value) {
      chapitreCountByModule.value[selectedModule.value.id] =
        (chapitreCountByModule.value[selectedModule.value.id] || 1) - 1
    }
  } catch (e) {
    error.value = e.message || 'Erreur suppression chapitre'
  }
}

const viewChapitre = (id) => {
  router.push(`/cours/${id}`)
}

const goToCours = () => {
  view.value = 'cours'
  selectedModule.value = null
  chapitres.value = []
}

// ────────────────────────── upload ──────────────────────────
const onFileChange = (e) => {
  selectedFile.value = e.target.files?.[0] || null
}

const closeUpload = () => {
  showUpload.value = false
  selectedFile.value = null
  uploading.value = false
}

const submitUpload = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    await apiFetch(`${apiBase}/api/cours/upload`, { method: 'POST', body: fd })
    successMessage.value = 'Cours importé avec succès'
    closeUpload()
    await fetchModules()
  } catch (e) {
    error.value = e.message || "Erreur lors de l'import"
  } finally {
    uploading.value = false
  }
}

// ────────────────────────── auth ──────────────────────────
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  router.push('/login')
}

onMounted(() => {
  if (!localStorage.getItem('token')) { router.push('/login'); return }
  fetchModules()
})
</script>

<style scoped>
/* ── Base ── */
.home-container {
  min-height: 100vh;
  background: #f5f7ff;
}

/* ── Navbar ── */
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 10px rgba(0, 0, 0, .12);
}

.nav-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
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
  gap: 14px;
}

.logout-btn {
  background: rgba(255, 255, 255, .2);
  color: white;
  border: 1px solid rgba(255, 255, 255, .3);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: background .2s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, .35);
}

/* ── Main ── */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* ── Breadcrumb ── */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
  font-size: .95rem;
}

.crumb {
  background: none;
  border: none;
  color: #999;
  cursor: default;
  font-weight: 600;
  padding: 4px 0;
  font-size: .95rem;
}

.crumb.active {
  color: #667eea;
}

button.crumb {
  cursor: pointer;
  transition: color .15s;
}

button.crumb:not(.active):hover {
  color: #667eea;
}

.crumb-sep {
  color: #ccc;
  font-size: 1.1rem;
}

/* ── Header row ── */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: .08em;
  font-size: 11px;
  color: #667eea;
  margin: 0 0 4px;
  font-weight: 800;
}

h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #1a1a2e;
}

.subtitle {
  margin: 4px 0 0;
  color: #666;
  font-size: .9rem;
}

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

/* ── Table ── */
.table-wrapper {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, .07);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #fafbff;
  padding: 13px 16px;
  text-align: left;
  font-size: .82rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: #888;
  border-bottom: 1px solid #f0f0f0;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f5f5f5;
  vertical-align: middle;
  font-size: .95rem;
  color: #333;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.clickable-row {
  cursor: pointer;
  transition: background .15s;
}

.clickable-row:hover {
  background: #f7f8ff;
}

.clickable-row:hover .title-cell {
  color: #667eea;
}

.icon-cell {
  font-size: 1.1rem;
  color: #aaa;
  width: 32px;
}

.title-cell {
  font-weight: 700;
  color: #1a1a2e;
  transition: color .15s;
}

.desc-cell {
  color: #777;
  font-size: .9rem;
  max-width: 400px;
}

.center-cell {
  text-align: center;
}

.actions-cell {
  text-align: right;
}

.empty-row {
  text-align: center;
  color: #aaa;
  padding: 32px !important;
  font-size: .95rem;
}

/* ── Badge ── */
.badge {
  background: #eef0ff;
  color: #667eea;
  font-size: 12px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 999px;
}

/* ── Skeleton ── */
.skeleton-row td {
  padding: 18px 16px;
}

.skeleton-line {
  height: 13px;
  background: #ececec;
  border-radius: 6px;
  position: relative;
  overflow: hidden;
}

.skeleton-line::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, .7), transparent);
  animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
  from {
    transform: translateX(-100%);
  }

  to {
    transform: translateX(100%);
  }
}

/* ── Buttons ── */
.primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  font-weight: 700;
  cursor: pointer;
  font-size: .9rem;
  transition: opacity .15s, transform .1s;
}

.primary:hover {
  opacity: .9;
  transform: translateY(-1px);
}

.primary:disabled {
  opacity: .6;
  cursor: not-allowed;
  transform: none;
}

.ghost {
  background: transparent;
  color: #667eea;
  border: 1.5px solid #d8ddff;
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
  font-size: .9rem;
  transition: background .15s, border-color .15s;
}

.ghost:hover {
  background: #f0f2ff;
  border-color: #b7c0f9;
}

.ghost:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.ghost_csv {
  background: #05e80540;
  color: #1a7312;
  border: 1.5px solid #35773c;
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
  font-size: .9rem;
  transition: background .15s, border-color .15s;
}

.ghost_csv:hover {
  background: #10af105f;
}

.ghost_csv:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.danger {
  background: #fff0f0;
  color: #c0392b;
  border: 1.5px solid #ffc5c5;
  border-radius: 8px;
  padding: 8px 14px;
  font-weight: 700;
  cursor: pointer;
  font-size: .85rem;
  transition: background .15s;
}

.danger:hover {
  background: #ffe0e0;
}

.small {
  padding: 7px 12px;
  font-size: .83rem;
}

/* ── Modal ── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 50;
}

.modal {
  width: 100%;
  max-width: 560px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, .15);
  padding: 24px;
}

.modal h3 {
  margin: 0 0 14px;
  color: #1a1a2e;
}

.field {
  display: grid;
  gap: 6px;
  margin-bottom: 14px;
}

.field span {
  font-size: .85rem;
  font-weight: 700;
  color: #444;
}

.input {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #e0e0e0;
  border-radius: 8px;
  font-size: .95rem;
  background: #fafafa;
  box-sizing: border-box;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.csv-hint {
  font-size: .88rem;
  color: #444;
  background: #f4f5ff;
  border: 1px solid #d8ddff;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 16px;
  line-height: 1.6;
}

.csv-hint code {
  font-family: monospace;
  color: #667eea;
  font-weight: 700;
}

.csv-hint-sub {
  font-size: .82rem;
  color: #888;
}

/* ── Toast ── */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  pointer-events: all;
  min-width: 280px;
  max-width: 420px;
  padding: 14px 16px;
  border-radius: 12px;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, .12);
  animation: slideInRight .3s cubic-bezier(.22, .61, .36, 1) forwards;
}

.toast-error {
  background: #ffe3e3;
  color: #b00020;
  border-color: #ffb3b3;
}

.toast-success {
  background: #e7fff1;
  color: #0a6b2b;
  border-color: #b6f2cb;
}

.close-x {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
  color: inherit;
  flex-shrink: 0;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(60px);
  }

  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* ── Transition drill-down ── */
.slide-enter-active,
.slide-leave-active {
  transition: opacity .22s ease, transform .22s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(28px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-28px);
}

/* ── Responsive ── */
@media (max-width: 640px) {
  .header-row {
    flex-direction: column;
  }

  .desc-cell {
    display: none;
  }
}
</style>