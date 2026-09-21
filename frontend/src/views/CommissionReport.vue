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
          <label class="form-label">From Date</label>
          <input class="form-input" type="date" v-model="filters.from_date" />
        </div>
        <div class="filter-group">
          <label class="form-label">To Date</label>
          <input class="form-input" type="date" v-model="filters.to_date" />
        </div>
        <button class="btn btn-primary" @click="loadReport" style="align-self:flex-end;">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          Refresh
        </button>
        <button class="btn btn-ghost" @click="clearFilters" style="align-self:flex-end;">Clear</button>
      </div>
    </div>

    <!-- KPI row -->
    <div class="kpi-row" v-if="!loading && rows.length">
      <div class="stat-card">
        <div class="stat-label">Customers</div>
        <div class="stat-val">{{ rows.length }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Transactions</div>
        <div class="stat-val">{{ totalTx }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Premium</div>
        <div class="stat-val money">{{ fmtCurrency(totalAmount) }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Total Commission</div>
        <div class="stat-val comm">{{ fmtCurrency(totalComm) }}</div>
      </div>
    </div>

    <!-- Table -->
    <div class="panel-card">
      <div class="panel-header">
        <div>
          <div class="panel-title">Commission by Customer</div>
          <div class="panel-desc">Aggregated totals and latest renewal dates per customer</div>
        </div>
      </div>
      <div v-if="loading" style="padding:16px;">
        <div class="skeleton" style="height:44px;margin-bottom:8px;border-radius:4px;" v-for="i in 5" :key="i"></div>
      </div>
      <div style="overflow-x:auto;" v-else>
        <table class="data-table">
          <thead><tr>
            <th>Customer</th><th>Rate</th><th>Transactions</th><th>Total Premium</th><th>Commission</th><th>Latest Renewal</th>
          </tr></thead>
          <tbody>
            <tr v-for="r in rows" :key="r.customer">
              <td>
                <div class="cust-cell">
                  <div class="mini-avatar">{{ initials(r.customer) }}</div>
                  <router-link :to="`/customers/${r.customer}`" class="link-cell">{{ r.customer }}</router-link>
                </div>
              </td>
              <td><span class="badge badge-blue">{{ r.commission_rate }}%</span></td>
              <td style="font-weight:600;">{{ r.total_transactions }}</td>
              <td class="amount-cell">{{ fmtCurrency(r.total_amount) }}</td>
              <td>
                <div style="display:flex;flex-direction:column;gap:5px;min-width:120px;">
                  <span class="amount-cell comm-color">{{ fmtCurrency(r.total_commission) }}</span>
                  <div class="mini-bar-wrap"><div class="mini-bar" :style="{ width: barPct(r.total_commission) }"></div></div>
                </div>
              </td>
              <td><span class="badge" :class="renewalClass(r.latest_renewal_date)">{{ r.latest_renewal_date }}</span></td>
            </tr>
            <tr v-if="rows.length === 0">
              <td colspan="6" class="empty-cell">No data — run the report with filters above</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'

const loading = ref(true)
const rows = ref([])
const customers = ref([])
const filters = ref({ customer: '', from_date: '', to_date: '' })

const totalTx     = computed(() => rows.value.reduce((s, r) => s + (r.total_transactions || 0), 0))
const totalAmount = computed(() => rows.value.reduce((s, r) => s + (r.total_amount || 0), 0))
const totalComm   = computed(() => rows.value.reduce((s, r) => s + (r.total_commission || 0), 0))

function fmtCurrency(v) { return 'TZS ' + Number(v || 0).toLocaleString('en-TZ', { maximumFractionDigits: 0 }) }
function initials(n) { return (n || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() }
function clearFilters() { filters.value = { customer: '', from_date: '', to_date: '' }; loadReport() }
function barPct(v) {
  const max = Math.max(...rows.value.map(r => r.total_commission || 0), 1)
  return Math.round((v / max) * 100) + '%'
}
function renewalClass(d) {
  const days = Math.round((new Date(d) - new Date()) / 86400000)
  if (days < 0) return 'badge-red'
  if (days < 30) return 'badge-yellow'
  return 'badge-green'
}

async function loadReport() {
  loading.value = true
  try {
    const f = {}
    if (filters.value.customer)  f.customer  = filters.value.customer
    if (filters.value.from_date) f.from_date = filters.value.from_date
    if (filters.value.to_date)   f.to_date   = filters.value.to_date
    const report = await api.report('Customer Commission and Renewal Summary', f)
    rows.value = report.result || []
  } catch (e) { console.error(e); rows.value = [] }
  finally { loading.value = false }
}

onMounted(async () => {
  customers.value = await api.list('Bavic Customer', { fields: ['name'], limit: 200 })
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
.panel-header { padding: 16px 20px; border-bottom: 1px solid var(--border-subtle); }
.panel-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.panel-desc  { font-size: 12px; color: var(--text-secondary); }

.filter-bar { padding: 16px 20px; margin-bottom: 16px; overflow: visible; }
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 5px; flex: 1 1 180px; }

.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; color: var(--text-secondary); margin-bottom: 6px; font-weight: 700; }
.stat-val { font-size: 22px; font-weight: 700; color: var(--text-primary); }
.stat-val.money { color: var(--primary-300); }
.stat-val.comm  { color: #4ade80; }

.cust-cell { display: flex; align-items: center; gap: 10px; }
.mini-avatar {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, var(--primary-500), var(--accent-500));
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; color: #fff;
}
.amount-cell { font-family: monospace; font-size: 12px; font-weight: 600; color: var(--primary-300); }
.comm-color { color: #4ade80 !important; }
.mini-bar-wrap { height: 3px; background: rgba(255,255,255,0.05); border-radius: 99px; overflow: hidden; }
.mini-bar { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #4ade80, #22d3ee); }
.link-cell { color: var(--primary-300); font-weight: 600; }
.link-cell:hover { text-decoration: underline; }
.empty-cell { text-align: center; color: var(--text-muted); padding: 48px !important; }

@media (max-width: 900px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
</style>
