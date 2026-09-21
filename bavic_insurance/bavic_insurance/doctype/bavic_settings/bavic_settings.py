# Copyright (c) 2026, Dev and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class BavicSettings(Document):
	pass


@frappe.whitelist()
def get_settings():
	doc = frappe.get_single("Bavic Settings")
	return {
		"agent_commission_percent": float(doc.agent_commission_percent or 40.0),
		"company_commission_percent": float(doc.company_commission_percent or 60.0),
	}
