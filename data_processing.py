import pandas as pd
import re
import streamlit as st

# Function to process JSON data
def process_json_data(json_data):
    try:
        accounts_df = pd.json_normalize(json_data['accounts'])
        transactions_df = pd.json_normalize(json_data['transactions'])

        data = pd.merge(accounts_df, transactions_df, on="account_id", how="left")

        selected_columns = [
            'account_id',
            'balances.available',
            'amount',
            'merchant_name',
            'website',
            'name_y',
            'authorized_date',
            'authorized_datetime',
            'category',
            'date',
            'payment_channel',
            'personal_finance_category.confidence_level',
            'personal_finance_category.detailed',
            'personal_finance_category.primary'
        ]

        data = data[selected_columns]
        data["date"] = pd.to_datetime(data["date"], errors='coerce')
        data = data.sort_values(by='date', ascending=False)

        # Recalculate balance
        current_balance = data.iloc[0]['balances.available']
        updated_balances = [current_balance]

        for index in range(1, len(data)):
            current_balance += data.iloc[index]['amount']
            updated_balances.append(current_balance)

        data['balances.available'] = updated_balances

        data['amount_1'] = data['amount']
        data['amount'] = data['amount'].abs()

        data['subcategory'] = data.apply(map_transaction_category, axis=1)

        return data

    except Exception as e:
        st.error(f"Error processing JSON data: {e}")
        return None

