<template>
  <div class="page-container">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="search-box">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input v-model="search" class="search-input" placeholder="Search customers..." />
      </div>
      <button class="btn btn-primary" @click="openCreate">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        New Customer
      </button>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="cust-grid">
      <div class="cust-card-skeleton" v-for="i in 6" :key="i">
        <div class="skeleton" style="height:48px;width:48px;border-radius:50%;margin-bottom:14px;"></div>
        <div class="skeleton" style="height:16px;width:70%;margin-bottom:8px;border-radius:4px;"></div>
        <div class="skeleton" style="height:12px;width:50%;margin-bottom:16px;border-radius:4px;"></div>
        <div class="skeleton" style="height:28px;border-radius:4px;"></div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="filtered.length === 0" class="empty-state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/></svg>
      <p class="empty-title">No customers found</p>
      <button class="btn btn-primary" @click="openCreate">Add first customer</button>
    </div>

    <!-- Grid -->
    <div v-else class="cust-grid">
      <div class="cust-card" v-for="c in filtered" :key="c.name" @click="goDetail(c.name)">
        <div class="cust-avatar">{{ initials(c.name) }}</div>
        <div class="cust-name">{{ c.name }}</div>
        <div class="cust-sub">{{ c.holder_count || 0 }} policy holder{{ c.holder_count !== 1 ? 's' : '' }}</div>
        <div class="cust-badges">
          <span class="badge badge-blue">{{ c.commission_rate || 0 }}% rate</span>
          <span class="badge badge-green" v-if="c.tx_count">{{ c.tx_count }} tx</span>
        </div>
        <div class="cust-footer">
          <div>
            <div class="cust-vol">{{ fmtCurrency(c.total_amount) }}</div>
            <div class="cust-vol-label">Total Volume</div>
          </div>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <Teleport to="body">
      <div class="modal-bg" v-if="showCreate" @click.self="closeCreate">
        <div class="modal">
          <div class="modal-head">
            <div>
              <div class="modal-title">New Customer</div>
              <div class="modal-sub">Register a new insurance customer</div>
            </div>
            <button class="close-btn" @click="closeCreate">✕</button>
          </div>
          <div class="form-group">
            <label class="form-label">Customer Name *</label>
            <input class="form-input" v-model="form.customer_name" placeholder="Company or individual name" />
          </div>
          <div class="divider"></div>
          <div class="holders-head">
            <span style="font-size:13px;font-weight:600;color:var(--text-primary);">Policy Holders</span>
            <button class="btn btn-ghost" style="padding:5px 10px;font-size:12px;" @click="addHolder">+ Add</button>
          </div>
          <div style="margin-top:12px;display:flex;flex-direction:column;gap:8px;">
            <div v-for="(h, i) in form.policy_holders" :key="i" class="holder-row">
              <input class="form-input" v-model="h.policy_holder_name" placeholder="Name" />
              <input class="form-input" v-model="h.email" placeholder="Email" />
              <input class="form-input" v-model="h.phone" placeholder="Phone" />
              <button class="del-btn" @click="form.policy_holders.splice(i, 1)">✕</button>
            </div>
            <div v-if="!form.policy_holders.length" class="no-holders">No policy holders added yet</div>
          </div>
          <div class="modal-foot">
            <button class="btn btn-ghost" @click="closeCreate">Cancel</button>
            <button class="btn btn-primary" @click="saveCustomer" :disabled="saving">{{ saving ? 'Saving...' : 'Save Customer' }}</button>
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'

const router = useRouter()
const loading = ref(true)
const customers = ref([])
const search = ref('')
const showCreate = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref({ customer_name: '', policy_holders: [] })

const filtered = computed(() => {
  const q = search.value.toLowerCase()
  return customers.value.filter(c => c.name.toLowerCase().includes(q))
})

