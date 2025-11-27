<template>
  <div>
    <Navbar v-if="authStore.isLoggedIn" />
    <router-view />
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/authStore'
import Navbar from './components/Navbar.vue'

const authStore = useAuthStore()
</script>
