import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000/api'
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  // Existing methods...
  login(email, password) {
    return api.post('/auth/login', { Email_Address: email, User_Password: password })
  },

  adminLogin(email, password) {
    return api.post('/auth/admin-login', { Email_Address: email, User_Password: password })
  },

  register(data) {
    return api.post('/auth/register', data)
  },

  getAdminDashboard() {
    return api.get('/admin/dashboard')
  },

  getAllLots() {
    return api.get('/admin/lots')
  },

  createLot(data) {
    return api.post('/admin/lots', data)
  },

  updateLot(lotId, data) {
    return api.put(`/admin/lots/${lotId}`, data)
  },

  deleteLot(id) {
    return api.delete(`/admin/lots/${id}`)
  },

  getAllUsers() {
    return api.get('/admin/users')
  },

  getAllReservations() {
    return api.get('/admin/reservations')
  },

  getAnalytics() {
    return api.get('/admin/analytics')
  },

  getActiveParkings() {
    return api.get('/admin/active-parkings')
  },

  getUserDashboard() {
    return api.get('/user/dashboard')
  },

  bookSpot(lotId, vehicleNumber) {
    return api.post(`/user/book/${lotId}`, { Vehicle_Number: vehicleNumber })
  },

  releaseSpot(id) {
    return api.put(`/user/release/${id}`)
  },

  getHistory() {
    return api.get('/user/history')
  },

  exportHistory() {
    return api.post('/user/export')
  }
}
