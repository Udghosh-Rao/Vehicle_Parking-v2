<template>
  <div>
    <h3 class="mb-4">Parking Summary</h3>

    <!-- Summary Stats -->
    <div class="mb-4">
      <p><strong>Total Parking Lots:</strong> {{ totalLots }}</p>
      <p><strong>Total Spots:</strong> {{ totalSpots }}</p>
      <p><strong>Available Spots:</strong> {{ availableSpots }}</p>
      <p><strong>Occupied Spots:</strong> {{ occupiedSpots }}</p>
      <p><strong>Overall Occupancy Rate:</strong> {{ occupancyRate }}%</p>
    </div>

    <!-- Revenue Bar Chart -->
    <div>
      <canvas ref="revenueChart"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../../services/api'
import Chart from 'chart.js/auto'

const revenueChart = ref(null)
const analyticsData = ref(null)

const totalLots = computed(() => analyticsData.value?.lot_usage.length || 0)

const totalSpots = computed(() => {
  if (!analyticsData.value) return 0
  return analyticsData.value.current_status.reduce((sum, item) => sum + item.value, 0)
})

const availableSpots = computed(() => {
  if (!analyticsData.value) return 0
  const avail = analyticsData.value.current_status.find(s => s.name === 'Available')
  return avail ? avail.value : 0
})

const occupiedSpots = computed(() => {
  if (!analyticsData.value) return 0
  const occ = analyticsData.value.current_status.find(s => s.name === 'Occupied')
  return occ ? occ.value : 0
})

const occupancyRate = computed(() => {
  if (totalSpots.value === 0) return 0
  return Math.round((occupiedSpots.value / totalSpots.value) * 100)
})

onMounted(async () => {
  try {
    const res = await api.getAnalytics()
    analyticsData.value = res.data
    renderRevenueChart()
  } catch (err) {
    console.error('Failed to load parking summary', err)
  }
})

const renderRevenueChart = () => {
  if (!analyticsData.value) return

  new Chart(revenueChart.value, {
    type: 'bar',
    data: {
      labels: analyticsData.value.revenue_by_lot.map(r => r.name),
      datasets: [{
        label: 'Revenue (Rs.)',
        data: analyticsData.value.revenue_by_lot.map(r => r.revenue),
        backgroundColor: '#007bff'
      }]
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true } },
      plugins: { legend: { display: false } }
    }
  })
}
</script>
