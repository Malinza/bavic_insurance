frappe.ui.form.on("Excel Business Import", {

	refresh(frm) {
		// Initialize or re-render the live progress and feed dashboard
		render_live_dashboard(frm);

		// Show "Import Now" button only when document is not currently running
		if (["Draft", "Failed", "Completed", "Completed with Errors"].includes(frm.doc.status)) {
			frm.add_custom_button(__("🚀 Import Now"), () => {
				start_import(frm);
			}).addClass("btn-primary");
		}

		// Subscribe to realtime socket events (once per form instance)
		setup_realtime_listeners(frm);
	},
});


// ---------------------------------------------------------------------------
// Realtime Event Handlers
// ---------------------------------------------------------------------------

function setup_realtime_listeners(frm) {
	if (frm._ebi_subscribed) return;
	frm._ebi_subscribed = true;

	// 1. Import Init Event
	frappe.realtime.on("excel_import_init", (data) => {
		if (data.docname !== frm.docname) return;

		frm.set_value("status", "In Progress");
		frm.page.clear_custom_actions();

		// Reset counters and progress UI
		update_dashboard_counts(frm, {
			total: data.total || 0,
			imported: 0,
			skipped: 0,
			failed: 0,
			percent: 0,
			current: 0,
			statusText: "Processing rows...",
		});

		// Clear feed table
		const $tbody = frm.$wrapper.find("#ebi-feed-tbody");
		$tbody.empty();
		frm.$wrapper.find("#ebi-empty-placeholder").hide();
		frm.$wrapper.find("#ebi-feed-container").show();
	});

	// 2. Row Progress Event — Fires for EVERY single input row
	frappe.realtime.on("excel_import_row", (data) => {
		if (data.docname !== frm.docname) return;

		// Update Top Progress Bar and Counts
		update_dashboard_counts(frm, {
			total: data.total,
			current: data.current,
			percent: data.percent,
			imported: data.imported,
			skipped: data.skipped,
			failed: data.failed,
			statusText: `Processing Row ${data.current} of ${data.total}: ${data.customer}`,
		});

		// Frappe Desk standard top dashboard progress
		frm.dashboard.show_progress(
			__("Importing Businesses"),
			data.percent,
			__("Row {0} of {1} ({2}%) — {3}", [data.current, data.total, data.percent, data.customer])
		);

		// Add row to live stream table
		append_feed_row(frm, data);
	});

	// 3. Import Complete Event
	frappe.realtime.on("excel_import_complete", (data) => {
		if (data.docname !== frm.docname) return;

		update_dashboard_counts(frm, {
			total: data.total,
			current: data.total,
			percent: 100,
			imported: data.imported,
			skipped: data.skipped,
			failed: data.failed,
			statusText: data.status === "Completed" ? "🏁 Import Completed Successfully!" : "⚠️ Import Finished with Errors",
		});

		setTimeout(() => {
			frm.dashboard.hide();
			frm.reload_doc();
		}, 1500);
	});
}


// ---------------------------------------------------------------------------
// Trigger Import API
// ---------------------------------------------------------------------------

function start_import(frm) {
	if (!frm.doc.excel_file) {
		frappe.msgprint({
			title: __("File Required"),
			message: __("Please attach an Excel (.xlsx) file before starting the import."),
			indicator: "red",
		});
		return;
	}

	const confirm_msg = frm.doc.submit_after_import
		? __("<b>⚠️ Warning:</b> 'Submit After Import' is checked. Each transaction will be <b>submitted</b> immediately. Proceed?")
		: __("Start importing all rows from the attached file? Transactions will be saved as <b>Draft</b>.");

	frappe.confirm(confirm_msg, () => {
		// Update UI optimistically
		frm.set_value("status", "In Progress");
		frm.page.clear_custom_actions();

		// Show progress state
		update_dashboard_counts(frm, {
			total: 0,
			current: 0,
			percent: 0,
			imported: 0,
			skipped: 0,
			failed: 0,
			statusText: "Reading Excel file and initializing masters...",
		});

		const $tbody = frm.$wrapper.find("#ebi-feed-tbody");
		$tbody.empty();
		frm.$wrapper.find("#ebi-empty-placeholder").hide();
		frm.$wrapper.find("#ebi-feed-container").show();

		frappe.call({
			method: "bavic_insurance.bavic_insurance.doctype.excel_business_import.excel_business_import.run_import",
			args: { docname: frm.docname },
			freeze: false, // keep UI live so WebSocket events update smoothly
			callback(r) {
				if (r.message && !r.message.error) {
					const { imported, skipped, failed } = r.message;
					frappe.show_alert({
						message: __(`✅ Import Done — ${imported} imported, ${skipped} skipped (duplicates), ${failed} failed.`),
						indicator: failed > 0 ? "orange" : "green",
					}, 10);
				}
				frm.reload_doc();
			},
			error() {
				frappe.show_alert({
					message: __("❌ Import encountered an unexpected error."),
					indicator: "red",
				}, 8);
				frm.reload_doc();
			},
		});
	});
}


