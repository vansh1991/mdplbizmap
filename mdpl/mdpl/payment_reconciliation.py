import frappe
import json
from erpnext.accounts.doctype.payment_reconciliation.payment_reconciliation import PaymentReconciliation

@frappe.whitelist()
def get_unreconciled_entries_for_doc(doc):
    reconciliation_doc = PaymentReconciliation(doc)
    return reconciliation_doc.get_unreconciled_entries()
