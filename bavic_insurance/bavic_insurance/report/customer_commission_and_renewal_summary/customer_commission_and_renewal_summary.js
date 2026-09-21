// Copyright (c) 2026, Dev and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Commission and Renewal Summary"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date"
		}
	]
};