// ---------------------------------------------------------------------------
// Render Dashboard Component
// ---------------------------------------------------------------------------

function render_live_dashboard(frm) {
	const field = frm.get_field("live_progress_html");
	if (!field || !field.$wrapper) return;

	const is_running = frm.doc.status === "In Progress";
	const is_done = ["Completed", "Completed with Errors"].includes(frm.doc.status);
	const total = (frm.doc.imported_rows || 0) + (frm.doc.skipped_rows || 0) + (frm.doc.failed_rows || 0);
	const percent = is_done ? 100 : (total > 0 ? Math.min(100, Math.round(((frm.doc.imported_rows || 0) / total) * 100)) : 0);

	const html = `
	<div id="ebi-dashboard-root" style="margin-bottom: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
		
		<!-- 1. Top Status & Metric Cards -->
		<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 16px;">
			
			<div class="ebi-card" style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
				<div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-muted, #64748b); letter-spacing: 0.5px;">Status</div>
				<div id="ebi-badge-status" style="margin-top: 6px; display: inline-flex; align-items: center; gap: 6px; font-size: 14px; font-weight: 700; color: ${get_status_color(frm.doc.status)};">
					<span style="width: 8px; height: 8px; border-radius: 50%; background: currentColor; ${is_running ? 'animation: pulse 1.5s infinite;' : ''}"></span>
					<span id="ebi-text-status">${frm.doc.status || "Draft"}</span>
				</div>
			</div>

			<div class="ebi-card" style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
				<div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #16a34a; letter-spacing: 0.5px;">✅ Imported / Created</div>
				<div id="ebi-count-imported" style="margin-top: 6px; font-size: 20px; font-weight: 800; color: #16a34a;">${frm.doc.imported_rows || 0}</div>
			</div>

			<div class="ebi-card" style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
				<div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #d97706; letter-spacing: 0.5px;">⏭️ Skipped (Duplicates)</div>
				<div id="ebi-count-skipped" style="margin-top: 6px; font-size: 20px; font-weight: 800; color: #d97706;">${frm.doc.skipped_rows || 0}</div>
			</div>

			<div class="ebi-card" style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
				<div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #dc2626; letter-spacing: 0.5px;">❌ Failed / Errors</div>
				<div id="ebi-count-failed" style="margin-top: 6px; font-size: 20px; font-weight: 800; color: #dc2626;">${frm.doc.failed_rows || 0}</div>
			</div>

		</div>

		<!-- 2. Live Animated Progress Bar -->
		<div style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e2e8f0); border-radius: 10px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
			<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
				<div style="font-size: 13px; font-weight: 700; color: var(--text-color, #1e293b); display: flex; align-items: center; gap: 8px;">
					<span>📈 Import Progress</span>
					<span id="ebi-progress-state-text" style="font-size: 12px; font-weight: 500; color: var(--text-muted, #64748b);">
						${is_done ? "All rows processed" : (is_running ? "Processing rows..." : "Ready to import")}
					</span>
				</div>
				<div id="ebi-progress-percentage" style="font-size: 14px; font-weight: 800; color: #2563eb;">
					${percent}%
				</div>
			</div>

			<div style="width: 100%; height: 16px; background: #e2e8f0; border-radius: 9999px; overflow: hidden; position: relative;">
				<div id="ebi-progress-bar-fill" style="width: ${percent}%; height: 100%; background: linear-gradient(90deg, #3b82f6 0%, #06b6d4 50%, #10b981 100%); border-radius: 9999px; transition: width 0.25s ease-in-out;"></div>
			</div>
		</div>

		<!-- 3. Live Feed Stream Table ("where i could see every input") -->
		<div style="background: #111827; border: 1px solid #1f2937; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
			
			<!-- Feed Toolbar -->
			<div style="padding: 12px 16px; background: #1f2937; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
				<div style="display: flex; align-items: center; gap: 10px;">
					<span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #10b981;"></span>
					<span style="font-size: 13px; font-weight: 700; color: #f9fafb; letter-spacing: 0.3px;">⚡ LIVE ROW ACTIVITY FEED</span>
				</div>

				<div style="display: flex; align-items: center; gap: 12px;">
					<div class="btn-group btn-group-sm" id="ebi-filter-buttons">
						<button type="button" class="btn btn-xs btn-primary ebi-filter-btn" data-filter="all">All</button>
						<button type="button" class="btn btn-xs btn-default ebi-filter-btn" data-filter="imported">Imported</button>
						<button type="button" class="btn btn-xs btn-default ebi-filter-btn" data-filter="skipped">Duplicates</button>
						<button type="button" class="btn btn-xs btn-default ebi-filter-btn" data-filter="failed">Errors</button>
					</div>

					<label style="margin: 0; font-size: 11px; color: #9ca3af; display: flex; align-items: center; gap: 5px; cursor: pointer;">
						<input type="checkbox" id="ebi-autoscroll" checked style="cursor: pointer;"> Auto-scroll
					</label>
				</div>
			</div>

			<!-- Feed Table Container -->
			<div id="ebi-feed-container" style="max-height: 380px; overflow-y: auto; overflow-x: auto; scroll-behavior: smooth;">
				<table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 12px; color: #e5e7eb; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;">
					<thead style="background: #1e293b; position: sticky; top: 0; z-index: 2; border-bottom: 1px solid #334155;">
						<tr>
							<th style="padding: 10px 12px; width: 65px; color: #94a3b8; font-weight: 600;">#</th>
							<th style="padding: 10px 12px; width: 120px; color: #94a3b8; font-weight: 600;">Status</th>
							<th style="padding: 10px 12px; color: #94a3b8; font-weight: 600;">Customer / Policy Holder</th>
							<th style="padding: 10px 12px; width: 160px; color: #94a3b8; font-weight: 600;">Product</th>
							<th style="padding: 10px 12px; width: 130px; text-align: right; color: #94a3b8; font-weight: 600;">Amount (TZS)</th>
							<th style="padding: 10px 12px; color: #94a3b8; font-weight: 600;">Details / Reason</th>
						</tr>
					</thead>
					<tbody id="ebi-feed-tbody">
						<!-- Rows inserted here live -->
					</tbody>
				</table>
			</div>

			<!-- Empty State Message -->
			<div id="ebi-empty-placeholder" style="padding: 40px 20px; text-align: center; color: #9ca3af; display: ${frm.doc.import_log ? 'none' : 'block'};">
				<div style="font-size: 28px; margin-bottom: 8px;">📂</div>
				<div style="font-size: 13px; font-weight: 600;">No Import Runs Yet</div>
				<div style="font-size: 12px; color: #6b7280; margin-top: 4px;">Attach an Excel file and click <b>🚀 Import Now</b> to start live processing.</div>
			</div>

		</div>

	</div>
	`;

	field.$wrapper.html(html);

	// Setup Filter click events
	field.$wrapper.find(".ebi-filter-btn").on("click", function () {
		field.$wrapper.find(".ebi-filter-btn").removeClass("btn-primary").addClass("btn-default");
		$(this).removeClass("btn-default").addClass("btn-primary");
		const filter = $(this).data("filter");

		const $rows = field.$wrapper.find("#ebi-feed-tbody tr");
		if (filter === "all") {
			$rows.show();
		} else {
			$rows.hide();
			$rows.filter(`[data-status="${filter}"]`).show();
		}
	});

	// If the document already has saved log text, parse and populate table
	if (frm.doc.import_log && frm.doc.import_log.trim().length > 0) {
		populate_feed_from_log(frm, frm.doc.import_log);
	}
}


