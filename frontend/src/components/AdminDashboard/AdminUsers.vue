<template>
  <div class="table-responsive">
    <table class="table table-striped">
      <thead class="table-dark">
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Bookings</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.User_id">
          <td>{{ user.Full_Name }}</td>
          <td>{{ user.Email_Address }}</td>
          <td>{{ user.Phone_Number }}</td>
          <td><span class="badge bg-info">{{ user.total_bookings }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const users = ref([])

onMounted(async () => {
  try {
    const res = await api.getAllUsers()
    users.value = res.data.users
  } catch (err) {
    console.error(err)
  }
})
</script>