# Categorisation function
def map_transaction_category(transaction):
    name = (transaction.get("name_y") or "")
    if isinstance(name, list): name = " ".join(name)
    name = name.lower()

    description = (transaction.get("merchant_name") or "")
    if isinstance(description, list): description = " ".join(description)
    description = description.lower()

    # Normalise Plaid category
    category = (transaction.get("personal_finance_category.detailed") or "")
    if isinstance(category, list): category = " ".join(category)
    category = category.lower().strip().replace(" ", "_")

    amount = transaction.get("amount_1", 0)
    combined_text = f"{name} {description}"

    is_credit = amount < 0
    is_debit = amount > 0

    # Step 1: Custom keyword overrides
    if is_credit and re.search(
        r"(?i)\b("
        r"stripe|sumup|zettle|square|take\s*payments|shopify|card\s+settlement|daily\s+takings|payout"
        r"|paypal|go\s*cardless|klarna|worldpay|izettle|ubereats|just\s*eat|deliveroo|uber|bolt"
        r"|fresha|treatwell|taskrabbit|terminal|pos\s+deposit|revolut"
        r"|capital\s+on\s+tap|capital\s+one|evo\s*payments?|tink|teya(\s+solutions)?|talech"
        r"|barclaycard|elavon|adyen|payzone|verifone|ingenico"
        r"|nmi|trust\s+payments?|global\s+payments?|checkout\.com|epdq|santander|handepay"
        r"|dojo|valitor|paypoint|mypos|moneris"
        r"|merchant\s+services|payment\s+sense"
        r")\b", 
        combined_text
    ):
        return "Income"
    if is_credit and re.search(r"(you\s?lend|yl\s?ii|yl\s?ltd|yl\s?limited|yl\s?a\s?limited)(?!.*\b(fnd|fund|funding)\b)", combined_text):
        return "Income"
    if is_credit and re.search(r"(you\s?lend|yl\s?ii|yl\s?ltd|yl\s?limited|yl\s?a\s?limited).*\b(fnd|fund|funding)\b", combined_text):
        return "Loans"
    if is_credit and re.search(
    r"\biwoca\b|\bcapify\b|\bfundbox\b|\bgot[\s\-]?capital\b|\bfunding[\s\-]?circle\b|"
    r"\bfleximize\b|\bmarketfinance\b|\bliberis\b|\besme[\s\-]?loans\b|\bthincats\b|"
    r"\bwhite[\s\-]?oak\b|\bgrowth[\s\-]?street\b|\bnucleus[\s\-]?commercial[\s\-]?finance\b|"
    r"\bultimate[\s\-]?finance\b|\bjust[\s\-]?cash[\s\-]?flow\b|\bboost[\s\-]?capital\b|"
    r"\bmerchant[\s\-]?money\b|\bcapital[\s\-]?on[\s\-]?tap\b|\bkriya\b|\buncapped\b|"
    r"\blendingcrowd\b|\bfolk2folk\b|\bfunding[\s\-]?tree\b|\bstart[\s\-]?up[\s\-]?loans\b|"
    r"\bbcrs[\s\-]?business[\s\-]?loans\b|\bbusiness[\s\-]?enterprise[\s\-]?fund\b|"
    r"\bswig[\s\-]?finance\b|\benterprise[\s\-]?answers\b|\blet's[\s\-]?do[\s\-]?business[\s\-]?finance\b|"
    r"\bfinance[\s\-]?for[\s\-]?enterprise\b|\bdsl[\s\-]?business[\s\-]?finance\b|"
    r"\bbizcap[\s\-]?uk\b|\bsigma[\s\-]?lending\b|\bbizlend[\s\-]?ltd\b|\bloans?\b",
    combined_text
):
    return "Loans"

    if is_debit and re.search(r"\biwoca\b", combined_text):
        return "Debt Repayments"

    # Step 2: Plaid category fallback
    plaid_map = {
        "income_wages": "Income",
        "income_other_income": "Income",
        "income_dividends": "Special Inflow",
        "income_interest_earned": "Special Inflow",
        "income_retirement_pension": "Special Inflow",
        "income_unemployment": "Special Inflow",
        "transfer_in_cash_advances_and_loans": "Loans",
        "loan_payments_credit_card_payment": "Debt Repayments",
        "loan_payments_personal_loan_payment": "Debt Repayments",
        "loan_payments_other_payment": "Debt Repayments",
        "loan_payments_car_payment": "Debt Repayments",
        "loan_payments_mortgage_payment": "Debt Repayments",
        "loan_payments_student_loan_payment": "Debt Repayments",
        "transfer_in_investment_and_retirement_funds": "Special Inflow",
        "transfer_in_savings": "Special Inflow",
        "transfer_in_account_transfer": "Special Inflow",
        "transfer_in_other_transfer_in": "Special Inflow",
        "transfer_in_deposit": "Special Inflow",
        "transfer_out_investment_and_retirement_funds": "Special Outflow",
        "transfer_out_savings": "Special Outflow",
        "transfer_out_other_transfer_out": "Special Outflow",
        "transfer_out_withdrawal": "Special Outflow",
        "transfer_out_account_transfer": "Special Outflow",
        "bank_fees_insufficient_funds": "Failed Payment",
        "bank_fees_late_payment": "Failed Payment",
    }

    # Match exact key
    if category in plaid_map:
        return plaid_map[category]

    # Step 3: Fallback for Plaid broad categories
    broad_matchers = [
        ("Expenses", [
            "bank_fees_", "entertainment_", "food_and_drink_", "general_merchandise_",
            "general_services_", "government_and_non_profit_", "home_improvement_",
            "medical_", "personal_care_", "rent_and_utilities_", "transportation_", "travel_"
        ])
    ]

    for label, patterns in broad_matchers:
        if any(category.startswith(p) for p in patterns):
            return label

    return "Uncategorised"

