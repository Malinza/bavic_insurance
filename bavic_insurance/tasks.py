import frappe
from frappe.utils import getdate, nowdate, add_months


def daily_update_ipf_payment_dates():
	"""
	Daily scheduled task for Insurance Premium Finance (IPF) transactions.
	When next_payment_date is reached or passed (the month is done),
	increments next_payment_date by 1 month (capped at renewal_date if specified).
	"""
	today = getdate(nowdate())
	
	ipf_transactions = frappe.db.sql("""
		SELECT name, effective_date, next_payment_date, renewal_date
		FROM `tabInsurance Transaction`
		WHERE premium_payment = 'Insurance Premium Finance IPF'
		  AND docstatus < 2
		  AND next_payment_date IS NOT NULL
		  AND next_payment_date <= %(today)s
	""", {"today": today}, as_dict=True)

	updated_count = 0
	for tx in ipf_transactions:
		current_next_date = getdate(tx.next_payment_date)
		renewal_date = getdate(tx.renewal_date) if tx.renewal_date else None

		new_date = current_next_date
		while new_date <= today:
			new_date = add_months(new_date, 1)

		# Cap at renewal_date if renewal_date exists
		if renewal_date and new_date > renewal_date:
			new_date = renewal_date

		if new_date != current_next_date:
			frappe.db.set_value("Insurance Transaction", tx.name, "next_payment_date", new_date, update_modified=False)
			updated_count += 1

	if updated_count > 0:
		frappe.db.commit()
		frappe.logger().info(f"daily_update_ipf_payment_dates: updated {updated_count} IPF transactions.")

	return updated_count


@frappe.whitelist()
def run_ipf_payment_update():
	"""
	Whitelisted method to trigger IPF payment date update on demand.
	"""
	count = daily_update_ipf_payment_dates()
	return {"message": f"Successfully updated {count} IPF transaction next payment dates.", "updated_count": count}
