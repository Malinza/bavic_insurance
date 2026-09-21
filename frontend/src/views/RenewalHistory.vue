<template>
  <div class="page-container">
    <!-- Filters -->
    <div class="panel-card filter-bar">
      <div class="filter-row">
        <div class="filter-group">
          <label class="form-label">Customer</label>
          <select class="form-select" v-model="filters.customer">
            <option value="">All Customers</option>
            <option v-for="c in customers" :key="c.name" :value="c.name">{{ c.name }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="form-label">Product</label>
          <select class="form-select" v-model="filters.product">
            <option value="">All Products</option>
            <option v-for="p in products" :key="p.name" :value="p.name">{{ p.name }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="form-label">Business Type</label>
          <select class="form-select" v-model="filters.business_type">
            <option value="">All Types</option>
            <option v-for="b in businessTypes" :key="b.name" :value="b.name">{{ b.name }}</option>
          </select>
        </div>
        <button class="btn btn-primary" @click="loadReport" style="align-self:flex-end;">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          Refresh
        </button>
        <button class="btn btn-ghost" @click="clearFilters" style="align-self:flex-end;">Clear</button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading">
      <div class="panel-card" style="padding:20px;margin-bottom:16px;" v-for="i in 3" :key="i">
        <div class="skeleton" style="height:14px;width:140px;margin-bottom:12px;border-radius:4px;"></div>
        <div class="skeleton" style="height:40px;margin-bottom:8px;border-radius:4px;" v-for="j in 2" :key="j"></div>
      </div>
    </div>

    <!-- Customer blocks -->
    <template v-else>
      <div v-for="group in groupedByCustomer" :key="group.customer" class="panel-card cust-block">
        <!-- Block header -->
        <div class="block-header">
          <div class="mini-avatar">{{ initials(group.customer) }}</div>
          <div style="flex:1;min-width:0;">
            <router-link :to="`/customers/${group.customer}`" class="link-cell block-name">{{ group.customer }}</router-link>
            <div class="block-sub">{{ group.rows.length }} renewal records</div>
          </div>
          <div class="block-right">
            <span class="badge badge-green">{{ fmtCurrency(group.totalAmount) }} total</span>
          </div>
        </div>

        <!-- Rows table -->
        <table class="data-table">
          <thead><tr>
            <th>Policy Holder</th><th>Product</th><th>Type</th><th>Effective</th><th>Renewal</th><th>Days</th><th>Amount</th><th>Intermediary</th>
          </tr></thead>
          <tbody>
            <tr v-for="r in group.rows" :key="r.name">
              <td style="font-weight:600;">{{ r.policy_holder_name }}</td>
              <td>{{ r.product }}</td>
              <td><span class="badge badge-blue">{{ r.business_type }}</span></td>
              <td class="date-cell">{{ r.effective_date }}</td>
              <td>
                <span :class="['ren-date', renewalClass(r.renewal_date)]">{{ r.renewal_date }}</span>
              </td>
              <td>
                <span class="badge" :class="daysClass(r.renewal_date)">
                  {{ Math.abs(daysLeft(r.renewal_date)) }}d {{ daysLeft(r.renewal_date) >= 0 ? 'left' : 'ago' }}
                </span>
              </td>
              <td class="amount-cell">{{ fmtCurrency(r.amount) }}</td>
              <td class="date-cell">{{ r.intermediary }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="panel-card empty-state" v-if="groupedByCustomer.length === 0">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
        <p>No renewal records found</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const loading = ref(true)
const allRows = ref([])
const customers = ref([])
const products  = ref([])
const businessTypes = ref([])
const filters = ref({ customer: '', product: '', business_type: '' })

const filtered = computed(() => {
  let rows = allRows.value
  if (filters.value.customer) rows = rows.filter(r => r.customer === filters.value.customer)
  if (filters.value.product) rows = rows.filter(r => r.product === filters.value.product)
  if (filters.value.business_type) rows = rows.filter(r => r.business_type === filters.value.business_type)
  return rows
})

const groupedByCustomer = computed(() => {
  const map = {}
  filtered.value.forEach(r => {
    if (!map[r.customer]) map[r.customer] = { customer: r.customer, rows: [], totalAmount: 0 }
    map[r.customer].rows.push(r)
    map[r.customer].totalAmount += r.amount || 0
  })
  return Object.values(map).sort((a, b) => a.customer.localeCompare(b.customer))
})

function initials(n) { return (n || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() }
function fmtCurrency(v) { return 'TZS ' + Number(v || 0).toLocaleString('en-TZ', { maximumFractionDigits: 0 }) }
function daysLeft(d) { return Math.round((new Date(d) - new Date()) / 86400000) }
function renewalClass(d) {
  const days = daysLeft(d)
  if (days < 0) return 'expired'
  if (days < 30) return 'soon'
  return 'ok'
}
function daysClass(d) {
  const days = daysLeft(d)
  if (days < 0) return 'badge-red'
  if (days < 30) return 'badge-yellow'
  return 'badge-green'
}
function clearFilters() { filters.value = { customer: '', product: '', business_type: '' } }

async function loadReport() {
  loading.value = true
  try {
    const report = await api.report('Customer Renewal History', {
      ...(filters.value.customer ? { customer: filters.value.customer } : {}),
      ...(filters.value.product ? { product: filters.value.product } : {}),
      ...(filters.value.business_type ? { business_type: filters.value.business_type } : {}),
    })
    allRows.value = report.result || []
  } catch (e) { console.error(e); allRows.value = [] }
  finally { loading.value = false }
}

onMounted(async () => {
  const [custList, prodList, btList] = await Promise.all([
    api.list('Bavic Customer', { fields: ['name'], limit: 200 }),
    api.list('Insurance Product', { fields: ['name'], limit: 50 }),
    api.list('Business Type', { fields: ['name'], limit: 50 }),
  ])
  customers.value = custList
  products.value = prodList
  businessTypes.value = btList
  loadReport()
})
</script>

<style scoped>
.panel-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.filter-bar { padding: 16px 20px; margin-bottom: 16px; overflow: visible; }
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 5px; flex: 1 1 180px; }

.cust-block { margin-bottom: 16px; }
.block-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 20px; border-bottom: 1px solid var(--border-subtle);
}
.mini-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, var(--primary-500), var(--accent-500));
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #fff;
}
.block-name { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.block-sub  { font-size: 11px; color: var(--text-secondary); }
.block-right { margin-left: auto; }
.link-cell { color: var(--primary-300); }
.link-cell:hover { text-decoration: underline; }

.amount-cell { font-family: monospace; font-size: 12px; font-weight: 600; color: var(--primary-300); }
.date-cell { font-size: 12px; color: var(--text-secondary); white-space: nowrap; }
.ren-date { font-size: 13px; font-weight: 700; }
.ren-date.ok      { color: #4ade80; }
.ren-date.soon    { color: #fbbf24; }
.ren-date.expired { color: #f87171; }

.empty-state {
  padding: 64px 32px; display: flex; flex-direction: column;
  align-items: center; gap: 12px; color: var(--text-secondary); text-align: center;
}
.empty-state svg { opacity: 0.4; }
</style>
