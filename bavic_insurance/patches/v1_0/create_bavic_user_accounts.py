import frappe

from bavic_insurance.bavic_insurance.doctype.bulk_user.bulk_user import create_desk_user


# firstname.lastname@bavicinsurance.co.tz from the key personnel list.
KEY_PERSONNEL = [
	{
		"first_name": "Consolatha",
		"middle_name": "C.",
		"last_name": "William",
		"email": "consolatha.william@bavicinsurance.co.tz",
		"role_profile": "BAVIC Executive",
	},
	{
		"first_name": "Alphonce",
		"last_name": "Nyambita",
		"email": "alphonce.nyambita@bavicinsurance.co.tz",
		"role_profile": "BAVIC System Owner and Administrator",
	},
	{
		"first_name": "Hatibu",
		"middle_name": "S.",
		"last_name": "Zuberi",
		"email": "hatibu.zuberi@bavicinsurance.co.tz",
		"role_profile": "BAVIC Department Data Owner",
	},
	{
		"first_name": "Tercy",
		"last_name": "Tesimwa",
		"email": "tercy.tesimwa@bavicinsurance.co.tz",
		"role_profile": "BAVIC Department Data Owner",
	},
	{
		"first_name": "Anna",
		"last_name": "Michael",
		"email": "anna.michael@bavicinsurance.co.tz",
		"role_profile": "BAVIC Department Data Owner",
	},
	{
		"first_name": "Devotha",
		"middle_name": "C.",
		"last_name": "William",
		"email": "devotha.william@bavicinsurance.co.tz",
		"role_profile": "BAVIC Department Data Owner and Finance",
	},
	{
		"first_name": "Mwanahawa",
		"middle_name": "Ibrahimu",
		"last_name": "Msoke",
		"email": "mwanahawa.msoke@bavicinsurance.co.tz",
		"role_profile": "BAVIC Department Data Owner and Client Support",
	},
	{
		"first_name": "Doris",
		"middle_name": "John",
		"last_name": "Chacha",
		"email": "doris.chacha@bavicinsurance.co.tz",
		"role_profile": "BAVIC Department Data Owner",
	},
	{
		"first_name": "Aniceth",
		"last_name": "Michael",
		"email": "aniceth.michael@bavicinsurance.co.tz",
		"role_profile": "BAVIC Team Supervisor",
	},
	{
		"first_name": "Leonard",
		"last_name": "Nyagiro",
		"email": "leonard.nyagiro@bavicinsurance.co.tz",
		"role_profile": "BAVIC Compliance Reviewer",
	},
]


def execute():
	for person in KEY_PERSONNEL:
		create_desk_user(
			email=person["email"],
			first_name=person["first_name"],
			last_name=person["last_name"],
			role_profile=person["role_profile"],
			password="Bavic@123",
			middle_name=person.get("middle_name"),
			update_existing=True,
		)