// ---------------------------------------------------------------------------
// Helpers to Update Dashboard Counts & Feed Rows
// ---------------------------------------------------------------------------

function update_dashboard_counts(frm, data) {
	const $root = frm.$wrapper;
	if (data.statusText) $root.find("#ebi-progress-state-text").text(data.statusText);
	if (data.percent !== undefined) {
		$root.find("#ebi-progress-percentage").text(`${data.percent}%`);
		$root.find("#ebi-progress-bar-fill").css("width", `${data.percent}%`);
	}
	if (data.imported !== undefined) $root.find("#ebi-count-imported").text(data.imported);
	if (data.skipped !== undefined) $root.find("#ebi-count-skipped").text(data.skipped);
	if (data.failed !== undefined) $root.find("#ebi-count-failed").text(data.failed);

	if (data.status) {
		$root.find("#ebi-text-status").text(data.status);
		$root.find("#ebi-badge-status").css("color", get_status_color(data.status));
	}
}

function append_feed_row(frm, row) {
	const $tbody = frm.$wrapper.find("#ebi-feed-tbody");
	frm.$wrapper.find("#ebi-empty-placeholder").hide();

	const badge = get_row_badge(row.status);
	const formatted_amount = Number(row.amount || 0).toLocaleString("en-US", {
		minimumFractionDigits: 2,
		maximumFractionDigits: 2,
	});

	const filter_class = row.status === "submitted" ? "imported" : row.status;

	const tr_html = `
	<tr data-status="${filter_class}" style="border-bottom: 1px solid #1f2937; transition: background 0.3s; animation: fadeInRow 0.3s ease-out;">
		<td style="padding: 8px 12px; color: #94a3b8; font-weight: 500;">${row.row_num || row.current}</td>
		<td style="padding: 8px 12px;">${badge}</td>
		<td style="padding: 8px 12px; font-weight: 600; color: #f3f4f6;">${frappe.utils.escape_html(row.customer || "-")}</td>
		<td style="padding: 8px 12px; color: #cbd5e1;">${frappe.utils.escape_html(row.product || "-")}</td>
		<td style="padding: 8px 12px; text-align: right; font-weight: 600; color: #38bdf8;">${formatted_amount}</td>
		<td style="padding: 8px 12px; color: #9ca3af; font-size: 11px;">${frappe.utils.escape_html(row.detail || row.message || "-")}</td>
	</tr>
	`;

	$tbody.append(tr_html);

	// Auto-scroll to keep latest row in view if checkbox is enabled
	const autoscroll = frm.$wrapper.find("#ebi-autoscroll").is(":checked");
	if (autoscroll) {
		const container = frm.$wrapper.find("#ebi-feed-container")[0];
		if (container) {
			container.scrollTop = container.scrollHeight;
		}
	}
}

