import pandas as pd
import streamlit as st
import joblib
from model_utils import predict_score
from data_processing import process_json_data, categorize_transactions, calculate_monthly_summary, summarize_monthly_revenue, count_bounced_payments
from financial_metrics import calculate_metrics, avg_revenue, process_balance_report
from score_calculation import calculate_weighted_score, calculate_industry_score
from config import weights, calculate_risk, industry_thresholds as industry_thresholds_config, penalties
from analysis import plot_revenue_vs_expense, plot_outflow_transactions, plot_transaction_graphs, plot_loan_vs_expense_graph
from plaid_config import get_plaid_data_by_company, COMPANY_ACCESS_TOKENS
import json
from datetime import datetime, timedelta
# Load the model and scaler
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')


# Streamlit App
def main():
    st.title("Business Finance Application Scorecard")
    
    # Create two main tabs
    main_tab1, main_tab2 = st.tabs(["Overview and Analysis", "Bank Account and Payment Processing"])
    
    with main_tab1:
        st.header("Financial Analysis")
        
        # Input fields for analysis
        requested_loan = st.number_input("Enter the requested loan amount:", min_value=0.0)
        industry = st.selectbox("Select Industry", list(industry_thresholds_config.keys()))
        industry_thresholds = industry_thresholds_config[industry]
        sector_risk = industry_thresholds['Sector Risk']
        directors_score = st.number_input("Director Score", min_value=0)
        company_age_months = st.number_input("Enter Company Age (in months)", min_value=0, max_value=1000, value=24, step=1)
        personal_default_12m = st.checkbox("Any personal credit defaults in last 12 months?", value=False)
        business_ccj = st.checkbox("Any business County Court Judgments (CCJs)?", value=False)
        director_ccj = st.checkbox("Any director County Court Judgments (CCJs)?", value=False)
        uploaded_file = st.file_uploader("Upload a JSON file", type="json")
        
        if uploaded_file:
            try:
                # Load and process JSON data
                json_data = json.load(uploaded_file)
                data = process_json_data(json_data)
                if data is not None:
                    # Create subtabs for Overview and Analysis
                    subtab1, subtab2 = st.tabs(["Overview", "Analysis"])
                    
                    with subtab1:
                        st.write("Transaction Data", data)
                    
                        # Categorize transactions
                        data = categorize_transactions(data) 

                        # Calculate financial metrics
                        metrics = calculate_metrics(data, company_age_months)
                        st.write("Calculated Financial Metrics", metrics)

                        # Balance Report
                        report = process_balance_report(data)
                        st.write("Monthly Balance Report", report)

                        revenue_report = summarize_monthly_revenue(data)
                        st.write("Report", revenue_report)

                        bounced_payments = count_bounced_payments(data, description_column='name_y', date_column='authorized_date')
                        st.write("Bounced Payments", bounced_payments)

                        # Calculate the weighted score
                        revised_weighted_d_score = calculate_weighted_score(metrics, directors_score, sector_risk, industry_thresholds, weights, company_age_months, personal_default_12m=personal_default_12m, business_ccj=business_ccj, director_ccj=director_ccj, penalties=penalties)

                        st.write(f"Weighted Score: {revised_weighted_d_score}")

                        probability_score = predict_score(model, metrics, directors_score, sector_risk, scaler, company_age_months)
                        st.write(f"Repayment Probability: {probability_score:.2f}")

                        # Calculate the revised score based on industry thresholds
                        industry_d_score = calculate_industry_score(metrics, directors_score, sector_risk, industry_thresholds, company_age_months)
                        st.write(f"Financial Score: {industry_d_score}")

                        monthly_avg_revenue = avg_revenue(data)
                        loan_risk = calculate_risk(requested_loan, monthly_avg_revenue)
                        st.write(f"Loan Risk Level: {loan_risk}")

                    with subtab2:
                        selected_categories = ['Expenses', 'Debt Repayments', 'Special Outflow', 'Failed Payment']
                        expenses = data[data['subcategory'].isin(selected_categories)]
                        expenses_grouped = expenses.groupby('personal_finance_category.primary')['amount'].sum().reset_index()
                        expenses_grouped = expenses_grouped.sort_values(by='amount', ascending=False).reset_index(drop=True)
                        st.write("Total Expenses", expenses_grouped)

                        # Plot Revenue vs Expenses
                        monthly_summary = calculate_monthly_summary(data)
                        st.write("Revenue vs Expenses Graph")
                        plot_revenue_vs_expense(monthly_summary)

                        plot_transaction_graphs(data)

                        # Filter loans received
                        loans_received = data[data['subcategory'] == 'Loans'][['date', 'amount']]
                        loans_received = loans_received.sort_values(by='date').reset_index(drop=True)

                        # Create a new dataframe to store loans and revenue for the same period
                        loans_with_revenue = loans_received.copy()

                        # Calculate the total revenue for the entire dataset
                        total_revenue = round(data.loc[data['is_revenue'], 'amount'].sum() or 0, 2)

                        # Find cumulative revenue up to and including the loan date
                        loans_with_revenue['cumulative_revenue'] = loans_with_revenue['date'].apply(
                            lambda loan_date: round(data.loc[(data['is_revenue']) & (data['date'] <= loan_date), 'amount'].sum() or 0, 2)
                        )

                        # Display loans and corresponding cumulative revenue up to that loan date
                        st.write("Loans Received with Cumulative Revenue Up to Loan Date")
                        st.write(loans_with_revenue)

                        # Loan inflow vs Expense
                        plot_loan_vs_expense_graph(data, loans_received['date'])

                        # Initialize a list to store grouped expenses after each loan within 10 days
                        grouped_expenses = []

                        # Loop through loans to get expenses within the next 10 days of each loan
                        for i in range(len(loans_received)):
                            start_date = loans_received.iloc[i]['date']
                            end_date = start_date + pd.DateOffset(days=10)
                            start_date_10_before = start_date - pd.DateOffset(days=10)

                            # Filter expenses 10 days before the loan date
                            expenses_before_loan = expenses[(expenses['date'] > start_date_10_before) & (expenses['date'] <= start_date)]
                            expenses_grouped_before_loan = expenses_before_loan.groupby('personal_finance_category.primary')['amount'].sum().reset_index()

                            # Filter expenses between the start date (loan date) and the end date (next 10 days)
                            expenses_after_loan = expenses[(expenses['date'] > start_date) & (expenses['date'] <= end_date)]
                            expenses_grouped_after_loan = expenses_after_loan.groupby('personal_finance_category.primary')['amount'].sum().reset_index()

                            grouped_expenses.append({
                                'Loan Date': start_date,
                                '10 Days Before Loan Expenses': expenses_grouped_before_loan,
                                '10 Days After Loan Expenses': expenses_grouped_after_loan
                            })

                        # Display the grouped expenses for each loan
                        for idx, entry in enumerate(grouped_expenses):
                            st.write(f"Expenses before and after Loan {idx + 1} (from {entry['Loan Date']}):")
                            st.write("Expenses in the 10 days before loan:")
                            st.write(entry['10 Days Before Loan Expenses'])
                            st.write("Expenses in the 10 days after loan:")
                            st.write(entry['10 Days After Loan Expenses'])
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("Please upload a JSON file to view financial analysis.")
    
    with main_tab2:
        # Create subtabs for Bank Account and Payment Processing
        subtab3, subtab4 = st.tabs(["Bank Account Information", "Daily MCA Payment Processing"])
        
        with subtab3:
            st.header("Bank Account Information")
            
            # Define a dictionary of companies and their access tokens
            companies = COMPANY_ACCESS_TOKENS

            # Create a form to collect company info before processing
            with st.form("simple_transaction_form"):
                st.subheader("Select Company")
                
                # Company selection dropdown
                selected_company = st.selectbox(
                    "Select Company", 
                    list(companies.keys()),
                    key="simple_company_selector"
                )
                
                # Submit button
                submit_button = st.form_submit_button("View Information")
            
            # Only process data if the form has been submitted
            if submit_button:
                st.info(f"Selected Company: {selected_company}")
                
                access_token = companies[selected_company]
                
                try:
                    # Show a spinner while fetching data
                    with st.spinner('Fetching transaction data...'):
                        # Get default date range (last 30 days)
                        end_date = datetime.now().date()
                        start_date = end_date - timedelta(days=30)
                        
                        # Get bank account data for the selected company and date range
                        _, transaction_data = get_plaid_data_by_company(
                            selected_company, 
                            access_token,
                            start_date,
                            end_date
                        )
                    
                    if not transaction_data.empty:
                        # Format transaction data
                        transaction_data['date'] = pd.to_datetime(transaction_data['date'])
                        sorted_transactions = transaction_data.sort_values('date', ascending=False)
                        
                        # Display the actual date range of transactions
                        actual_min_date = transaction_data['date'].min().date()
                        actual_max_date = transaction_data['date'].max().date()
                        st.success(f"Showing transactions from {actual_min_date} to {actual_max_date}")
                        
                        # Add download button for transactions
                        csv = sorted_transactions[['date', 'name', 'amount', 'category', 'is_authorised_account', 'sort_code', 'account_number', 'account_name']].to_csv(index=False)
                        st.download_button(
                            "Download Transactions as CSV",
                            data=csv,
                            file_name=f"{selected_company}_transactions.csv",
                            mime="text/csv",
                        )
                        
                        # Display transactions table (the main dataframe)
                        st.subheader("Transactions")
                        st.dataframe(sorted_transactions[['date', 'name', 'amount', 'category', 'is_authorised_account', 'sort_code', 'account_number', 'account_name','subcategory','personal_finance_category.detailed']])
                    else:
                        st.warning(f"No transaction data found for company: {selected_company}")
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")
        
        with subtab4:
            st.header("Daily MCA Payment Processing")
            companies = COMPANY_ACCESS_TOKENS

            with st.form("bank_data_form"):
                st.subheader("Select Company and Date Range")
                selected_company = st.selectbox("Select Company", list(companies.keys()), key="company_selector")
                col1, col2 = st.columns(2)
                with col1:
                    default_start = datetime.now().date() - timedelta(days=30)
                    start_date = st.date_input("Start Date", value=default_start, max_value=datetime.now().date())
                with col2:
                    end_date = st.date_input("End Date", value=datetime.now().date(), min_value=start_date, max_value=datetime.now().date())
                submit_button = st.form_submit_button("Fetch Data")

            if submit_button:
                try:
                    access_token = companies[selected_company]
                    with st.spinner("Fetching bank data..."):
                        account_info, transaction_data = get_plaid_data_by_company(
                            selected_company,
                            access_token,
                            start_date,
                            end_date
                        )
                    st.session_state["account_info"] = account_info
                    st.session_state["transaction_data"] = transaction_data
                    st.session_state["selected_company"] = selected_company
                    st.session_state["start_date"] = start_date
                    st.session_state["end_date"] = end_date
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")

            if (
                "account_info" in st.session_state and
                not st.session_state["account_info"].empty and
                "transaction_data" in st.session_state
            ):
                account_info = st.session_state["account_info"]
                transaction_data = st.session_state["transaction_data"]
                selected_company = st.session_state["selected_company"]
                start_date = st.session_state["start_date"]
                end_date = st.session_state["end_date"]

                st.success(f"Data loaded for {selected_company} from {start_date} to {end_date}")
                st.subheader("Bank Accounts Overview")
                st.dataframe(account_info[['account_name', 'account_type', 'balance_current', 'balance_available']])

                transaction_data['date'] = pd.to_datetime(transaction_data['date'])
                income_transactions = transaction_data[
                    transaction_data['subcategory'].isin(['Income', 'Special Inflow'])
                ]

                account_options = account_info['account_name'].tolist()
                selected_account_name = st.selectbox("Select an account to view details", account_options, key="account_selector")

                selected_account = account_info[account_info['account_name'] == selected_account_name].iloc[0]
                st.subheader(f"Account Details: {selected_account_name}")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Account ID:** {selected_account['account_id']}")
                    st.write(f"**Type:** {selected_account['account_type']} / {selected_account['account_subtype']}")
                with col2:
                    st.write(f"**Sort Code:** {selected_account['sort_code']}")
                    st.write(f"**Account Number:** {selected_account['account_number']}")

                account_income_transactions = income_transactions[
                    income_transactions['account_id'] == selected_account['account_id']
                ]

                st.subheader("Income Transactions")
                if not account_income_transactions.empty:
                    sorted_txns = account_income_transactions.sort_values("date", ascending=False)
                    display_cols = [
                        col for col in ['date', 'name', 'amount', 'category', 'subcategory', 'personal_finance_category.detailed']
                        if col in sorted_txns.columns
                    ]
                    csv = sorted_txns[display_cols].to_csv(index=False)
                    st.download_button(
                        "Download Income Transactions as CSV",
                        data=csv,
                        file_name=f"{selected_company}_{selected_account_name}_income.csv",
                        mime="text/csv"
                    )
                    st.dataframe(sorted_txns[display_cols])
                else:
                    st.info("No income transactions found for this account.")
            else:
                st.info("\U0001F446 Please select a company and date range, then click 'Fetch Data'.")

if __name__ == "__main__":
    main()
