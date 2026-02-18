import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  
  // État
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const token = ref(localStorage.getItem('token') || '')
  const isAuthenticated = computed(() => !!token.value)
  const returnUrl = ref(null)

  // Initialisation des en-têtes Axios
  if (token.value) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  // Actions
  async function login(credentials) {
    try {
      const response = await api.post('/api/auth/login', credentials)
      
      // Mise à jour de l'état
      user.value = response.data.user
      token.value = response.data.token
      
      // Stockage dans le localStorage
      localStorage.setItem('user', JSON.stringify(response.data.user))
      localStorage.setItem('token', response.data.token)
      
      // Configuration d'Axios
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
      
      return response.data
    } catch (error) {
      console.error('Erreur de connexion:', error)
      throw error
    }
  }

  async function register(userData) {
    try {
      const response = await api.post('/api/auth/register', userData)
      
      // Mise à jour de l'état
      user.value = response.data.user
      token.value = response.data.token
      
      // Stockage dans le localStorage
      localStorage.setItem('user', JSON.stringify(response.data.user))
      localStorage.setItem('token', response.data.token)
      
      // Configuration d'Axios
      api.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`
      
      return response.data
    } catch (error) {
      console.error("Erreur d'inscription:", error)
      throw error
    }
  }

  async function logout() {
    try {
      await api.post('/api/auth/logout')
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    } finally {
      // Nettoyage
      user.value = null
      token.value = ''
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
      
      // Redirection
      router.push('/login')
    }
  }

  async function fetchUser() {
    if (!token.value) return
    
    try {
      const response = await api.get('/api/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
      return response.data
    } catch (error) {
      console.error('Erreur lors de la récupération du profil:', error)
      if (error.response?.status === 401) {
        logout()
      }
      throw error
    }
  }

  function setReturnUrl(url) {
    returnUrl.value = url
  }

  function getReturnUrl() {
    const url = returnUrl.value || '/'
    returnUrl.value = null
    return url
  }

  return {
    user,
    token,
    isAuthenticated,
    returnUrl,
    login,
    register,
    logout,
    fetchUser,
    setReturnUrl,
    getReturnUrl
  }
})
