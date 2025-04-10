app_name = "mdpl"
app_title = "MDPL"
app_publisher = "bizmap"
app_description = "mdpl"
app_email = "bizmap@gmail.com"
app_license = "mit"
# required_apps = []

# override delivery note
import erpnext.stock.doctype.delivery_note.delivery_note as delivery_note
from mdpl.mdpl.doctype.delivery_note import custom_make_sales_invoice

delivery_note.make_sales_invoice = custom_make_sales_invoice

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/mdpl/css/mdpl.css"
# app_include_js = "/assets/mdpl/js/mdpl.js"
app_include_js = ["/home/bizmap/frappe-bench/apps/mdpl/mdpl/public/js/custom_navbar.js",
                  "/home/bizmap/frappe-bench/apps/mdpl/mdpl/public/js/testing.js"]
# include js, css files in header of web template
# web_include_css = "/assets/mdpl/css/mdpl.css"
# web_include_js = "/assets/mdpl/js/mdpl.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "mdpl/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    # "doctype" : "public/js/doctype.js"
    "Payment Reconciliation": "public/js/payment_reconcilation.js",
    }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "mdpl/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "mdpl.utils.jinja_methods",
# 	"filters": "mdpl.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "mdpl.install.before_install"
# after_install = "mdpl.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "mdpl.uninstall.before_uninstall"
# after_uninstall = "mdpl.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "mdpl.utils.before_app_install"
# after_app_install = "mdpl.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "mdpl.utils.before_app_uninstall"
# after_app_uninstall = "mdpl.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "mdpl.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
"Sales Invoice":"mdpl.mdpl.doctype.sales_invoice.CustomSalesInvoice"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"*": {
       
        "validate":[
			"mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven",
            "mdpl.mdpl.doctype.raven_notification.raven_notification.trigger_on_save_for_value_change"
			
			],
        "on_cancel":[
			"mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven",
			
			],
        "on_submit":[
			"mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven",
			
			],
        "after_insert":[
			"mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven",
			
			],
        "before_insert":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "before_validate":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "after_save":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "before_save":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        # "before_rename":[
        #     "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		# ],
        # "after_rename":[
        #     "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		# ],
        "before_submit":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "on_update_after_submit":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "before_submit":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "before_cancel":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "on_cancel":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "after_delete":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "before_update_after_submit":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        "on_trash":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_a_raven_for_method_event",
		],
        
        

	},
    "Communication":{
        "after_insert":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_raven_to_email_receiver",],
        "validate":[
            "mdpl.mdpl.doctype.raven_notification.raven_notification.send_raven_to_email_receiver",]
    },
    "Sales Invoice":{
         "after_save":[
            "mdpl.mdpl.doctype.task.remove_account_head_row_for_is_return_sales",]

    },
    "Journal Entry":{
    "before_save":["mdpl.mdpl.doctype.journal_entry.change_title",]
    }
    
}

jinja = {
    "templates": [
        "/mdpl/templates/navbar.html"
    ]
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron":{
        "0 8 * * *":[
               "mdpl.mdpl.doctype.task.send_email_on_incomplete_task",
		],
        },
    # "all": [
	# 	"mdpl.tasks.all"
	# ],    
	"daily": [
		"mdpl.mdpl.doctype.task.send_email_on_incomplete_task",
        "mdpl.mdpl.doctype.raven_notification.raven_notification.send_raven_for_daily"
	],
	# "hourly": [
	# 	"mdpl.tasks.hourly"
	# ],
	# "weekly": [
	# 	"mdpl.tasks.weekly"
	# ],
	# "monthly": [
	# 	"mdpl.tasks.monthly"
	# ],
}

# Testing
# -------

# before_tests = "mdpl.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "mdpl.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "mdpl.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["mdpl.utils.before_request"]
# after_request = ["mdpl.utils.after_request"]

# Job Events
# ----------
# before_job = ["mdpl.utils.before_job"]
# after_job = ["mdpl.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"mdpl.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