def count_bounced_payments(data, description_column='description', date_column='date'):
    """
    Identifies and categorizes problem payments based on keywords in descriptions.
    Returns full rows of matching problem payments or a zero-row if none found.
    """

    data['Date'] = pd.to_datetime(data[date_column])
    data['Month'] = data['Date'].dt.to_period('M')
    descriptions = data[description_column].fillna('').str.lower()

    # Define categories and their keyword patterns
    bounce_categories = {
        "Unpaid": r'\bunpaid\b|\bunpaid debit\b|\bunpaid credit\b|\bnot paid\b',
        "Returned Payment": r'\breturned payment\b|\bpayment returned\b|\breturned\b',
        "Payment Reversal": r'\bpayment reversal\b|\breversed payment\b|\bchargeback\b|\breversal\b',
        "Late Payment": r'\blate payment\b|\boverdue payment\b|\bdelayed payment\b|\bmissed payment\b|\bpayment past due\b',
        "Insufficient Funds": r'\binsufficient funds\b|\bdeclined payment\b|\bnsf\b|\bnon-sufficient funds\b|\bnot enough funds\b|\bpayment returned due to insufficient funds\b|\bfailed direct debit\b|\bdirect debit failure\b',
        "Unp": r'\bunp\b'
    }

    data['Bounce Category'] = ''

    # Apply category detection
    for category, pattern in bounce_categories.items():
        match_mask = descriptions.str.contains(pattern, regex=True)
        data.loc[match_mask, 'Bounce Category'] = category

    bounced = data[data['Bounce Category'] != ''].copy()

    if bounced.empty:
        return pd.DataFrame({'Bounce Category': ['None'],'Count': [0]})
    return bounced





# Function to calculate monthly summary
def calculate_monthly_summary(data):
    data['month'] = data['date'].dt.to_period('M')
    monthly_summary = data.groupby('month').agg(
        Monthly_Revenue=('amount', lambda x: x[data['is_revenue']].sum()),
        Monthly_Expenses=('amount', lambda x: x[data['is_expense']].sum()),
        Debt_Repayments=('amount', lambda x: x[data['is_debt_repayment']].sum()),
        Net_Cashflow=('amount', lambda x: x[data['is_revenue']].sum() - x[data['is_expense']].sum())
    ).reset_index()
    return monthly_summary

# Function to categorize transactions
def categorize_transactions(data):
    data['is_revenue'] = data['subcategory'].str.strip().isin(['Income', 'Special Inflow'])
    data['is_expense'] = data['subcategory'].str.strip().isin(['Expenses', 'Special Outflow'])
    data['is_debt_repayment'] = data['subcategory'].str.strip().isin(['Debt Repayments'])
    data['is_debt'] = data['subcategory'].str.strip().isin(['Loans'])
    return data


# Function to calculate all metrics
def summarize_monthly_revenue(data):
    data['Date'] = pd.to_datetime(data['date'])
    data['Month'] = data['Date'].dt.to_period('M')
    categorized_df = categorize_transactions(data)

    relevant_subcats = [
        "Income", "Special Inflow", "Expenses", "Special Outflow", "Debt Repayments", "Loans"
    ]

    # Ensure all relevant subcategories are present with at least one zero entry
    for subcat in relevant_subcats:
        if subcat not in categorized_df['subcategory'].unique():
            dummy_row = pd.DataFrame([{
                'subcategory': subcat,
                'Month': data['Month'].iloc[0],
                'amount': 0
            }])
            categorized_df = pd.concat([categorized_df, dummy_row], ignore_index=True)

    monthly_summary = (
        categorized_df[categorized_df['subcategory'].isin(relevant_subcats)]
        .groupby(['subcategory', 'Month'])['amount']
        .sum()
        .unstack()
        .fillna(0)
    )

    report = pd.DataFrame()

    # Add each block/metric using helper functions
    report = add_revenue_section(monthly_summary, report)
    report = add_operational_expenses_section(monthly_summary, report)
    report = add_debt_repayment_section(monthly_summary, report)
    report = add_gross_profit_section(monthly_summary, report)
    report = add_expenses_including_debt(monthly_summary, report)
    report = add_grossprofit_including_debt(monthly_summary, report)
    report = add_monthly_revenue_ration(monthly_summary, report)
    report = add_loans_section(monthly_summary, report)
    report = add_special_inflow(monthly_summary, report)
    report = add_special_outflow(monthly_summary, report)

    report = report.reset_index().rename(columns={"index": "Category"})
    return report

# ---------- Section Functions ---------- #

def add_revenue_section(summary, report):
    section_keys = ["Income", "Special Inflow"]
    section = summary.reindex(section_keys).fillna(0)
    total_revenue = section.sum()
    summary.loc["Total Revenue"] = total_revenue
    section.loc["Total Revenue"] = total_revenue
    return pd.concat([report, section])

