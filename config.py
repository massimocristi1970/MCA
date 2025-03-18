
months_threshold = 6 

# 0-Low Risk 1-High Risk
"""
Low -Risk
    Healthcare and Pharmaceuticals -
    Information Technology and Software -
    Education and Training -
    Utilities and Energy -
    Professional and Financial Services -
    Consumer Staples -
    Real Estate -
    Government and Public Sector -
    Transportation and Logistics -
    Environmental Services -
    Scientific Research and Development -

High Risk
    Hospitality and Tourism -
    Entertainment and Leisure -
    Retail -
    Construction -
    Automotive -
    Agriculture and Farming -
    Manufacturing -
    Telecommunications -
    Mining and Extraction 
    Media and Advertising 
    Personal Services 
    Arts and Culture 
    Event Management 
"""

# Define industry-specific thresholds
industry_thresholds = dict(sorted({
    'Retail': {
        'Debt Service Coverage Ratio': 1.2, 
        'Net Income': 0, 
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 15000,
        'Directors Score': 60,
        'Sector Risk': 1
    },
    'Manufacturing': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Information Technology and Software': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.05,
        'Revenue Growth Rate': 0.05,
        'Cash Flow Volatility': 0.3,
        'Gross Burn Rate': 50000,
        'Directors Score': 70,
        'Sector Risk': 0
    },
    'Healthcare and Pharmaceuticals': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Education and Training': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Utilities and Energy': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Professional and Financial Services': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Consumer Staples': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Real Estate': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Government and Public Sector': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Transportation and Logistics': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Environmental Services': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Scientific Research and Development': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0,
    },
    'Hospitality and Tourism': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Entertainment and Leisure': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Construction': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Automotive': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Agriculture and Farming': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Telecommunications': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Mining and Extraction': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Media and Advertising': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Personal Services': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Arts and Culture': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
    'Event Management': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.1,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 65,
        'Sector Risk': 1
    },
}.items()))


weights = {
    'Debt Service Coverage Ratio': 20,  
    'Net Income': 15,                   
    'Operating Margin': 10,             
    'Expense-to-Revenue Ratio': 5,     
    'Revenue Growth Rate': 10,           
    'Debt Repayment Coverage Ratio': 5,
    'Cash Flow Volatility': 10,          
    'Gross Burn Rate': 5,               
    'Months': 5,                       
    'Directors Score': 10,
    'Sector Risk': 5
}


def calculate_risk(requested_loan, monthly_average_revenue):
    if requested_loan <= monthly_average_revenue:
        return 'Low Risk', f"Requested loan amount of {requested_loan} is less than or equal to 100% of the average monthly revenue ({monthly_average_revenue}), classified as Low Risk."
    elif monthly_average_revenue < requested_loan <= (1.5 * monthly_average_revenue):
        return 'Medium Risk', f"Requested loan amount of {requested_loan} is between 100% and 150% of the average monthly revenue ({monthly_average_revenue}), classified as Medium Risk."
    else:
        return 'High Risk', f"Requested loan amount of {requested_loan} is greater than 150% of the average monthly revenue ({monthly_average_revenue}), classified as High Risk."
