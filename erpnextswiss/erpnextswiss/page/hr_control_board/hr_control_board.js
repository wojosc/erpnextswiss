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
					var placeholder = $('#employee_content_placeholder').empty();
					$(frappe.render_template('employee_content', {
							employees: r.message.employees,
							earnings: r.message.earnings,
							deductions: r.message.deductions,
							already_paid: r.message.already_paid,
							cap_alv_1: r.message.cap_alv_1,
							cap_alv_2: r.message.cap_alv_2,
							cap_uvg: r.message.cap_uvg})).appendTo(placeholder);
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

function change_sal_typ(btn) {
	$(btn).parent().addClass("active");
	$(btn).parent().siblings().removeClass("active");
	if ($(btn).parent().attr("id") == 'm_sal') {
		frappe.hr_control_board.show_employee_content();
	} else {
		frappe.call({
			method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.get_employee_content',
			args: {
				'timesheet': 1
			},
			callback: function(r) {
				if (r.message) {
					var placeholder = $('#employee_content_placeholder').empty();
					$(frappe.render_template('employee_content', {
							employees: r.message.employees,
							earnings: r.message.earnings,
							deductions: r.message.deductions,
							already_paid: r.message.already_paid,
							cap_alv_1: r.message.cap_alv_1,
							cap_alv_2: r.message.cap_alv_2,
							cap_uvg: r.message.cap_uvg})).appendTo(placeholder);
				} 
			}
		});
	}
}