def add_operational_expenses_section(summary, report):
    section_keys = ["Expenses", "Special Outflow"]
    section = summary.reindex(section_keys).fillna(0)
    total_expenses = section.sum()
    summary.loc["Total Operational Expenses"] = total_expenses
    section.loc["Total Operational Expenses"] = total_expenses
    return pd.concat([report, section])

def add_debt_repayment_section(summary, report):
    debt = summary.loc["Debt Repayments"] if "Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    summary.loc["Total Debt Repayments"] = debt
    section = pd.DataFrame([debt], index=["Total Debt Repayments"])
    return pd.concat([report, section])

def add_gross_profit_section(summary, report):
    if "Total Revenue" in summary.index:
        total_revenue = summary.loc["Total Revenue"]
    else:
        total_revenue = pd.Series(0, index=summary.columns)

    if "Total Operational Expenses" in summary.index:
        total_expense = summary.loc["Total Operational Expenses"]
    else:
        total_expense = pd.Series(0, index=summary.columns)

    gross_profit = total_revenue - total_expense
    gross_profit_ratio = (gross_profit / total_revenue.replace(0, pd.NA)) * 100
    gross_profit_ratio = gross_profit_ratio.fillna(0)

    section = pd.DataFrame([gross_profit], index=["Gross Profit"])
    ratio_section = pd.DataFrame([gross_profit_ratio], index=["Gross Profit Ratio (%)"])

    return pd.concat([report, section, ratio_section])


def add_expenses_including_debt(summary, report):
    operational = summary.loc["Total Operational Expenses"] if "Total Operational Expenses" in summary.index else pd.Series(0, index=summary.columns)
    debt = summary.loc["Total Debt Repayments"] if "Total Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    combined = operational + debt
    summary.loc["Expenses including Debt Repayments"] = combined
    section = pd.DataFrame([combined], index=["Expenses including Debt Repayments"])
    return pd.concat([report, section])


def add_grossprofit_including_debt(summary, report):
    revenue = summary.loc["Total Revenue"] if "Total Revenue" in summary.index else pd.Series(0, index=summary.columns)
    combined_expenses = summary.loc["Expenses including Debt Repayments"] if "Expenses including Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    gross_profit_with_debt = revenue - combined_expenses
    section = pd.DataFrame([gross_profit_with_debt], index=["Total Gross Profit including Debts"])
    return pd.concat([report, section])


def add_monthly_revenue_ration(summary, report):
    revenue = summary.loc["Total Revenue"] if "Total Revenue" in summary.index else pd.Series(0, index=summary.columns)
    debt = summary.loc["Total Debt Repayments"] if "Total Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    ratio = (debt / revenue.replace(0, pd.NA)).fillna(0)
    section = pd.DataFrame([ratio], index=["Debt Repayment : Revenue Ratio (Monthly)"])
    return pd.concat([report, section])


def add_loans_section(summary, report):
    loans = summary.loc["Loans"] if "Loans" in summary.index else pd.Series(0, index=summary.columns)
    section = pd.DataFrame([loans], index=["Loans"])
    return pd.concat([report, section])


def add_special_inflow(summary, report):
    inflow = summary.loc["Special Inflow"] if "Special Inflow" in summary.index else pd.Series(0, index=summary.columns)
    section = pd.DataFrame([inflow], index=["Special Inflow"])
    return pd.concat([report, section])


def add_special_outflow(summary, report):
    outflow = summary.loc["Special Outflow"] if "Special Outflow" in summary.index else pd.Series(0, index=summary.columns)
    section = pd.DataFrame([outflow], index=["Special Outflow"])
    return pd.concat([report, section])

