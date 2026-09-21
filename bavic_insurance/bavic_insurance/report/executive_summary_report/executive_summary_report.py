import frappe
from frappe.utils import getdate, nowdate, add_days, add_months, flt

def execute(filters=None):
	if not filters:
		filters = {}

	period = filters.get("period", "Monthly")
	from_date, to_date = get_date_range(filters)

	columns = get_columns()
	data = get_data(filters, period, from_date, to_date)
	chart = get_chart(data, period)
	report_summary = get_report_summary(data)
	
	return columns, data, None, chart, report_summary

def get_date_range(filters):
	period = filters.get("period", "Monthly")
	today = getdate(nowdate())

	if filters.get("from_date") and filters.get("to_date"):
		return getdate(filters.get("from_date")), getdate(filters.get("to_date"))

	if period == "Daily":
		return add_days(today, -30), today
	elif period == "Weekly":
		return add_days(today, -90), today
	elif period == "Monthly":
		start = today.replace(month=1, day=1)
		return start, today
	elif period == "Quarterly":
		return add_months(today, -12), today
	elif period == "Yearly":
		return add_months(today, -36), today
	
	return add_months(today, -12), today

def get_date_bucket(date_val, period):
	d = getdate(date_val)
	if period == "Daily":
		return d.strftime("%Y-%m-%d")
	elif period == "Weekly":
		year, week, _ = d.isocalendar()
		return f"{year}-W{week:02d}"
	elif period == "Monthly":
		return d.strftime("%Y-%m")
	elif period == "Quarterly":
		q = ((d.month - 1) // 3) + 1
		return f"{d.year}-Q{q}"
	elif period == "Yearly":
		return str(d.year)
	return d.strftime("%Y-%m")

def get_columns():
	return [
		{
			"label": "Time Period",
			"fieldname": "period_bucket",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": "Policies Issued",
			"fieldname": "total_policies",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": "New Business",
			"fieldname": "new_business_count",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": "Renewals",
			"fieldname": "renewals_count",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": "Claims Handled",
			"fieldname": "claims_count",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": "Client Visits",
			"fieldname": "visits_count",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": "Total Premium (TZS)",
			"fieldname": "total_premium",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Gross Commission (TZS)",
			"fieldname": "total_commission",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Withholding Tax (TZS)",
			"fieldname": "withholding_tax",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Net Commission (TZS)",
			"fieldname": "net_commission",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Company Share (TZS)",
			"fieldname": "company_share",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Agent Share (TZS)",
			"fieldname": "agent_share",
			"fieldtype": "Currency",
			"width": 150
		}
	]

def get_data(filters, period, from_date, to_date):
	cust_filter = filters.get("customer")

	tx_where = ["posting_date >= %(from_date)s AND posting_date <= %(to_date)s"]
	tx_vals = {"from_date": from_date, "to_date": to_date}
	if cust_filter:
		tx_where.append("customer = %(customer)s")
		tx_vals["customer"] = cust_filter
	tx_clause = "WHERE " + " AND ".join(tx_where)

	tx_rows = frappe.db.sql(f"""
		SELECT name, posting_date, amount, commission_amount, withholding_tax_amount, net_commission_amount, company_amount, agent_amount, business_type
		FROM `tabInsurance Transaction`
		{tx_clause}
		ORDER BY posting_date ASC
	""", tx_vals, as_dict=True)

	clm_where = ["claim_date >= %(from_date)s AND claim_date <= %(to_date)s"]
	clm_vals = {"from_date": from_date, "to_date": to_date}
	if cust_filter:
		clm_where.append("customer = %(customer)s")
		clm_vals["customer"] = cust_filter
	clm_clause = "WHERE " + " AND ".join(clm_where)

	clm_rows = frappe.db.sql(f"""
		SELECT name, claim_date FROM `tabInsurance Claim` {clm_clause}
	""", clm_vals, as_dict=True)

	vst_where = ["visit_date >= %(from_date)s AND visit_date <= %(to_date)s"]
	vst_vals = {"from_date": from_date, "to_date": to_date}
	if cust_filter:
		vst_where.append("customer = %(customer)s")
		vst_vals["customer"] = cust_filter
	vst_clause = "WHERE " + " AND ".join(vst_where)

	vst_rows = frappe.db.sql(f"""
		SELECT name, visit_date FROM `tabClient Visit` {vst_clause}
	""", vst_vals, as_dict=True)

	# Group by Date Bucket
	buckets = {}

	for tx in tx_rows:
		bkey = get_date_bucket(tx.posting_date, period)
		if bkey not in buckets:
			buckets[bkey] = {
				"period_bucket": bkey, "total_policies": 0, "new_business_count": 0,
				"renewals_count": 0, "claims_count": 0, "visits_count": 0,
				"total_premium": 0.0, "total_commission": 0.0, "withholding_tax": 0.0,
				"net_commission": 0.0, "company_share": 0.0, "agent_share": 0.0
			}
		b = buckets[bkey]
		b["total_policies"] += 1
		b["total_premium"] += flt(tx.amount)
		comm = flt(tx.commission_amount)
		wht = flt(tx.withholding_tax_amount)
		net_comm = flt(tx.net_commission_amount) if tx.net_commission_amount is not None else (comm - wht)
		
		b["total_commission"] += comm
		b["withholding_tax"] += wht
		b["net_commission"] += net_comm
		b["company_share"] += flt(tx.company_amount)
		b["agent_share"] += flt(tx.agent_amount)
		
		btype = str(tx.business_type or "").lower()
		if "new" in btype:
			b["new_business_count"] += 1
		elif "renewal" in btype:
			b["renewals_count"] += 1

	for clm in clm_rows:
		bkey = get_date_bucket(clm.claim_date, period)
		if bkey not in buckets:
			buckets[bkey] = {
				"period_bucket": bkey, "total_policies": 0, "new_business_count": 0,
				"renewals_count": 0, "claims_count": 0, "visits_count": 0,
				"total_premium": 0.0, "total_commission": 0.0, "withholding_tax": 0.0,
				"net_commission": 0.0, "company_share": 0.0, "agent_share": 0.0
			}
		buckets[bkey]["claims_count"] += 1

	for vst in vst_rows:
		bkey = get_date_bucket(vst.visit_date, period)
		if bkey not in buckets:
			buckets[bkey] = {
				"period_bucket": bkey, "total_policies": 0, "new_business_count": 0,
				"renewals_count": 0, "claims_count": 0, "visits_count": 0,
				"total_premium": 0.0, "total_commission": 0.0, "withholding_tax": 0.0,
				"net_commission": 0.0, "company_share": 0.0, "agent_share": 0.0
			}
		buckets[bkey]["visits_count"] += 1

	sorted_keys = sorted(buckets.keys())
	return [buckets[k] for k in sorted_keys]

def get_chart(data, period):
	if not data:
		return None

	labels = [d["period_bucket"] for d in data]
	premiums = [d["total_premium"] for d in data]
	commissions = [d["total_commission"] for d in data]
	whts = [d["withholding_tax"] for d in data]
	net_comms = [d["net_commission"] for d in data]
	company_shares = [d["company_share"] for d in data]
	agent_shares = [d["agent_share"] for d in data]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Total Premium", "values": premiums},
				{"name": "Gross Commission", "values": commissions},
				{"name": "Withholding Tax", "values": whts},
				{"name": "Net Commission", "values": net_comms},
				{"name": "Company Share", "values": company_shares},
				{"name": "Agent Share", "values": agent_shares}
			]
		},
		"type": "bar",
		"colors": ["#3b5bdb", "#22d3ee", "#ef4444", "#10b981", "#8b5cf6", "#f59e0b"]
	}

