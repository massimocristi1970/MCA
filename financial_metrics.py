import pandas as pd
from collections import defaultdict
from data_processing import categorize_transactions
from rapidfuzz import fuzz

def count_bounced_payments(data, description_column='description', date_column='date'):
    
    data['Date'] = pd.to_datetime(data[date_column])
    data['Month'] = data['Date'].dt.to_period('M')
    descriptions = data[description_column].fillna('').str.lower()

    bounce_categories = {
        "Unpaid": r'\bunpaid\b|\bunpaid debit\b|\bunpaid credit\b|\bnot paid\b',
        "Returned Payment": r'\breturned payment\b|\bpayment returned\b|\breturned\b',
        "Payment Reversal": r'\bpayment reversal\b|\breversed payment\b|\bchargeback\b|\breversal\b',
        "Late Payment": r'\blate payment\b|\boverdue payment\b|\bdelayed payment\b|\bmissed payment\b|\bpayment past due\b',
        "Insufficient Funds": r'\binsufficient funds\b|\bdeclined payment\b|\bnsf\b|\bnon-sufficient funds\b|\bnot enough funds\b|\bpayment returned due to insufficient funds\b|\bfailed direct debit\b|\bdirect debit failure\b',
        "Unp": r'\bunp\b'
    }

    data['Bounce Category'] = ''
    for category, pattern in bounce_categories.items():
        match_mask = descriptions.str.contains(pattern, regex=True)
        data.loc[match_mask, 'Bounce Category'] = category

    bounced = data[data['Bounce Category'] != ''].copy()

    if bounced.empty:
        return pd.DataFrame()
    
    return bounced

def calculate_metrics(data, company_age_months):
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
    months_in_data = data['date'].dt.to_period('M').nunique()
    monthly_average_revenue = round(total_revenue / months_in_data, 2) if months_in_data else 0

    # Calculate Average Month-End Balance
    try:
        data_sorted = data.sort_values(by='date', ascending=False).copy()
        data_sorted['amount_1'] = pd.to_numeric(data_sorted['amount_1'], errors='coerce').fillna(0)
        data_sorted['balances.available'] = pd.to_numeric(data_sorted['balances.available'], errors='coerce').fillna(0)

        current_balance = data_sorted.loc[0, 'balances.available']
        updated_balances = [current_balance]

        for index in range(1, len(data_sorted)):
            current_balance += data_sorted.loc[index, 'amount_1']
            updated_balances.append(current_balance)

        data_sorted['balances.available'] = updated_balances
        data_sorted['month_end'] = data_sorted['date'].dt.to_period('M')

        month_end_balances = data_sorted.groupby('month_end').first()['balances.available']
        avg_month_end_balance = round(month_end_balances.mean(), 2)
    except Exception:
        avg_month_end_balance = 0.0

        # Calculate Average Number of Negative Balance Days per Month
    try:
        data_sorted = data.sort_values(by='date', ascending=False).copy()
        data_sorted['amount_1'] = pd.to_numeric(data_sorted['amount_1'], errors='coerce').fillna(0)
        data_sorted['balances.available'] = pd.to_numeric(data_sorted['balances.available'], errors='coerce').fillna(0)

        current_balance = data_sorted.loc[0, 'balances.available']
        updated_balances = [current_balance]

        for index in range(1, len(data_sorted)):
            current_balance += data_sorted.loc[index, 'amount_1']
            updated_balances.append(current_balance)

        data_sorted['balances.available'] = updated_balances
        data_sorted['month_end'] = data_sorted['date'].dt.to_period('M')
        data_sorted['day'] = data_sorted['date'].dt.date

        # Count negative days per month
        negative_days = data_sorted[data_sorted['balances.available'] < 0].groupby('month_end')['day'].nunique()

        # Average across all months
        avg_negative_days = round(negative_days.mean() if not negative_days.empty else 0.0, 2)
    except Exception:
        avg_negative_days = 0.0

    # Count Number of Bounced Payments
    try:
        bounced_df = count_bounced_payments(data, description_column='name_y', date_column='authorized_date')
        number_of_bounced_payments = len(bounced_df) if not bounced_df.empty else 0
    except Exception:
        number_of_bounced_payments = 0
        

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
        "Average Month-End Balance": avg_month_end_balance,
        "Average Negative Balance Days per Month": avg_negative_days,
        "Number of Bounced Payments": number_of_bounced_payments

    }

