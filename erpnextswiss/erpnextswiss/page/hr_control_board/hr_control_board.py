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
def get_employee_content(year=None, timesheet=None):
	data = {}
	ts_filter = ''
	if timesheet:
		ts_filter = ' WHERE `salary_based_on_timesheets` = 1'
	else:
		ts_filter = ' WHERE `salary_based_on_timesheets` = 0'
	data['employees'] = frappe.db.sql("""SELECT
								`name`,
								`employee_name`
							FROM `tabEmployee`{ts_filter}""".format(ts_filter=ts_filter), as_dict=True)
							
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
										
	if year:
		filter = """ AND YEAR(`posting_date`) = '{year}'""".format(year=year)
	else:
		filter = ' AND YEAR(`posting_date`) = YEAR(CURDATE())'
	data['already_paid'] = frappe.db.sql("""SELECT `employee`, SUM(`gross_pay`) AS 'gross_pay' FROM `tabSalary Slip` WHERE `status` = 'Submitted'{filter} GROUP BY `employee`""".format(filter=filter), as_dict=True)
	
	data['cap_alv_1'] = default_settings().cap_alv_1
	data['cap_alv_2'] = default_settings().cap_alv_2
	data['cap_uvg'] = default_settings().cap_uvg
	return data
	
def default_settings():
	return frappe.get_single('HR Default Settings')
	