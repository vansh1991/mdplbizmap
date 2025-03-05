# Copyright (c) 2024, bizmap and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RavenEmailNotificationForwarding(Document):

	def validate(self):
		if self.condition_based_on == "Message":
			condition = self.condition
			keywords = condition.split()
			keywords = [word for word in keywords if word.strip()]
			if len(keywords) < 3:
				frappe.throw(f"The condition must have at least three keywords.")

		if self.condition_based_on == "Subject":
			condition = self.condition
			keywords = condition.split()
			keywords = [word for word in keywords if word.strip()]
			if len(keywords) < 3:
				frappe.throw(f"The condition must have at least three keywords.")
			
