frappe.query_reports["Claims Report"] = {
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
			"fieldname": "claim_type",
			"label": __("Claim Type"),
			"fieldtype": "Select",
			"options": ["", "Medical", "Motor", "Life", "Fire & Property", "Marine", "Miscellaneous"]
		},
		{
			"fieldname": "status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options": ["", "Reported", "Under Review", "Approved", "Paid", "Rejected"]
		}
	]
};