function initials(name) { return (name || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase() }
function fmtCurrency(v) { return 'TZS ' + Number(v || 0).toLocaleString('en-TZ', { maximumFractionDigits: 0 }) }
function goDetail(name) { router.push('/customers/' + encodeURIComponent(name)) }
function openCreate() { showCreate.value = true }
function closeCreate() { showCreate.value = false; error.value = ''; form.value = { customer_name: '', policy_holders: [] } }
function addHolder() { form.value.policy_holders.push({ policy_holder_name: '', email: '', phone: '' }) }

async function saveCustomer() {
  if (!form.value.customer_name.trim()) { error.value = 'Customer name is required'; return }
  saving.value = true; error.value = ''
  try {
    await api.create('Bavic Customer', form.value)
    closeCreate()
    await loadCustomers()
  } catch (e) { error.value = e.message }
  finally { saving.value = false }
}

async function loadCustomers() {
  loading.value = true
  try {
    const [custList, rateList, txList] = await Promise.all([
      api.list('Bavic Customer', { fields: ['name'], limit: 200 }),
      api.list('Customer Commission Rate', { fields: ['customer','commission_rate'], limit: 200 }),
      api.list('Insurance Transaction', { fields: ['customer','amount'], limit: 500 }),
    ])
    const rateMap = {}
    rateList.forEach(r => { rateMap[r.customer] = r.commission_rate })
    const txMap = {}
    txList.forEach(t => {
      if (!txMap[t.customer]) txMap[t.customer] = { count: 0, total: 0 }
      txMap[t.customer].count++
      txMap[t.customer].total += t.amount || 0
    })
    customers.value = custList.map(c => ({
      ...c,
      commission_rate: rateMap[c.name],
      tx_count: txMap[c.name]?.count || 0,
      total_amount: txMap[c.name]?.total || 0,
      holder_count: 0,
    }))
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}
onMounted(loadCustomers)
</script>

<style scoped>
.toolbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px; gap: 12px;
}
.search-box {
  display: flex; align-items: center; gap: 10px;
  background: var(--bg-surface); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md); padding: 0 12px;
  flex: 1; max-width: 360px;
}
.search-input { background: none; border: none; outline: none; color: var(--text-primary); font-family: inherit; font-size: 13px; padding: 9px 0; flex: 1; }
.search-input::placeholder { color: var(--text-muted); }

.cust-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; }

.cust-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px;
  cursor: pointer;
}
.cust-card:hover {
  border-color: var(--border-muted);
  background: var(--bg-raised);
}

.cust-card-skeleton {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.cust-avatar {
  width: 48px; height: 48px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-500), var(--accent-500));
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700; color: #fff; margin-bottom: 14px;
}
.cust-name { font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 3px; }
.cust-sub  { font-size: 12px; color: var(--text-secondary); margin-bottom: 12px; }
.cust-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.cust-footer {
  border-top: 1px solid var(--border-subtle);
  padding-top: 12px; display: flex; align-items: center; justify-content: space-between;
  color: var(--text-muted);
}
.cust-vol       { font-size: 13px; font-weight: 700; color: var(--primary-300); }
.cust-vol-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }

.empty-state {
  padding: 64px 32px; display: flex; flex-direction: column;
  align-items: center; gap: 12px; color: var(--text-secondary); text-align: center;
  background: var(--bg-surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);
}
.empty-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }

/* Modal */
.modal-bg {
  position: fixed; inset: 0; background: rgba(0,0,0,0.6);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  width: 540px; max-width: 95vw;
  background: var(--bg-surface);
  border: 1px solid var(--border-muted);
  border-radius: var(--radius-lg);
  padding: 24px; max-height: 80vh; overflow-y: auto;
}
.modal-head { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 20px; }
.modal-title { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.modal-sub   { font-size: 12px; color: var(--text-secondary); }
.modal-foot  { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.close-btn   { background: none; border: none; color: var(--text-secondary); font-size: 16px; cursor: pointer; }
.close-btn:hover { color: var(--text-primary); }
.holders-head { display: flex; align-items: center; justify-content: space-between; }
.holder-row { display: grid; grid-template-columns: 1fr 1.2fr 1fr auto; gap: 8px; align-items: center; }
.del-btn { background: none; border: none; color: var(--danger); cursor: pointer; font-size: 14px; padding: 4px 6px; }
.no-holders { font-size: 12px; color: var(--text-muted); text-align: center; padding: 16px 0; }
.error-msg  { color: var(--danger); font-size: 12px; margin-top: 12px; }
</style>