function populate_feed_from_log(frm, log_text) {
	const lines = log_text.split("\n");
	const $tbody = frm.$wrapper.find("#ebi-feed-tbody");
	$tbody.empty();

	let row_count = 0;
	lines.forEach((line) => {
		line = line.trim();
		if (!line) return;

		let status = "imported";
		let badge = get_row_badge("imported");
		let row_num = "-";
		let customer = "-";
		let product = "-";
		let amount = "-";
		let detail = line;

		if (line.includes("✅ Row")) {
			status = line.includes("Submitted") ? "submitted" : "imported";
			badge = get_row_badge(status);
			const match = line.match(/Row (\d+): (?:Imported|Submitted) — (.*?) \| (.*?) \| ([\d,.-]+) TZS/);
			if (match) {
				row_num = match[1];
				customer = match[2];
				product = match[3];
				amount = match[4];
				detail = `Successfully ${status}`;
			}
		} else if (line.includes("⏭️ Row")) {
			status = "skipped";
			badge = get_row_badge("skipped");
			const match = line.match(/Row (\d+): Skipped duplicate — (.*?) \| (.*?) \| (.*)/);
			if (match) {
				row_num = match[1];
				customer = match[2];
				product = match[3];
				detail = `Duplicate: ${match[4]}`;
			}
		} else if (line.includes("⚠️ Row") || line.includes("❌ Row")) {
			status = "failed";
			badge = get_row_badge("failed");
			const match = line.match(/Row (\d+): (.*)/);
			if (match) {
				row_num = match[1];
				detail = match[2];
			}
		} else {
			return; // header/summary lines
		}

		row_count++;
		const filter_class = status === "submitted" ? "imported" : status;
		const tr_html = `
		<tr data-status="${filter_class}" style="border-bottom: 1px solid #1f2937;">
			<td style="padding: 8px 12px; color: #94a3b8; font-weight: 500;">${row_num}</td>
			<td style="padding: 8px 12px;">${badge}</td>
			<td style="padding: 8px 12px; font-weight: 600; color: #f3f4f6;">${frappe.utils.escape_html(customer)}</td>
			<td style="padding: 8px 12px; color: #cbd5e1;">${frappe.utils.escape_html(product)}</td>
			<td style="padding: 8px 12px; text-align: right; font-weight: 600; color: #38bdf8;">${amount !== "-" ? amount : ""}</td>
			<td style="padding: 8px 12px; color: #9ca3af; font-size: 11px;">${frappe.utils.escape_html(detail)}</td>
		</tr>
		`;
		$tbody.append(tr_html);
	});

	if (row_count > 0) {
		frm.$wrapper.find("#ebi-empty-placeholder").hide();
	}
}

function get_status_color(status) {
	switch (status) {
		case "Completed": return "#16a34a";
		case "Completed with Errors": return "#ea580c";
		case "In Progress": return "#2563eb";
		case "Failed": return "#dc2626";
		default: return "#64748b";
	}
}

function get_row_badge(status) {
	switch (status) {
		case "submitted":
			return '<span style="display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; background: #1e3a8a; color: #93c5fd; border: 1px solid #2563eb;">📋 SUBMITTED</span>';
		case "imported":
			return '<span style="display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; background: #064e3b; color: #6ee7b7; border: 1px solid #059669;">✅ IMPORTED</span>';
		case "skipped":
			return '<span style="display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; background: #78350f; color: #fcd34d; border: 1px solid #d97706;">⏭️ DUPLICATE</span>';
		case "failed":
			return '<span style="display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626;">❌ ERROR</span>';
		default:
			return '<span style="display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-weight: 700; background: #374151; color: #d1d5db;">QUEUED</span>';
	}
}
