from __future__ import unicode_literals

import frappe


def get_context(context):
	context.no_cache = 1

	task = frappe.get_doc('Task', frappe.form_dict.task)

	context.comments = frappe.get_all_with_user_permissions('Communication', filters={'reference_name': task.name, 'comment_type': 'comment'},
	fields=['subject', 'sender_full_name', 'communication_date'])

	context.doc = task
