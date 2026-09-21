// Copyright (c) 2026, Dev and contributors
// For license information, please see license.txt

frappe.query_reports["Agent Target Performance"] = {
	"filters": [
		{
			"fieldname": "agent",
			"label": __("Agent / SFE"),
			"fieldtype": "Link",
			"options": "Agent"
		},
		{
			"fieldname": "target_type",
			"label": __("Target Metric"),
			"fieldtype": "Select",
			"options": "\nPremium\nCommission"
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.year_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}
	]
};
