# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import json
import os

import frappe
from frappe import _
from frappe.desk.doctype.global_search_settings.global_search_settings import (
	update_global_search_doctypes,
)
from frappe.desk.page.setup_wizard.setup_wizard import make_records
from frappe.utils import cstr, getdate
from frappe.utils.nestedset import rebuild_tree

from erpnext.accounts.doctype.account.account import RootNotEditable
from erpnext.regional.address_template.setup import set_up_address_templates

default_lead_sources = ["Existing Customer", "Reference", "Advertisement",
	"Cold Calling", "Exhibition", "Supplier Reference", "Mass Mailing",
	"Customer's Vendor", "Campaign", "Walk In"]

default_sales_partner_type = ["Channel Partner", "Distributor", "Dealer", "Agent",
	"Retailer", "Implementation Partner", "Reseller"]

def install(country=None):
	records = [
		# domains
		{ 'doctype': 'Domain', 'domain': 'Distribution'},
		{ 'doctype': 'Domain', 'domain': 'Manufacturing'},
		{ 'doctype': 'Domain', 'domain': 'Retail'},
		{ 'doctype': 'Domain', 'domain': 'Services'},
		{ 'doctype': 'Domain', 'domain': 'Education'},
		{ 'doctype': 'Domain', 'domain': 'Healthcare'},
		{ 'doctype': 'Domain', 'domain': 'Agriculture'},
		{ 'doctype': 'Domain', 'domain': 'Non Profit'},

		# ensure at least an empty Address Template exists for this Country
		{'doctype':"Address Template", "country": country},

		# item group
		{'doctype': 'Item Group', 'item_group_name': ('All Item Groups'),
			'is_group': 1, 'parent_item_group': ''},
		{'doctype': 'Item Group', 'item_group_name': ('Products'),
			'is_group': 0, 'parent_item_group': ('All Item Groups'), "show_in_website": 1 },
		{'doctype': 'Item Group', 'item_group_name': ('Raw Material'),
			'is_group': 0, 'parent_item_group': ('All Item Groups') },
		{'doctype': 'Item Group', 'item_group_name': ('Services'),
			'is_group': 0, 'parent_item_group': ('All Item Groups') },
		{'doctype': 'Item Group', 'item_group_name': ('Sub Assemblies'),
			'is_group': 0, 'parent_item_group': ('All Item Groups') },
		{'doctype': 'Item Group', 'item_group_name': ('Consumable'),
			'is_group': 0, 'parent_item_group': ('All Item Groups') },

		# salary component
		{'doctype': 'Salary Component', 'salary_component': ('Income Tax'), 'description': ('Income Tax'), 'type': 'Deduction', 'is_income_tax_component': 1},
		{'doctype': 'Salary Component', 'salary_component': ('Basic'), 'description': ('Basic'), 'type': 'Earning'},
		{'doctype': 'Salary Component', 'salary_component': ('Arrear'), 'description': ('Arrear'), 'type': 'Earning'},
		{'doctype': 'Salary Component', 'salary_component': ('Leave Encashment'), 'description': ('Leave Encashment'), 'type': 'Earning'},


		# expense claim type
		{'doctype': 'Expense Claim Type', 'name': ('Calls'), 'expense_type': ('Calls')},
		{'doctype': 'Expense Claim Type', 'name': ('Food'), 'expense_type': ('Food')},
		{'doctype': 'Expense Claim Type', 'name': ('Medical'), 'expense_type': ('Medical')},
		{'doctype': 'Expense Claim Type', 'name': ('Others'), 'expense_type': ('Others')},
		{'doctype': 'Expense Claim Type', 'name': ('Travel'), 'expense_type': ('Travel')},

		# leave type
		{'doctype': 'Leave Type', 'leave_type_name': ('Casual Leave'), 'name': ('Casual Leave'),
			'allow_encashment': 1, 'is_carry_forward': 1, 'max_continuous_days_allowed': '3', 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': ('Compensatory Off'), 'name': ('Compensatory Off'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'include_holiday': 1, 'is_compensatory':1 },
		{'doctype': 'Leave Type', 'leave_type_name': ('Sick Leave'), 'name': ('Sick Leave'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': ('Privilege Leave'), 'name': ('Privilege Leave'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'include_holiday': 1},
		{'doctype': 'Leave Type', 'leave_type_name': ('Leave Without Pay'), 'name': ('Leave Without Pay'),
			'allow_encashment': 0, 'is_carry_forward': 0, 'is_lwp':1, 'include_holiday': 1},

		# Employment Type
		{'doctype': 'Employment Type', 'employee_type_name': ('Full-time')},
		{'doctype': 'Employment Type', 'employee_type_name': ('Part-time')},
		{'doctype': 'Employment Type', 'employee_type_name': ('Probation')},
		{'doctype': 'Employment Type', 'employee_type_name': ('Contract')},
		{'doctype': 'Employment Type', 'employee_type_name': ('Commission')},
		{'doctype': 'Employment Type', 'employee_type_name': ('Piecework')},
		{'doctype': 'Employment Type', 'employee_type_name': ('Intern')},
		{'doctype': 'Employment Type', 'employee_type_name': ('Apprentice')},


		# Stock Entry Type
		{'doctype': 'Stock Entry Type', 'name': 'Material Issue', 'purpose': 'Material Issue'},
		{'doctype': 'Stock Entry Type', 'name': 'Material Receipt', 'purpose': 'Material Receipt'},
		{'doctype': 'Stock Entry Type', 'name': 'Material Transfer', 'purpose': 'Material Transfer'},
		{'doctype': 'Stock Entry Type', 'name': 'Manufacture', 'purpose': 'Manufacture'},
		{'doctype': 'Stock Entry Type', 'name': 'Repack', 'purpose': 'Repack'},
		{'doctype': 'Stock Entry Type', 'name': 'Send to Subcontractor', 'purpose': 'Send to Subcontractor'},
		{'doctype': 'Stock Entry Type', 'name': 'Material Transfer for Manufacture', 'purpose': 'Material Transfer for Manufacture'},
		{'doctype': 'Stock Entry Type', 'name': 'Material Consumption for Manufacture', 'purpose': 'Material Consumption for Manufacture'},

		# Designation
		{'doctype': 'Designation', 'designation_name': ('CEO')},
		{'doctype': 'Designation', 'designation_name': ('Manager')},
		{'doctype': 'Designation', 'designation_name': ('Analyst')},
		{'doctype': 'Designation', 'designation_name': ('Engineer')},
		{'doctype': 'Designation', 'designation_name': ('Accountant')},
		{'doctype': 'Designation', 'designation_name': ('Secretary')},
		{'doctype': 'Designation', 'designation_name': ('Associate')},
		{'doctype': 'Designation', 'designation_name': ('Administrative Officer')},
		{'doctype': 'Designation', 'designation_name': ('Business Development Manager')},
		{'doctype': 'Designation', 'designation_name': ('HR Manager')},
		{'doctype': 'Designation', 'designation_name': ('Project Manager')},
		{'doctype': 'Designation', 'designation_name': ('Head of Marketing and Sales')},
		{'doctype': 'Designation', 'designation_name': ('Software Developer')},
		{'doctype': 'Designation', 'designation_name': ('Designer')},
		{'doctype': 'Designation', 'designation_name': ('Researcher')},

		# territory: with two default territories, one for home country and one named Rest of the World
		{'doctype': 'Territory', 'territory_name': ('All Territories'), 'is_group': 1, 'name': ('All Territories'), 'parent_territory': ''},
		{'doctype': 'Territory', 'territory_name': country.replace("'", ""), 'is_group': 0, 'parent_territory': ('All Territories')},
		{'doctype': 'Territory', 'territory_name': ("Rest Of The World"), 'is_group': 0, 'parent_territory': ('All Territories')},

		# customer group
		{'doctype': 'Customer Group', 'customer_group_name': ('All Customer Groups'), 'is_group': 1, 	'name': ('All Customer Groups'), 'parent_customer_group': ''},
		{'doctype': 'Customer Group', 'customer_group_name': ('Individual'), 'is_group': 0, 'parent_customer_group': ('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': ('Commercial'), 'is_group': 0, 'parent_customer_group': ('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': ('Non Profit'), 'is_group': 0, 'parent_customer_group': ('All Customer Groups')},
		{'doctype': 'Customer Group', 'customer_group_name': ('Government'), 'is_group': 0, 'parent_customer_group': ('All Customer Groups')},

		# supplier group
		{'doctype': 'Supplier Group', 'supplier_group_name': ('All Supplier Groups'), 'is_group': 1, 'name': ('All Supplier Groups'), 'parent_supplier_group': ''},
		{'doctype': 'Supplier Group', 'supplier_group_name': ('Services'), 'is_group': 0, 'parent_supplier_group': ('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': ('Local'), 'is_group': 0, 'parent_supplier_group': ('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': ('Raw Material'), 'is_group': 0, 'parent_supplier_group': ('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': ('Electrical'), 'is_group': 0, 'parent_supplier_group': ('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': ('Hardware'), 'is_group': 0, 'parent_supplier_group': ('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': ('Pharmaceutical'), 'is_group': 0, 'parent_supplier_group': ('All Supplier Groups')},
		{'doctype': 'Supplier Group', 'supplier_group_name': ('Distributor'), 'is_group': 0, 'parent_supplier_group': ('All Supplier Groups')},

		# Sales Person
		{'doctype': 'Sales Person', 'sales_person_name': ('Sales Team'), 'is_group': 1, "parent_sales_person": ""},

		# Mode of Payment
		{'doctype': 'Mode of Payment',
			'mode_of_payment': 'Check' if country=="United States" else ('Cheque'),
			'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': ('Cash'),
			'type': 'Cash'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': ('Credit Card'),
			'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': ('Wire Transfer'),
			'type': 'Bank'},
		{'doctype': 'Mode of Payment', 'mode_of_payment': ('Bank Draft'),
			'type': 'Bank'},

		# Activity Type
		{'doctype': 'Activity Type', 'activity_type': ('Planning')},
		{'doctype': 'Activity Type', 'activity_type': ('Research')},
		{'doctype': 'Activity Type', 'activity_type': ('Proposal Writing')},
		{'doctype': 'Activity Type', 'activity_type': ('Execution')},
		{'doctype': 'Activity Type', 'activity_type': ('Communication')},

		{'doctype': "Item Attribute", "attribute_name": ("Size"), "item_attribute_values": [
			{"attribute_value": ("Extra Small"), "abbr": "XS"},
			{"attribute_value": ("Small"), "abbr": "S"},
			{"attribute_value": ("Medium"), "abbr": "M"},
			{"attribute_value": ("Large"), "abbr": "L"},
			{"attribute_value": ("Extra Large"), "abbr": "XL"}
		]},

		{'doctype': "Item Attribute", "attribute_name": ("Colour"), "item_attribute_values": [
			{"attribute_value": ("Red"), "abbr": "RED"},
			{"attribute_value": ("Green"), "abbr": "GRE"},
			{"attribute_value": ("Blue"), "abbr": "BLU"},
			{"attribute_value": ("Black"), "abbr": "BLA"},
			{"attribute_value": ("White"), "abbr": "WHI"}
		]},

		# Issue Priority
		{'doctype': 'Issue Priority', 'name': ('Low')},
		{'doctype': 'Issue Priority', 'name': ('Medium')},
		{'doctype': 'Issue Priority', 'name': ('High')},

		#Job Applicant Source
		{'doctype': 'Job Applicant Source', 'source_name': ('Website Listing')},
		{'doctype': 'Job Applicant Source', 'source_name': ('Walk In')},
		{'doctype': 'Job Applicant Source', 'source_name': ('Employee Referral')},
		{'doctype': 'Job Applicant Source', 'source_name': ('Campaign')},

		{'doctype': "Email Account", "email_id": "sales@example.com", "append_to": "Opportunity"},
		{'doctype': "Email Account", "email_id": "support@example.com", "append_to": "Issue"},
		{'doctype': "Email Account", "email_id": "jobs@example.com", "append_to": "Job Applicant"},

		{'doctype': "Party Type", "party_type": "Customer", "account_type": "Receivable"},
		{'doctype': "Party Type", "party_type": "Supplier", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Employee", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Member", "account_type": "Receivable"},
		{'doctype': "Party Type", "party_type": "Shareholder", "account_type": "Payable"},
		{'doctype': "Party Type", "party_type": "Student", "account_type": "Receivable"},
		{'doctype': "Party Type", "party_type": "Donor", "account_type": "Receivable"},

		{'doctype': "Opportunity Type", "name": "Hub"},
		{'doctype': "Opportunity Type", "name": ("Sales")},
		{'doctype': "Opportunity Type", "name": ("Support")},
		{'doctype': "Opportunity Type", "name": ("Maintenance")},

		{'doctype': "Project Type", "project_type": "Internal"},
		{'doctype': "Project Type", "project_type": "External"},
		{'doctype': "Project Type", "project_type": "Other"},

		{"doctype": "Offer Term", "offer_term": ("Date of Joining")},
		{"doctype": "Offer Term", "offer_term": ("Annual Salary")},
		{"doctype": "Offer Term", "offer_term": ("Probationary Period")},
		{"doctype": "Offer Term", "offer_term": ("Employee Benefits")},
		{"doctype": "Offer Term", "offer_term": ("Working Hours")},
		{"doctype": "Offer Term", "offer_term": ("Stock Options")},
		{"doctype": "Offer Term", "offer_term": ("Department")},
		{"doctype": "Offer Term", "offer_term": ("Job Description")},
		{"doctype": "Offer Term", "offer_term": ("Responsibilities")},
		{"doctype": "Offer Term", "offer_term": ("Leaves per Year")},
		{"doctype": "Offer Term", "offer_term": ("Notice Period")},
		{"doctype": "Offer Term", "offer_term": ("Incentives")},

		{'doctype': "Print Heading", 'print_heading': ("Credit Note")},
		{'doctype': "Print Heading", 'print_heading': ("Debit Note")},

		# Assessment Group
		{'doctype': 'Assessment Group', 'assessment_group_name': ('All Assessment Groups'),
			'is_group': 1, 'parent_assessment_group': ''},

		# Share Management
		{"doctype": "Share Type", "title": ("Equity")},
		{"doctype": "Share Type", "title": ("Preference")},

		# Market Segments
		{"doctype": "Market Segment", "market_segment": ("Lower Income")},
		{"doctype": "Market Segment", "market_segment": ("Middle Income")},
		{"doctype": "Market Segment", "market_segment": ("Upper Income")},

		# Sales Stages
		{"doctype": "Sales Stage", "stage_name": ("Prospecting")},
		{"doctype": "Sales Stage", "stage_name": ("Qualification")},
		{"doctype": "Sales Stage", "stage_name": ("Needs Analysis")},
		{"doctype": "Sales Stage", "stage_name": ("Value Proposition")},
		{"doctype": "Sales Stage", "stage_name": ("Identifying Decision Makers")},
		{"doctype": "Sales Stage", "stage_name": ("Perception Analysis")},
		{"doctype": "Sales Stage", "stage_name": ("Proposal/Price Quote")},
		{"doctype": "Sales Stage", "stage_name": ("Negotiation/Review")},

		# Warehouse Type
		{'doctype': 'Warehouse Type', 'name': 'Transit'},
	]

	from erpnext.setup.setup_wizard.data.industry_type import get_industry_types
	records += [{"doctype":"Industry Type", "industry": d} for d in get_industry_types()]
	# records += [{"doctype":"Operation", "operation": d} for d in get_operations()]
	records += [{'doctype': 'Lead Source', 'source_name': (d)} for d in default_lead_sources]

	records += [{'doctype': 'Sales Partner Type', 'sales_partner_type': (d)} for d in default_sales_partner_type]

	base_path = frappe.get_app_path("erpnext", "hr", "doctype")
	response = frappe.read_file(os.path.join(base_path, "leave_application/leave_application_email_template.html"))

	records += [{'doctype': 'Email Template', 'name': _("Leave Approval Notification"), 'response': response,
		'subject': _("Leave Approval Notification"), 'owner': frappe.session.user}]

	records += [{'doctype': 'Email Template', 'name': _("Leave Status Notification"), 'response': response,
		'subject': _("Leave Status Notification"), 'owner': frappe.session.user}]

	response = frappe.read_file(os.path.join(base_path, "interview/interview_reminder_notification_template.html"))

	records += [{'doctype': 'Email Template', 'name': _('Interview Reminder'), 'response': response,
		'subject': _('Interview Reminder'), 'owner': frappe.session.user}]

	response = frappe.read_file(os.path.join(base_path, "interview/interview_feedback_reminder_template.html"))

	records += [{'doctype': 'Email Template', 'name': _('Interview Feedback Reminder'), 'response': response,
		'subject': _('Interview Feedback Reminder'), 'owner': frappe.session.user}]

	base_path = frappe.get_app_path("erpnext", "stock", "doctype")
	response = frappe.read_file(os.path.join(base_path, "delivery_trip/dispatch_notification_template.html"))

	records += [{'doctype': 'Email Template', 'name': _("Dispatch Notification"), 'response': response,
		'subject': _("Your order is out for delivery!"), 'owner': frappe.session.user}]

	# Records for the Supplier Scorecard
	from erpnext.buying.doctype.supplier_scorecard.supplier_scorecard import make_default_records

	make_default_records()
	make_records(records)
	set_up_address_templates(default_country=country)
	set_more_defaults()
	update_global_search_doctypes()

def set_more_defaults():
	# Do more setup stuff that can be done here with no dependencies
	update_selling_defaults()
	update_buying_defaults()
	# update_hr_defaults()
	add_uom_data()
	update_item_variant_settings()

def update_selling_defaults():
	selling_settings = frappe.get_doc("Selling Settings")
	selling_settings.set_default_customer_group_and_territory()
	selling_settings.cust_master_name = "Customer Name"
	selling_settings.so_required = "No"
	selling_settings.dn_required = "No"
	selling_settings.allow_multiple_items = 1
	selling_settings.sales_update_frequency = "Each Transaction"
	selling_settings.save()

def update_buying_defaults():
	buying_settings = frappe.get_doc("Buying Settings")
	buying_settings.supp_master_name = "Supplier Name"
	buying_settings.po_required = "No"
	buying_settings.pr_required = "No"
	buying_settings.maintain_same_rate = 1
	buying_settings.allow_multiple_items = 1
	buying_settings.save()

def update_hr_defaults():
	hr_settings = frappe.get_doc("HR Settings")
	hr_settings.emp_created_by = "Naming Series"
	hr_settings.leave_approval_notification_template = _("Leave Approval Notification")
	hr_settings.leave_status_notification_template = _("Leave Status Notification")

	hr_settings.send_interview_reminder = 1
	hr_settings.interview_reminder_template = _("Interview Reminder")
	hr_settings.remind_before = "00:15:00"

	hr_settings.send_interview_feedback_reminder = 1
	hr_settings.feedback_reminder_notification_template = _("Interview Feedback Reminder")

	hr_settings.save()

def update_item_variant_settings():
	# set no copy fields of an item doctype to item variant settings
	doc = frappe.get_doc('Item Variant Settings')
	doc.set_default_fields()
	doc.save()

def add_uom_data():
	# add UOMs
	uoms = json.loads(open(frappe.get_app_path("erpnext", "setup", "setup_wizard", "data", "uom_data.json")).read())
	for d in uoms:
		if not frappe.db.exists('UOM', (d.get("uom_name"))):
			uom_doc = frappe.get_doc({
				"doctype": "UOM",
				"uom_name": (d.get("uom_name")),
				"name": (d.get("uom_name")),
				"must_be_whole_number": d.get("must_be_whole_number")
			}).db_insert()

	# bootstrap uom conversion factors
	uom_conversions = json.loads(open(frappe.get_app_path("erpnext", "setup", "setup_wizard", "data", "uom_conversion_data.json")).read())
	for d in uom_conversions:
		if not frappe.db.exists("UOM Category", (d.get("category"))):
			frappe.get_doc({
				"doctype": "UOM Category",
				"category_name": (d.get("category"))
			}).db_insert()

		if not frappe.db.exists("UOM Conversion Factor", {"from_uom": (d.get("from_uom")), "to_uom": (d.get("to_uom"))}):
			uom_conversion = frappe.get_doc({
				"doctype": "UOM Conversion Factor",
				"category": (d.get("category")),
				"from_uom": (d.get("from_uom")),
				"to_uom": (d.get("to_uom")),
				"value": d.get("value")
			}).insert(ignore_permissions=True)

def add_market_segments():
	records = [
		# Market Segments
		{"doctype": "Market Segment", "market_segment": ("Lower Income")},
		{"doctype": "Market Segment", "market_segment": ("Middle Income")},
		{"doctype": "Market Segment", "market_segment": ("Upper Income")}
	]

	make_records(records)

def add_sale_stages():
	# Sale Stages
	records = [
		{"doctype": "Sales Stage", "stage_name": ("Prospecting")},
		{"doctype": "Sales Stage", "stage_name": ("Qualification")},
		{"doctype": "Sales Stage", "stage_name": ("Needs Analysis")},
		{"doctype": "Sales Stage", "stage_name": ("Value Proposition")},
		{"doctype": "Sales Stage", "stage_name": ("Identifying Decision Makers")},
		{"doctype": "Sales Stage", "stage_name": ("Perception Analysis")},
		{"doctype": "Sales Stage", "stage_name": ("Proposal/Price Quote")},
		{"doctype": "Sales Stage", "stage_name": ("Negotiation/Review")}
	]
	for sales_stage in records:
		frappe.get_doc(sales_stage).db_insert()

def install_company(args):
	records = [
		# Fiscal Year
		{
			'doctype': "Fiscal Year",
			'year': get_fy_details(args.fy_start_date, args.fy_end_date),
			'year_start_date': args.fy_start_date,
			'year_end_date': args.fy_end_date
		},

		# Company
		{
			"doctype":"Company",
			'company_name': args.company_name,
			'enable_perpetual_inventory': 1,
			'abbr': args.company_abbr,
			'default_currency': args.currency,
			'country': args.country,
			'create_chart_of_accounts_based_on': 'Standard Template',
			'chart_of_accounts': args.chart_of_accounts,
			'domain': args.domain
		}
	]

	make_records(records)


def install_post_company_fixtures(args=None):
	records = [
		# Department
		{'doctype': 'Department', 'department_name': 'All Departments', 'is_group': 1, 'parent_department': ''},
		{'doctype': 'Department', 'department_name': 'Accounts', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Marketing', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Sales', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Purchase', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Operations', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Production', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Dispatch', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Customer Service', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Human Resources', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Management', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Quality Management', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Research & Development', 'parent_department': 'All Departments', 'company': args.company_name},
		{'doctype': 'Department', 'department_name': 'Legal', 'parent_department': 'All Departments', 'company': args.company_name},
	]

	# Make root department with NSM updation
	make_records(records[:1])

	frappe.local.flags.ignore_update_nsm = True
	make_records(records[1:])
	frappe.local.flags.ignore_update_nsm = False
	rebuild_tree("Department", "parent_department")


def install_defaults(args=None):
	records = [
		# Price Lists
		{ "doctype": "Price List", "price_list_name": ("Standard Buying"), "enabled": 1, "buying": 1, "selling": 0, "currency": args.currency },
		{ "doctype": "Price List", "price_list_name": ("Standard Selling"), "enabled": 1, "buying": 0, "selling": 1, "currency": args.currency },
	]

	make_records(records)

	# enable default currency
	frappe.db.set_value("Currency", args.get("currency"), "enabled", 1)
	frappe.db.set_value("Stock Settings", None, "email_footer_address", args.get("company_name"))

	set_global_defaults(args)
	set_active_domains(args)
	update_stock_settings()
	update_shopping_cart_settings(args)

	args.update({"set_default": 1})
	create_bank_account(args)

def set_global_defaults(args):
	global_defaults = frappe.get_doc("Global Defaults", "Global Defaults")
	current_fiscal_year = frappe.get_all("Fiscal Year")[0]

	global_defaults.update({
		'current_fiscal_year': current_fiscal_year.name,
		'default_currency': args.get('currency'),
		'default_company':args.get('company_name')	,
		"country": args.get("country"),
	})

	global_defaults.save()

def set_active_domains(args):
	frappe.get_single('Domain Settings').set_active_domains(args.get('domains'))

def update_stock_settings():
	stock_settings = frappe.get_doc("Stock Settings")
	stock_settings.item_naming_by = "Item Code"
	stock_settings.valuation_method = "FIFO"
	stock_settings.default_warehouse = frappe.db.get_value('Warehouse', {'warehouse_name': ('Stores')})
	stock_settings.stock_uom = ("Nos")
	stock_settings.auto_indent = 1
	stock_settings.auto_insert_price_list_rate_if_missing = 1
	stock_settings.automatically_set_serial_nos_based_on_fifo = 1
	stock_settings.set_qty_in_transactions_based_on_serial_no_input = 1
	stock_settings.save()

def create_bank_account(args):
	if not args.get('bank_account'):
		return

	company_name = args.get('company_name')
	bank_account_group =  frappe.db.get_value("Account",
		{"account_type": "Bank", "is_group": 1, "root_type": "Asset",
			"company": company_name})
	if bank_account_group:
		bank_account = frappe.get_doc({
			"doctype": "Account",
			'account_name': args.get('bank_account'),
			'parent_account': bank_account_group,
			'is_group':0,
			'company': company_name,
			"account_type": "Bank",
		})
		try:
			doc = bank_account.insert()

			if args.get('set_default'):
				frappe.db.set_value("Company", args.get('company_name'), "default_bank_account", bank_account.name, update_modified=False)

			return doc

		except RootNotEditable:
			frappe.throw(("Bank account cannot be named as {0}").format(args.get('bank_account')))
		except frappe.DuplicateEntryError:
			# bank account same as a CoA entry
			pass

def update_shopping_cart_settings(args):
	shopping_cart = frappe.get_doc("E Commerce Settings")
	shopping_cart.update({
		"enabled": 1,
		'company': args.company_name,
		'price_list': frappe.db.get_value("Price List", {"selling": 1}),
		'default_customer_group': ("Individual"),
		'quotation_series': "QTN-",
	})
	shopping_cart.update_single(shopping_cart.get_valid_dict())

def get_fy_details(fy_start_date, fy_end_date):
	start_year = getdate(fy_start_date).year
	if start_year == getdate(fy_end_date).year:
		fy = cstr(start_year)
	else:
		fy = cstr(start_year) + '-' + cstr(start_year + 1)
	return fy
