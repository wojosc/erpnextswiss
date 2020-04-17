# -*- coding: utf-8 -*-
# Copyright (c) 2020, libracore and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import time
import cgi          
import re
from facturx import generate_facturx_from_file
from frappe.utils.pdf import get_pdf
from facturx import generate_facturx_from_binary, get_facturx_xml_from_pdf
from bs4 import BeautifulSoup
from frappe.utils.file_manager import save_file
from pathlib import Path

"""
Creates an XML file from a sales invoice
:params:sales_invoice:   document name of the sale invoice
:returns:                xml content (string)
"""

@frappe.whitelist()
def create_zugferd_pdf(sales_invoice_name, verify=True, format=None, doc=None, no_letterhead=0):
    try:
   
        doctype = "Sales Invoice"
        html = frappe.get_print(doctype, sales_invoice_name, format, doc=doc, no_letterhead=no_letterhead)
	
        pdf = get_pdf(html)
        xml = extract_xml(sales_invoice_name)
    
        # facturx_pdf = generate_facturx_from_binary(pdf, xml.encode('utf-8'))  ## The second argument of the method generate_facturx must be either a string, an etree.Element() object or a file (it is a <class 'bytes'>).
        facturx_pdf = generate_facturx_from_binary(pdf, xml)  ## Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.
        
        return facturx_pdf
    except Exception as err:
        frappe.log_error("Unable to create zugferdPDF: {0}\n{1}".format(err, xml), "ZUGFeRD")
        # fallback to normal pdf
        pdf = get_pdf(html)
    
    
    
   
def extract_xml(sales_invoice_name):
        if sinv:
            doc=frappe.get_doc('Sales Invoice', sinv) 
        else:
            frappe.throw("Please provide an argument")
            
        data = {}
        data['rechnungsnummer'] = doc.name
        
        #provider_details = frappe.get_doc('Healthcare Practitioner', doc.ref_practitioner)
        #provider_address = get_primary_address(target_name=doc.ref_practitioner, target_type="Healthcare Practitioner")
         
        #data['provider'] = {
            #'designation' : provider_details.designation or "",
            #'zip' : provider_address.get('pincode', ""),
            #}  
       
        content = frappe.render_template('erpnextswiss/erpnextswiss/zugferd/basicTemplate.html', data)
        return {'content': content}
