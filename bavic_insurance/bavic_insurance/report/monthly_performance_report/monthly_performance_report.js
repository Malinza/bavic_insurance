frappe.query_reports["Monthly Performance Report"] = {
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
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		}
	]
};
