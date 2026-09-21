<template>
  <div class="page-container">
    <!-- KPI row -->
    <div class="kpi-grid">
      <div class="stat-card" v-for="kpi in kpis" :key="kpi.label">
        <div class="stat-top">
          <div class="stat-icon" :style="{ background: kpi.iconBg }">
            <span v-html="kpi.icon"></span>
          </div>
          <div class="stat-trend" :class="kpi.up ? 'up' : 'down'">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline :points="kpi.up ? '18 15 12 9 6 15' : '6 9 12 15 18 9'"/>
            </svg>
            {{ kpi.trend }}
          </div>
        </div>
        <div class="stat-value">
          <span v-if="loading" class="skeleton" style="height:28px;width:100px;display:block;border-radius:4px;"></span>
          <span v-else>{{ kpi.value }}</span>
        </div>
        <div class="stat-label">{{ kpi.label }}</div>
      </div>
    </div>

    <div class="dash-grid">
      <!-- Recent Transactions -->
      <div class="panel-card">
        <div class="panel-header">
          <div>
            <div class="panel-title">Recent Transactions</div>
            <div class="panel-desc">Latest insurance policies recorded</div>
          </div>
          <router-link to="/transactions" class="btn btn-ghost btn-sm">View all →</router-link>
        </div>
        <div v-if="loading" style="padding:16px;">
          <div class="skeleton" style="height:40px;margin-bottom:8px;border-radius:4px;" v-for="i in 4" :key="i"></div>
        </div>
        <table class="data-table" v-else>
          <thead><tr>
            <th>Customer</th><th>Policy Holder</th><th>Amount</th><th>Renewal</th><th>Type</th>
          </tr></thead>
          <tbody>
            <tr v-for="t in recentTx" :key="t.name">
              <td><router-link :to="`/customers/${t.customer}`" class="link-cell">{{ t.customer }}</router-link></td>
              <td class="fw-med">{{ t.policy_holder_name }}</td>
              <td class="amount-cell">{{ fmtCurrency(t.amount) }}</td>
              <td><span class="badge" :class="renewalClass(t.renewal_date)">{{ t.renewal_date }}</span></td>
              <td><span class="badge badge-blue">{{ t.business_type }}</span></td>
            </tr>
            <tr v-if="!recentTx.length"><td colspan="5" class="empty-cell">No transactions</td></tr>
          </tbody>
        </table>
      </div>

      <!-- Commission Summary -->
      <div class="panel-card">
        <div class="panel-header">
          <div>
            <div class="panel-title">Commission Summary</div>
            <div class="panel-desc">Per customer commission earned</div>
          </div>
          <router-link to="/commission" class="btn btn-ghost btn-sm">View →</router-link>
        </div>
        <div v-if="loading" style="padding:16px;">
          <div class="skeleton" style="height:52px;margin-bottom:8px;border-radius:4px;" v-for="i in 3" :key="i"></div>
        </div>
        <div v-else>
          <div class="comm-row" v-for="c in commissionData" :key="c.customer">
            <div class="comm-avatar">{{ initials(c.customer) }}</div>
            <div class="comm-body">
              <div class="comm-name">{{ c.customer }}</div>
              <div class="comm-meta">{{ c.commission_rate }}% · {{ c.total_transactions }} tx</div>
              <div class="bar-wrap"><div class="bar-fill" :style="{ width: barWidth(c.total_commission) }"></div></div>
            </div>
            <div class="comm-amount">{{ fmtCurrencyShort(c.total_commission) }}</div>
          </div>
          <div v-if="!commissionData.length" class="empty-cell">No data</div>
        </div>
      </div>
    </div>

    <!-- Upcoming Renewals -->
    <div class="panel-card" style="margin-top:20px;">
      <div class="panel-header">
        <div>
          <div class="panel-title">Upcoming Renewals</div>
          <div class="panel-desc">Policies renewing in the next 90 days</div>
        </div>
        <router-link to="/renewals" class="btn btn-ghost btn-sm">View all →</router-link>
      </div>
      <div v-if="loading" style="padding:16px;">
        <div class="skeleton" style="height:40px;margin-bottom:8px;border-radius:4px;" v-for="i in 3" :key="i"></div>
      </div>
      <table class="data-table" v-else>
        <thead><tr>
          <th>Customer</th><th>Product</th><th>Policy Holder</th><th>Amount</th><th>Renewal Date</th><th>Days Left</th>
        </tr></thead>
        <tbody>
          <tr v-for="r in upcomingRenewals" :key="r.name">
            <td><router-link :to="`/customers/${r.customer}`" class="link-cell">{{ r.customer }}</router-link></td>
            <td>{{ r.product }}</td>
            <td class="fw-med">{{ r.policy_holder_name }}</td>
            <td class="amount-cell">{{ fmtCurrency(r.amount) }}</td>
            <td>{{ r.renewal_date }}</td>
            <td><span class="badge" :class="daysClass(r.renewal_date)">{{ daysLeft(r.renewal_date) }}d</span></td>
          </tr>
          <tr v-if="!upcomingRenewals.length"><td colspan="6" class="empty-cell">No upcoming renewals in 90 days</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const loading = ref(true)
