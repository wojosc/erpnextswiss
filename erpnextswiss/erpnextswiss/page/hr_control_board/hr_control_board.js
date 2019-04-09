frappe.pages['hr_control_board'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'HR Control Board',
		single_column: true
	});
	frappe.hr_control_board.make(page);
	frappe.hr_control_board.show_employee_content();
	frappe.hr_control_board.render_payroll_content();
	frappe.hr_control_board.render_salary_slip_content();
	$("#payroll_posting_date").val(moment().format("YYYY-MM-DD"));
	$("#payroll_start_date").val(moment().startOf('month').format("YYYY-MM-DD"));
	$("#payroll_end_date").val(moment().endOf('month').format("YYYY-MM-DD"));
	$("#payroll_frequency").change(function(){
		date_control();
	});
	$("#payroll_posting_date").change(function() {
		date_control();
	});
	// add the application reference
	frappe.breadcrumbs.add("ERPNextSwiss");
}

function date_control() {
	var value = $("#payroll_frequency").val();
	var posting_date = $("#payroll_posting_date").val();
	if (value == 'Monthly') {
		$("#payroll_start_date").val(moment(posting_date).startOf('month').format("YYYY-MM-DD"));
		$("#payroll_end_date").val(moment(posting_date).endOf('month').format("YYYY-MM-DD"));
	} else if (value == 'Fortnightly') {
		$("#payroll_start_date").val(moment(posting_date).format("YYYY-MM-DD"));
		$("#payroll_end_date").val(moment(posting_date).add(13, 'days').format("YYYY-MM-DD"));
	} else if (value == 'Weekly') {
		$("#payroll_start_date").val(moment(posting_date).format("YYYY-MM-DD"));
		$("#payroll_end_date").val(moment(posting_date).add(6, 'days').format("YYYY-MM-DD"));
	} else if (value == 'Daily') {
		$("#payroll_start_date").val(moment(posting_date).format("YYYY-MM-DD"));
		$("#payroll_end_date").val(moment(posting_date).format("YYYY-MM-DD"));
	}
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
							cap_uvg: r.message.cap_uvg,
							timesheet: 0,
							fgz_ggz_total: r.message.fgz_ggz_total,
							fgz_paid: r.message.fgz_paid,
							ggz_paid: r.message.ggz_paid})).appendTo(placeholder);
				} 
			}
		});
	},
	render_payroll_content: function() {
		frappe.call({
			method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.get_existing_payrolls',
			args: {},
			callback: function(r) {
				if (r.message) {
					var placeholder = $('#existing_payroll_content_placeholder').empty();
					$(frappe.render_template('existing_payroll_content', {
							payrolls: r.message
						})
					).appendTo(placeholder);
				} 
			}
		});
	},
	render_salary_slip_content: function() {
		frappe.call({
			method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.get_existing_salary_slips',
			args: {},
			callback: function(r) {
				if (r.message) {
					var placeholder = $('#salary_slip_content_placeholder').empty();
					$(frappe.render_template('salary_slip_content', {
							salslips: r.message
						})
					).appendTo(placeholder);
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
							cap_uvg: r.message.cap_uvg,
							timesheet: 1,
							fgz_ggz_total: r.message.fgz_ggz_total,
							fgz_paid: r.message.fgz_paid,
							ggz_paid: r.message.ggz_paid
						})
					).appendTo(placeholder);
				} 
			}
		});
	}
}

function add_fgz(btn) {
	var emp = $(btn).attr("data-employee");
	frappe.call({
		method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.get_ss_of_emp',
		args: {
			'emp': emp
		},
		callback: function(r) {
			if (r.message) {
				frappe.prompt([
					{'fieldname': 'fgz', 'fieldtype': 'Currency', 'label': __('FGZ Value'), 'reqd': 1}  
				],
				function(values){
					frappe.call({
						method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.add_fgz',
						args: {
							'ss': r.message[0].name,
							'fgz': values.fgz
						},
						callback: function(r) {
							if (r.message) {
								frappe.msgprint(__("FGZ successfully added"), __("Success"));
							} 
						}
					});
				},
				'Add FGZ',
				'Add'
				)
			} 
		}
	});
}

function add_ggz(btn) {
	var emp = $(btn).attr("data-employee");
	frappe.call({
		method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.get_ss_of_emp',
		args: {
			'emp': emp
		},
		callback: function(r) {
			if (r.message) {
				frappe.prompt([
					{'fieldname': 'ggz', 'fieldtype': 'Currency', 'label': __('GGZ Value'), 'reqd': 1}  
				],
				function(values){
					frappe.call({
						method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.add_ggz',
						args: {
							'ss': r.message[0].name,
							'ggz': values.ggz
						},
						callback: function(r) {
							if (r.message) {
								frappe.msgprint(__("GGZ successfully added"), __("Success"));
							} 
						}
					});
				},
				'Add GGZ',
				'Add'
				)
			} 
		}
	});
}

function create_payroll() {
	console.log("hurra");
	var freq = $("#payroll_frequency").val();
	var type = $("#payroll_type").val();
	var posting_date = $("#payroll_posting_date").val();
	var start = $("#payroll_start_date").val();
	var end = $("#payroll_end_date").val();
	frappe.call({
		method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.create_payroll',
		args: {
			'freq': freq,
			'type': type,
			'posting_date': posting_date,
			'start': start,
			'end': end
		},
		callback: function(r) {
			if (r.message) {
				open_existing_payroll_list();
			} 
		}
	});
}

function open_existing_payroll_list() {
	frappe.call({
		method: 'erpnextswiss.erpnextswiss.page.hr_control_board.hr_control_board.get_existing_payrolls',
		args: {},
		callback: function(r) {
			if (r.message) {
				var placeholder = $('#existing_payroll_content_placeholder').empty();
				$(frappe.render_template('existing_payroll_content', {
						payrolls: r.message
					})
				).appendTo(placeholder);
			} 
		}
	});
	$("#click_to_old_payroll").click();
}

function openPayroll(btn) {
  var url_raw = $(btn).attr("data-payroll");
  var url = 'desk#Form/Payroll Entry/' + url_raw;
  var win = window.open(url, '_blank');
  win.focus();
}