import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Dashboard' },
  },
  {
    path: '/customers',
    component: () => import('@/views/Customers.vue'),
    meta: { title: 'Customers' },
  },
  {
    path: '/customers/:name',
    component: () => import('@/views/CustomerDetail.vue'),
    meta: { title: 'Customer Detail' },
  },
  {
    path: '/transactions',
    component: () => import('@/views/Transactions.vue'),
    meta: { title: 'Transactions' },
  },
  {
    path: '/commission',
    component: () => import('@/views/CommissionReport.vue'),
    meta: { title: 'Commission Report' },
  },
  {
    path: '/renewals',
    component: () => import('@/views/RenewalHistory.vue'),
    meta: { title: 'Renewal History' },
  },
  {
    path: '/masters',
    component: () => import('@/views/Masters.vue'),
    meta: { title: 'Masters' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || 'BAVIC'} — BAVIC Insurance`
})

export default router