def count_bounced_payments(data, description_column='description', date_column='date'):
    """
    Identifies and categorizes problem payments based on keywords in descriptions.
    Returns full rows of matching problem payments or a zero-row if none found.
    """

    data['Date'] = pd.to_datetime(data[date_column])
    data['Month'] = data['Date'].dt.to_period('M')
    descriptions = data[description_column].fillna('').str.lower()

    # Define categories and their keyword patterns
    bounce_categories = {
        "Unpaid": r'\bunpaid\b|\bunpaid debit\b|\bunpaid credit\b|\bnot paid\b',
        "Returned Payment": r'\breturned payment\b|\bpayment returned\b|\breturned\b',
        "Payment Reversal": r'\bpayment reversal\b|\breversed payment\b|\bchargeback\b|\breversal\b',
        "Late Payment": r'\blate payment\b|\boverdue payment\b|\bdelayed payment\b|\bmissed payment\b|\bpayment past due\b',
        "Insufficient Funds": r'\binsufficient funds\b|\bdeclined payment\b|\bnsf\b|\bnon-sufficient funds\b|\bnot enough funds\b|\bpayment returned due to insufficient funds\b|\bfailed direct debit\b|\bdirect debit failure\b',
        "Unp": r'\bunp\b'
    }

    data['Bounce Category'] = ''

    # Apply category detection
    for category, pattern in bounce_categories.items():
        match_mask = descriptions.str.contains(pattern, regex=True)
        data.loc[match_mask, 'Bounce Category'] = category

    bounced = data[data['Bounce Category'] != ''].copy()

    if bounced.empty:
        return pd.DataFrame({'Bounce Category': ['None'],'Count': [0]})
    return bounced





# Function to calculate monthly summary
def calculate_monthly_summary(data):
    data['month'] = data['date'].dt.to_period('M')
    monthly_summary = data.groupby('month').agg(
        Monthly_Revenue=('amount', lambda x: x[data['is_revenue']].sum()),
        Monthly_Expenses=('amount', lambda x: x[data['is_expense']].sum()),
        Debt_Repayments=('amount', lambda x: x[data['is_debt_repayment']].sum()),
        Net_Cashflow=('amount', lambda x: x[data['is_revenue']].sum() - x[data['is_expense']].sum())
    ).reset_index()
    return monthly_summary

# Function to categorize transactions
def categorize_transactions(data):
    data['is_revenue'] = data['subcategory'].str.strip().isin(['Income', 'Special Inflow'])
    data['is_expense'] = data['subcategory'].str.strip().isin(['Expenses', 'Special Outflow'])
    data['is_debt_repayment'] = data['subcategory'].str.strip().isin(['Debt Repayments'])
    data['is_debt'] = data['subcategory'].str.strip().isin(['Loans'])
    return data


# Function to calculate all metrics
def summarize_monthly_revenue(data):
    data['Date'] = pd.to_datetime(data['date'])
    data['Month'] = data['Date'].dt.to_period('M')
    categorized_df = categorize_transactions(data)

    relevant_subcats = [
        "Income", "Special Inflow", "Expenses", "Special Outflow", "Debt Repayments", "Loans"
    ]

    # Ensure all relevant subcategories are present with at least one zero entry
    for subcat in relevant_subcats:
        if subcat not in categorized_df['subcategory'].unique():
            dummy_row = pd.DataFrame([{
                'subcategory': subcat,
                'Month': data['Month'].iloc[0],
                'amount': 0
            }])
            categorized_df = pd.concat([categorized_df, dummy_row], ignore_index=True)

    monthly_summary = (
        categorized_df[categorized_df['subcategory'].isin(relevant_subcats)]
        .groupby(['subcategory', 'Month'])['amount']
        .sum()
        .unstack()
        .fillna(0)
    )

    report = pd.DataFrame()

    # Add each block/metric using helper functions
    report = add_revenue_section(monthly_summary, report)
    report = add_operational_expenses_section(monthly_summary, report)
    report = add_debt_repayment_section(monthly_summary, report)
    report = add_gross_profit_section(monthly_summary, report)
    report = add_expenses_including_debt(monthly_summary, report)
    report = add_grossprofit_including_debt(monthly_summary, report)
    report = add_monthly_revenue_ration(monthly_summary, report)
    report = add_loans_section(monthly_summary, report)
    report = add_special_inflow(monthly_summary, report)
    report = add_special_outflow(monthly_summary, report)

    report = report.reset_index().rename(columns={"index": "Category"})
    return report

