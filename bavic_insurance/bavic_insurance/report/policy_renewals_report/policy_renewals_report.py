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
			"label": "Insurance Product",
			"fieldname": "product",
			"fieldtype": "Link",
			"options": "Insurance Product",
			"width": 150
		},
		{
			"label": "Renewal Date",
			"fieldname": "renewal_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": "Effective Date",
			"fieldname": "effective_date",
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
	conditions = ["t.renewal_date >= %(from_date)s AND t.renewal_date <= %(to_date)s"]
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
			t.renewal_date,
			t.effective_date,
			t.amount,
			t.commission_amount,
			t.company_amount,
			t.agent_amount,
			t.intermediary,
			CASE 
				WHEN t.renewal_date < CURRENT_DATE THEN 'Overdue'
				WHEN t.renewal_date <= DATEDIFF(CURRENT_DATE, -30) THEN 'Due Soon'
				ELSE 'Active / Renewed'
			END as status
		FROM 
			`tabInsurance Transaction` t
		{where_clause}
		ORDER BY 
			t.renewal_date ASC
	"""
	return frappe.db.sql(query, values, as_dict=True)

def get_chart(data, period):
	if not data:
		return None

	bucket_sums = {}
	for d in data:
		bkey = get_date_bucket(d.renewal_date, period)
		bucket_sums[bkey] = bucket_sums.get(bkey, 0.0) + flt(d.amount)

	sorted_keys = sorted(bucket_sums.keys())
	values = [bucket_sums[k] for k in sorted_keys]

	return {
		"data": {
			"labels": sorted_keys,
			"datasets": [{"name": "Renewal Premium (TZS)", "values": values}]
		},
		"type": "bar",
		"colors": ["#10b981"]
	}

def get_report_summary(data):
	if not data:
		return []

	tot_renewals = len(data)
	tot_premium = sum(flt(d.amount) for d in data)
	tot_comm = sum(flt(d.commission_amount) for d in data)
	overdue = sum(1 for d in data if d.status == "Overdue")

	return [
		{"value": tot_renewals, "indicator": "Blue", "label": "Total Renewals Count", "datatype": "Int"},
		{"value": overdue, "indicator": "Red", "label": "Overdue Renewals", "datatype": "Int"},
		{"value": tot_premium, "indicator": "Green", "label": "Total Renewal Premium (TZS)", "datatype": "Currency"},
		{"value": tot_comm, "indicator": "Teal", "label": "Renewal Commission (TZS)", "datatype": "Currency"}
	]
