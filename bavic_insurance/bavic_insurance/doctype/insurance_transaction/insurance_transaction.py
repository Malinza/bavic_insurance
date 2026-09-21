import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, flt


class InsuranceTransaction(Document):
	def validate(self):
		self.set_defaults_from_settings()
		self.calculate_renewal_date()
		self.calculate_next_payment_date()
		self.calculate_commission()
		self.validate_and_fetch_policy_holder()

	def set_defaults_from_settings(self):
		settings = frappe.get_single("Bavic Settings")
		if self.withholding_tax_percent is None or flt(self.withholding_tax_percent) == 0.0:
			if flt(settings.withholding_tax_percent) > 0.0:
				self.withholding_tax_percent = flt(settings.withholding_tax_percent)
		if (self.company_percent is None or flt(self.company_percent) == 0.0) and \
		   (self.agent_percent is None or flt(self.agent_percent) == 0.0):
			self.company_percent = flt(settings.company_commission_percent or 60.0)
			self.agent_percent = flt(settings.agent_commission_percent or 40.0)

	def calculate_renewal_date(self):
		if self.effective_date:
			months = int(self.months or 12)
			self.renewal_date = add_months(getdate(self.effective_date), months)

	def calculate_next_payment_date(self):
		if self.premium_payment == "Insurance Premium Finance IPF":
			if not self.next_payment_date and self.effective_date:
				self.next_payment_date = add_months(getdate(self.effective_date), 1)

	def calculate_commission(self):
		# Default commission rate from product if not provided
		if self.commission_rate is None or (flt(self.commission_rate) == 0.0 and not self.is_new()):
			if self.product:
				rate = frappe.db.get_value("Insurance Product", self.product, "commission_rate")
				self.commission_rate = flt(rate or 0.0)
			else:
				self.commission_rate = 0.0
		elif self.product and self.commission_rate is None:
			rate = frappe.db.get_value("Insurance Product", self.product, "commission_rate")
			self.commission_rate = flt(rate or 0.0)

		# Fetch settings for defaults
		settings = frappe.get_single("Bavic Settings")
		
		# Default withholding tax percent if None
		if self.withholding_tax_percent is None or flt(self.withholding_tax_percent) == 0.0:
			self.withholding_tax_percent = flt(settings.withholding_tax_percent or 0.0)

		# Default company and agent percentages if both are unset/0
		if (self.company_percent is None or flt(self.company_percent) == 0.0) and \
		   (self.agent_percent is None or flt(self.agent_percent) == 0.0):
			self.company_percent = flt(settings.company_commission_percent or 60.0)
			self.agent_percent = flt(settings.agent_commission_percent or 40.0)
		elif self.company_percent is None:
			self.company_percent = flt(settings.company_commission_percent or 60.0)
		elif self.agent_percent is None:
			self.agent_percent = flt(settings.agent_commission_percent or 40.0)

		premium = flt(self.amount or 0.0)
		comm_rate = flt(self.commission_rate or 0.0)
		wht_percent = flt(self.withholding_tax_percent or 0.0)
		comp_pct = flt(self.company_percent or 0.0)
		agent_pct = flt(self.agent_percent or 0.0)

		# 1. Total Commission Amount
		self.commission_amount = (premium * comm_rate) / 100.0

		# 2. Withholding Tax Amount
		self.withholding_tax_amount = (self.commission_amount * wht_percent) / 100.0

		# 3. Net Commission Amount
		self.net_commission_amount = self.commission_amount - self.withholding_tax_amount

		# 4. Split Net Commission between Company and Agent
		self.company_amount = (self.net_commission_amount * comp_pct) / 100.0
		self.agent_amount = (self.net_commission_amount * agent_pct) / 100.0

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
def get_settings_defaults():
	settings = frappe.get_single("Bavic Settings")
	return {
		"company_percent": flt(settings.company_commission_percent or 60.0),
		"agent_percent": flt(settings.agent_commission_percent or 40.0),
		"withholding_tax_percent": flt(settings.withholding_tax_percent or 0.0)
	}


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
	settings = frappe.get_single("Bavic Settings")
	if not product:
		return {
			"commission_rate": 0.0,
			"company_percent": flt(settings.company_commission_percent or 60.0),
			"agent_percent": flt(settings.agent_commission_percent or 40.0),
			"withholding_tax_percent": flt(settings.withholding_tax_percent or 0.0)
		}

	rate = frappe.db.get_value("Insurance Product", product, "commission_rate") or 0.0

	return {
		"commission_rate": flt(rate),
		"company_percent": flt(settings.company_commission_percent or 60.0),
		"agent_percent": flt(settings.agent_commission_percent or 40.0),
		"withholding_tax_percent": flt(settings.withholding_tax_percent or 0.0)
	}
