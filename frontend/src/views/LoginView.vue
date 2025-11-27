<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card">
          <div class="card-body">
            <h2 class="text-center">Login</h2>
            
            <div class="mb-3">
              <label>Select Type:</label>
              <div>
                <input type="radio" v-model="type" value="user" id="user"> 
                <label for="user">User</label>
                &nbsp;&nbsp;
                <input type="radio" v-model="type" value="admin" id="admin"> 
                <label for="admin">Admin</label>
              </div>
            </div>

            <form @submit.prevent="login">
              <input v-model="email" type="email" placeholder="Email" class="form-control mb-2" required>
              <input v-model="password" type="password" placeholder="Password" class="form-control mb-3" required>
              <button type="submit" :disabled="loading" class="btn btn-primary w-100">
                {{ loading ? 'Logging...' : 'Login' }}
              </button>
            </form>

            <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
            
            <div v-if="type === 'user'" class="text-center mt-3">
              <p>New user? <router-link to="/register">Register here</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import api from '../services/api'

const router = useRouter()
const authStore = useAuthStore()
const type = ref('user')
const email = ref('udghosh@gmail.com')
const password = ref('1234')
const loading = ref(false)
const error = ref('')

const login = async () => {
  error.value = ''
  loading.value = true
  try {
    const res = type.value === 'admin' 
      ? await api.adminLogin(email.value, password.value)
      : await api.login(email.value, password.value)
    authStore.setAuth(res.data.access_token, res.data.user)
    router.push(res.data.user.Role === 'admin' ? '/admin' : '/user')
  } catch (err) {
    error.value = err.response?.data?.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