# ---------- Section Functions ---------- #

def add_revenue_section(summary, report):
    section_keys = ["Income", "Special Inflow"]
    section = summary.reindex(section_keys).fillna(0)
    total_revenue = section.sum()
    summary.loc["Total Revenue"] = total_revenue
    section.loc["Total Revenue"] = total_revenue
    return pd.concat([report, section])

def add_operational_expenses_section(summary, report):
    section_keys = ["Expenses", "Special Outflow"]
    section = summary.reindex(section_keys).fillna(0)
    total_expenses = section.sum()
    summary.loc["Total Operational Expenses"] = total_expenses
    section.loc["Total Operational Expenses"] = total_expenses
    return pd.concat([report, section])

def add_debt_repayment_section(summary, report):
    debt = summary.loc["Debt Repayments"] if "Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    summary.loc["Total Debt Repayments"] = debt
    section = pd.DataFrame([debt], index=["Total Debt Repayments"])
    return pd.concat([report, section])

def add_gross_profit_section(summary, report):
    if "Total Revenue" in summary.index:
        total_revenue = summary.loc["Total Revenue"]
    else:
        total_revenue = pd.Series(0, index=summary.columns)

    if "Total Operational Expenses" in summary.index:
        total_expense = summary.loc["Total Operational Expenses"]
    else:
        total_expense = pd.Series(0, index=summary.columns)

    gross_profit = total_revenue - total_expense
    gross_profit_ratio = (gross_profit / total_revenue.replace(0, pd.NA)) * 100
    gross_profit_ratio = gross_profit_ratio.fillna(0)

    section = pd.DataFrame([gross_profit], index=["Gross Profit"])
    ratio_section = pd.DataFrame([gross_profit_ratio], index=["Gross Profit Ratio (%)"])

    return pd.concat([report, section, ratio_section])


def add_expenses_including_debt(summary, report):
    operational = summary.loc["Total Operational Expenses"] if "Total Operational Expenses" in summary.index else pd.Series(0, index=summary.columns)
    debt = summary.loc["Total Debt Repayments"] if "Total Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    combined = operational + debt
    summary.loc["Expenses including Debt Repayments"] = combined
    section = pd.DataFrame([combined], index=["Expenses including Debt Repayments"])
    return pd.concat([report, section])


def add_grossprofit_including_debt(summary, report):
    revenue = summary.loc["Total Revenue"] if "Total Revenue" in summary.index else pd.Series(0, index=summary.columns)
    combined_expenses = summary.loc["Expenses including Debt Repayments"] if "Expenses including Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    gross_profit_with_debt = revenue - combined_expenses
    section = pd.DataFrame([gross_profit_with_debt], index=["Total Gross Profit including Debts"])
    return pd.concat([report, section])


def add_monthly_revenue_ration(summary, report):
    revenue = summary.loc["Total Revenue"] if "Total Revenue" in summary.index else pd.Series(0, index=summary.columns)
    debt = summary.loc["Total Debt Repayments"] if "Total Debt Repayments" in summary.index else pd.Series(0, index=summary.columns)
    ratio = (debt / revenue.replace(0, pd.NA)).fillna(0)
    section = pd.DataFrame([ratio], index=["Debt Repayment : Revenue Ratio (Monthly)"])
    return pd.concat([report, section])


def add_loans_section(summary, report):
    loans = summary.loc["Loans"] if "Loans" in summary.index else pd.Series(0, index=summary.columns)
    section = pd.DataFrame([loans], index=["Loans"])
    return pd.concat([report, section])


def add_special_inflow(summary, report):
    inflow = summary.loc["Special Inflow"] if "Special Inflow" in summary.index else pd.Series(0, index=summary.columns)
    section = pd.DataFrame([inflow], index=["Special Inflow"])
    return pd.concat([report, section])


def add_special_outflow(summary, report):
    outflow = summary.loc["Special Outflow"] if "Special Outflow" in summary.index else pd.Series(0, index=summary.columns)
    section = pd.DataFrame([outflow], index=["Special Outflow"])
    return pd.concat([report, section])
