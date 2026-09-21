<template>
  <div class="page-container">
    <div class="masters-grid">
      <div class="panel-card master-card" v-for="m in masters" :key="m.doctype">
        <!-- Card top -->
        <div class="master-top">
          <div class="master-icon" :style="{ background: m.iconBg }">
            <span v-html="m.icon"></span>
          </div>
          <div class="master-info">
            <div class="master-title">{{ m.label }}</div>
            <div class="master-desc">{{ m.desc }}</div>
            <div class="master-count">
              <span v-if="loading" class="skeleton" style="height:12px;width:60px;display:inline-block;border-radius:4px;"></span>
              <span v-else class="badge badge-blue">{{ counts[m.doctype] || 0 }} records</span>
            </div>
          </div>
        </div>

        <!-- Divider -->
        <div style="height:1px;background:var(--border-subtle);"></div>

        <!-- Preview list -->
        <div class="master-preview">
          <div v-if="loading">
            <div class="skeleton" style="height:30px;margin-bottom:8px;border-radius:4px;" v-for="i in 2" :key="i"></div>
          </div>
          <template v-else>
            <div class="preview-row" v-for="item in (previews[m.doctype] || [])" :key="item.name">
              <span class="preview-dot" :style="{ background: m.dotColor }"></span>
              <span class="preview-name">{{ getLabel(item, m.labelField) }}</span>
            </div>
            <div class="preview-more" v-if="(counts[m.doctype] || 0) > 3">
              +{{ counts[m.doctype] - 3 }} more
            </div>
            <div class="preview-empty" v-if="!(previews[m.doctype] || []).length">No records</div>
          </template>
        </div>

        <!-- Footer action -->
        <div style="height:1px;background:var(--border-subtle);"></div>
        <div class="master-footer">
          <a :href="`/app/${m.route}`" class="btn btn-ghost" style="width:100%;justify-content:center;font-size:12px;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
            Open in Frappe Desk
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const loading = ref(true)
const counts  = ref({})
const previews = ref({})

const masters = [
  {
    doctype: 'Business Type',
    label: 'Business Types',
    desc: 'Policy categories (New Business, Renewal…)',
    route: 'business-type',
    labelField: 'business_type_name',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#818cf8" stroke-width="2.5"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/></svg>`,
    iconBg: 'rgba(79,70,229,.12)',
    dotColor: '#818cf8',
  },
  {
    doctype: 'Insurance Product',
    label: 'Insurance Products',
    desc: 'Product catalogue (SME IBIZ, Motor…)',
    route: 'insurance-product',
    labelField: 'product_name',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="2.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>`,
    iconBg: 'rgba(6,182,212,.12)',
    dotColor: '#22d3ee',
  },
  {
    doctype: 'Intermediary Type',
    label: 'Intermediary Types',
    desc: 'Broker and agent categories',
    route: 'intermediary-type',
    labelField: 'type_name',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>`,
    iconBg: 'rgba(16,185,129,.12)',
    dotColor: '#4ade80',
  },
  {
    doctype: 'Intermediary',
    label: 'Intermediaries',
    desc: 'Agency and broker registry',
    route: 'intermediary',
    labelField: 'intermediary_name',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`,
    iconBg: 'rgba(245,158,11,.12)',
    dotColor: '#fbbf24',
  },
  {
    doctype: 'Customer Commission Rate',
    label: 'Commission Rates',
    desc: 'Per-customer commission percentages',
    route: 'customer-commission-rate',
    labelField: 'customer',
    icon: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f87171" stroke-width="2.5"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>`,
    iconBg: 'rgba(239,68,68,.10)',
    dotColor: '#f87171',
  },
]

function getLabel(item, field) { return item[field] || item.name }

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all(masters.map(async m => {
      const items = await api.list(m.doctype, { fields: ['name', m.labelField], limit: 4 })
      counts.value[m.doctype]   = items.length
      previews.value[m.doctype] = items.slice(0, 3)
    }))
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<style scoped>
.masters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.panel-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.panel-card:hover { border-color: var(--border-muted); }

.master-top {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 20px;
}
.master-icon {
  width: 40px; height: 40px; border-radius: var(--radius-md); flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.master-info { flex: 1; min-width: 0; }
.master-title { font-size: 14px; font-weight: 700; color: var(--text-primary); margin-bottom: 3px; }
.master-desc  { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; line-height: 1.4; }
.master-count { }

.master-preview {
  padding: 14px 20px; flex: 1;
  display: flex; flex-direction: column; gap: 2px;
}
.preview-row { display: flex; align-items: center; gap: 8px; padding: 5px 0; }
.preview-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.preview-name { font-size: 12px; color: var(--text-secondary); font-weight: 500; }
.preview-more  { font-size: 11px; color: var(--text-muted); margin-top: 4px; font-weight: 600; }
.preview-empty { font-size: 12px; color: var(--text-muted); font-style: italic; }

.master-footer { padding: 12px; }
</style>
