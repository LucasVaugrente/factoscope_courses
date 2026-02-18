import axios from 'axios'

// Création d'une instance Axios personnalisée
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
})

// Intercepteur pour ajouter le token d'authentification
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour gérer les réponses
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // Si l'erreur est 401 (non autorisé) et que ce n'est pas une tentative de rafraîchissement
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // Tentative de rafraîchissement du token
        const response = await axios.post(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/refresh`,
          {},
          { withCredentials: true }
        )
        
        const { token } = response.data
        
        // Mise à jour du token dans le localStorage
        localStorage.setItem('token', token)
        
        // Mise à jour de l'en-tête d'autorisation
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        originalRequest.headers['Authorization'] = `Bearer ${token}`
        
        // Renouvellement de la requête originale
        return api(originalRequest)
      } catch (error) {
        // En cas d'échec de rafraîchissement, déconnecter l'utilisateur
        console.error('Erreur de rafraîchissement du token:', error)
        const authStore = useAuthStore()
        await authStore.logout()
        return Promise.reject(error)
      }
    }
    
    return Promise.reject(error)
  }
)

export default api
