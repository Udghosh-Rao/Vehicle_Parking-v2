<template>
  <div class="container p-3">
    <h2>Admin Dashboard</h2>

    <!-- Stats -->
    <div class="row my-3">
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <strong>Total Lots:</strong> {{ stats.total_lots || 0 }}
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <strong>Available:</strong> {{ stats.available || 0 }}
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <strong>Occupied:</strong> {{ stats.occupied || 0 }}
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card">
          <div class="card-body">
            <strong>Revenue:</strong> Rs. {{ stats.total_revenue || 0 }}
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-tabs">
      <li class="nav-item">
        <button :class="['nav-link', {active: tab==='lots'}]" @click="tab='lots'">Lots</button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', {active: tab==='users'}]" @click="tab='users'">Users</button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', {active: tab==='reservations'}]" @click="tab='reservations'">Reservations</button>
      </li>
      <li class="nav-item">
        <button :class="['nav-link', {active: tab==='analytics'}]" @click="tab='analytics'">Analytics</button>
      </li>
    </ul>

    <!-- Lots Tab -->
    <div v-show="tab==='lots'" class="mt-3">
      <button @click="openAddForm" class="btn btn-primary mb-3">Add Lot</button>
      <!-- Add Form -->
      <div v-if="showAddForm" class="card mb-3">
        <div class="card-body">
          <h5>Add New Lot</h5>
          <form @submit.prevent="addLot">
            <input v-model="newLot.Location_Name" placeholder="Location" class="form-control mb-2" required>
            <input v-model="newLot.Address_name" placeholder="Address" class="form-control mb-2" required>
            <input v-model.number="newLot.PRICE" type="number" placeholder="Price/hour" class="form-control mb-2" required>
            <input v-model.number="newLot.Maximum_Number_Spots" type="number" placeholder="Spots" class="form-control mb-2" required>
            <button type="submit" class="btn btn-success">Create</button>
            <button type="button" @click="showAddForm=false" class="btn btn-secondary ms-2">Cancel</button>
          </form>
        </div>
      </div>
      <!-- Edit Form -->
      <div v-if="showEditForm" class="card mb-3 border-warning">
        <div class="card-body">
          <h5>Edit Lot: {{ editLot.Location_Name }}</h5>
          <p class="text-muted">
            Current: {{ editLot.currentTotal }} spots 
            ({{ editLot.occupiedSpots }} occupied, {{ editLot.currentTotal - editLot.occupiedSpots }} available)
          </p>
          <form @submit.prevent="updateLot">
            <div class="mb-2">
              <label>Location Name</label>
              <input v-model="editLot.Location_Name" class="form-control" required>
            </div>
            <div class="mb-2">
              <label>Address</label>
              <input v-model="editLot.Address_name" class="form-control" required>
            </div>
            <div class="mb-2">
              <label>Price per Hour</label>
              <input v-model.number="editLot.PRICE" type="number" class="form-control" required>
            </div>
            <div class="mb-2">
              <label>Total Spots (Min: {{ editLot.occupiedSpots }})</label>
              <input 
                v-model.number="editLot.Maximum_Number_Spots" 
                type="number" 
                class="form-control" 
                :min="editLot.occupiedSpots" 
                required
              >
              <small v-if="editLot.Maximum_Number_Spots !== editLot.currentTotal" class="text-info">
                <span v-if="editLot.Maximum_Number_Spots > editLot.currentTotal">
                  Will ADD {{ editLot.Maximum_Number_Spots - editLot.currentTotal }} spots
                </span>
                <span v-else>
                  Will REMOVE {{ editLot.currentTotal - editLot.Maximum_Number_Spots }} empty spots
                </span>
              </small>
            </div>
            <button type="submit" class="btn btn-warning">Update Lot</button>
            <button type="button" @click="showEditForm=false" class="btn btn-secondary ms-2">Cancel</button>
          </form>
        </div>
      </div>
      <!-- Lots Table -->
      <table class="table table-sm table-striped">
        <thead class="table-dark">
          <tr>
            <th>Location</th>
            <th>Address</th>
            <th>Price/hr</th>
            <th>Total</th>
            <th>Available</th>
            <th>Occupied</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="lot in lots" :key="lot.id">
            <td>{{ lot.Location_Name }}</td>
            <td>{{ lot.Address_name }}</td>
            <td>Rs. {{ lot.PRICE }}</td>
            <td>{{ lot.Total_Spots }}</td>
            <td><span class="badge bg-success">{{ lot.Available_Spots }}</span></td>
            <td><span class="badge bg-danger">{{ lot.Occupied_Spots }}</span></td>
            <td>
              <button @click="openEditForm(lot)" class="btn btn-warning btn-sm me-1">Edit</button>
              <button @click="deleteLot(lot.id)" class="btn btn-danger btn-sm">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Users Tab -->
    <div v-show="tab==='users'" class="mt-3">
      <table class="table table-sm">
        <thead>
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
            <td>{{ user.total_bookings }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reservations Tab -->
    <div v-show="tab==='reservations'" class="mt-3">
      <table class="table table-sm">
        <thead>
          <tr>
            <th>ID</th>
            <th>Lot</th>
            <th>Vehicle</th>
            <th>Entry</th>
            <th>Exit</th>
            <th>Cost</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="res in reservations" :key="res.Reservation_Id">
            <td>{{ res.Reservation_Id }}</td>
            <td>{{ res.Lot_Name }}</td>
            <td>{{ res.Vehicle_Number }}</td>
            <td>{{ formatDate(res.Entry_Time) }}</td>
            <td>{{ res.Exit_Time ? formatDate(res.Exit_Time) : 'Active' }}</td>
            <td>Rs. {{ (res.Total_Cost || 0).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Analytics Tab -->
    <div v-show="tab==='analytics'" class="mt-3">
      <AdminAnalytics />
    </div>

    <!-- Errors -->
    <div v-if="error" class="alert alert-danger mt-3">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'
import AdminAnalytics from '../components/AdminDashboard/AdminAnalytics.vue'

const tab = ref('lots')
const lots = ref([])
const users = ref([])
const reservations = ref([])
const stats = ref({})
const showAddForm = ref(false)
const showEditForm = ref(false)
const error = ref('')

const newLot = ref({
  Location_Name: '',
  Address_name: '',
  PRICE: 50,
  Maximum_Number_Spots: 50
})

const editLot = ref({
  id: null,
  Location_Name: '',
  Address_name: '',
  PRICE: 0,
  Maximum_Number_Spots: 0,
  currentTotal: 0,
  occupiedSpots: 0
})

onMounted(async () => {
  await loadData()
})

const loadData = async () => {
  try {
    const [d, l, u, r] = await Promise.all([
      api.getAdminDashboard(),
      api.getAllLots(),
      api.getAllUsers(),
      api.getAllReservations()
    ])
    stats.value = d.data.stats
    lots.value = l.data.lots
    users.value = u.data.users
    reservations.value = r.data.reservations
  } catch (err) {
    error.value = 'Failed to load data'
  }
}

const openAddForm = () => {
  showAddForm.value = true
  showEditForm.value = false
}

const openEditForm = (lot) => {
  editLot.value = {
    id: lot.id,
    Location_Name: lot.Location_Name,
    Address_name: lot.Address_name,
    PRICE: lot.PRICE,
    Maximum_Number_Spots: lot.Maximum_Number_Spots,
    currentTotal: lot.Total_Spots,
    occupiedSpots: lot.Occupied_Spots
  }
  showEditForm.value = true
  showAddForm.value = false
}

const addLot = async () => {
  try {
    await api.createLot(newLot.value)
    await loadData()
    showAddForm.value = false
    newLot.value = { Location_Name: '', Address_name: '', PRICE: 50, Maximum_Number_Spots: 50 }
    alert('Lot created successfully!')
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to create lot'
  }
}

const updateLot = async () => {
  try {
    await api.updateLot(editLot.value.id, {
      Location_Name: editLot.value.Location_Name,
      Address_name: editLot.value.Address_name,
      PRICE: editLot.value.PRICE,
      Maximum_Number_Spots: editLot.value.Maximum_Number_Spots
    })
    await loadData()
    showEditForm.value = false
    alert('Lot updated successfully!')
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to update lot'
  }
}

const deleteLot = async (id) => {
  if (!confirm('Delete this lot? All empty spots will be removed.')) return
  try {
    await api.deleteLot(id)
    await loadData()
    alert('Lot deleted successfully!')
  } catch (err) {
    error.value = err.response?.data?.message || 'Cannot delete lot with occupied spots'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('en-IN')
}
</script>