def avg_revenue(data):
    total_revenue = round(data.loc[data['is_revenue'], 'amount'].sum() or 0, 2)
    months_in_data = data['date'].dt.to_period('M').nunique()
    monthly_average_revenue = round(total_revenue / months_in_data, 2) if months_in_data else 0
    return monthly_average_revenue

def process_balance_report(data):
    if data.empty:
        return pd.DataFrame()

    required_columns = ['date', 'balances.available', 'amount_1']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing required column: {col}")

    data['date'] = pd.to_datetime(data['date'], errors='coerce')
    data = data.dropna(subset=['date'])

    data = data.sort_values(by='date', ascending=False).reset_index(drop=True)

    data['amount_1'] = pd.to_numeric(data['amount_1'], errors='coerce').fillna(0)
    data['balances.available'] = pd.to_numeric(data['balances.available'], errors='coerce').fillna(0)

    if data.empty:
        return pd.DataFrame()

    current_balance = data.loc[0, 'balances.available']
    updated_balances = [current_balance]

    for index in range(1, len(data)):
        current_balance += data.loc[index, 'amount_1']
        updated_balances.append(current_balance)

    data['balances.available'] = updated_balances

    data['month_end'] = data['date'].dt.to_period('M')
    data['day'] = data['date'].dt.date

    month_last = data.groupby('month_end').first()
    month_first = data.groupby('month_end').last()

    monthly_balances = pd.DataFrame({
        'Month End Balance': month_last['balances.available'],
        'Months First Day Balance': month_first['balances.available'],
    })

    negative_days = data[data['balances.available'] < 0].groupby('month_end')['day'].nunique()
    monthly_balances['Negative Balance Days'] = negative_days
    monthly_balances['Negative Balance Days'] = monthly_balances['Negative Balance Days'].fillna(0).astype(int)

    return monthly_balances
    
def count_revenue_sources(data):
    if 'subcategory' not in data.columns:
        data = categorize_transactions(data)

    income_only = data[data['subcategory'].str.strip() == 'Income']
    return income_only['name_y'].nunique()


def daily_revenue_summary(data):
    if 'subcategory' not in data.columns:
        data = categorize_transactions(data)

    income_only = data[data['subcategory'].str.strip() == 'Income'].copy()
    income_only['date'] = pd.to_datetime(income_only['date'])

    daily_counts = income_only.groupby(income_only['date'].dt.date).agg(
        daily_txn_count=('amount', 'count'),
        daily_txn_sum=('amount', 'sum')
    )

    avg_txns_per_day = round(daily_counts['daily_txn_count'].mean(), 2)
    avg_amount_per_day = round(daily_counts['daily_txn_sum'].mean(), 2)

    return avg_txns_per_day, avg_amount_per_day

def check_loan_vs_repayment(data):
    if 'subcategory' not in data.columns:
        data = categorize_transactions(data)

    loans_total = data[data['subcategory'] == 'Loans']['amount'].sum()
    repayments_total = data[data['subcategory'] == 'Debt Repayments']['amount'].sum()

    return round(loans_total, 2), round(repayments_total, 2)

def check_lender_repayments(data, threshold=75):
    if 'subcategory' not in data.columns:
        data = categorize_transactions(data)

    # 1. Get loan inflows
    loans = data[data['subcategory'] == 'Loans'].copy()
    loans['source'] = loans['name_y'].str.lower().str.strip()
    loan_sources = loans.groupby('source')['amount'].sum()

    # 2. Get debt repayments
    repayments = data[data['subcategory'] == 'Debt Repayments'].copy()
    repayments['recipient'] = repayments['name_y'].str.lower().str.strip()
    repayment_targets = repayments.groupby('recipient')['amount'].sum()

    # 3. Fuzzy match
    unmatched_lenders = []
    matched_lenders = []

    for lender in loan_sources.index:
        match_found = False
        for rep_name in repayment_targets.index:
            similarity = fuzz.token_sort_ratio(lender, rep_name)
            if similarity >= threshold:
                match_found = True
                break
        if match_found:
            matched_lenders.append(lender)
        else:
            unmatched_lenders.append(lender)

    # Format for display
    loans_display = loan_sources.round(2).to_dict()
    repayments_display = repayment_targets.round(2).to_dict()

    return loans_display, repayments_display, unmatched_lenders


