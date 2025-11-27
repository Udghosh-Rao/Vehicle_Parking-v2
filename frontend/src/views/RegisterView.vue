<template>
  <div style="max-width: 500px; margin: 30px auto; padding: 20px; border: 1px solid #ddd;">
    <h2>Register</h2>
    
    <form @submit.prevent="register">
      <input v-model="form.Login_name" placeholder="Username" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc;" required>
      <input v-model="form.Full_Name" placeholder="Full Name" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc;" required>
      <input v-model="form.Email_Address" placeholder="Email" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc;" required>
      <input v-model="form.User_Password" type="password" placeholder="Password" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc;" required>
      <input v-model="form.Phone_Number" placeholder="Phone" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc;" required>
      <input v-model="form.Pin_Code" placeholder="Pincode" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc;" required>
      <textarea v-model="form.Address" placeholder="Address" style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ccc;" required></textarea>
      
      <button type="submit" :disabled="loading" style="width: 100%; padding: 10px; background: #28a745; color: white; border: none; cursor: pointer; margin-top: 10px;">
        {{ loading ? 'Creating...' : 'Register' }}
      </button>
    </form>

    <div v-if="error" style="color: red; margin-top: 10px;">{{ error }}</div>
    <div v-if="success" style="color: green; margin-top: 10px;">{{ success }}</div>

    <p style="margin-top: 10px;">
      <router-link to="/login">Already registered? Login</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../services/api'

const form = ref({
  Login_name: '',
  Full_Name: '',
  Email_Address: '',
  User_Password: '',
  Phone_Number: '',
  Pin_Code: '',
  Address: ''
})

const loading = ref(false)
const error = ref('')
const success = ref('')

const register = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    await api.register(form.value)
    success.value = 'Registered! Redirecting...'
    setTimeout(() => window.location.href = '/login', 2000)
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed'
  } finally {
    loading.value = false
  }
}
</script>