const recentTx = ref([])
const commissionData = ref([])
const upcomingRenewals = ref([])

const kpis = ref([
  { label: 'Total Customers', value: '—', icon: svgUsers(), iconBg: 'rgba(59,91,219,0.12)', trend: '', up: true },
  { label: 'Transactions',    value: '—', icon: svgDoc(),   iconBg: 'rgba(6,182,212,0.12)',  trend: '', up: true },
  { label: 'Total Volume',    value: '—', icon: svgMoney(), iconBg: 'rgba(16,185,129,0.12)', trend: '', up: true },
  { label: 'Commission',      value: '—', icon: svgPct(),   iconBg: 'rgba(245,158,11,0.12)', trend: '', up: true },
])

function svgUsers() { return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#84a5f8" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>` }
function svgDoc()   { return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>` }
function svgMoney() { return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>` }
function svgPct()   { return `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>` }

function fmtCurrency(v) { return 'TZS ' + Number(v || 0).toLocaleString('en-TZ', { maximumFractionDigits: 0 }) }
function fmtCurrencyShort(v) {
  const n = Number(v || 0)
  if (n >= 1000000) return 'TZS ' + (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return 'TZS ' + (n / 1000).toFixed(0) + 'K'
  return 'TZS ' + n.toLocaleString()
}
function initials(name) { return (name || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() }
function barWidth(v) {
  const max = Math.max(...commissionData.value.map(c => c.total_commission), 1)
  return Math.round((v / max) * 100) + '%'
}
function daysLeft(d) { return Math.round((new Date(d) - new Date()) / 86400000) }
function renewalClass(d) {
  const days = daysLeft(d)
  if (days < 0) return 'badge-red'
  if (days < 30) return 'badge-yellow'
  return 'badge-green'
}
function daysClass(d) {
  const days = daysLeft(d)
  if (days < 0) return 'badge-red'
  if (days < 30) return 'badge-yellow'
  return 'badge-blue'
}

onMounted(async () => {
  try {
    const [txList, custList] = await Promise.all([
      api.list('Insurance Transaction', {
        fields: ['name','customer','policy_holder_name','amount','renewal_date','business_type','product','commission_amount'],
        order_by: 'creation desc', limit: 10,
      }),
      api.list('Bavic Customer', { fields: ['name'], limit: 100 }),
    ])
    recentTx.value = txList.slice(0, 5)
    const totalAmount = txList.reduce((s, t) => s + (t.amount || 0), 0)
    const totalComm   = txList.reduce((s, t) => s + (t.commission_amount || 0), 0)
    kpis.value[0].value = custList.length.toString(); kpis.value[0].trend = custList.length + ' total'
    kpis.value[1].value = txList.length.toString();   kpis.value[1].trend = txList.length + ' records'
    kpis.value[2].value = fmtCurrencyShort(totalAmount); kpis.value[2].trend = 'Total'
    kpis.value[3].value = fmtCurrencyShort(totalComm);   kpis.value[3].trend = 'Total'
    try {
      const report = await api.report('Customer Commission and Renewal Summary')
      commissionData.value = (report.result || []).slice(0, 5)
    } catch (_) {}
    const today = new Date().toISOString().split('T')[0]
    const in90 = new Date(Date.now() + 90 * 86400000).toISOString().split('T')[0]
    upcomingRenewals.value = txList.filter(t => t.renewal_date >= today && t.renewal_date <= in90)
      .sort((a, b) => a.renewal_date.localeCompare(b.renewal_date))
  } catch (e) {
    console.error('Dashboard error', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}
.stat-top { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 16px; }
.stat-icon {
  width: 40px; height: 40px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
}
.stat-value { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.stat-label { font-size: 12px; color: var(--text-secondary); }
.stat-trend { display: flex; align-items: center; gap: 3px; font-size: 11px; font-weight: 600; color: var(--success); }
.stat-trend.down { color: var(--danger); }

.dash-grid { display: grid; grid-template-columns: 1.4fr 1fr; gap: 16px; }

.panel-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.panel-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}
.panel-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 2px; }
.panel-desc  { font-size: 12px; color: var(--text-secondary); }
.btn-sm { font-size: 12px; padding: 5px 10px; }

.amount-cell { font-family: monospace; font-size: 12px; color: var(--primary-300); }
.fw-med { font-weight: 600; }
.link-cell { color: var(--primary-300); font-weight: 500; }
.link-cell:hover { text-decoration: underline; }
.empty-cell { text-align: center; color: var(--text-muted); padding: 40px !important; font-size: 13px; }

/* Commission rows */
.comm-row {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border-subtle);
}
.comm-row:last-child { border-bottom: none; }
.comm-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, var(--primary-500), var(--accent-500));
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: #fff;
}
.comm-body { flex: 1; min-width: 0; }
.comm-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.comm-meta { font-size: 11px; color: var(--text-secondary); margin-bottom: 6px; }
.bar-wrap { height: 3px; background: rgba(255,255,255,0.05); border-radius: 99px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, var(--primary-500), var(--accent-500)); }
.comm-amount { font-size: 12px; font-weight: 700; color: var(--primary-300); white-space: nowrap; }

@media (max-width: 1100px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
  .dash-grid { grid-template-columns: 1fr; }
}
</style>
