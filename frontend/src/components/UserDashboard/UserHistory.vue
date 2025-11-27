<template>
  <div>
    <h4>Parking History</h4>
    <div v-if="reservations.length > 0" class="table-responsive">
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Lot</th>
            <th>Vehicle</th>
            <th>Entry</th>
            <th>Exit</th>
            <th>Cost</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="res in reservations" :key="res.Reservation_Id">
            <td>{{ res.Lot_Name }}</td>
            <td>{{ res.Vehicle_Number }}</td>
            <td>{{ formatTime(res.Entry_Time) }}</td>
            <td>{{ formatTime(res.Exit_Time) }}</td>
            <td>Rs. {{ res.Total_Cost }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="alert alert-info">No history</div>
  </div>
</template>
<script setup>
const props = defineProps({ reservations: Array })
const formatTime = str => str ? new Date(str).toLocaleString() : 'N/A'
</script>
