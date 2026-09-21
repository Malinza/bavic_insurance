frappe.query_reports["Policy Renewals Report"] = {
	"filters": [
		{
			"fieldname": "period",
			"label": __("Trend Period"),
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
		},
		{
			"fieldname": "product",
			"label": __("Insurance Product"),
			"fieldtype": "Link",
			"options": "Insurance Product"
		},
		{
			"fieldname": "agent_sfe",
			"label": __("Agent / SFE"),
			"fieldtype": "Link",
			"options": "Agent"
		}
	]
};
