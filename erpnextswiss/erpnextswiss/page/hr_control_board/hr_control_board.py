# -*- coding: utf-8 -*-
#
# hr_control_board.py
#
# Copyright (C) libracore, 2017-2018
# https://www.libracore.com or https://github.com/libracore
#
# For information on ERPNext, refer to https://erpnext.org/
#

import frappe

@frappe.whitelist()
def get_employee_content():
	data = {}
	data['employees'] = frappe.db.sql("""SELECT
								`name`,
								`employee_name`
							FROM `tabEmployee`""", as_dict=True)
							
	data['earnings'] = frappe.db.sql("""SELECT
											`salary_component`,
											`parent`,
											CASE
												WHEN `amount_based_on_formula` = 1 THEN `formula`
												ELSE `amount`
											END AS 'value',
											IFNULL(`condition`, '') AS 'condition'
										FROM `tabSwiss Salary Detail`
										WHERE `parentfield` = 'earnings'
										AND `parenttype` = 'Employee'""", as_dict=True)
										
	data['deductions'] = frappe.db.sql("""SELECT
											`salary_component`,
											`parent`,
											CASE
												WHEN `amount_based_on_formula` = 1 THEN `formula`
												ELSE `amount`
											END AS 'value',
											IFNULL(`condition`, '') AS 'condition'
										FROM `tabSwiss Salary Detail`
										WHERE `parentfield` = 'deductions'
										AND `parenttype` = 'Employee'""", as_dict=True)
										
	return data