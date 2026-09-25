import frappe


ROLE_PROFILES = {
	"BAVIC Executive": ["BAVIC Executive"],
	"BAVIC System Owner": ["BAVIC System Owner"],
	"BAVIC System Administrator": ["BAVIC System Administrator"],
	"BAVIC Director of Operations": ["BAVIC Director of Operations"],
	"BAVIC Department Data Owner": ["BAVIC Department Data Owner"],
	"BAVIC Team Supervisor": ["BAVIC Team Supervisor"],
	"BAVIC Sales User": ["BAVIC Sales User"],
	"BAVIC Finance User": ["BAVIC Finance User"],
	"BAVIC Client Support": ["BAVIC Client Support"],
	"BAVIC Compliance Reviewer": ["BAVIC Compliance Reviewer"],
	"BAVIC External User": ["BAVIC External User"],
	"BAVIC System Owner and Administrator": [
		"BAVIC System Owner",
		"BAVIC System Administrator",
	],
	"BAVIC Department Data Owner and Finance": [
		"BAVIC Department Data Owner",
		"BAVIC Finance User",
	],
	"BAVIC Department Data Owner and Client Support": [
		"BAVIC Department Data Owner",
		"BAVIC Client Support",
	],
}


def execute():
	for role_name in sorted({role for roles in ROLE_PROFILES.values() for role in roles}):
		ensure_role(role_name)

	for profile_name, roles in ROLE_PROFILES.items():
		ensure_role_profile(profile_name, roles)


def ensure_role(role_name):
	if frappe.db.exists("Role", role_name):
		return

	frappe.get_doc(
		{
			"doctype": "Role",
			"role_name": role_name,
			"desk_access": 1,
			"disabled": 0,
			"is_custom": 0,
			"two_factor_auth": 0,
		}
	).insert(ignore_permissions=True)


def ensure_role_profile(profile_name, roles):
	if frappe.db.exists("Role Profile", profile_name):
		profile = frappe.get_doc("Role Profile", profile_name)
		current = [row.role for row in profile.roles]
		if current == roles:
			return
		profile.set("roles", [])
	else:
		profile = frappe.get_doc(
			{
				"doctype": "Role Profile",
				"role_profile": profile_name,
			}
		)

	for role in roles:
		profile.append("roles", {"role": role})

	profile.flags.ignore_permissions = True
	profile.save(ignore_permissions=True)
