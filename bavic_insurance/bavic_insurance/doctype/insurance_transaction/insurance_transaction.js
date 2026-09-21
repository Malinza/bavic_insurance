frappe.ui.form.on("Insurance Transaction", {
	setup(frm) {
		frm.policy_holders_cache = {};
	},
	refresh(frm) {
		if (frm.doc.customer && frm.doc.docstatus == 0) {
			frm.trigger("customer");
		}
		if (frm.doc.product && frm.doc.docstatus == 0) {
			frm.trigger("product");
		}
	},
	customer(frm) {
		if (frm.doc.customer) {
			frappe.call({
				method: "bavic_insurance.bavic_insurance.doctype.insurance_transaction.insurance_transaction.get_customer_details",
				args: {
					customer: frm.doc.customer
				},
				callback: function (r) {
					if (r.message) {
						let holders = r.message.policy_holders || [];

						frm.policy_holders_cache = {};
						let options = [""];
						holders.forEach(h => {
							options.push(h.name);
							frm.policy_holders_cache[h.name] = h;
						});

						frm.set_df_property("policy_holder_name", "options", options);
						if (options.includes(frm.doc.policy_holder_name)) {
							frm.set_value("policy_holder_name", frm.doc.policy_holder_name);
						}
					}
				}
			});
		} else {
			frm.set_df_property("policy_holder_name", "options", [""]);
			frm.set_value("policy_holder_name", "");
			frm.set_value("policy_holder_email", "");
			frm.set_value("policy_holder_phone", "");
			frm.policy_holders_cache = {};
		}
	},
	product(frm) {
		if (frm.doc.product) {
			frappe.call({
				method: "bavic_insurance.bavic_insurance.doctype.insurance_transaction.insurance_transaction.get_product_details",
				args: {
					product: frm.doc.product
				},
				callback: function (r) {
					if (r.message) {
						frm.set_value("commission_rate", r.message.commission_rate || 0);
						frm.set_value("company_percent", r.message.company_percent || 60);
						frm.set_value("agent_percent", r.message.agent_percent || 40);
						frm.trigger("calculate_commission");
					}
				}
			});
		} else {
			frm.set_value("commission_rate", 0);
			frm.trigger("calculate_commission");
		}
	},
	policy_holder_name(frm) {
		if (frm.doc.policy_holder_name && frm.policy_holders_cache[frm.doc.policy_holder_name]) {
			let h = frm.policy_holders_cache[frm.doc.policy_holder_name];
			frm.set_value("policy_holder_email", h.email);
			frm.set_value("policy_holder_phone", h.phone);
		} else {
			if (Object.keys(frm.policy_holders_cache).length > 0) {
				frm.set_value("policy_holder_email", "");
				frm.set_value("policy_holder_phone", "");
			}
		}
	},
	amount(frm) {
		frm.trigger("calculate_commission");
	},
	commission_rate(frm) {
		frm.trigger("calculate_commission");
	},
	calculate_commission(frm) {
		let amount = frm.doc.amount || 0;
		let rate = frm.doc.commission_rate || 0;
		let comm_amount = (amount * rate) / 100;
		let comp_pct = frm.doc.company_percent || 60;
		let agent_pct = frm.doc.agent_percent || 40;

		frm.set_value("commission_amount", comm_amount);
		frm.set_value("company_amount", (comm_amount * comp_pct) / 100);
		frm.set_value("agent_amount", (comm_amount * agent_pct) / 100);
	}
});
