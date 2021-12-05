from __future__ import unicode_literals

import frappe

from erpnext.regional.united_states.setup import make_custom_fields


def execute():
	company = frappe.get_all_with_user_permissions('Company', filters={'country': 'United States'})
	if not company:
		return

	make_custom_fields()
