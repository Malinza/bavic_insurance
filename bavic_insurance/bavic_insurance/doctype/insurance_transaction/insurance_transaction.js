frappe.ui.form.on("Insurance Transaction", {
	setup(frm) {
		frm.policy_holders_cache = {};
	},
	onload(frm) {
		if (frm.is_new()) {
			frappe.call({
				method: "bavic_insurance.bavic_insurance.doctype.insurance_transaction.insurance_transaction.get_settings_defaults",
				callback: function (r) {
					if (r.message) {
						if (frm.doc.withholding_tax_percent === undefined || frm.doc.withholding_tax_percent === null || flt(frm.doc.withholding_tax_percent) === 0) {
							frm.set_value("withholding_tax_percent", r.message.withholding_tax_percent || 0);
						}
						if (!frm.doc.company_percent && !frm.doc.agent_percent) {
							frm.set_value("company_percent", r.message.company_percent || 60);
							frm.set_value("agent_percent", r.message.agent_percent || 40);
						}
					}
				}
			});
		}
	},
	refresh(frm) {
		if (frm.is_new()) {
			if (frm.doc.withholding_tax_percent === undefined || frm.doc.withholding_tax_percent === null || flt(frm.doc.withholding_tax_percent) === 0) {
				frappe.call({
					method: "bavic_insurance.bavic_insurance.doctype.insurance_transaction.insurance_transaction.get_settings_defaults",
					callback: function (r) {
						if (r.message) {
							frm.set_value("withholding_tax_percent", r.message.withholding_tax_percent || 0);
							if (!frm.doc.company_percent && !frm.doc.agent_percent) {
								frm.set_value("company_percent", r.message.company_percent || 60);
								frm.set_value("agent_percent", r.message.agent_percent || 40);
							}
						}
					}
				});
			}
		}
		if (frm.doc.customer && frm.doc.docstatus == 0) {
			frm.trigger("customer");
		}
		if (frm.doc.product && frm.doc.docstatus == 0 && !frm.doc.commission_rate) {
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
						if (!frm.doc.commission_rate) {
							frm.set_value("commission_rate", r.message.commission_rate || 0);
						}
						if (!frm.doc.company_percent && !frm.doc.agent_percent) {
							frm.set_value("company_percent", r.message.company_percent || 60);
							frm.set_value("agent_percent", r.message.agent_percent || 40);
						}
						if (frm.doc.withholding_tax_percent === undefined || frm.doc.withholding_tax_percent === null || flt(frm.doc.withholding_tax_percent) === 0) {
							frm.set_value("withholding_tax_percent", r.message.withholding_tax_percent || 0);
						}
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
	effective_date(frm) {
		frm.trigger("calculate_renewal_date");
		frm.trigger("calculate_next_payment_date");
	},
	months(frm) {
		frm.trigger("calculate_renewal_date");
	},
	premium_payment(frm) {
		frm.trigger("calculate_next_payment_date");
	},
	calculate_renewal_date(frm) {
		if (frm.doc.effective_date) {
			let months = parseInt(frm.doc.months || 12);
			let renewal = frappe.datetime.add_months(frm.doc.effective_date, months);
			frm.set_value("renewal_date", renewal);
		}
	},
	calculate_next_payment_date(frm) {
		if (frm.doc.premium_payment === "Insurance Premium Finance IPF" && frm.doc.effective_date) {
			if (!frm.doc.next_payment_date) {
				let next_date = frappe.datetime.add_months(frm.doc.effective_date, 1);
				frm.set_value("next_payment_date", next_date);
			}
		}
	},
	amount(frm) {
		frm.trigger("calculate_commission");
	},
	commission_rate(frm) {
		frm.trigger("calculate_commission");
	},
	withholding_tax_percent(frm) {
		frm.trigger("calculate_commission");
	},
	company_percent(frm) {
		frm.trigger("calculate_commission");
	},
	agent_percent(frm) {
		frm.trigger("calculate_commission");
	},
	calculate_commission(frm) {
		let amount = flt(frm.doc.amount || 0);
		let rate = flt(frm.doc.commission_rate || 0);
		let comm_amount = (amount * rate) / 100.0;

		let wht_pct = flt(frm.doc.withholding_tax_percent || 0);
		let wht_amount = (comm_amount * wht_pct) / 100.0;
		let net_comm = comm_amount - wht_amount;

		let comp_pct = (frm.doc.company_percent !== undefined && frm.doc.company_percent !== null && flt(frm.doc.company_percent) !== 0) ? flt(frm.doc.company_percent) : 60.0;
		let agent_pct = (frm.doc.agent_percent !== undefined && frm.doc.agent_percent !== null && flt(frm.doc.agent_percent) !== 0) ? flt(frm.doc.agent_percent) : 40.0;

		frm.set_value("commission_amount", comm_amount);
		frm.set_value("withholding_tax_amount", wht_amount);
		frm.set_value("net_commission_amount", net_comm);
		frm.set_value("company_amount", (net_comm * comp_pct) / 100.0);
		frm.set_value("agent_amount", (net_comm * agent_pct) / 100.0);
	}
});
