<template>
  <div v-if="activeBookings.length > 0">
    <h4>Your Active Bookings</h4>
    <div v-for="booking in activeBookings" :key="booking.Reservation_Id" class="card mb-2">
      <div class="card-body">
        <strong>Lot:</strong> {{ booking.Lot_Name }}<br>
        <strong>Spot:</strong> {{ booking.Spot_Number }}<br>
        <strong>Vehicle:</strong> {{ booking.Vehicle_Number }}<br>
        <strong>Entry:</strong> {{ formatTime(booking.Entry_Time) }}<br>
        <button @click="releaseSpot(booking.Reservation_Id)" class="btn btn-danger btn-sm mt-2">
          Release Spot
        </button>
      </div>
    </div>
  </div>
  <div v-else class="alert alert-warning">
    No active booking. Book from Available Lots.
  </div>
</template>

<script setup>
import api from '../../services/api'
const props = defineProps({ activeBookings: Array })
const emit = defineEmits(['released'])

const releaseSpot = async (rid) => {
  try {
    const res = await api.releaseSpot(rid)
    alert(`Released! Cost: Rs. ${res.data.cost}`)
    emit('released')
  } catch (err) {
    alert('Release failed')
  }
}
const formatTime = str => str ? new Date(str).toLocaleString() : 'N/A'
</script>
