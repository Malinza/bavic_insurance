import frappe
from frappe.utils import getdate, nowdate, add_days, add_months, flt

def execute(filters=None):
	if not filters:
		filters = {}

	period = filters.get("period", "Monthly")
	from_date, to_date = get_date_range(filters)

	columns = get_columns()
	data = get_data(filters, from_date, to_date)
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
			"label": "Transaction ID",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Insurance Transaction",
			"width": 140
		},
		{
			"label": "Client Name",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200
		},
		{
			"label": "Insurance Type",
			"fieldname": "product",
			"fieldtype": "Link",
			"options": "Insurance Product",
			"width": 150
		},
		{
			"label": "Number of Members",
			"fieldname": "members_count",
			"fieldtype": "Int",
			"width": 140
		},
		{
			"label": "Posting Date",
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": "Premium (TZS)",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Commission (TZS)",
			"fieldname": "commission_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Company Share",
			"fieldname": "company_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Agent Share",
			"fieldname": "agent_amount",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Agent / SFE",
			"fieldname": "intermediary",
			"fieldtype": "Link",
			"options": "Agent",
			"width": 160
		},
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 120
		}
	]

def get_data(filters, from_date, to_date):
	conditions = ["t.posting_date >= %(from_date)s AND t.posting_date <= %(to_date)s"]
	values = {"from_date": from_date, "to_date": to_date}

	if filters.get("customer"):
		conditions.append("t.customer = %(customer)s")
		values["customer"] = filters.get("customer")

	if filters.get("product"):
		conditions.append("t.product = %(product)s")
		values["product"] = filters.get("product")

	if filters.get("agent_sfe"):
		conditions.append("t.intermediary = %(agent_sfe)s")
		values["agent_sfe"] = filters.get("agent_sfe")

	where_clause = "WHERE " + " AND ".join(conditions)

	query = f"""
		SELECT 
			t.name,
			t.customer,
			t.product,
			t.posting_date,
			t.amount,
			t.commission_amount,
			t.company_amount,
			t.agent_amount,
			t.intermediary,
			COALESCE((SELECT COUNT(ph.name) FROM `tabPolicy Holder Detail` ph WHERE ph.parent = t.customer), 1) as members_count,
			'Active' as status
		FROM 
			`tabInsurance Transaction` t
		{where_clause} AND (t.business_type LIKE '%%New%%' OR t.business_type IS NULL OR t.business_type = '')
		ORDER BY 
			t.posting_date DESC
	"""
	return frappe.db.sql(query, values, as_dict=True)

def get_chart(data, period):
	if not data:
		return None

	bucket_sums = {}
	for d in data:
		bkey = get_date_bucket(d.posting_date, period)
		bucket_sums[bkey] = bucket_sums.get(bkey, 0.0) + flt(d.amount)

	sorted_keys = sorted(bucket_sums.keys())
	values = [bucket_sums[k] for k in sorted_keys]

	return {
		"data": {
			"labels": sorted_keys,
			"datasets": [{"name": "New Business Premium (TZS)", "values": values}]
		},
		"type": "bar",
		"colors": ["#3b5bdb"]
	}

def get_report_summary(data):
	if not data:
		return []

	tot_tx = len(data)
	tot_premium = sum(flt(d.amount) for d in data)
	tot_comm = sum(flt(d.commission_amount) for d in data)
	tot_members = sum(int(d.members_count or 1) for d in data)

	return [
		{"value": tot_tx, "indicator": "Blue", "label": "New Business Count", "datatype": "Int"},
		{"value": tot_members, "indicator": "Teal", "label": "Members Covered", "datatype": "Int"},
		{"value": tot_premium, "indicator": "Blue", "label": "Total Premium (TZS)", "datatype": "Currency"},
		{"value": tot_comm, "indicator": "Green", "label": "Total Commission (TZS)", "datatype": "Currency"}
	]
