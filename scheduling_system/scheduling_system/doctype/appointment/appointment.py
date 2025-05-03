# Copyright (c) 2025, Gabriel Menezes and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class Appointment(Document):
	def calculate_end_date(self):
		if self.start and self.duration:
			hour, minute, second = map(int, self.duration.split(":"))
			return datetime.strptime(self.start, "%Y-%m-%d %H:%M:%S") + timedelta(hours=hour, minutes=minute, seconds=second)
		return None

	def before_save(self):
		self.end = self.calculate_end_date()
	

	def validate(self):
		end = self.calculate_end_date()
		confliting_appointments = frappe.db.get_all(
			"Appointment",
			filters={
				"seller": self.seller,
				"name": ["!=", self.name],
				"start": ["<=", end],
				"end": [">=", self.start],
				"status": ["!=", "Canceled"]
			},
			fields=["name", "client_name", "start", "end"]
		)
		frappe.log(f"{confliting_appointments}")
		if confliting_appointments:
			frappe.throw(
				f"Scheduling conflict for seller {self.seller}. "
				f"Already booked with client {confliting_appointments[0].client_name} from {confliting_appointments[0].start} to {confliting_appointments[0].end}."
			)	 

