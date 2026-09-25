# Copyright (c) 2026, Dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class BulkUser(Document):
	def validate(self):
		if not self.accounts:
			frappe.throw(_("Add at least one user"))

		seen = set()
		for row in self.accounts:
			row.email = (row.email or "").strip().lower()
			if not row.password:
				row.password = "Bavic@123"
			if row.email in seen:
				frappe.throw(_("Email {0} is listed more than once").format(row.email))
			seen.add(row.email)

	def on_submit(self):
		for row in self.accounts:
			create_desk_user(
				email=row.email,
				first_name=row.first_name,
				last_name=row.last_name,
				role_profile=self.role_profile,
				password=row.password,
				mobile=row.mobile,
			)


def create_desk_user(
	email,
	first_name,
	last_name,
	role_profile,
	password="Bavic@123",
	mobile=None,
	middle_name=None,
	update_existing=False,
):
	"""Create a desk user and assign a Role Profile without sending email."""
	email = (email or "").strip().lower()
	if frappe.db.exists("User", email):
		if not update_existing:
			frappe.throw(_("User {0} already exists").format(email))
		user = frappe.get_doc("User", email)
		user.first_name = first_name
		user.last_name = last_name
		user.middle_name = middle_name
		user.mobile_no = mobile or user.mobile_no
		user.enabled = 1
		user.user_type = "System User"
		user.send_welcome_email = 0
		user.role_profile_name = role_profile
		user.flags.no_welcome_mail = True
		user.flags.mute_emails = True
		user.save(ignore_permissions=True)
		return user.name

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": first_name,
			"middle_name": middle_name,
			"last_name": last_name,
			"mobile_no": mobile,
			"enabled": 1,
			"user_type": "System User",
			"send_welcome_email": 0,
			"role_profile_name": role_profile,
			"new_password": password or "Bavic@123",
		}
	)
	user.flags.no_welcome_mail = True
	user.flags.mute_emails = True
	user.flags.ignore_password_policy = True
	user.insert(ignore_permissions=True)
	return user.name
