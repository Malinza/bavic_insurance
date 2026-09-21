frappe.query_reports["Executive Summary Report"] = {
	"filters": [
		{
			"fieldname": "period",
			"label": __("Reporting Period"),
			"fieldtype": "Select",
			"options": ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"],
			"default": "Monthly",
			"reqd": 1
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		}
	]
};
