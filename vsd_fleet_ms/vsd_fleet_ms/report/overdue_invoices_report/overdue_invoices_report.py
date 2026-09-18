# Copyright (c) 2026, VV SYSTEMS DEVELOPER LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate


def execute(filters=None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, None


def get_columns():
	return [
		{"fieldname": "name", "label": _("Sales Invoice"), "fieldtype": "Link", "options": "Sales Invoice", "width": 130},
		{"fieldname": "trip", "label": _("Trip"), "fieldtype": "Link", "options": "Trips", "width": 120},
		{"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link", "options": "Customer", "width": 160},
		{"fieldname": "posting_date", "label": _("Posting Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "due_date", "label": _("Due Date"), "fieldtype": "Date", "width": 110},
		{"fieldname": "days_overdue", "label": _("Days Overdue"), "fieldtype": "Int", "width": 110},
		{"fieldname": "grand_total", "label": _("Grand Total"), "fieldtype": "Currency", "options": "currency", "width": 130},
		{"fieldname": "outstanding_amount", "label": _("Outstanding Amount"), "fieldtype": "Currency", "options": "currency", "width": 150},
		{"fieldname": "currency", "label": _("Currency"), "fieldtype": "Link", "options": "Currency", "width": 90},
	]


def get_data(filters):
	# Only invoices booked against a fleet trip (Trip -> Cargo Registration -> Cargo Detail -> Sales Invoice)
	conditions, values = get_conditions(filters)
	values["today"] = nowdate()

	return frappe.db.sql(
		f"""
		SELECT DISTINCT
			si.name, cr.trip, si.customer, si.posting_date, si.due_date,
			DATEDIFF(%(today)s, si.due_date) AS days_overdue,
			si.grand_total, si.outstanding_amount, si.currency
		FROM `tabSales Invoice` si
		INNER JOIN `tabCargo Detail` cd ON cd.invoice = si.name
		INNER JOIN `tabCargo Registration` cr ON cr.name = cd.parent AND cr.trip IS NOT NULL AND cr.trip != ''
		WHERE si.docstatus = 1 AND si.outstanding_amount > 0 AND si.due_date < %(today)s {conditions}
		ORDER BY days_overdue DESC
		""",
		values,
		as_dict=1,
	)


def get_conditions(filters):
	conditions = ""
	values = {}

	if filters.get("customer"):
		conditions += " AND si.customer = %(customer)s"
		values["customer"] = filters.get("customer")

	return conditions, values
