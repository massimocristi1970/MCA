
months_threshold = 6 

# 0-Low Risk 1-High Risk
"""
Low-Risk Sectors:
    Agriculture / Forestry / Fishing
    Business Services
    Charities / Social Enterprises
    Convenience Store
    Dental Practice
    Education
    Environmental
    Engineering
    Finance & Insurance
    IT Services
    Medical / Healthcare
    Property
    Technology
    Utilities
    Waste Management / Recycling
    Wholesaler / Distributor

High-Risk Sectors:
    Arts / Entertainment / Recreation
    B&B / Hotel / Guest House
    Car / Motorbike / Vehicle Dealership
    Construction
    Courier / Logistics
    Ecommerce / Online Shop
    Franchise
    Hair / Nail / Beauty Salon
    Import / Export
    Manufacturing
    Marketing / Advertising / Design
    Mining / Quarrying
    MOT / Servicing / Tyre Centre
    Off-Licence Business
    Personal Services
    Printing / Publishing
    Production
    Professional
    Restaurant / Pub
    Recruitment
    Retail
    Security Services
    Spa
    Telecommunications
    Tradesman
    Transportation & Storage
    Travel Agent / Tour Operator
    Other Food Service
"""

# Define industry-specific thresholds based on updated sector risk classifications
industry_thresholds = dict(sorted({
    'Agriculture / Forestry / Fishing': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 18000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Business Services': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Convenience Store': {
        'Debt Service Coverage Ratio': 1.4,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Charities / Social Enterprises': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 12000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Dental Practice': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Education': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Environmental': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Engineering': {
        'Debt Service Coverage Ratio': 1.4,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Finance & Insurance': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.10,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'IT Services': {
        'Debt Service Coverage Ratio': 1.4,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.20,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.4,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Medical / Healthcare': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Technology': {
        'Debt Service Coverage Ratio': 1.4,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.4,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
   },
   'Manufacturing': {
        'Debt Service Coverage Ratio': 1.4,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.18,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'B&B / Hotel / Guest House': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.4,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.23,
        'Gross Burn Rate': 14000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Car / Motorbike / Vehicle Dealership': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 18000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Courier / Logistics': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 16000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Ecommerce / Online Shop': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.25,
        'Gross Burn Rate': 14000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Franchise': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Hair / Nail / Beauty Salon': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.22,
        'Gross Burn Rate': 12000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Import / Export': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.23,
        'Gross Burn Rate': 17000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Marketing / Advertising / Design': {
        'Debt Service Coverage Ratio': 1.2,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.25,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'MOT / Servicing / Tyre Centre': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.18,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Off-Licence Business': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 12000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Printing / Publishing': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.01,
        'Cash Flow Volatility': 0.22,
        'Gross Burn Rate': 14000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Production': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.22,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Professional': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Restaurant / Pub': {
        'Debt Service Coverage Ratio': 1.2,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.25,
        'Gross Burn Rate': 13000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Recruitment': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 16000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Security Services': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.18,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Spa': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.01,
        'Cash Flow Volatility': 0.24,
        'Gross Burn Rate': 12000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Tradesman': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.18,
        'Gross Burn Rate': 14000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Transportation & Storage': {
        'Debt Service Coverage Ratio': 1.4,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Travel Agent / Tour Operator': {
        'Debt Service Coverage Ratio': 1.2,
        'Net Income': 0,
        'Operating Margin': 0.03,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.01,
        'Cash Flow Volatility': 0.25,
        'Gross Burn Rate': 13000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Waste Management / Recycling': {
        'Debt Service Coverage Ratio': 1.5,
        'Net Income': 0,
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Wholesaler / Distributor': {
        'Debt Service Coverage Ratio': 1.4,
        'Net Income': 0,
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 18000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Other Food Service': {
        'Debt Service Coverage Ratio': 1.3,
        'Net Income': 0,
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.22,
        'Gross Burn Rate': 14000,
        'Directors Score': 70,
        'Sector Risk': 1
    }
}.items()))


weights = {
    'Debt Service Coverage Ratio': 20,  
    'Net Income': 15,                   
    'Operating Margin': 8,             
    'Expense-to-Revenue Ratio': 7,     
    'Revenue Growth Rate': 5,           
    'Debt Repayment Coverage Ratio': 5,
    'Cash Flow Volatility': 12,          
    'Gross Burn Rate': 3,               
    'Months': 5,                       
    'Directors Score': 12,
    'Sector Risk': 8
}


def calculate_risk(requested_loan, monthly_average_revenue):
    if requested_loan <= monthly_average_revenue:
        return 'Low Risk', f"Requested loan amount of {requested_loan} is less than or equal to 100% of the average monthly revenue ({monthly_average_revenue}), classified as Low Risk."
    elif monthly_average_revenue < requested_loan <= (1.5 * monthly_average_revenue):
        return 'Medium Risk', f"Requested loan amount of {requested_loan} is between 100% and 150% of the average monthly revenue ({monthly_average_revenue}), classified as Medium Risk."
    else:
        return 'High Risk', f"Requested loan amount of {requested_loan} is greater than 150% of the average monthly revenue ({monthly_average_revenue}), classified as High Risk."
