// Copyright (c) 2024, bizmap and contributors
// For license information, please see license.txt

frappe.query_reports["TCS Report"] = {
	"filters": [
		{	
			fieldname:"company",
			label:("Company"),
			fieldtype:"Link",
			options:"Company",
			default:"Mahesh Distributor"
		},
		{
			label:__("From Date"),
			fieldname:"from_date",
			fieldtype:"Date"
		},
		{
			label:__("To Date"),
			fieldname:"to_date",
			fieldtype:"Date"
		},
		{
			label:__("Customer"),
			fieldname:"customer",
			fieldtype:"Link",
			options:"Customer"
		}
	]
};
