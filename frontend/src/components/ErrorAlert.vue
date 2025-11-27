<template>
  <div v-if="message" class="alert alert-danger alert-dismissible fade show" role="alert">
    <i class="bi bi-exclamation-circle"></i> {{ message }}
    <button type="button" class="btn-close" @click="$emit('close')"></button>
  </div>
</template>

<script setup>
defineProps({ message: String })
defineEmits(['close'])
</script>
