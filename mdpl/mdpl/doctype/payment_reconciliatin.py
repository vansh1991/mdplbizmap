import frappe
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import get_unreconciled_entries
@frappe.whitelist()
def get_autoreconciled_entries(self):
    get_unreconciled_entries(self)
    # self.get_nonreconciled_payment_entries()
    # self.get_invoice_entries()