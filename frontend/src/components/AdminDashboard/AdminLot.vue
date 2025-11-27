<template>
  <div>
    <button @click="showAddForm=true" class="btn btn-primary mb-3">Add Lot</button>

    <!-- Add Form -->
    <div v-if="showAddForm" class="card mb-3">
      <div class="card-body">
        <h5>Add New Lot</h5>
        <form @submit.prevent="addLot">
          <input v-model="addForm.Location_Name" placeholder="Location" class="form-control mb-2" required>
          <input v-model="addForm.Address_name" placeholder="Address" class="form-control mb-2" required>
          <input v-model.number="addForm.PRICE" type="number" placeholder="Price/hour" class="form-control mb-2" required>
          <input v-model.number="addForm.Maximum_Number_Spots" type="number" placeholder="Total Spots" class="form-control mb-2" required>
          <button type="submit" class="btn btn-success">Create</button>
          <button type="button" @click="showAddForm=false" class="btn btn-secondary ms-2">Cancel</button>
        </form>
      </div>
    </div>

    <!-- Edit Form -->
    <div v-if="showEditForm" class="card mb-3 border-warning">
      <div class="card-body">
        <h5>Edit Lot: {{ editForm.Location_Name }}</h5>
        <p class="text-muted">Current: {{ editForm.currentSpots }} spots ({{ editForm.occupiedSpots }} occupied, {{ editForm.currentSpots - editForm.occupiedSpots }} available)</p>
        <form @submit.prevent="updateLot">
          <div class="mb-2">
            <label>Location Name</label>
            <input v-model="editForm.Location_Name" class="form-control" required>
          </div>
          <div class="mb-2">
            <label>Address</label>
            <input v-model="editForm.Address_name" class="form-control" required>
          </div>
          <div class="mb-2">
            <label>Price per Hour</label>
            <input v-model.number="editForm.PRICE" type="number" class="form-control" required>
          </div>
          <div class="mb-2">
            <label>Total Spots (Min: {{ editForm.occupiedSpots }})</label>
            <input v-model.number="editForm.Maximum_Number_Spots" type="number" class="form-control" :min="editForm.occupiedSpots" required>
            <small class="text-info">
              Change to {{ editForm.Maximum_Number_Spots }}: 
              {{ editForm.Maximum_Number_Spots > editForm.currentSpots ? 'Will ADD ' + (editForm.Maximum_Number_Spots - editForm.currentSpots) + ' spots' : '' }}
              {{ editForm.Maximum_Number_Spots < editForm.currentSpots ? 'Will REMOVE ' + (editForm.currentSpots - editForm.Maximum_Number_Spots) + ' empty spots' : '' }}
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
          <th>Action</th>
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
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const lots = ref([])
const showAddForm = ref(false)
const showEditForm = ref(false)
const addForm = ref({
  Location_Name: '',
  Address_name: '',
  PRICE: 50,
  Maximum_Number_Spots: 50
})
const editForm = ref({
  id: null,
  Location_Name: '',
  Address_name: '',
  PRICE: 0,
  Maximum_Number_Spots: 0,
  currentSpots: 0,
  occupiedSpots: 0
})

onMounted(async () => {
  await loadLots()
})

const loadLots = async () => {
  try {
    const res = await api.getAllLots()
    lots.value = res.data.lots
  } catch (err) {
    console.error(err)
  }
}

const addLot = async () => {
  try {
    await api.createLot(addForm.value)
    showAddForm.value = false
    addForm.value = { Location_Name: '', Address_name: '', PRICE: 50, Maximum_Number_Spots: 50 }
    await loadLots()
    alert('Lot created successfully!')
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to create lot')
  }
}

const openEditForm = (lot) => {
  editForm.value = {
    id: lot.id,
    Location_Name: lot.Location_Name,
    Address_name: lot.Address_name,
    PRICE: lot.PRICE,
    Maximum_Number_Spots: lot.Maximum_Number_Spots,
    currentSpots: lot.Total_Spots,
    occupiedSpots: lot.Occupied_Spots
  }
  showEditForm.value = true
  showAddForm.value = false
}

const updateLot = async () => {
  try {
    await api.updateLot(editForm.value.id, {
      Location_Name: editForm.value.Location_Name,
      Address_name: editForm.value.Address_name,
      PRICE: editForm.value.PRICE,
      Maximum_Number_Spots: editForm.value.Maximum_Number_Spots
    })
    showEditForm.value = false
    await loadLots()
    alert('Lot updated successfully!')
  } catch (err) {
    alert(err.response?.data?.message || 'Failed to update lot')
  }
}

const deleteLot = async (id) => {
  if (!confirm('Delete this lot? All empty spots will be removed.')) return
  try {
    await api.deleteLot(id)
    await loadLots()
    alert('Lot deleted successfully!')
  } catch (err) {
    alert(err.response?.data?.message || 'Cannot delete lot with occupied spots')
  }
}
</script>
