import pandas as pd

def calculate_metrics(data):
    # Total Revenue (Income + Special Inflow)
    total_revenue = round(data.loc[data['is_revenue'], 'amount'].sum() or 0, 2)

    # Total Expenses
    total_expenses = round(data.loc[data['is_expense'], 'amount'].sum() or 0, 2)

    # Net Income (Revenue - Expenses)
    net_income = round(total_revenue - total_expenses, 2)

    # Total Debt Repayments
    total_debt_repayments = round(data.loc[data['is_debt_repayment'], 'amount'].sum() or 0, 2)

    # Total Debt (Loans)
    total_debt = round(data.loc[data['is_debt'], 'amount'].sum() or 0, 2)

    # Debt-to-Income Ratio
    debt_to_income_ratio = round(total_debt / total_revenue if total_revenue != 0 else 0, 2)

    # Expense-to-Revenue Ratio
    expense_to_revenue_ratio = round(total_expenses / total_revenue if total_revenue != 0 else 0, 2)

    # Operating Income (EBIT)
    operating_income = total_revenue - total_expenses

    # Operating Margin
    operating_margin = round(operating_income / total_revenue if total_revenue != 0 else 0, 2)

    # Debt Service Coverage Ratio
    debt_service_coverage_ratio = round(total_revenue / total_debt_repayments if total_debt_repayments != 0 else 0, 2)

    # Convert 'date' column to datetime for burn rate calculation
    data['date'] = pd.to_datetime(data['date'])

    # Calculate the number of months (company age)
    first_date = data['date'].min()
    last_date = data['date'].max()
    company_age_months = ((last_date.year - first_date.year) * 12 + (last_date.month - first_date.month)) + 1

    # Extract month and year for grouping transactions by month
    data['year_month'] = data['date'].dt.to_period('M')

    # Calculate monthly revenue and expenses
    monthly_summary = data.groupby('year_month').agg(
        Net_Cashflow=('amount', lambda x: x[data['is_revenue']].sum() - x[data['is_expense']].sum()),
        Monthly_Revenue=('amount', lambda x: x[data['is_revenue']].sum())
    ).reset_index()

    monthly_summary.columns = ['Year-Month', 'Net Cashflow', 'Monthly Revenue']
    monthly_summary['Monthly Expenses'] = monthly_summary['Monthly Revenue'] - monthly_summary['Net Cashflow']

    # Gross Burn Rate: Average of monthly expenses
    total_months = len(monthly_summary)
    gross_burn_rate = round(monthly_summary['Monthly Expenses'].sum() / total_months if total_months > 0 else 0, 2)

    # Cash Flow Volatility: Coefficient of Variation (CV) for Cash Flow
    cash_flow_mean = monthly_summary['Net Cashflow'].mean()
    cash_flow_std = monthly_summary['Net Cashflow'].std()
    cash_flow_volatility = round((cash_flow_std / cash_flow_mean) if cash_flow_mean != 0 else 0, 2)

    # Revenue Growth Rate: Median of the percentage change in revenue
    revenue_growth_rate = round(monthly_summary['Monthly Revenue'].pct_change().median() * 100, 2)

    # Monthly average Revenue
    monthly_average_revenue = round(total_revenue/company_age_months , 2)

    # Return the calculated metrics, rounded to 2 decimal places
    return {
        "Total Revenue": total_revenue,
        "Monthly Average Revenue":monthly_average_revenue,
        "Total Expenses": total_expenses,
        "Net Income": net_income,
        "Total Debt Repayments": total_debt_repayments,
        "Total Debt": total_debt,
        "Debt-to-Income Ratio": debt_to_income_ratio,
        "Expense-to-Revenue Ratio": expense_to_revenue_ratio,
        "Operating Margin": operating_margin,
        "Debt Service Coverage Ratio": debt_service_coverage_ratio,
        "Gross Burn Rate": gross_burn_rate,
        "Cash Flow Volatility": cash_flow_volatility,
        "Revenue Growth Rate": revenue_growth_rate,
        "Company Age (Months)": company_age_months
    }

def avg_revenue(data):
    total_revenue = round(data.loc[data['is_revenue'], 'amount'].sum() or 0, 2)
    first_date = data['date'].min()
    last_date = data['date'].max()
    company_age_months = ((last_date.year - first_date.year) * 12 + (last_date.month - first_date.month)) + 1
    monthly_average_revenue = round(total_revenue/company_age_months , 2)
    return monthly_average_revenue

