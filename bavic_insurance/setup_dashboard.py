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
			"label": "Total Gross Commission Received",
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
			"label": "Total Withholding Tax Deducted",
			"type": "Document Type",
			"document_type": "Insurance Transaction",
			"function": "Sum",
			"aggregate_function_based_on": "withholding_tax_amount",
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"show_percentage_stats": 1,
			"stats_time_interval": "Monthly"
		},
		{
			"label": "Total Net Commission Received",
			"type": "Document Type",
			"document_type": "Insurance Transaction",
			"function": "Sum",
			"aggregate_function_based_on": "net_commission_amount",
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
		},
		{
			"label": "Total Company Targets Defined",
			"type": "Document Type",
			"document_type": "Target Detail",
			"is_child_table": 1,
			"parent_document_type": "Bavic Settings",
			"function": "Count",
			"is_public": 1,
			"is_standard": 1,
			"module": module
		},
		{
			"label": "Total Premium Targets Set",
			"type": "Document Type",
			"document_type": "Target Detail",
			"is_child_table": 1,
			"parent_document_type": "Bavic Settings",
			"function": "Sum",
			"aggregate_function_based_on": "target_amount",
			"filters_json": '[["Target Detail","target_type","=","Premium"]]',
			"is_public": 1,
			"is_standard": 1,
			"module": module
		},
		{
			"label": "Total Commission Targets Set",
			"type": "Document Type",
			"document_type": "Target Detail",
			"is_child_table": 1,
			"parent_document_type": "Bavic Settings",
			"function": "Sum",
			"aggregate_function_based_on": "target_amount",
			"filters_json": '[["Target Detail","target_type","=","Commission"]]',
			"is_public": 1,
			"is_standard": 1,
			"module": module
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
		else:
			doc = frappe.get_doc("Number Card", label)
			doc.update(card_data)
			doc.save(ignore_permissions=True)
			frappe.db.commit()
		created_card_names.append(label)

	charts = [
		{
			"chart_name": "Company Target vs Actual",
			"chart_type": "Report",
			"report_name": "Company Target Performance",
			"use_report_chart": 1,
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"filters_json": "{}"
		},
		{
			"chart_name": "Agent Target vs Actual",
			"chart_type": "Report",
			"report_name": "Agent Target Performance",
			"use_report_chart": 1,
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"filters_json": "{}"
		},
		{
			"chart_name": "Product Target vs Actual",
			"chart_type": "Report",
			"report_name": "Product Target Performance",
			"use_report_chart": 1,
			"is_public": 1,
			"is_standard": 1,
			"module": module,
			"filters_json": "{}"
		},
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
		},
		{
			"chart_name": "Policies by Insurer",
			"chart_type": "Group By",
			"document_type": "Insurance Transaction",
			"group_by_based_on": "insurer",
			"group_by_type": "Count",
			"type": "Bar",
			"color": "#818cf8",
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
		else:
			doc = frappe.get_doc("Dashboard Chart", name)
			doc.update(chart_data)
			doc.save(ignore_permissions=True)
			frappe.db.commit()
		created_chart_names.append(name)

	dashboard_name = "Bavic Performance Dashboard"
	if not frappe.db.exists("Dashboard", dashboard_name):
		doc = frappe.new_doc("Dashboard")
		doc.dashboard_name = dashboard_name
		doc.name = dashboard_name
		doc.is_default = 1
		doc.is_standard = 1
		doc.module = module
		for c in created_card_names:
			doc.append("cards", {"card": c})
		for c in created_chart_names:
			doc.append("charts", {"chart": c, "width": "Half"})
		doc.insert(ignore_permissions=True)
		frappe.db.commit()
	else:
		doc = frappe.get_doc("Dashboard", dashboard_name)
		doc.set("cards", [])
		doc.set("charts", [])
		for c in created_card_names:
			doc.append("cards", {"card": c})
		for c in created_chart_names:
			doc.append("charts", {"chart": c, "width": "Half"})
		doc.save(ignore_permissions=True)
		frappe.db.commit()

	print("Successfully setup Bavic Performance Dashboard, Cards, and Charts.")
