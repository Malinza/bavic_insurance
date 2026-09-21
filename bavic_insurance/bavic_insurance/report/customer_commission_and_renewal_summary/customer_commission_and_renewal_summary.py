import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)
	return columns, data, None, chart, report_summary

def get_columns():
	return [
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200
		},
		{
			"label": "Total Transactions",
			"fieldname": "total_transactions",
			"fieldtype": "Int",
			"width": 140
		},
		{
			"label": "Total Premium (TZS)",
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Total Commission",
			"fieldname": "total_commission",
			"fieldtype": "Currency",
			"width": 160
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
			"label": "Latest Renewal Date",
			"fieldname": "latest_renewal_date",
			"fieldtype": "Date",
			"width": 150
		}
	]

def get_data(filters):
	conditions = []
	values = {}
	
	if filters and filters.get("customer"):
		conditions.append("t.customer = %(customer)s")
		values["customer"] = filters.get("customer")
	
	if filters and filters.get("from_date"):
		conditions.append("t.posting_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")
		
	if filters and filters.get("to_date"):
		conditions.append("t.posting_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")
		
	where_clause = ""
	if conditions:
		where_clause = "WHERE " + " AND ".join(conditions)
		
	query = f"""
		SELECT 
			t.customer,
			COUNT(t.name) as total_transactions,
			SUM(t.amount) as total_amount,
			SUM(t.commission_amount) as total_commission,
			SUM(t.company_amount) as company_amount,
			SUM(t.agent_amount) as agent_amount,
			MAX(t.renewal_date) as latest_renewal_date
		FROM 
			`tabInsurance Transaction` t
		{where_clause}
		GROUP BY 
			t.customer
		ORDER BY 
			total_amount DESC
	"""
	
	return frappe.db.sql(query, values, as_dict=True)

def get_chart(data):
	if not data:
		return None
		
	labels = [d.customer for d in data[:8]]
	premiums = [d.total_amount or 0 for d in data[:8]]
	commissions = [d.total_commission or 0 for d in data[:8]]

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Total Premium", "values": premiums},
				{"name": "Total Commission", "values": commissions}
			]
		},
		"type": "bar",
		"colors": ["#3b5bdb", "#22d3ee"]
	}

def get_report_summary(data):
	if not data:
		return []

	tot_premium = sum(d.total_amount or 0 for d in data)
	tot_comm = sum(d.total_commission or 0 for d in data)
	tot_comp = sum(d.company_amount or 0 for d in data)
	tot_agent = sum(d.agent_amount or 0 for d in data)

	return [
		{"value": tot_premium, "indicator": "Blue", "label": "Total Premium (TZS)", "datatype": "Currency"},
		{"value": tot_comm, "indicator": "Green", "label": "Total Commission (TZS)", "datatype": "Currency"},
		{"value": tot_comp, "indicator": "Teal", "label": "Company Share (TZS)", "datatype": "Currency"},
		{"value": tot_agent, "indicator": "Orange", "label": "Agent Share (TZS)", "datatype": "Currency"}
	]
