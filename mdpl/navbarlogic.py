import frappe

@frappe.whitelist(allow_guest=True)
def get_customer_for_user(user_email):
    # Fetch the customer based on the user
    customer = frappe.get_all('Portal User',
                              filters={'user': user_email},
                              fields=['parent'])

    if customer:
        return customer[0].parent
    else:
        return None
