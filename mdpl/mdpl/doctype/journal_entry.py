import frappe
from frappe.model.document import Document

def change_title(doc,method):
    if doc.accounts and len(doc.accounts) >0:
    
        title = doc.accounts[0].get("account")
        if doc.title != title:
            
            doc.title = title
    return