<template>
  <div class="container p-3">
    <h2>User Dashboard</h2>

    <!-- Tabs -->
    <ul class="nav nav-tabs">
      <li class="nav-item">
        <button :class="['nav-link', {active: tab==='available'}]" @click="tab='available'">
          Available Lots
        </button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', {active: tab==='history'}]" @click="tab='history'">
          History
        </button>
      </li>
    </ul>

    <!-- ===== MULTIPLE ACTIVE BOOKINGS SECTION ===== -->
    <div v-if="activeBookings.length > 0" class="alert alert-info mt-3">
      <h5>Active Bookings ({{ activeBookings.length }})</h5>
      <div v-for="booking in activeBookings" :key="booking.Reservation_Id" class="card mb-2">
        <div class="card-body">
          <strong>Lot:</strong> {{ booking.Lot_Name }} <br>
          <strong>Spot:</strong> {{ booking.Spot_Number }} <br>
          <strong>Vehicle:</strong> {{ booking.Vehicle_Number }} <br>
          <strong>Entry:</strong> {{ formatDate(booking.Entry_Time) }}
          <br>
          <button @click="releaseSpot(booking.Reservation_Id)" class="btn btn-danger btn-sm mt-2">
            Release Spot
          </button>
        </div>
      </div>
    </div>
    <div v-else class="alert alert-warning mt-3">
      <p>No active bookings. Book from available lots below.</p>
    </div>

    <!-- Available Lots Tab -->
    <div v-show="tab==='available'" class="mt-3">
      <h4>Available Lots</h4>
      <div v-if="loading" class="alert alert-info">Loading...</div>

      <div v-else-if="lots.length > 0" class="row">
        <div v-for="lot in lots" :key="lot.id" class="col-md-6 col-lg-4 mb-3">
          <div class="card">
            <div class="card-body">
              <h6>{{ lot.Location_Name }}</h6>
              <p>{{ lot.Address_name }}</p>
              <p><strong>Rs. {{ lot.PRICE }}/hr</strong></p>
              <p>Available: {{ lot.Available_Spots }} | Occupied: {{ lot.Occupied_Spots }}</p>
              <button 
                @click="bookLot(lot.id)" 
                class="btn btn-primary btn-sm w-100"
                :disabled="lot.Available_Spots === 0"
              >
                Book Now
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="alert alert-warning">
        No lots available
      </div>
    </div>

    <!-- History Tab -->
    <div v-show="tab==='history'" class="mt-3">

      <!-- Header + Export button -->
      <div class="d-flex justify-content-between align-items-center mb-2">
        <h4 class="mb-0">Parking History</h4>
        <button
          class="btn btn-outline-secondary btn-sm"
          @click="exportCsv"
          :disabled="exportLoading || completedBookings.length === 0"
        >
          {{ exportLoading ? 'Exporting…' : 'Export CSV' }}
        </button>
      </div>

      <div v-if="loading" class="alert alert-info">Loading...</div>
      <div v-else-if="completedBookings.length > 0" class="table-responsive">
        <table class="table table-sm">
          <thead>
            <tr>
              <th>Lot</th>
              <th>Vehicle</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>Duration</th>
              <th>Cost</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="res in completedBookings" :key="res.Reservation_Id">
              <td>{{ res.Lot_Name }}</td>
              <td>{{ res.Vehicle_Number }}</td>
              <td>{{ formatDate(res.Entry_Time) }}</td>
              <td>{{ formatDate(res.Exit_Time) }}</td>
              <td>{{ res.Duration_Hours ? res.Duration_Hours.toFixed(2) + ' hrs' : '-' }}</td>
              <td>Rs. {{ (res.Total_Cost || 0).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="alert alert-info">
        No booking history yet.
      </div>
    </div>

    <!-- Booking Modal -->
    <div v-if="showBookingModal" class="modal d-block">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Book Parking</h5>
            <button type="button" class="btn-close" @click="showBookingModal=false"></button>
          </div>
          <div class="modal-body">
            <label>Vehicle Number:</label>
            <input 
              v-model="bookingForm.vehicleNumber" 
              type="text" 
              class="form-control" 
              placeholder="e.g., DL01AB1234"
              @keyup.enter="confirmBooking"
            >
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showBookingModal=false">
              Cancel
            </button>
            <button type="button" class="btn btn-primary" @click="confirmBooking">
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts -->
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
      <button type="button" class="btn-close" @click="error=''"></button>
    </div>
    <div v-if="success" class="alert alert-success mt-3">
      {{ success }}
      <button type="button" class="btn-close" @click="success=''"></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const tab = ref('available')
const lots = ref([])
const activeBookings = ref([])
const completedBookings = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const showBookingModal = ref(false)
const bookingForm = ref({ vehicleNumber: '', lotId: null })
const exportLoading = ref(false)

onMounted(() => { loadData() })

const loadData = async () => {
  loading.value = true
  error.value = ''
  try {
    const lotsRes = await api.getUserDashboard()
    lots.value = lotsRes.data.lots || []
    const reservations = lotsRes.data.reservations || []

    // Multiple bookings: split into active & completed
    activeBookings.value = reservations.filter(r => !r.Exit_Time)
    completedBookings.value = reservations.filter(r => r.Exit_Time)
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to load data'
  } finally {
    loading.value = false
  }
}

const bookLot = (lotId) => {
  bookingForm.value.lotId = lotId
  bookingForm.value.vehicleNumber = ''
  showBookingModal.value = true
}

const confirmBooking = async () => {
  if (!bookingForm.value.vehicleNumber.trim()) {
    error.value = 'Enter vehicle number'
    return
  }
  try {
    await api.bookSpot(bookingForm.value.lotId, bookingForm.value.vehicleNumber)
    success.value = 'Booked successfully!'
    showBookingModal.value = false
    setTimeout(loadData, 500)
  } catch (err) {
    error.value = err.response?.data?.message || 'Booking failed'
  }
}

const releaseSpot = async (reservationId) => {
  if (!confirm('Exit parking?')) return
  try {
    const res = await api.releaseSpot(reservationId)
    success.value = `Released! Cost: Rs. ${res.data.cost}`
    setTimeout(loadData, 500)
  } catch (err) {
    error.value = err.response?.data?.message || 'Release failed'
  }
}

const exportCsv = async () => {
  if (completedBookings.value.length === 0) {
    error.value = 'No history to export'
    return
  }

  exportLoading.value = true
  error.value = ''
  try {
    // trigger Celery export job
    const res = await api.exportHistory()
    success.value = res.data.message || 'Export started. You will get an email when it is ready.'
  } catch (err) {
    error.value = err.response?.data?.message || 'CSV export failed'
  } finally {
    exportLoading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('en-IN')
}
</script>

<style scoped>
.modal.d-block {
  display: block !important;
  background: rgba(0,0,0,0.5);
}
</style>
