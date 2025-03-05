# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
import erpnext
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class CustomSalesInvoice(SalesInvoice):
    def on_submit(self):
        super().on_submit()
        if self.is_return == 1:
            self.remove_tcs_row()
            self.calculate_taxes_and_totals()
            
        
    def before_save(self):
        super().before_save()
        if self.is_return == 1:
            self.remove_tcs_row()
            self.calculate_taxes_and_totals()

    def validate(self):
        super().validate()
        if self.is_return == 1:
            self.remove_tcs_row()
            self.calculate_taxes_and_totals()

            
    def remove_tcs_row(self):
        account_head = frappe.get_single("India TCS 206C_1H App Settings")
        tcs_payble = 0
        if self.taxes and self.taxes[-1].get("account_head") == account_head.tcs_account:
            tcs_payble = self.taxes[-1].get("tax_amount")
        self.taxes = [row for row in self.taxes if row.get("account_head") != account_head.tcs_account]
        
        if self.taxes:
            total_amount = 0
            for row in self.taxes:
                total_amount += row.get("tax_amount")
            self.total_taxes_and_charges = total_amount
            self.grand_total = self.grand_total - tcs_payble
            self.rounded_total = round((self.rounded_total - tcs_payble))

    