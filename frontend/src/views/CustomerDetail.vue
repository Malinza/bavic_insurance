<template>
  <div class="page-container">
    <div class="back-link" @click="$router.back()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
      Back to Customers
    </div>

    <!-- Skeleton -->
    <div v-if="loading">
      <div class="skeleton" style="height:100px;border-radius:8px;margin-bottom:20px;"></div>
      <div class="skeleton" style="height:320px;border-radius:8px;"></div>
    </div>

    <template v-else-if="customer">
      <!-- Header card -->
      <div class="panel-card ch-header">
        <div class="ch-avatar">{{ initials(customer.customer_name) }}</div>
        <div class="ch-body">
          <h2 class="ch-name">{{ customer.customer_name }}</h2>
          <div class="ch-sub">{{ customer.policy_holders?.length || 0 }} policy holders registered</div>
          <div class="ch-badges">
            <span class="badge badge-blue">{{ commissionRate || 0 }}% Commission</span>
            <span class="badge badge-green">{{ txStats.count }} Transactions</span>
            <span class="badge badge-yellow">{{ fmtCurrency(txStats.total) }} Volume</span>
          </div>
        </div>
        <div class="ch-kpis">
          <div class="ch-kpi">
            <div class="ch-kpi-val">{{ txStats.count }}</div>
            <div class="ch-kpi-label">Transactions</div>
          </div>
          <div class="ch-kpi">
            <div class="ch-kpi-val money">{{ fmtShort(txStats.total) }}</div>
            <div class="ch-kpi-label">Total Premium</div>
          </div>
          <div class="ch-kpi">
            <div class="ch-kpi-val comm">{{ fmtShort(txStats.commission) }}</div>
            <div class="ch-kpi-label">Commission</div>
          </div>
        </div>
      </div>

      <div class="detail-row">
        <!-- Policy Holders -->
        <div class="panel-card" style="flex:1">
          <div class="panel-header">
            <div>
              <div class="panel-title">Policy Holders</div>
              <div class="panel-desc">Contacts linked to this customer</div>
            </div>
          </div>
          <table class="data-table">
            <thead><tr><th>Name</th><th>Email</th><th>Phone</th></tr></thead>
            <tbody>
              <tr v-for="ph in customer.policy_holders" :key="ph.name">
                <td style="font-weight:600;">{{ ph.policy_holder_name }}</td>
                <td style="color:var(--text-secondary);">{{ ph.email || '—' }}</td>
                <td style="color:var(--text-secondary);">{{ ph.phone || '—' }}</td>
              </tr>
              <tr v-if="!customer.policy_holders?.length">
                <td colspan="3" class="empty-cell">No policy holders</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Quick numbers -->
        <div style="display:flex;flex-direction:column;gap:12px;width:220px;">
          <div class="stat-card">
            <div class="stat-label">Commission Rate</div>
            <div class="stat-big">{{ commissionRate || 0 }}<span class="stat-unit">%</span></div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Total Volume</div>
            <div class="stat-big money">{{ fmtShort(txStats.total) }}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Commission Earned</div>
            <div class="stat-big comm">{{ fmtShort(txStats.commission) }}</div>
          </div>
        </div>
      </div>

      <!-- Transaction table -->
      <div class="panel-card" style="margin-top:16px;">
        <div class="panel-header">
          <div>
            <div class="panel-title">Transaction History</div>
            <div class="panel-desc">All insurance policy transactions</div>
          </div>
        </div>
        <table class="data-table">
          <thead><tr>
            <th>Policy Holder</th><th>Product</th><th>Type</th><th>Effective</th><th>Renewal</th><th>Amount</th><th>Commission</th>
          </tr></thead>
          <tbody>
            <tr v-for="t in transactions" :key="t.name">
              <td style="font-weight:600;">{{ t.policy_holder_name }}</td>
              <td>{{ t.product }}</td>
              <td><span class="badge badge-blue">{{ t.business_type }}</span></td>
              <td style="color:var(--text-secondary);font-size:12px;">{{ t.effective_date }}</td>
              <td><span class="badge" :class="renewalClass(t.renewal_date)">{{ t.renewal_date }}</span></td>
              <td class="amount-cell">{{ fmtNum(t.amount) }}</td>
              <td class="amount-cell comm-color">{{ fmtNum(t.commission_amount) }}</td>
            </tr>
            <tr v-if="!transactions.length">
              <td colspan="7" class="empty-cell">No transactions found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <div v-else class="panel-card empty-cell" style="padding:64px;text-align:center;">Customer not found</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const loading = ref(true)
