<template>
  <nav style="background: #333; padding: 10px 20px; color: white; display: flex; justify-content: space-between;">
    <div>Parking App</div>
    <div>
      <span style="margin-right: 20px;">{{ authStore.user?.Full_Name }}</span>
      <button @click="logout" style="padding: 5px 10px; cursor: pointer;">Logout</button>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/authStore'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
