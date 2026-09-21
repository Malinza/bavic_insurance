import frappe
from frappe.utils import getdate, nowdate, add_days, add_months, flt

def execute(filters=None):
	if not filters:
		filters = {}

	from_date, to_date = get_date_range(filters)

	columns = get_columns()
	data, message, chart, report_summary = get_data(filters, from_date, to_date)
	
	return columns, data, message, chart, report_summary

def get_date_range(filters):
	period = filters.get("period", "Monthly")
	today = getdate(nowdate())

	if filters.get("from_date") and filters.get("to_date"):
		return getdate(filters.get("from_date")), getdate(filters.get("to_date"))

	if period == "Daily":
		return today, today
	elif period == "Weekly":
		return add_days(today, -7), today
	elif period == "Monthly":
		start = today.replace(day=1)
		return start, today
	elif period == "Quarterly":
		quarter_month = ((today.month - 1) // 3) * 3 + 1
		start = today.replace(month=quarter_month, day=1)
		return start, today
	elif period == "Yearly":
		start = today.replace(month=1, day=1)
		return start, today
	
	return add_months(today, -1), today

def get_columns():
	return [
		{
			"label": "Section",
			"fieldname": "section",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": "Client / Title",
			"fieldname": "client_name",
			"fieldtype": "Data",
			"width": 200
		},
		{
			"label": "Insurance / Claim Type",
			"fieldname": "type",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"label": "Date / Renewal Date",
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Members",
			"fieldname": "members_count",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": "Premium / Amount (TZS)",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Total Commission (TZS)",
			"fieldname": "commission_amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Company Share (TZS)",
			"fieldname": "company_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Agent Share (TZS)",
			"fieldname": "agent_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Status / Outcome",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": "Created By",
			"fieldname": "owner",
			"fieldtype": "Link",
			"options": "User",
			"width": 140
		},
		{
			"label": "Created At",
			"fieldname": "creation",
			"fieldtype": "Datetime",
			"width": 160
		}
	]

def get_data(filters, from_date, to_date):
	data = []
	cust_filter = filters.get("customer")

	# 1. Executive Summary
	tx_where = ["posting_date >= %(from_date)s AND posting_date <= %(to_date)s"]
	tx_vals = {"from_date": from_date, "to_date": to_date}
	if cust_filter:
		tx_where.append("customer = %(customer)s")
		tx_vals["customer"] = cust_filter
	tx_clause = "WHERE " + " AND ".join(tx_where)

	tx_stats = frappe.db.sql(f"""
		SELECT 
			COUNT(name) as total_tx,
			COALESCE(SUM(amount), 0.0) as total_premium,
			COALESCE(SUM(commission_amount), 0.0) as total_comm,
			COALESCE(SUM(company_amount), 0.0) as comp_comm,
			COALESCE(SUM(agent_amount), 0.0) as agent_comm
		FROM `tabInsurance Transaction`
		{tx_clause}
	""", tx_vals, as_dict=True)[0]

	clm_where = ["claim_date >= %(from_date)s AND claim_date <= %(to_date)s"]
	clm_vals = {"from_date": from_date, "to_date": to_date}
	if cust_filter:
		clm_where.append("customer = %(customer)s")
		clm_vals["customer"] = cust_filter
	clm_clause = "WHERE " + " AND ".join(clm_where)

	clm_stats = frappe.db.sql(f"""
		SELECT COUNT(name) as count, COALESCE(SUM(amount), 0.0) as total
		FROM `tabInsurance Claim` {clm_clause}
	""", clm_vals, as_dict=True)[0]

	vst_where = ["visit_date >= %(from_date)s AND visit_date <= %(to_date)s"]
	vst_vals = {"from_date": from_date, "to_date": to_date}
	if cust_filter:
		vst_where.append("customer = %(customer)s")
		vst_vals["customer"] = cust_filter
	vst_clause = "WHERE " + " AND ".join(vst_where)

	vst_stats = frappe.db.sql(f"""
		SELECT COUNT(name) as count FROM `tabClient Visit` {vst_clause}
	""", vst_vals, as_dict=True)[0]

	# Executive Summary Header Row
	data.append({
		"section": "1. EXECUTIVE SUMMARY",
		"client_name": f"Reporting Period: {from_date} to {to_date}",
		"status": "Summary"
	})
	data.append({
		"section": "1. EXECUTIVE SUMMARY",
		"client_name": "Total Premium Generated",
		"amount": tx_stats.total_premium,
		"commission_amount": tx_stats.total_comm,
		"company_amount": tx_stats.comp_comm,
		"agent_amount": tx_stats.agent_comm,
		"status": f"{tx_stats.total_tx} Policies"
	})
	data.append({
		"section": "1. EXECUTIVE SUMMARY",
		"client_name": "Claims & Client Engagements",
		"amount": clm_stats.total,
		"status": f"{clm_stats.count} Claims, {vst_stats.count} Visits"
	})
	data.append({})

	# 2. New Business Acquired
	data.append({"section": "2. NEW BUSINESS ACQUIRED"})
	new_biz = frappe.db.sql(f"""
		SELECT t.customer, t.product, t.amount, t.commission_amount, t.company_amount, t.agent_amount, t.posting_date,
		       t.owner, t.creation,
		       (SELECT COUNT(name) FROM `tabPolicy Holder Detail` ph WHERE ph.parent = t.customer) as members
		FROM `tabInsurance Transaction` t
		{tx_clause} AND t.business_type LIKE '%%New%%'
		ORDER BY t.posting_date DESC
	""", tx_vals, as_dict=True)

	for row in new_biz:
		data.append({
			"section": "2. NEW BUSINESS ACQUIRED",
			"client_name": row.customer,
			"type": row.product,
			"date": row.posting_date,
			"members_count": row.members or 1,
			"amount": row.amount,
			"commission_amount": row.commission_amount,
			"company_amount": row.company_amount,
			"agent_amount": row.agent_amount,
			"status": "Active",
			"owner": row.owner,
			"creation": row.creation
		})
	data.append({})

	# 3. Policy Renewals
	data.append({"section": "3. POLICY RENEWALS"})
	renewals = frappe.db.sql(f"""
		SELECT customer, product, renewal_date, amount, commission_amount, company_amount, agent_amount, owner, creation
		FROM `tabInsurance Transaction`
		{tx_clause} AND (business_type LIKE '%%Renewal%%' OR renewal_date <= %(to_date)s)
		ORDER BY renewal_date DESC
	""", tx_vals, as_dict=True)

	for r in renewals:
		data.append({
			"section": "3. POLICY RENEWALS",
			"client_name": r.customer,
			"type": r.product,
			"date": r.renewal_date,
			"amount": r.amount,
			"commission_amount": r.commission_amount,
			"company_amount": r.company_amount,
			"agent_amount": r.agent_amount,
			"status": "Renewed",
			"owner": r.owner,
			"creation": r.creation
		})
	data.append({})

	# 4. Claims Report
	data.append({"section": "4. CLAIMS REPORT"})
	claims = frappe.db.sql(f"""
		SELECT customer, claim_type, amount, status, claim_date, owner, creation
		FROM `tabInsurance Claim`
		{clm_clause}
		ORDER BY claim_date DESC
	""", clm_vals, as_dict=True)

	for c in claims:
		data.append({
			"section": "4. CLAIMS REPORT",
			"client_name": c.customer,
			"type": c.claim_type,
			"date": c.claim_date,
			"amount": c.amount,
			"status": c.status,
			"owner": c.owner,
			"creation": c.creation
		})
	data.append({})

	# 5. Client Visits and Meetings
	data.append({"section": "5. CLIENT VISITS & MEETINGS"})
	visits = frappe.db.sql(f"""
		SELECT customer, purpose_of_visit, outcome, visit_date, owner, creation
		FROM `tabClient Visit`
		{vst_clause}
		ORDER BY visit_date DESC
	""", vst_vals, as_dict=True)

	for v in visits:
		data.append({
			"section": "5. CLIENT VISITS & MEETINGS",
			"client_name": v.customer,
			"type": v.purpose_of_visit,
			"date": v.visit_date,
			"status": v.outcome,
			"owner": v.owner,
			"creation": v.creation
		})
	data.append({})

	# 6. Financial Summary
	data.append({
		"section": "6. FINANCIAL SUMMARY",
		"client_name": "Total Premium Generated",
		"amount": tx_stats.total_premium
	})
	data.append({
		"section": "6. FINANCIAL SUMMARY",
		"client_name": "Total Commission Earned",
		"commission_amount": tx_stats.total_comm
	})
	data.append({
		"section": "6. FINANCIAL SUMMARY",
		"client_name": "Company Commission Share",
		"company_amount": tx_stats.comp_comm
	})
	data.append({
		"section": "6. FINANCIAL SUMMARY",
		"client_name": "Agent Commission Share",
		"agent_amount": tx_stats.agent_comm
	})
	data.append({})

	# 7. Recommendations
	data.append({"section": "7. RECOMMENDATIONS & ACTION ITEMS"})
	recs = frappe.db.get_all("Business Recommendation", fields=["title", "category", "priority", "status", "description", "owner", "creation"])
	for rec in recs:
		data.append({
			"section": "7. RECOMMENDATIONS",
			"client_name": rec.title,
			"type": rec.category,
			"status": f"{rec.priority} | {rec.status}",
			"owner": rec.owner,
			"creation": rec.creation
		})

	# Chart Data
	chart = {
		"data": {
			"labels": ["Total Premium", "Total Commission", "Company Share", "Agent Share"],
			"datasets": [
				{
					"name": "Financial Overview (TZS)",
					"values": [
						tx_stats.total_premium,
						tx_stats.total_comm,
						tx_stats.comp_comm,
						tx_stats.agent_comm
					]
				}
			]
		},
		"type": "bar",
		"colors": ["#3b5bdb", "#22d3ee", "#10b981", "#f59e0b"]
	}

	# Report Summary Cards
	report_summary = [
		{"value": tx_stats.total_premium, "indicator": "Blue", "label": "Total Premium (TZS)", "datatype": "Currency"},
		{"value": tx_stats.total_comm, "indicator": "Green", "label": "Total Commission (TZS)", "datatype": "Currency"},
		{"value": tx_stats.comp_comm, "indicator": "Teal", "label": "Company Share (TZS)", "datatype": "Currency"},
		{"value": tx_stats.agent_comm, "indicator": "Orange", "label": "Agent Share (TZS)", "datatype": "Currency"},
	]

	message = f"<b>Period:</b> {from_date} to {to_date} | <b>Policies:</b> {tx_stats.total_tx} | <b>Claims:</b> {clm_stats.count}"

	return data, message, chart, report_summary
