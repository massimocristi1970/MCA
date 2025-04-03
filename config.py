
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
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.04,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.2,
        'Gross Burn Rate': 12000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Manufacturing': {
        'Debt Service Coverage Ratio': 1.4, 
        'Net Income': 0, 
        'Operating Margin': 0.6,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.18,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Information Technology and Software': {
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
    'Healthcare and Pharmaceuticals': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Education and Training': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Utilities and Energy': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Professional and Financial Services': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Consumer Staples': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.3,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Real Estate': {
        'Debt Service Coverage Ratio': 1.4, 
        'Net Income': 0, 
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Government and Public Sector': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.1,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Transportation and Logistics': {
        'Debt Service Coverage Ratio': 1.4, 
        'Net Income': 0, 
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Environmental Services': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.06,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.12,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Scientific Research and Development': {
        'Debt Service Coverage Ratio': 1.5, 
        'Net Income': 0, 
        'Operating Margin': 0.05,
        'Expense-to-Revenue Ratio': 1.2,
        'Revenue Growth Rate': 0.03,
        'Cash Flow Volatility': 0.15,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 0,
    },
    'Hospitality and Tourism': {
        'Debt Service Coverage Ratio': 1.4, 
        'Net Income': 0, 
        'Operating Margin': 0.4,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.22,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Entertainment and Leisure': {
        'Debt Service Coverage Ratio': 1.2, 
        'Net Income': 0, 
        'Operating Margin': 0.4,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.01,
        'Cash Flow Volatility': 0.25,
        'Gross Burn Rate': 12000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Construction': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.18,
        'Gross Burn Rate': 20000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Automotive': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.18,
        'Gross Burn Rate': 18000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Agriculture and Farming': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.20,
        'Gross Burn Rate': 18000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Telecommunications': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.20,
        'Gross Burn Rate': 18000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Mining and Extraction': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.20,
        'Gross Burn Rate': 18000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Media and Advertising': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.5,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.20,
        'Gross Burn Rate': 15000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Personal Services': {
        'Debt Service Coverage Ratio': 1.3, 
        'Net Income': 0, 
        'Operating Margin': 0.4,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.02,
        'Cash Flow Volatility': 0.22,
        'Gross Burn Rate': 12000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Arts and Culture': {
        'Debt Service Coverage Ratio': 1.2, 
        'Net Income': 0, 
        'Operating Margin': 0.3,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.01,
        'Cash Flow Volatility': 0.25,
        'Gross Burn Rate': 10000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
    'Event Management': {
        'Debt Service Coverage Ratio': 1.2, 
        'Net Income': 0, 
        'Operating Margin': 0.3,
        'Expense-to-Revenue Ratio': 1.1,
        'Revenue Growth Rate': 0.01,
        'Cash Flow Volatility': 0.25,
        'Gross Burn Rate': 10000,
        'Directors Score': 70,
        'Sector Risk': 1
    },
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


def calculate_risk_with_term(requested_loan, monthly_average_revenue, repayment_split=0.1):
    estimated_monthly_repayment = monthly_average_revenue * repayment_split
    estimated_term_months = requested_loan / estimated_monthly_repayment

    # Loan-to-revenue risk level
    loan_ratio = requested_loan / monthly_average_revenue
    if loan_ratio <= 0.7:
        risk_level = "Low Risk"
    elif loan_ratio <= 1.2:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"

    # Term check
    if estimated_term_months <= 6:
        term_risk = "Acceptable"
    elif estimated_term_months <= 9:
        term_risk = "Borderline"
    else:
        term_risk = "Too Long"

    message = (
        f"Loan is {risk_level} based on loan-to-revenue ratio ({loan_ratio:.2f}). "
        f"Estimated repayment term: {estimated_term_months:.1f} months ({term_risk})."
    )
    
    return risk_level, estimated_term_months, term_risk, message
