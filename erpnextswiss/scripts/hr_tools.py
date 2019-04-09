# -*- coding: utf-8 -*-
#
# hr_tools.py
#
# Copyright (C) libracore, 2017-2018
# https://www.libracore.com or https://github.com/libracore
#
# For information on ERPNext, refer to https://erpnext.org/
#

import frappe

@frappe.whitelist()
def sync_employee_salary_structure(emp):
	emp = frappe.get_doc("Employee", emp)
	try:
		salary_structure = frappe.get_doc("Salary Structure", emp.name)
		sync_defaults(salary_structure, emp)
	except:
		salary_structure = create_salary_structure(emp)
	
	
def default_settings():
	return frappe.get_single('HR Default Settings')

def create_salary_structure(emp):
	salary_structure = frappe.new_doc("Salary Structure")
	salary_structure.name = emp.name
	salary_structure.payment_account = default_settings().payment_account
	if emp.status == 'Activ':
		salary_structure.is_activ = 'Yes'
	else:
		salary_structure.is_activ = 'No'
	row = salary_structure.append('employees', {})
	row.employee = emp.name
	row.from_date = emp.date_of_joining
	row.base = 0
	salary_structure.save()
	
	sync_defaults(salary_structure, emp)
	
	return salary_structure

def sync_defaults(ss, emp):
	ss.payment_account = default_settings().payment_account
	if ss.salary_slip_based_on_timesheet != emp.salary_based_on_timesheets:
		ss.salary_slip_based_on_timesheet = emp.salary_based_on_timesheets
	if emp.salary_based_on_timesheets == 1:
		ss.salary_component = emp.salary_component
		ss.hour_rate = emp.hour_rate
	if emp.status == 'Activ':
		ss.is_activ = 'Yes'
	else:
		ss.is_activ = 'No'
	ss.save()
	sync_earnings(ss, emp)
	

def sync_earnings(ss, emp):
	ss.earnings = []
	
	for earning in emp.earnings:
		row = ss.append("earnings", {})
		row.salary_component = earning.salary_component
		row.condition = earning.condition
		row.amount_based_on_formula = earning.amount_based_on_formula
		row.formula = earning.formula
		row.amount = earning.amount
		row.statistical_component = earning.statistical_component
	ss.save()
	sync_deductions(ss, emp)
	
def sync_deductions(ss, emp):
	ss.deductions = []
	for deduction in emp.deductions:
		row = ss.append("deductions", {})
		row.salary_component = deduction.salary_component
		row.condition = deduction.condition
		row.amount_based_on_formula = deduction.amount_based_on_formula
		row.formula = deduction.formula
		row.amount = deduction.amount
		row.statistical_component = deduction.statistical_component
	ss.save()