<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <svg width="24" height="24" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="6" fill="#3b5bdb"/>
            <path d="M16 6L8 11v6c0 4.4 3.4 8.5 8 9.5 4.6-1 8-5.1 8-9.5v-6L16 6z" fill="white" opacity="0.95"/>
          </svg>
        </div>
        <Transition name="fade">
          <div class="logo-text" v-if="!sidebarCollapsed">
            <span class="logo-name">BAVIC</span>
            <span class="logo-sub">Insurance Portal</span>
          </div>
        </Transition>
        <button class="collapse-btn" @click="sidebarCollapsed = !sidebarCollapsed" :title="sidebarCollapsed ? 'Expand' : 'Collapse'">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path v-if="!sidebarCollapsed" d="M15 18l-6-6 6-6"/>
            <path v-else d="M9 18l6-6-6-6"/>
          </svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-group">
          <span class="nav-group-label" v-if="!sidebarCollapsed">Overview</span>
          <router-link to="/dashboard" class="nav-item" :title="sidebarCollapsed ? 'Dashboard' : ''">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
            <span class="nav-label" v-if="!sidebarCollapsed">Dashboard</span>
          </router-link>
        </div>

        <div class="nav-group">
          <span class="nav-group-label" v-if="!sidebarCollapsed">Core</span>
          <router-link to="/customers" class="nav-item" :title="sidebarCollapsed ? 'Customers' : ''">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            <span class="nav-label" v-if="!sidebarCollapsed">Customers</span>
          </router-link>
          <router-link to="/transactions" class="nav-item" :title="sidebarCollapsed ? 'Transactions' : ''">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
            <span class="nav-label" v-if="!sidebarCollapsed">Transactions</span>
          </router-link>
        </div>

        <div class="nav-group">
          <span class="nav-group-label" v-if="!sidebarCollapsed">Reports</span>
          <router-link to="/commission" class="nav-item" :title="sidebarCollapsed ? 'Commission Report' : ''">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
            <span class="nav-label" v-if="!sidebarCollapsed">Commission</span>
          </router-link>
          <router-link to="/renewals" class="nav-item" :title="sidebarCollapsed ? 'Renewal History' : ''">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
            <span class="nav-label" v-if="!sidebarCollapsed">Renewals</span>
          </router-link>
        </div>

        <div class="nav-group">
          <span class="nav-group-label" v-if="!sidebarCollapsed">Configuration</span>
          <router-link to="/masters" class="nav-item" :title="sidebarCollapsed ? 'Masters' : ''">
            <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93l-1.41 1.41M4.93 4.93l1.41 1.41M12 2v2M12 20v2M4.93 19.07l1.41-1.41M18.36 18.36l1.41 1.41M2 12h2M20 12h2"/></svg>
            <span class="nav-label" v-if="!sidebarCollapsed">Masters</span>
          </router-link>
        </div>
      </nav>

      <div class="sidebar-footer" v-if="!sidebarCollapsed">
        <div class="footer-info">
          <div class="footer-version">v1.0.0</div>
          <div class="footer-brand">BAVIC Insurance</div>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="main-area">
      <!-- Topbar -->
      <header class="topbar">
        <div class="topbar-left">
          <h1 class="page-title">{{ currentTitle }}</h1>
          <div class="breadcrumb" v-if="currentDesc">{{ currentDesc }}</div>
        </div>
        <div class="topbar-right">
          <div class="topbar-badge">
            <span class="status-dot"></span>
            Live
          </div>
          <a href="/app" class="btn btn-ghost" style="font-size: 12px; padding: 6px 12px;" title="Go to Frappe Desk">
            Frappe Desk
          </a>
        </div>
      </header>

      <!-- Router outlet -->
      <main class="content-area">
        <router-view v-slot="{ Component }">
          <Transition name="page" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

const sidebarCollapsed = ref(false)
const route = useRoute()

const titleMap = {
  '/dashboard':    { title: 'Dashboard',         desc: 'Overview of your insurance portfolio' },
  '/customers':    { title: 'Customers',          desc: 'Manage customer records and policy holders' },
  '/transactions': { title: 'Transactions',       desc: 'Insurance policy transactions' },
  '/commission':   { title: 'Commission Report',  desc: 'Per-customer commission analysis' },
  '/renewals':     { title: 'Renewal History',    desc: 'Track policy renewals over time' },
  '/masters':      { title: 'Masters',            desc: 'Configure reference data' },
}

const currentTitle = computed(() => {
  const base = '/' + (route.path.split('/')[1] || 'dashboard')
  return titleMap[base]?.title || 'BAVIC Insurance'
})
const currentDesc = computed(() => {
  const base = '/' + (route.path.split('/')[1] || 'dashboard')
  return titleMap[base]?.desc || ''
})
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  background: var(--bg-base);
  overflow: hidden;
}

/* ── Sidebar ──────────────────────────────── */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-surface);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease, min-width 0.2s ease;
  position: relative;
  z-index: 10;
}
.sidebar.collapsed { width: 64px; min-width: 64px; }

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-bottom: 1px solid var(--border-subtle);
  min-height: 64px;
  position: relative;
}
.logo-icon { flex-shrink: 0; }
.logo-text { flex: 1; min-width: 0; }
.logo-name {
  display: block;
  font-weight: 700;
  font-size: 15px;
  color: var(--text-primary);
}
.logo-sub {
  display: block;
  font-size: 10px;
  color: var(--text-secondary);
}
.collapse-btn {
  position: absolute;
  right: -10px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  background: var(--bg-raised);
  border: 1px solid var(--border-subtle);
  border-radius: 50%;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
}
.collapse-btn:hover { color: var(--text-primary); }

.sidebar-nav {
  flex: 1;
  padding: 16px 8px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.nav-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 8px;
}
.nav-group-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  padding: 4px 12px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
}
.nav-item:hover {
  background: rgba(255, 255, 255, 0.02);
  color: var(--text-primary);
}
.nav-item.router-link-active {
  background: rgba(59, 91, 219, 0.1);
  color: var(--primary-300);
}
.nav-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}
.nav-label { flex: 1; }

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-subtle);
}
.footer-version { font-size: 10px; color: var(--text-muted); }
.footer-brand   { font-size: 11px; color: var(--text-secondary); font-weight: 500; }

/* ── Main area ────────────────────────────── */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.topbar {
  height: 64px;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-subtle);
  background: var(--bg-surface);
  flex-shrink: 0;
}
.page-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}
.breadcrumb { font-size: 11px; color: var(--text-secondary); }

.topbar-right { display: flex; align-items: center; gap: 12px; }
.topbar-badge {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 600; color: var(--success);
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 99px;
}
.status-dot {
  width: 6px; height: 6px;
  background: var(--success);
  border-radius: 50%;
}

.content-area {
  flex: 1;
  overflow-y: auto;
}

/* ── Transitions ──────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.page-enter-active, .page-leave-active { transition: opacity 0.15s ease, transform 0.15s ease; }
.page-enter-from { opacity: 0; transform: translateY(4px); }
.page-leave-to   { opacity: 0; transform: translateY(-4px); }
</style>
