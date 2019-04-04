frappe.pages['hr_control_board'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'HR Control Board',
		single_column: true
	});
	frappe.hr_control_board.make(page);
	frappe.hr_control_board.show_employee_content();
	
	// add the application reference
	frappe.breadcrumbs.add("ERPNextSwiss");
}

frappe.hr_control_board = {
	start: 0,
	make: function(page) {
		var me = frappe.hr_control_board;
		me.page = page;
		me.body = $('<div></div>').appendTo(me.page.main);
		var data = "";
		$(frappe.render_template('hr_control_board', data)).appendTo(me.body);
	},
	show_employee_content: function() {
		frappe.call({
			method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.get_employee_content',
			args: {},
			callback: function(r) {
				if (r.message) {
					var placeholder = $('#employee_content_placeholder');
					$(frappe.render_template('employee_content', {employees: r.message.employees, earnings: r.message.earnings, deductions: r.message.deductions})).appendTo(placeholder);
				} 
			}
		});
	}
}

function open_employee(btn) {
	var url = '/desk#Form/Employee/' + $(btn).attr("data-employee");
	var win = window.open(url, '_blank');
	win.focus();
}