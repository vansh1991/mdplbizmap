import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_data(filters=None):
    if filters.get('company') and filters.get('from_date') and filters.get('to_date') and not filters.get('customer'):
        data = frappe.db.sql('''
            SELECT 
                si.customer_name AS customer,
                c.pan AS pan_number,
                c.customer_type AS entity,
                c.tax_withholding_category AS section,
                stc.rate AS tax_rate,
                (SELECT stc2.total FROM `tabSales Taxes and Charges` stc2 
                 WHERE stc2.parent = si.name AND stc2.idx < stc.idx 
                 ORDER BY stc2.idx DESC LIMIT 1) AS taxable_value,
                SUM(stc.tax_amount) AS total_tax,
                SUM(stc.total) AS total
            FROM `tabSales Invoice` si
            LEFT JOIN `tabCustomer` c ON si.customer_name = c.name
            LEFT JOIN `tabSales Taxes and Charges` stc ON si.name = stc.parent
            WHERE si.docstatus = 1 
                AND stc.account_head = "TCS payable - MDPL"
                AND si.posting_date BETWEEN %s AND %s
            GROUP BY si.customer_name
            HAVING SUM(stc.tax_amount) > 0
        ''', (filters.get('from_date'), filters.get('to_date')), as_dict=1)

        return data

    if filters.get('company') and filters.get('from_date') and filters.get('to_date') and filters.get('customer'):
        data = frappe.db.sql('''
            SELECT 
                si.customer_name AS customer,
                c.pan AS pan_number,
                c.customer_type AS entity,
                c.tax_withholding_category AS section,
                stc.rate AS tax_rate,
                (SELECT stc2.total FROM `tabSales Taxes and Charges` stc2 
                 WHERE stc2.parent = si.name AND stc2.idx < stc.idx 
                 ORDER BY stc2.idx DESC LIMIT 1) AS taxable_value,
                SUM(stc.tax_amount) AS total_tax,
                SUM(stc.total) AS total
            FROM `tabSales Invoice` si
            LEFT JOIN `tabCustomer` c ON si.customer_name = c.name
            LEFT JOIN `tabSales Taxes and Charges` stc ON si.name = stc.parent
            WHERE si.docstatus = 1 
                AND stc.account_head = "TCS payable - MDPL"
                AND si.posting_date BETWEEN %s AND %s
                AND c.name = %s
            GROUP BY si.customer_name
            HAVING SUM(stc.tax_amount) > 0
        ''', (filters.get('from_date'), filters.get('to_date'), filters.get('customer')), as_dict=1)

        return data

def get_columns():
    return [
        {   
            "fieldname": "customer",
            "label": "Customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {   
            "fieldname": "pan_number",
            "label": "Pan Number",
            "fieldtype": "Data",
            "width": 150
        },
        {   
            "fieldname": "entity",
            "label": "Entity",
            "fieldtype": "Data",
            "width": 150
        },
        {   
            "fieldname": "section",
            "label": "Section",
            "fieldtype": "Data",
            "width": 150
        },
        {   
            "fieldname": "tax_rate",
            "label": "Tax Rate",
            "fieldtype": "Float",
            "width": 150
        },
        {   
            "fieldname": "taxable_value",
            "label": "Taxable Value",
            "fieldtype": "Float",
            "width": 150
        },
        {   
            "fieldname": "total_tax",
            "label": "Total Tax",
            "fieldtype": "Float",
            "width": 150
        },
        {   
            "fieldname": "total",
            "label": "Total",
            "fieldtype": "Float",
            "width": 150
        }
    ]

