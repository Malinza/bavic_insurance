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
			"label": "Transaction ID",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Insurance Transaction",
			"width": 140
		},
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 180
		},
		{
			"label": "Policy Holder Name",
			"fieldname": "policy_holder_name",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": "Product",
			"fieldname": "product",
			"fieldtype": "Link",
			"options": "Insurance Product",
			"width": 140
		},
		{
			"label": "Business Type",
			"fieldname": "business_type",
			"fieldtype": "Link",
			"options": "Business Type",
			"width": 130
		},
		{
			"label": "Effective Date",
			"fieldname": "effective_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": "Renewal Date",
			"fieldname": "renewal_date",
			"fieldtype": "Date",
			"width": 110
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
			"width": 140
		},
		{
			"label": "Agent / SFE",
			"fieldname": "intermediary",
			"fieldtype": "Link",
			"options": "Agent",
			"width": 160
		}
	]

def get_data(filters):
	conditions = []
	values = {}
	
	if filters and filters.get("customer"):
		conditions.append("customer = %(customer)s")
		values["customer"] = filters.get("customer")
		
	if filters and filters.get("product"):
		conditions.append("product = %(product)s")
		values["product"] = filters.get("product")
		
	if filters and filters.get("business_type"):
		conditions.append("business_type = %(business_type)s")
		values["business_type"] = filters.get("business_type")
		
	where_clause = ""
	if conditions:
		where_clause = "WHERE " + " AND ".join(conditions)
		
	query = f"""
		SELECT 
			name,
			customer,
			policy_holder_name,
			product,
			business_type,
			effective_date,
			renewal_date,
			posting_date,
			amount,
			intermediary
		FROM 
			`tabInsurance Transaction`
		{where_clause}
		ORDER BY 
			customer ASC, renewal_date DESC, posting_date DESC
	"""
	
	return frappe.db.sql(query, values, as_dict=True)

def get_chart(data):
	if not data:
		return None

	prod_totals = {}
	for d in data:
		p = d.product or "Other"
		prod_totals[p] = prod_totals.get(p, 0) + (d.amount or 0)

	return {
		"data": {
			"labels": list(prod_totals.keys()),
			"datasets": [{"name": "Premium Volume", "values": list(prod_totals.values())}]
		},
		"type": "bar",
		"colors": ["#3b5bdb", "#10b981", "#22d3ee", "#f59e0b", "#8b5cf6"]
	}

def get_report_summary(data):
	if not data:
		return []

	tot_tx = len(data)
	tot_vol = sum(d.amount or 0 for d in data)

	return [
		{"value": tot_tx, "indicator": "Blue", "label": "Total Policies", "datatype": "Int"},
		{"value": tot_vol, "indicator": "Green", "label": "Total Volume (TZS)", "datatype": "Currency"}
	]
