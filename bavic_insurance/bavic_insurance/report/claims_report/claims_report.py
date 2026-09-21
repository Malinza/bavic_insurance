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
			"label": "Claim ID",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Insurance Claim",
			"width": 140
		},
		{
			"label": "Claim Date",
			"fieldname": "claim_date",
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
			"label": "Policy Holder Name",
			"fieldname": "policy_holder_name",
			"fieldtype": "Data",
			"width": 160
		},
		{
			"label": "Claim Type",
			"fieldname": "claim_type",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": "Amount (TZS)",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": "Description",
			"fieldname": "description",
			"fieldtype": "Small Text",
			"width": 200
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
	conditions = ["claim_date >= %(from_date)s AND claim_date <= %(to_date)s"]
	values = {"from_date": from_date, "to_date": to_date}

	if filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters.get("customer")

	if filters.get("claim_type"):
		conditions.append("claim_type = %(claim_type)s")
		values["claim_type"] = filters.get("claim_type")

	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters.get("status")

	where_clause = "WHERE " + " AND ".join(conditions)

	query = f"""
		SELECT 
			name,
			claim_date,
			customer,
			policy_holder_name,
			claim_type,
			amount,
			status,
			description,
			owner,
			creation
		FROM 
			`tabInsurance Claim`
		{where_clause}
		ORDER BY 
			claim_date DESC
	"""
	return frappe.db.sql(query, values, as_dict=True)

def get_chart(data, period):
	if not data:
		return None

	bucket_sums = {}
	for d in data:
		bkey = get_date_bucket(d.claim_date, period)
		bucket_sums[bkey] = bucket_sums.get(bkey, 0.0) + flt(d.amount)

	sorted_keys = sorted(bucket_sums.keys())
	values = [bucket_sums[k] for k in sorted_keys]

	return {
		"data": {
			"labels": sorted_keys,
			"datasets": [{"name": "Claim Amount (TZS)", "values": values}]
		},
		"type": "bar",
		"colors": ["#ef4444"]
	}

def get_report_summary(data):
	if not data:
		return []

	tot_claims = len(data)
	tot_amount = sum(flt(d.amount) for d in data)
	approved = sum(flt(d.amount) for d in data if d.status in ["Approved", "Paid"])

	return [
		{"value": tot_claims, "indicator": "Blue", "label": "Total Claims Count", "datatype": "Int"},
		{"value": tot_amount, "indicator": "Red", "label": "Total Claim Amount (TZS)", "datatype": "Currency"},
		{"value": approved, "indicator": "Green", "label": "Approved / Paid Amount (TZS)", "datatype": "Currency"}
	]
