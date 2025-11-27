<template>
  <div>
    <h4>Available Lots</h4>
    <div class="row">
      <div v-for="lot in lots" :key="lot.id" class="col-md-4 mb-3">
        <div class="card">
          <div class="card-body">
            <h6>{{ lot.Location_Name }}</h6>
            <p class="mb-1 text-muted">{{ lot.Address_name }}</p>
            <p><strong>Rs. {{ lot.PRICE }}/hr</strong></p>
            <p>
              <span class="badge bg-success">{{ lot.Available_Spots }}</span>
              <span class="badge bg-danger">{{ lot.Occupied_Spots }}</span>
            </p>
            <button 
              @click="bookLot(lot.id)" 
              class="btn btn-primary btn-sm w-100"
              :disabled="lot.Available_Spots === 0"
            >Book</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="modal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5>Enter Vehicle Number</h5>
            <button type="button" class="btn-close" @click="modal = false"></button>
          </div>
          <div class="modal-body">
            <input v-model="vehicle" type="text" placeholder="DL01AB1234" class="form-control">
          </div>
          <div class="modal-footer">
            <button @click="submitBooking" class="btn btn-success">Confirm</button>
            <button @click="modal = false" class="btn btn-secondary">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import api from '../../services/api'

const props = defineProps({ lots: Array })
const emit = defineEmits(['booked'])
const modal = ref(false)
const lotId = ref(null)
const vehicle = ref('')

const bookLot = (id) => {
  lotId.value = id
  vehicle.value = ''
  modal.value = true
}
const submitBooking = async () => {
  try {
    await api.bookSpot(lotId.value, vehicle.value)
    modal.value = false
    vehicle.value = ''
    alert('Booked successfully!')
    emit('booked')
  } catch (err) {
    alert(err.response?.data?.message || 'Booking failed')
  }
}
</script>

<style scoped>
.modal.d-block { display: block; }
</style>
