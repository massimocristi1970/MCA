import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import joblib
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

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
    'Debt Service Coverage Ratio': 20,  # 22%
    'Net Income': 15,                   # 18%
    'Operating Margin': 10,             # 12%
    'Expense-to-Revenue Ratio': 5,     # 10%
    'Revenue Growth Rate': 10,           # 8%
    'Debt Repayment Coverage Ratio': 5,# 10%
    'Cash Flow Volatility': 10,          # 5%
    'Gross Burn Rate': 5,               # 5%
    'Months': 5,                       # 10% for Company Age
    'Directors Score': 10,
    'Sector Risk': 5
}
months_threshold = 6  

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
            'authorized_date',
            'category',
            'date',
            'payment_channel',
            'personal_finance_category.confidence_level',
            'personal_finance_category.detailed',
            'personal_finance_category.primary'
        ]

        data = data[selected_columns]
        data["date"] = pd.to_datetime(data["date"])
        data["authorized_date"] = pd.to_datetime(data["authorized_date"])
        data['amount'] = data['amount'].abs()

        # Function to map transaction category using regex
        category_patterns = {
            "Income": [
                r"INCOME_(WAGES|OTHER_INCOME|DIVIDENDS|INTEREST_EARNED|RETIREMENT_PENSION|TAX_REFUND|UNEMPLOYMENT)"
            ],
            "Loans": [r"TRANSFER_IN_CASH_ADVANCES_AND_LOANS"],
            "Debt Repayments": [
                r"LOAN_PAYMENTS_(CREDIT_CARD_PAYMENT|PERSONAL_LOAN_PAYMENT|OTHER_PAYMENT|CAR_PAYMENT|MORTGAGE_PAYMENT|STUDENT_LOAN_PAYMENT)"
            ],
            "Special Inflow": [
                r"INCOME_(DIVIDENDS|INTEREST_EARNED|RETIREMENT_PENSION|TAX_REFUND|UNEMPLOYMENT)",
                r"TRANSFER_IN_(INVESTMENT_AND_RETIREMENT_FUNDS|SAVINGS|ACCOUNT_TRANSFER|OTHER_TRANSFER_IN|DEPOSIT)"
            ],
            "Special Outflow": [
                r"TRANSFER_OUT_(INVESTMENT_AND_RETIREMENT_FUNDS|SAVINGS|OTHER_TRANSFER_OUT|WITHDRAWAL|ACCOUNT_TRANSFER)"
            ],
            "Failed Payment": [
                r"BANK_FEES_(INSUFFICIENT_FUNDS|LATE_PAYMENT)"
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
    data['is_expense'] = data['subcategory'].str.strip().isin(['Expenses'])
    data['is_debt_repayment'] = data['subcategory'].str.strip().isin(['Debt Repayments'])
    data['is_debt'] = data['subcategory'].str.strip().isin(['Loans'])
    return data


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

    # Return the calculated metrics, rounded to 2 decimal places
    return {
        "Total Revenue": total_revenue,
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

def calculate_weighted_score(metrics, directors_score, sector_risk, thresholds, weights):
    weighted_score = 0
    # Debt Service Coverage Ratio
    if metrics["Debt Service Coverage Ratio"] >= thresholds["Debt Service Coverage Ratio"]:
        weighted_score += weights["Debt Service Coverage Ratio"]

    # Net Income
    if metrics["Net Income"] >= thresholds["Net Income"]:
        weighted_score += weights["Net Income"]

    # Operating Margin
    if metrics["Operating Margin"] >= thresholds["Operating Margin"]:
        weighted_score += weights["Operating Margin"]

    # Expense-to-Revenue Ratio (lower is better)
    if metrics["Expense-to-Revenue Ratio"] <= thresholds["Expense-to-Revenue Ratio"]:
        weighted_score += weights["Expense-to-Revenue Ratio"]

    # Revenue Growth Rate
    if metrics["Revenue Growth Rate"] >= thresholds["Revenue Growth Rate"]:
        weighted_score += weights["Revenue Growth Rate"]

    # Cash Flow Volatility (lower is better)
    if metrics["Cash Flow Volatility"] <= thresholds["Cash Flow Volatility"]:
        weighted_score += weights["Cash Flow Volatility"]

    # Burn Rate (lower is better)
    if metrics["Gross Burn Rate"] <= thresholds["Gross Burn Rate"]:
        weighted_score += weights["Gross Burn Rate"]

    # Company Age
    if metrics["Company Age (Months)"] >= months_threshold:
        weighted_score += weights["Months"]

    # Directors Score
    if directors_score >= thresholds["Directors Score"]:
        weighted_score += weights["Directors Score"]

    # Sector Risk (Industry Risk) adjustment based on input
    # Add weight for Sector Risk if it's low
    if sector_risk <= thresholds["Sector Risk"]:
        weighted_score += weights["Sector Risk"]
        
    return weighted_score

# Function to predict the score using the trained Logistic Regression model
def predict_score(model, metrics, directors_score, sector_risk, scaler):
    # Prepare the input data as a dictionary
    features = {
        'Directors Score': directors_score,                  
        'Sector': sector_risk,                             
        'Total Revenue': metrics["Total Revenue"],         
        'Total Expenses': metrics["Total Expenses"],       
        'Net Income': metrics["Net Income"],               
        'Total Debt Repayments': metrics["Total Debt Repayments"],  
        'Total Debt': metrics["Total Debt"],               
        'Debt-to-Income Ratio': metrics["Debt-to-Income Ratio"], 
        'Expense-to-Revenue Ratio': metrics["Expense-to-Revenue Ratio"],
        'Operating Margin': metrics["Operating Margin"],     
        'Debt Service Coverage Ratio': metrics["Debt Service Coverage Ratio"], 
        'Gross Burn Rate': metrics["Gross Burn Rate"],       
        'Cash Flow Volatility': metrics["Cash Flow Volatility"], 
        'Revenue Growth Rate': metrics["Revenue Growth Rate"],  
        'Company Age (Months)': metrics["Company Age (Months)"]  
    }

    # Convert features to a DataFrame
    features_df = pd.DataFrame([features])

    # Handle infinite values by replacing them with NaN, then fill NaN with 0
    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.fillna(0, inplace=True)

    # Scale the features using the scaler
    features_scaled = scaler.transform(features_df)

    # Predict the probability of repayment (class 1)
    probability_score = model.predict_proba(features_scaled)[:, 1]

    return probability_score[0]

# Function to calculate revised score based on financial metrics, thresholds, and binary scoring
def calculate_industry_score(metrics, directors_score, sector_risk, thresholds):
    industry_score = 0
    feedback = []  # List to store feedback for each metric

    # Debt Service Coverage Ratio
    if metrics["Debt Service Coverage Ratio"] >= thresholds["Debt Service Coverage Ratio"]:
        industry_score += 1
        feedback.append(f"✅ Debt Service Coverage Ratio is {metrics['Debt Service Coverage Ratio']}, which meets the threshold of {thresholds['Debt Service Coverage Ratio']}.")
    else:
        feedback.append(f"❌ Debt Service Coverage Ratio is {metrics['Debt Service Coverage Ratio']}, below the threshold of {thresholds['Debt Service Coverage Ratio']}.")

    # Net Income
    if metrics["Net Income"] >= thresholds["Net Income"]:
        industry_score += 1
        feedback.append(f"✅ Net Income is {metrics['Net Income']}, which meets or exceeds the threshold of {thresholds['Net Income']}.")
    else:
        feedback.append(f"❌ Net Income is {metrics['Net Income']}, which is negative, indicating more expenses than revenue.")

    # Operating Margin
    if metrics["Operating Margin"] >= thresholds["Operating Margin"]:
        industry_score += 1
        feedback.append(f"✅ Operating Margin is {metrics['Operating Margin']}, which meets or exceeds the threshold of {thresholds['Operating Margin']}.")
    else:
        feedback.append(f"❌ Operating Margin is {metrics['Operating Margin']}, below the threshold of {thresholds['Operating Margin']}.")

    # Expense-to-Revenue Ratio (lower is better)
    if metrics["Expense-to-Revenue Ratio"] <= thresholds["Expense-to-Revenue Ratio"]:
        industry_score += 1
        feedback.append(f"✅ Expense-to-Revenue Ratio is {metrics['Expense-to-Revenue Ratio']}, which is within the acceptable range (threshold is {thresholds['Expense-to-Revenue Ratio']}).")
    else:
        feedback.append(f"❌ Expense-to-Revenue Ratio is {metrics['Expense-to-Revenue Ratio']}, exceeding the threshold of {thresholds['Expense-to-Revenue Ratio']}.")

    # Revenue Growth Rate
    if metrics["Revenue Growth Rate"] >= thresholds["Revenue Growth Rate"]:
        industry_score += 1
        feedback.append(f"✅ Revenue Growth Rate is {metrics['Revenue Growth Rate']}%, which exceeds the threshold of {thresholds['Revenue Growth Rate']}%.")
    else:
        feedback.append(f"❌ Revenue Growth Rate is {metrics['Revenue Growth Rate']}%, below the threshold.")

    # Cash Flow Volatility (lower is better)
    if metrics["Cash Flow Volatility"] <= thresholds["Cash Flow Volatility"]:
        industry_score += 1
        feedback.append(f"✅ Cash Flow Volatility is {metrics['Cash Flow Volatility']}, which is stable (threshold is {thresholds['Cash Flow Volatility']}).")
    else:
        feedback.append(f"❌ Cash Flow Volatility is {metrics['Cash Flow Volatility']}, indicating instability.")

    # Gross Burn Rate (lower is better)
    if metrics["Gross Burn Rate"] <= thresholds["Gross Burn Rate"]:
        industry_score += 1
        feedback.append(f"✅ Gross Burn Rate is {metrics['Gross Burn Rate']}, which is below the threshold of {thresholds['Gross Burn Rate']}.")
    else:
        feedback.append(f"❌ Gross Burn Rate is {metrics['Gross Burn Rate']}, which is too high.")

    # Company Age (Months)
    if metrics["Company Age (Months)"] >= months_threshold:
        industry_score += 1
        feedback.append(f"✅ Company Age is {metrics['Company Age (Months)']} months, meeting the threshold of {months_threshold} months.")
    else:
        feedback.append(f"❌ Company Age is {metrics['Company Age (Months)']} months, which is below the threshold.")

    # Directors Score
    if directors_score >= thresholds["Directors Score"]:
        industry_score += 1
        feedback.append(f"✅ Directors Score is {directors_score}, meeting the threshold of {thresholds['Directors Score']}.")
    else:
        feedback.append(f"❌ Directors Score is {directors_score}, which is below the threshold of {thresholds['Directors Score']}.")

    # Sector Risk (lower is better, 0 is low risk, 1 is high risk)
    if sector_risk == 0:
        industry_score += 1
        feedback.append("✅ Sector Risk is low.")
    else:
        feedback.append("❌ Sector Risk is high.")

    # Display the feedback as a list
    st.write("### Scoring Breakdown:")
    for line in feedback:
        st.write(line)

    return industry_score



# Function to plot revenue vs expenses
def plot_revenue_vs_expense(monthly_summary):
    plt.figure(figsize=(10, 6))
    plt.plot(monthly_summary['month'].astype(str), monthly_summary['Monthly_Revenue'], label='Monthly Revenue', marker='o')
    plt.plot(monthly_summary['month'].astype(str), monthly_summary['Monthly_Expenses'], label='Monthly Expenses', marker='o')
    plt.xlabel('Month')
    plt.ylabel('Amount')
    plt.title('Revenue vs Expenses Over Time')
    plt.xticks(rotation=45)
    plt.legend()
    st.pyplot(plt)

# Function to plot outflow transactions for anomaly detection
def plot_outflow_transactions(data):
    outflows = data.loc[data['is_expense'], ['date', 'amount']].set_index('date').resample('D').sum()
    plt.figure(figsize=(10, 6))
    plt.plot(outflows.index, outflows['amount'], label='Outflow Transactions', color='r', marker='o')
    plt.xlabel('Date')
    plt.ylabel('Amount')
    plt.title('Outflow Transactions for Anomaly Detection')
    plt.xticks(rotation=45)
    st.pyplot(plt)

st.title("Metrics Scoring Tool")

# Add an industry dropdown menu
industry = st.selectbox("Select Industry", list(industry_thresholds.keys()))
# Retrieve the thresholds for the selected industry
industry_thresholds = industry_thresholds[industry]
directors_score = st.number_input("Director Score",min_value=0)
sector_risk = st.radio("Sector Risk", options=[0, 1])
uploaded_file = st.file_uploader("Upload a JSON file", type="json")


if uploaded_file:
    try:
        # Load and process JSON data
        json_data = json.load(uploaded_file)
        data = process_json_data(json_data)
        if data is not None:
            st.write("Processed Transaction Data", data)

        # Categorize transactions
        data = categorize_transactions(data)

        # Calculate financial metrics
        metrics = calculate_metrics(data)
        st.write("Calculated Financial Metrics", metrics)

        # Plot Revenue vs Expenses
        monthly_summary = calculate_monthly_summary(data)
        st.write("Revenue vs Expenses Graph")
        plot_revenue_vs_expense(monthly_summary)

        # Plot Outflow Transactions for Anomaly Detection
        st.write("Outflow Transactions Graph (for Anomaly Detection)")
        plot_outflow_transactions(data)

        # Calculate the revised weighted score
        revised_weighted_score = calculate_weighted_score(metrics, directors_score, sector_risk, thresholds, weights)
        st.write(f"Weighted Score with same threshold: {revised_weighted_score}")

        # Calculate the revised weighted score
        revised_weighted_d_score = calculate_weighted_score(metrics, directors_score, sector_risk, industry_thresholds, weights)
        st.write(f"Weighted Score with diffrent threshold: {revised_weighted_d_score}")

        predicted_score = predict_score(model, metrics, directors_score, sector_risk, scaler)
        st.write(f"Predicted Score: {predicted_score}")

        # Calculate the revised score
        industry_score = calculate_industry_score(metrics, directors_score, sector_risk, industry_thresholds)
        st.write(f"Score with different industry threshold: {industry_score}")

        # Calculate the revised score
        industry_d_score = calculate_industry_score(metrics, directors_score, sector_risk, thresholds)
        st.write(f"Score with different industry threshold: {industry_d_score}")


    except Exception as e:
        st.error(f"Error processing the file: {e}")

