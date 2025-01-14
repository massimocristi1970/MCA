# Define the revised thresholds and weights
thresholds = {
    'Debt Service Coverage Ratio': 1.5, 
    'Net Income': 0,
    'Operating Margin': 0,
    'Expense-to-Revenue Ratio': 1.5,
    'Revenue Growth Rate': 0,
    'Debt Repayment Coverage Ratio': 0.3,
    'Cash Flow Volatility': 0,  
    'Gross Burn Rate': 10000,
    'Directors Score': 65,
    'Sector Risk': 0  
}
months_threshold = 6 

# Define industry-specific thresholds
industry_thresholds = {
    'Retail': {
        'Debt Service Coverage Ratio': 1.2, 
        'Net Income': 0, 
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 15000,
        'Directors Score': 60,
        'Sector Risk': 0
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
        'Sector Risk': 0
    },
    'Tech': {
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
    'Healthcare': {
        'Debt Service Coverage Ratio': 1.7, 
        'Net Income': 0, 
        'Operating Margin': 0.07,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.04,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 25000,
        'Directors Score': 67,
        'Sector Risk': 0
    }
}

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

 