<template>
  <div class="table-responsive">
    <table class="table table-striped table-sm">
      <thead class="table-dark">
        <tr>
          <th>User</th>
          <th>Lot</th>
          <th>Vehicle</th>
          <th>Entry</th>
          <th>Exit</th>
          <th>Cost</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="res in reservations" :key="res.Reservation_Id">
          <td>{{ res.User_id }}</td>
          <td>{{ res.Lot_Name }}</td>
          <td>{{ res.Vehicle_Number }}</td>
          <td>{{ formatTime(res.Entry_Time) }}</td>
          <td>{{ formatTime(res.Exit_Time) }}</td>
          <td>Rs. {{ res.Total_Cost || 0 }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api'

const reservations = ref([])

onMounted(async () => {
  try {
    const res = await api.getAllReservations()
    reservations.value = res.data.reservations
  } catch (err) {
    console.error(err)
  }
})

const formatTime = (str) => {
  if (!str) return 'N/A'
  return new Date(str).toLocaleString()
}
</script>
