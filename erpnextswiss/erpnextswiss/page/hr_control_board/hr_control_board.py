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
from frappe import _

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
	data['fgz_ggz_total'] = get_fgz_ggz_total()
	data['fgz_paid'] = get_fgz_paid()
	data['ggz_paid'] = get_ggz_paid()
	data['cap_alv_1'] = default_settings().cap_alv_1
	data['cap_alv_2'] = default_settings().cap_alv_2
	data['cap_uvg'] = default_settings().cap_uvg
	return data
	
def default_settings():
	return frappe.get_single('HR Default Settings')
	
def get_fgz_ggz_total():
	return frappe.db.sql("""SELECT
								`emp`.`name` AS `employee`,
								(SUM(`sd`.`amount`) * 0.0833) AS `fgz_total`,
								(SUM(`sd`.`amount`) * 0.0833) AS `ggz_total`
							FROM ((`tabEmployee` AS `emp`
							INNER JOIN `tabSalary Slip` AS `ss` ON `emp`.`name` = `ss`.`employee`)
							INNER JOIN `tabSalary Detail` AS `sd` ON `ss`.`name` = `sd`.`parent`)
							WHERE `emp`.`salary_based_on_timesheets` = 1
							AND `ss`.`docstatus` = 1
							AND `sd`.`parentfield` = 'earnings'
							AND `sd`.`salary_component` = `emp`.`salary_component`
							GROUP BY `emp`.`name`""", as_dict=True)
							
def get_fgz_paid():
	return frappe.db.sql("""SELECT
								`emp`.`name` AS `employee`,
								SUM(`sd`.`amount`) AS `fgz`
							FROM ((`tabEmployee` AS `emp`
							INNER JOIN `tabSalary Slip` AS `ss` ON `emp`.`name` = `ss`.`employee`)
							INNER JOIN `tabSalary Detail` AS `sd` ON `ss`.`name` = `sd`.`parent`)
							WHERE `emp`.`salary_based_on_timesheets` = 1
							AND `ss`.`docstatus` = 1
							AND `sd`.`parentfield` = 'earnings'
							AND `sd`.`salary_component` = '{fgz_account}'
							GROUP BY `emp`.`name`""".format(fgz_account=default_settings().fgz_component), as_dict=True)
							
def get_ggz_paid():
	return frappe.db.sql("""SELECT
								`emp`.`name` AS `employee`,
								SUM(`sd`.`amount`) AS `ggz`
							FROM ((`tabEmployee` AS `emp`
							INNER JOIN `tabSalary Slip` AS `ss` ON `emp`.`name` = `ss`.`employee`)
							INNER JOIN `tabSalary Detail` AS `sd` ON `ss`.`name` = `sd`.`parent`)
							WHERE `emp`.`salary_based_on_timesheets` = 1
							AND `ss`.`docstatus` = 1
							AND `sd`.`parentfield` = 'earnings'
							AND `sd`.`salary_component` = '{ggz_account}'
							GROUP BY `emp`.`name`""".format(ggz_account=default_settings().ggz_component), as_dict=True)
							
@frappe.whitelist()
def get_ss_of_emp(emp):
	ss_list = frappe.db.sql("""SELECT `name` FROM `tabSalary Slip` WHERE `employee` = '{emp}' AND `docstatus` = 0""".format(emp=emp), as_dict=True)
	if len(ss_list) == 1:
		return ss_list
	elif len(ss_list) > 1:
		frappe.throw(_("Please remove all unused Draft Salary Slips."))
	else:
		frappe.throw(_("Please create Pay Roll first."))
		
@frappe.whitelist()
def add_fgz(ss, fgz):
	try:
		ss = frappe.get_doc("Salary Slip", ss)
		row = ss.append('earnings', {})
		row.salary_component = default_settings().fgz_component
		row.amount = fgz
		ss.save()
		return 'ok'
	except:
		frappe.throw(_("There was something wrong"))
		
@frappe.whitelist()
def add_ggz(ss, ggz):
	try:
		ss = frappe.get_doc("Salary Slip", ss)
		row = ss.append('earnings', {})
		row.salary_component = default_settings().ggz_component
		row.amount = ggz
		ss.save()
		return 'ok'
	except:
		frappe.throw(_("There was something wrong"))
	
@frappe.whitelist()
def get_existing_payrolls():
	return frappe.db.sql("""SELECT
								`name`,
								`posting_date`,
								`start_date`,
								`end_date`,
								`salary_slip_based_on_timesheet`,
								`docstatus`
							FROM `tabPayroll Entry`
							WHERE `docstatus` != 2
							ORDER BY `posting_date` DESC""", as_dict=True)
							
@frappe.whitelist()
def create_payroll(freq, type, posting_date, start, end):
	pr = frappe.new_doc("Payroll Entry")
	pr.posting_date = posting_date
	pr.payroll_frequency = freq
	pr.salary_slip_based_on_timesheet = type
	pr.start_date = start
	pr.end_date = end
	pr.cost_center = default_settings().cost_center
	pr.payment_account = default_settings().payment_account
	pr.save()
	return pr.name
	
@frappe.whitelist()
def get_existing_salary_slips():
	sss = frappe.db.sql("""SELECT
								`name`,
								`posting_date`,
								`employee_name`,
								`salary_slip_based_on_timesheet`,
								`rounded_total`,
								REPLACE(REPLACE(`name`, ' ', '_'), '/', '_') AS `name_replaced`
							FROM `tabSalary Slip`
							WHERE `docstatus` = 0
							ORDER BY `employee_name` ASC""", as_dict=True)
							
	for ss in sss:
		ss['earnings'] = frappe.db.sql("""SELECT `salary_component`, `amount` FROM `tabSalary Detail` WHERE `parentfield` = 'earnings' AND `parent` = '{ss}'""".format(ss=ss.name), as_dict=True)
		ss['decuctions'] = frappe.db.sql("""SELECT `salary_component`, `amount` FROM `tabSalary Detail` WHERE `parentfield` = 'decuctions' AND `parent` = '{ss}'""".format(ss=ss.name), as_dict=True)
		
	return sss