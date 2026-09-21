// Copyright (c) 2026, Dev and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Renewal History"] = {
	"filters": [
		{
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname": "product",
			"label": "Product",
			"fieldtype": "Link",
			"options": "Insurance Product"
		},
		{
			"fieldname": "business_type",
			"label": "Business Type",
			"fieldtype": "Link",
			"options": "Business Type"
		}
	]
};
