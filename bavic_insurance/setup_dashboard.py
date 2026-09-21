import frappe

def create_dashboard_and_cards():
	module = "BAVIC Insurance"

	cards = [
		{
			"label": "Total Premium Generated",
			"type": "Document Type",
			"document_type": "Insurance Transaction",
			"function": "Sum",
			"aggregate_function_based_on": "amount",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Total Commission Received",
			"type": "Document Type",
			"document_type": "Insurance Transaction",
			"function": "Sum",
			"aggregate_function_based_on": "commission_amount",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Company Share Amount",
			"type": "Document Type",
			"document_type": "Insurance Transaction",
			"function": "Sum",
			"aggregate_function_based_on": "company_amount",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Agent Share Amount",
			"type": "Document Type",
			"document_type": "Insurance Transaction",
			"function": "Sum",
			"aggregate_function_based_on": "agent_amount",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Total Policies Issued",
			"type": "Document Type",
			"document_type": "Insurance Transaction",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Total Claims Handled",
			"type": "Document Type",
			"document_type": "Insurance Claim",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Total Claims Amount",
			"type": "Document Type",
			"document_type": "Insurance Claim",
			"function": "Sum",
			"aggregate_function_based_on": "amount",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Client Visits Held",
			"type": "Document Type",
			"document_type": "Client Visit",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		}
	]

	created_card_names = []
	for card_data in cards:
		label = card_data["label"]
		if not frappe.db.exists("Number Card", label):
			doc = frappe.get_doc({
				"doctype": "Number Card",
				"name": label,
				**card_data
			})
			doc.insert(ignore_permissions=True)
			frappe.db.commit()
		created_card_names.append(label)

	charts = [
		{
			"chart_name": "Monthly Premium Volume",
			"chart_type": "Sum",
			"document_type": "Insurance Transaction",
			"value_based_on": "amount",
			"based_on": "posting_date",
			"timeseries": 1,
			"time_interval": "Monthly",
			"timespan": "Last Year",
			"type": "Bar",
			"color": "#3b5bdb",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"filters_json": "{}"
		},
		{
			"chart_name": "Monthly Commission Volume",
			"chart_type": "Sum",
			"document_type": "Insurance Transaction",
			"value_based_on": "commission_amount",
			"based_on": "posting_date",
			"timeseries": 1,
			"time_interval": "Monthly",
			"timespan": "Last Year",
			"type": "Line",
			"color": "#10b981",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"filters_json": "{}"
		},
		{
			"chart_name": "Claims by Status",
			"chart_type": "Group By",
			"document_type": "Insurance Claim",
			"group_by_based_on": "status",
			"group_by_type": "Count",
			"type": "Donut",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"filters_json": "{}"
		},
		{
			"chart_name": "Policies by Product",
			"chart_type": "Group By",
			"document_type": "Insurance Transaction",
			"group_by_based_on": "product",
			"group_by_type": "Count",
			"type": "Bar",
			"color": "#22d3ee",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"filters_json": "{}"
		}
	]

	created_chart_names = []
	for chart_data in charts:
		name = chart_data["chart_name"]
		if not frappe.db.exists("Dashboard Chart", name):
			doc = frappe.get_doc({
				"doctype": "Dashboard Chart",
				"name": name,
				**chart_data
			})
			doc.insert(ignore_permissions=True)
			frappe.db.commit()
		created_chart_names.append(name)

	dashboard_name = "Bavic Performance Dashboard"
	if not frappe.db.exists("Dashboard", dashboard_name):
		doc = frappe.get_doc({
			"doctype": "Dashboard",
			"dashboard_name": dashboard_name,
			"name": dashboard_name,
			"is_default": 1,
			"is_standard": 1,
			"module": module,
			"cards": [{"card": c} for c in created_card_names],
			"charts": [{"chart": c, "width": "Half"} for c in created_chart_names]
		})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
	else:
		doc = frappe.get_doc("Dashboard", dashboard_name)
		doc.cards = [{"card": c} for c in created_card_names]
		doc.charts = [{"chart": c, "width": "Half"} for c in created_chart_names]
		doc.save(ignore_permissions=True)
		frappe.db.commit()

	print("Successfully setup Bavic Performance Dashboard, Cards, and Charts.")