const customer = ref(null)
const commissionRate = ref(null)
const transactions = ref([])

const txStats = computed(() => ({
  count:      transactions.value.length,
  total:      transactions.value.reduce((s, t) => s + (t.amount || 0), 0),
  commission: transactions.value.reduce((s, t) => s + (t.commission_amount || 0), 0),
}))

function initials(name) { return (name || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() }
function fmtNum(v) { return 'TZS ' + Number(v || 0).toLocaleString('en-TZ', { maximumFractionDigits: 0 }) }
function fmtCurrency(v) { return 'TZS ' + Number(v || 0).toLocaleString('en-TZ', { maximumFractionDigits: 0 }) }
function fmtShort(v) {
  const n = Number(v || 0)
  if (n >= 1000000) return 'TZS ' + (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return 'TZS ' + (n / 1000).toFixed(0) + 'K'
  return 'TZS ' + n
}
function renewalClass(d) {
  const days = Math.round((new Date(d) - new Date()) / 86400000)
  if (days < 0) return 'badge-red'
  if (days < 30) return 'badge-yellow'
  return 'badge-green'
}

onMounted(async () => {
  const name = decodeURIComponent(route.params.name)
  try {
    const [cust, rate, txList] = await Promise.all([
      api.get('Bavic Customer', name),
      api.list('Customer Commission Rate', { fields: ['commission_rate'], filters: [['customer', '=', name]], limit: 1 }),
      api.list('Insurance Transaction', {
        fields: ['name', 'policy_holder_name', 'product', 'business_type', 'effective_date', 'renewal_date', 'amount', 'commission_amount'],
        filters: [['customer', '=', name]], order_by: 'renewal_date desc', limit: 100,
      }),
    ])
    customer.value = cust
    commissionRate.value = rate[0]?.commission_rate ?? null
    transactions.value = txList
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.back-link {
  display: inline-flex; align-items: center; gap: 8px;
  color: var(--text-secondary); font-size: 13px; font-weight: 600; cursor: pointer;
  margin-bottom: 20px;
}
.back-link:hover { color: var(--primary-300); }

.panel-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.panel-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid var(--border-subtle);
}
.panel-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.panel-desc  { font-size: 12px; color: var(--text-secondary); }

.ch-header {
  display: flex; align-items: center; gap: 24px;
  padding: 24px; margin-bottom: 16px;
}
.ch-avatar {
  width: 64px; height: 64px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, var(--primary-500), var(--accent-500));
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 800; color: #fff;
}
.ch-body { flex: 1; min-width: 0; }
.ch-name { font-size: 20px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.ch-sub  { font-size: 12px; color: var(--text-secondary); margin-bottom: 10px; }
.ch-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.ch-kpis { display: flex; gap: 0; border-left: 1px solid var(--border-subtle); padding-left: 24px; }
.ch-kpi { padding: 0 20px; text-align: center; }
.ch-kpi + .ch-kpi { border-left: 1px solid var(--border-subtle); }
.ch-kpi-val  { font-size: 20px; font-weight: 700; color: var(--text-primary); }
.ch-kpi-val.money { color: var(--primary-300); }
.ch-kpi-val.comm  { color: #4ade80; }
.ch-kpi-label { font-size: 11px; color: var(--text-secondary); margin-top: 2px; }

.detail-row { display: flex; gap: 16px; align-items: flex-start; }

.stat-label { font-size: 11px; text-transform: uppercase; letter-spacing: 0.6px; color: var(--text-secondary); margin-bottom: 6px; font-weight: 700; }
.stat-big   { font-size: 22px; font-weight: 800; color: var(--text-primary); }
.stat-big.money { color: var(--primary-300); }
.stat-big.comm  { color: #4ade80; }
.stat-unit { font-size: 14px; font-weight: 600; color: var(--text-muted); margin-left: 2px; }

.amount-cell { font-size: 12px; font-weight: 600; color: var(--primary-300); font-family: monospace; }
.comm-color { color: #4ade80 !important; }
.empty-cell { text-align: center; color: var(--text-muted); padding: 40px !important; }
</style>
