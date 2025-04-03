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
            'balances.current',
            'amount',
            'merchant_name',
            'website',
            'name_y',
            'authorized_date',
            'category',
            'date',
            'payment_channel',
            'personal_finance_category.confidence_level',
            'personal_finance_category.detailed',
            'personal_finance_category.primary'
        ]

        data = data[selected_columns]
        data["date"] = pd.to_datetime(data["date"], errors='coerce')
        data["authorized_date"] = pd.to_datetime(data["authorized_date"], errors='coerce')
        data['amount'] = data['amount'].abs()

        # Function to map transaction category using regex
        category_patterns = {
            "Income": [
                r"INCOME_(WAGES|OTHER_INCOME|DIVIDENDS|INTEREST_EARNED|RETIREMENT_PENSION|UNEMPLOYMENT)"
            ],
            "Loans": [r"TRANSFER_IN_CASH_ADVANCES_AND_LOANS"],
            "Debt Repayments": [
                r"LOAN_PAYMENTS_(CREDIT_CARD_PAYMENT|PERSONAL_LOAN_PAYMENT|OTHER_PAYMENT|CAR_PAYMENT|MORTGAGE_PAYMENT|STUDENT_LOAN_PAYMENT)"
            ],
            "Special Inflow": [
                r"INCOME_(DIVIDENDS|INTEREST_EARNED|RETIREMENT_PENSION|TAX_REFUND|UNEMPLOYMENT|TAX_REFUND)",
                r"TRANSFER_IN_(INVESTMENT_AND_RETIREMENT_FUNDS|SAVINGS|ACCOUNT_TRANSFER|OTHER_TRANSFER_IN|DEPOSIT)"
            ],
            "Special Outflow": [
                r"TRANSFER_OUT_(INVESTMENT_AND_RETIREMENT_FUNDS|SAVINGS|OTHER_TRANSFER_OUT|WITHDRAWAL|ACCOUNT_TRANSFER)"
            ],
            "Failed Payment": [
    r"BANK_FEES_(INSUFFICIENT_FUNDS|LATE_PAYMENT)",
    r"Unp",
    r"Unpaid",
    r"returned",
    r"reversal",
    r"chargeback",
    r"RETURNED DD",
    r"direct debit",
    r"rejected",
    r"payment fee",
    r"returned payment"
],

            "Expenses": [
                r"BANK_FEES_.*",
                r"ENTERTAINMENT_.*",
                r"FOOD_AND_DRINK_.*",
                r"GENERAL_MERCHANDISE_.*",
                r"GENERAL_SERVICES_.*",
                r"GOVERNMENT_AND_NON_PROFIT_.*",
                r"HOME_IMPROVEMENT_.*",
                r"MEDICAL_.*",
                r"PERSONAL_CARE_.*",
                r"RENT_AND_UTILITIES_.*",
                r"TRANSPORTATION_.*",
                r"TRAVEL_.*"
            ]
        }

        def map_transaction_category(category_detailed):
            if pd.isnull(category_detailed):
                return "Unknown"
            for category, patterns in category_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, category_detailed):
                        return category
            return "Unknown"

        data['subcategory'] = data['personal_finance_category.detailed'].apply(map_transaction_category)

        return data

    except Exception as e:
        st.error(f"Error processing JSON data: {e}")
        return None
    
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
