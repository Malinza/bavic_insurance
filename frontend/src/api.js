// Frappe API adapter — uses Frappe's own REST /api/method & /api/resource
// In dev, this hits the proxy (configured in vite.config.js)
// In production, Frappe serves both the API and the built assets

const BASE = '/api'

async function request(method, url, body = null) {
  const opts = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': getCsrf(),
    },
    credentials: 'include',
  }
  if (body) opts.body = JSON.stringify(body)
  const res = await fetch(url, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }))
    throw new Error(err.message || 'Request failed')
  }
  return res.json()
}

function getCsrf() {
  // Frappe sets frappe.csrf_token in the page context
  if (typeof frappe !== 'undefined' && frappe.csrf_token) return frappe.csrf_token
  // Fallback: read from cookie
  const m = document.cookie.match(/csrftoken=([^;]+)/)
  return m ? m[1] : ''
}

// ─── Resource API ────────────────────────────────────────────────────────────

export const api = {
  // List documents
  async list(doctype, opts = {}) {
    const params = new URLSearchParams({
      fields: JSON.stringify(opts.fields || ['name', 'creation', 'modified']),
      limit: opts.limit || 50,
      ...(opts.filters ? { filters: JSON.stringify(opts.filters) } : {}),
      ...(opts.order_by ? { order_by: opts.order_by } : {}),
    })
    const data = await request('GET', `${BASE}/resource/${encodeURIComponent(doctype)}?${params}`)
    return data.data
  },

  // Get single document
  async get(doctype, name) {
    const data = await request('GET', `${BASE}/resource/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`)
    return data.data
  },

  // Create
  async create(doctype, doc) {
    const data = await request('POST', `${BASE}/resource/${encodeURIComponent(doctype)}`, doc)
    return data.data
  },

  // Update
  async update(doctype, name, doc) {
    const data = await request('PUT', `${BASE}/resource/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`, doc)
    return data.data
  },

  // Delete
  async delete(doctype, name) {
    return request('DELETE', `${BASE}/resource/${encodeURIComponent(doctype)}/${encodeURIComponent(name)}`)
  },

  // Call whitelisted method
  async call(method, args = {}) {
    const data = await request('POST', `${BASE}/method/${method}`, args)
    return data.message
  },

  // Script report
  async report(reportName, filters = {}) {
    const params = new URLSearchParams({
      report_name: reportName,
      filters: JSON.stringify(filters),
    })
    const data = await request('GET', `${BASE}/method/frappe.desk.query_report.run?${params}`)
    return data.message
  },
}

export default api
