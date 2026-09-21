import frappe
from frappe.utils import flt, getdate


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_report_summary(data)

	return columns, data, None, chart, report_summary


def get_columns():
	return [
		{
			"label": "Insurance Product",
			"fieldname": "product",
			"fieldtype": "Link",
			"options": "Insurance Product",
			"width": 180
		},
		{
			"label": "Period Start",
			"fieldname": "start_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": "Period End",
			"fieldname": "end_date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": "Target Metric",
			"fieldname": "target_type",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": "Target Amount (TZS)",
			"fieldname": "target_amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Actual Achieved (TZS)",
			"fieldname": "actual_amount",
			"fieldtype": "Currency",
			"width": 160
		},
		{
			"label": "Variance (TZS)",
			"fieldname": "variance",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": "Achievement (%)",
			"fieldname": "achievement_pct",
			"fieldtype": "Percent",
			"width": 140
		},
		{
			"label": "Status",
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": "Notes",
			"fieldname": "notes",
			"fieldtype": "Data",
			"width": 180
		}
	]


def get_data(filters):
	data = []
	conditions = ["parenttype = 'Insurance Product'"]
	values = {}

	if filters.get("product"):
		conditions.append("parent = %(product)s")
		values["product"] = filters.get("product")

	if filters.get("target_type"):
		conditions.append("target_type = %(target_type)s")
		values["target_type"] = filters.get("target_type")

	if filters.get("from_date"):
		conditions.append("end_date >= %(from_date)s")
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions.append("start_date <= %(to_date)s")
		values["to_date"] = filters.get("to_date")

	where_clause = "WHERE " + " AND ".join(conditions)

	targets = frappe.db.sql(f"""
		SELECT parent as product, start_date, end_date, target_type, target_amount, notes
		FROM `tabTarget Detail`
		{where_clause}
		ORDER BY parent ASC, start_date DESC
	""", values, as_dict=True)

	for t in targets:
		target_val = flt(t.target_amount)
		prod_name = t.product
		t_type = t.target_type or "Premium"

		# Query actual achieved for this product in this target period
		if t_type == "Premium":
			actual_val = flt(frappe.db.sql("""
				SELECT COALESCE(SUM(amount), 0.0)
				FROM `tabInsurance Transaction`
				WHERE product = %(product)s
				  AND posting_date >= %(start_date)s
				  AND posting_date <= %(end_date)s
				  AND docstatus < 2
			""", {"product": prod_name, "start_date": t.start_date, "end_date": t.end_date})[0][0])
		else:  # Commission
			actual_val = flt(frappe.db.sql("""
				SELECT COALESCE(SUM(commission_amount), 0.0)
				FROM `tabInsurance Transaction`
				WHERE product = %(product)s
				  AND posting_date >= %(start_date)s
				  AND posting_date <= %(end_date)s
				  AND docstatus < 2
			""", {"product": prod_name, "start_date": t.start_date, "end_date": t.end_date})[0][0])

		variance = actual_val - target_val
		achieve_pct = (actual_val / target_val * 100.0) if target_val > 0 else 0.0

		if achieve_pct >= 100.0:
			status = "Target Met"
		elif achieve_pct >= 70.0:
			status = "On Track"
		else:
			status = "Below Target"

		data.append({
			"product": prod_name,
			"start_date": t.start_date,
			"end_date": t.end_date,
			"target_type": t_type,
			"target_amount": target_val,
			"actual_amount": actual_val,
			"variance": variance,
			"achievement_pct": achieve_pct,
			"status": status,
			"notes": t.notes or ""
		})

	return data


def get_chart(data):
	if not data:
		return None

	labels = []
	target_vals = []
	actual_vals = []

	prod_targets = {}
	prod_actuals = {}
	for d in data:
		pr = d["product"]
		prod_targets[pr] = prod_targets.get(pr, 0.0) + flt(d["target_amount"])
		prod_actuals[pr] = prod_actuals.get(pr, 0.0) + flt(d["actual_amount"])

	for pr in sorted(prod_targets.keys()):
		labels.append(pr)
		target_vals.append(prod_targets[pr])
		actual_vals.append(prod_actuals[pr])

	return {
		"data": {
			"labels": labels[:10],
			"datasets": [
				{"name": "Target (TZS)", "values": target_vals[:10]},
				{"name": "Actual Achieved (TZS)", "values": actual_vals[:10]}
			]
		},
		"type": "bar",
		"colors": ["#06b6d4", "#10b981"]
	}


def get_report_summary(data):
	if not data:
		return []

	tot_target = sum(flt(d["target_amount"]) for d in data)
	tot_actual = sum(flt(d["actual_amount"]) for d in data)
	overall_pct = (tot_actual / tot_target * 100.0) if tot_target > 0 else 0.0
	net_variance = tot_actual - tot_target

	indicator = "Green" if overall_pct >= 100.0 else ("Orange" if overall_pct >= 70.0 else "Red")

	return [
		{"value": tot_target, "indicator": "Blue", "label": "Total Product Target (TZS)", "datatype": "Currency"},
		{"value": tot_actual, "indicator": "Teal", "label": "Total Achieved (TZS)", "datatype": "Currency"},
		{"value": net_variance, "indicator": indicator, "label": "Net Variance (TZS)", "datatype": "Currency"},
		{"value": overall_pct, "indicator": indicator, "label": "Overall Achievement", "datatype": "Percent"}
	]