def get_report_summary(data):
	if not data:
		return []

	tot_policies = sum(d["total_policies"] for d in data)
	tot_premium = sum(d["total_premium"] for d in data)
	tot_comm = sum(d["total_commission"] for d in data)
	tot_wht = sum(d["withholding_tax"] for d in data)
	tot_net = sum(d["net_commission"] for d in data)
	tot_comp = sum(d["company_share"] for d in data)
	tot_agent = sum(d["agent_share"] for d in data)

	return [
		{"value": tot_policies, "indicator": "Blue", "label": "Total Policies Issued", "datatype": "Int"},
		{"value": tot_premium, "indicator": "Blue", "label": "Total Premium (TZS)", "datatype": "Currency"},
		{"value": tot_comm, "indicator": "Teal", "label": "Gross Commission (TZS)", "datatype": "Currency"},
		{"value": tot_wht, "indicator": "Red", "label": "Withholding Tax (TZS)", "datatype": "Currency"},
		{"value": tot_net, "indicator": "Green", "label": "Net Commission (TZS)", "datatype": "Currency"},
		{"value": tot_comp, "indicator": "Purple", "label": "Company Share (TZS)", "datatype": "Currency"},
		{"value": tot_agent, "indicator": "Orange", "label": "Agent Share (TZS)", "datatype": "Currency"}
	]
