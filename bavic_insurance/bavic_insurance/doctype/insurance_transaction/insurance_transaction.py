import frappe
from frappe.model.document import Document


class InsuranceTransaction(Document):
	def validate(self):
		self.calculate_commission()
		self.validate_and_fetch_policy_holder()

	def calculate_commission(self):
		# Fetch commission rate from product
		if self.product:
			rate = frappe.db.get_value("Insurance Product", self.product, "commission_rate")
			self.commission_rate = float(rate or 0.0)
		else:
			self.commission_rate = 0.0

		premium = float(self.amount or 0.0)
		self.commission_amount = (premium * float(self.commission_rate)) / 100.0

		# Fetch company and agent shares from Bavic Settings
		settings = frappe.get_single("Bavic Settings")
		self.company_percent = float(settings.company_commission_percent or 60.0)
		self.agent_percent = float(settings.agent_commission_percent or 40.0)

		self.company_amount = (self.commission_amount * self.company_percent) / 100.0
		self.agent_amount = (self.commission_amount * self.agent_percent) / 100.0

	def validate_and_fetch_policy_holder(self):
		if self.customer and self.policy_holder_name:
			customer_doc = frappe.get_doc("Customer", self.customer)
			found = False
			for ph in customer_doc.policy_holders:
				if ph.policy_holder_name == self.policy_holder_name:
					self.policy_holder_email = ph.email
					self.policy_holder_phone = ph.phone
					found = True
					break
			if not found:
				self.policy_holder_email = None
				self.policy_holder_phone = None


@frappe.whitelist()
def get_customer_details(customer):
	if not customer:
		return {}

	doc = frappe.get_doc("Customer", customer)
	policy_holders = []
	for ph in doc.policy_holders:
		policy_holders.append({
			"name": ph.policy_holder_name,
			"email": ph.email,
			"phone": ph.phone
		})

	return {
		"policy_holders": policy_holders
	}


@frappe.whitelist()
def get_product_details(product):
	if not product:
		return {"commission_rate": 0.0}

	rate = frappe.db.get_value("Insurance Product", product, "commission_rate") or 0.0
	settings = frappe.get_single("Bavic Settings")

	return {
		"commission_rate": float(rate),
		"company_percent": float(settings.company_commission_percent or 60.0),
		"agent_percent": float(settings.agent_commission_percent or 40.0)
	}
