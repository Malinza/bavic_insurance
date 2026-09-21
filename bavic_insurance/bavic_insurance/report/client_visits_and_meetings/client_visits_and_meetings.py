import frappe
from frappe.utils import getdate, nowdate, add_days, add_months

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
			"label": "Visit ID",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Client Visit",
			"width": 140
		},
		{
			"label": "Date",
			"fieldname": "visit_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": "Client Name",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200
		},
		{
			"label": "Agent / SFE",
			"fieldname": "agent_sfe",
			"fieldtype": "Link",
			"options": "Agent",
			"width": 160
		},
		{
			"label": "Purpose of Visit",
			"fieldname": "purpose_of_visit",
			"fieldtype": "Small Text",
			"width": 220
		},
		{
			"label": "Outcome",
			"fieldname": "outcome",
			"fieldtype": "Small Text",
			"width": 220
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
	conditions = ["visit_date >= %(from_date)s AND visit_date <= %(to_date)s"]
	values = {"from_date": from_date, "to_date": to_date}

	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters.get("customer")

	if filters.get("agent_sfe"):
		conditions.append("agent_sfe = %(agent_sfe)s")
		values["agent_sfe"] = filters.get("agent_sfe")

	where_clause = "WHERE " + " AND ".join(conditions)

	query = f"""
		SELECT 
			name,
			visit_date,
			customer,
			agent_sfe,
			purpose_of_visit,
			outcome,
			owner,
			creation
		FROM 
			`tabClient Visit`
		{where_clause}
		ORDER BY 
			visit_date DESC
	"""
	return frappe.db.sql(query, values, as_dict=True)

def get_chart(data, period):
	if not data:
		return None

	bucket_counts = {}
	for d in data:
		bkey = get_date_bucket(d.visit_date, period)
		bucket_counts[bkey] = bucket_counts.get(bkey, 0) + 1

	sorted_keys = sorted(bucket_counts.keys())
	values = [bucket_counts[k] for k in sorted_keys]

	return {
		"data": {
			"labels": sorted_keys,
			"datasets": [{"name": "Number of Client Visits", "values": values}]
		},
		"type": "bar",
		"colors": ["#8b5cf6"]
	}

def get_report_summary(data):
	if not data:
		return []

	tot_visits = len(data)
	unique_clients = len(set(d.customer for d in data if d.customer))

	return [
		{"value": tot_visits, "indicator": "Purple", "label": "Total Client Visits", "datatype": "Int"},
		{"value": unique_clients, "indicator": "Blue", "label": "Unique Clients Visited", "datatype": "Int"}
	]
