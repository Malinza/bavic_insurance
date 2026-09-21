<template>
  <div class="page-container">
    <!-- Filters bar -->
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
          <label class="form-label">Business Type</label>
          <select class="form-select" v-model="filters.business_type">
            <option value="">All Types</option>
            <option v-for="b in businessTypes" :key="b.name" :value="b.name">{{ b.name }}</option>
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
          <label class="form-label">Policy Holder</label>
          <input class="form-input" v-model="search" placeholder="Search name..." />
        </div>
        <button class="btn btn-ghost" @click="clearFilters" style="align-self:flex-end;">Clear</button>
      </div>
      <!-- Summary pills -->
      <div class="summary-pills">
        <div class="pill"><span class="pill-val">{{ filtered.length }}</span> records</div>
        <div class="pill"><span class="pill-val money">{{ fmtCurrency(totalAmount) }}</span> volume</div>
        <div class="pill"><span class="pill-val comm">{{ fmtCurrency(totalComm) }}</span> commission</div>
      </div>
    </div>

    <!-- Table -->
    <div class="panel-card">
      <div v-if="loading" style="padding:16px;">
        <div class="skeleton" style="height:44px;margin-bottom:8px;border-radius:4px;" v-for="i in 6" :key="i"></div>
      </div>
      <div style="overflow-x:auto;" v-else>
        <table class="data-table">
          <thead><tr>
            <th>Customer</th>
            <th>Policy Holder</th>
            <th>Product</th>
            <th>Type</th>
            <th>Effective</th>
            <th>Renewal</th>
            <th>Posting</th>
            <th>Amount</th>
            <th>Commission</th>
            <th>Intermediary</th>
          </tr></thead>
          <tbody>
            <tr v-for="t in filtered" :key="t.name">
              <td><router-link :to="`/customers/${t.customer}`" class="link-cell">{{ t.customer }}</router-link></td>
              <td style="font-weight:600;">{{ t.policy_holder_name }}</td>
              <td>{{ t.product }}</td>
              <td><span class="badge badge-blue">{{ t.business_type }}</span></td>
              <td class="date-cell">{{ t.effective_date }}</td>
              <td><span class="badge" :class="renewalClass(t.renewal_date)">{{ t.renewal_date }}</span></td>
              <td class="date-cell">{{ t.posting_date }}</td>
              <td class="amount-cell">{{ fmtNum(t.amount) }}</td>
              <td class="amount-cell comm-color">{{ fmtNum(t.commission_amount) }}</td>
              <td class="date-cell">{{ t.intermediary }}</td>
            </tr>
            <tr v-if="filtered.length === 0">
              <td colspan="10" class="empty-cell">No transactions match your filters</td>
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
const allTx = ref([])
const customers = ref([])
const businessTypes = ref([])
const products = ref([])
const filters = ref({ customer: '', business_type: '', product: '' })
const search = ref('')

const filtered = computed(() => {
  let list = allTx.value
  if (filters.value.customer) list = list.filter(t => t.customer === filters.value.customer)
  if (filters.value.business_type) list = list.filter(t => t.business_type === filters.value.business_type)
  if (filters.value.product) list = list.filter(t => t.product === filters.value.product)
  if (search.value) list = list.filter(t => t.policy_holder_name?.toLowerCase().includes(search.value.toLowerCase()))
  return list
})

const totalAmount = computed(() => filtered.value.reduce((s, t) => s + (t.amount || 0), 0))
const totalComm   = computed(() => filtered.value.reduce((s, t) => s + (t.commission_amount || 0), 0))

function fmtNum(v) { return Number(v || 0).toLocaleString('en-TZ', { maximumFractionDigits: 0 }) }
function fmtCurrency(v) { return 'TZS ' + fmtNum(v) }
function clearFilters() { filters.value = { customer: '', business_type: '', product: '' }; search.value = '' }
function renewalClass(d) {
  const days = Math.round((new Date(d) - new Date()) / 86400000)
  if (days < 0) return 'badge-red'
  if (days < 30) return 'badge-yellow'
  return 'badge-green'
}

onMounted(async () => {
  try {
    const [txList, custList, btList, prodList] = await Promise.all([
      api.list('Insurance Transaction', {
        fields: ['name','customer','policy_holder_name','product','business_type','effective_date','renewal_date','posting_date','amount','commission_amount','intermediary'],
        order_by: 'posting_date desc', limit: 500,
      }),
      api.list('Bavic Customer', { fields: ['name'], limit: 200 }),
      api.list('Business Type', { fields: ['name'], limit: 50 }),
      api.list('Insurance Product', { fields: ['name'], limit: 50 }),
    ])
    allTx.value = txList
    customers.value = custList
    businessTypes.value = btList
    products.value = prodList
  } catch (e) { console.error(e) }
  finally { loading.value = false }
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
.filter-row { display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; margin-bottom: 16px; }
.filter-group { display: flex; flex-direction: column; gap: 5px; flex: 1 1 180px; }
.summary-pills { display: flex; gap: 10px; flex-wrap: wrap; padding-top: 14px; border-top: 1px solid var(--border-subtle); }
.pill {
  display: inline-flex; align-items: center; gap: 6px; font-size: 12px;
  color: var(--text-secondary); background: var(--bg-raised);
  border: 1px solid var(--border-subtle); border-radius: 99px; padding: 4px 14px;
}
.pill-val { font-weight: 700; color: var(--text-primary); }
.pill-val.money { color: var(--primary-300); }
.pill-val.comm  { color: #4ade80; }
.amount-cell { font-family: monospace; font-size: 12px; font-weight: 600; color: var(--primary-300); }
.comm-color { color: #4ade80 !important; }
.date-cell { font-size: 12px; white-space: nowrap; color: var(--text-secondary); }
.link-cell { color: var(--primary-300); font-weight: 600; }
.link-cell:hover { text-decoration: underline; }
.empty-cell { text-align: center; color: var(--text-muted); padding: 48px !important; }
</style>
