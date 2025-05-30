import pandas as pd
import streamlit as st
import joblib
from model_utils import predict_score
from data_processing import process_json_data, categorize_transactions, calculate_monthly_summary, summarize_monthly_revenue, count_bounced_payments
from financial_metrics import calculate_metrics, avg_revenue, process_balance_report, count_revenue_sources, daily_revenue_summary, check_loan_vs_repayment, check_lender_repayments
from score_calculation import calculate_weighted_score, calculate_industry_score
from config import weights, calculate_risk, industry_thresholds as industry_thresholds_config, penalties
from analysis import plot_revenue_vs_expense, plot_outflow_transactions, plot_transaction_graphs, plot_loan_vs_expense_graph
from plaid_config import get_plaid_data_by_company, COMPANY_ACCESS_TOKENS
from daily_transactions_loader import get_data_from_uploaded_file
import json
from datetime import datetime, timedelta, date

def filter_last_n_months(data, n):
    data = data.copy()
    data['date'] = pd.to_datetime(data['date'])
    latest_date = data['date'].max()
    start_date = (latest_date - pd.DateOffset(months=n)).replace(day=1)
    return data[data['date'] >= start_date]

# Load the model and scaler
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

# Streamlit App
def main():
    st.title("Business Finance Application Scorecard")

    # Create two main tabs
    main_tab1, main_tab2, main_tab3 = st.tabs([
        "Overview and Analysis", 
        "Bank Account and Payment Processing", 
        "Upload Transaction File"
    ])

    with main_tab1:
        st.header("Financial Analysis")

        # Input fields for analysis
        requested_loan = st.number_input("Enter the requested loan amount:", min_value=0.0)
        industry = st.selectbox("Select Industry", list(industry_thresholds_config.keys()))
        industry_thresholds = industry_thresholds_config[industry]
        sector_risk = industry_thresholds['Sector Risk']
        directors_score = st.number_input("Director Score", min_value=0)
        company_age_months = st.number_input("Enter Company Age (in months)", min_value=0, max_value=1000, value=24, step=1)

        # New section for credit checks
        st.subheader("Additional Credit History Checks")
        personal_default_12m = st.checkbox("Any personal credit defaults in last 12 months?", value=False)
        business_ccj = st.checkbox("Any business County Court Judgments (CCJs)?", value=False)
        director_ccj = st.checkbox("Any director County Court Judgments (CCJs)?", value=False)

        # Business Digital Footprint Checks
        st.subheader("Business Digital Footprint Checks")
        website_or_social_outdated = st.checkbox("Website or social presence hasn't been updated in 3+ months?", value=False)
        uses_generic_email = st.checkbox("Business email is Gmail, Hotmail or other generic provider?", value=False)
        no_online_presence = st.checkbox("No website or minimal/no online footprint?", value=False)

        uploaded_file = st.file_uploader("Upload a JSON file", type="json")

        if uploaded_file:
            try:
                json_data = json.load(uploaded_file)
                data = process_json_data(json_data)
                if data is not None:
                    subtab1, subtab2, subtab3, subtab4 = st.tabs(["Overview", "Analysis", "Last 3 Months", "Last 6 Months"])

                    with subtab1:
                        st.write("Transaction Data", data)
                        data = categorize_transactions(data)
                        metrics = calculate_metrics(data, company_age_months)
                        st.write("Calculated Financial Metrics", metrics)

                        revenue_sources = count_revenue_sources(data)
                        avg_txn_count, avg_txn_amount = daily_revenue_summary(data)
                        st.markdown("### Additional Revenue Insights")
                        st.write(f"**Number of Unique Revenue Sources:** {revenue_sources}")
                        if revenue_sources == 1:
                            st.warning("⚠️ This business has only **one** revenue source. This may indicate a higher risk due to income concentration.")
                        st.write(f"**Average Revenue Transactions per Day:** {avg_txn_count}")
                        st.write(f"**Average Daily Revenue Amount:** £{avg_txn_amount}")

                        loans_total, repayments_total = check_loan_vs_repayment(data)
                        st.markdown("### Loan vs Repayment Check")
                        st.write(f"**Total Loans Received:** £{loans_total}")
                        st.write(f"**Total Debt Repayments:** £{repayments_total}")
                        if loans_total > 0 and repayments_total == 0:
                            st.warning("⚠️ Loans have been received but no debt repayments were detected. Investigate repayment behaviour or timing.")

                        st.markdown("### Lender-Specific Repayment Check")
                        loans_display, repayments_display, unmatched_lenders = check_lender_repayments(data)
                        st.write("**Loans Received From:**")
                        for lender, amount in loans_display.items():
                            st.write(f"- {lender.title()} (£{amount:,.2f})")

                        st.write("**Repayments Made To:**")
                        for recipient, amount in repayments_display.items():
                            st.write(f"- {recipient.title()} (£{amount:,.2f})")

                        if unmatched_lenders:
                            st.warning("⚠️ No repayments detected to the following lenders:")
                            for lender in unmatched_lenders:
                                st.write(f"- {lender.title()}")
                        else:
                            st.success("✅ Repayments were detected for all known loan sources.")

                        report = process_balance_report(data)
                        st.write("Monthly Balance Report", report)

                        revenue_report = summarize_monthly_revenue(data)
                        st.write("Revenue Report", revenue_report)

                        bounced_payments = count_bounced_payments(data, description_column='name_y', date_column='authorized_date')
                        st.write("Bounced Payments", bounced_payments)

                        weighted_score = calculate_weighted_score(metrics, directors_score, sector_risk, industry_thresholds, weights, company_age_months, personal_default_12m, business_ccj, director_ccj, website_or_social_outdated, uses_generic_email, no_online_presence, penalties)
                        st.write(f"Weighted Score: {weighted_score}")

                        probability_score = predict_score(model, metrics, directors_score, sector_risk, scaler, company_age_months)
                        st.write(f"Repayment Probability: {probability_score:.2f}")

                        industry_d_score = calculate_industry_score(metrics, directors_score, sector_risk, industry_thresholds, company_age_months)
                        st.write(f"Financial Score: {industry_d_score}")

                        monthly_avg_revenue = avg_revenue(data)
                        loan_risk = calculate_risk(requested_loan, monthly_avg_revenue)
                        st.write(f"Loan Risk Level: {loan_risk}")

                    with subtab2:
                        monthly_summary = calculate_monthly_summary(data)
                        st.write("Revenue vs Expenses Graph")
                        plot_revenue_vs_expense(monthly_summary)
                        plot_transaction_graphs(data)

                    with subtab3:
                        st.subheader("Last 3 Months Overview")
                        data_3m = filter_last_n_months(data, 3)
                        if not data_3m.empty:
                            data_3m = categorize_transactions(data_3m)
                            metrics_3m = calculate_metrics(data_3m, company_age_months)
                            st.write("Calculated Financial Metrics (3 Months)", metrics_3m)

                            report_3m = process_balance_report(data_3m)
                            st.write("Monthly Balance Report (3 Months)", report_3m)

                            revenue_report_3m = summarize_monthly_revenue(data_3m)
                            st.write("Revenue Report (3 Months)", revenue_report_3m)

                            bounced_3m = count_bounced_payments(data_3m, description_column='name_y', date_column='authorized_date')
                            st.write("Bounced Payments (3 Months)", bounced_3m)

                            weighted_score_3m = calculate_weighted_score(metrics_3m, directors_score, sector_risk, industry_thresholds, weights, company_age_months, personal_default_12m, business_ccj, director_ccj, website_or_social_outdated, uses_generic_email, no_online_presence, penalties)
                            st.write(f"Weighted Score (3 Months): {weighted_score_3m}")

                            probability_3m = predict_score(model, metrics_3m, directors_score, sector_risk, scaler, company_age_months)
                            st.write(f"Repayment Probability (3 Months): {probability_3m:.2f}")

                            industry_score_3m = calculate_industry_score(metrics_3m, directors_score, sector_risk, industry_thresholds, company_age_months)
                            st.write(f"Financial Score (3 Months): {industry_score_3m}")

                            avg_rev_3m = avg_revenue(data_3m)
                            loan_risk_3m = calculate_risk(requested_loan, avg_rev_3m)
                            st.write(f"Loan Risk Level (3 Months): {loan_risk_3m}")
                        else:
                            st.warning("No transaction data available for the last 3 months.")

                    with subtab4:
                        st.subheader("Last 6 Months Overview")
                        data_6m = filter_last_n_months(data, 6)
                        if not data_6m.empty:
                            data_6m = categorize_transactions(data_6m)
                            metrics_6m = calculate_metrics(data_6m, company_age_months)
                            st.write("Calculated Financial Metrics (6 Months)", metrics_6m)

                            report_6m = process_balance_report(data_6m)
                            st.write("Monthly Balance Report (6 Months)", report_6m)

                            revenue_report_6m = summarize_monthly_revenue(data_6m)
                            st.write("Revenue Report (6 Months)", revenue_report_6m)

                            bounced_6m = count_bounced_payments(data_6m, description_column='name_y', date_column='authorized_date')
                            st.write("Bounced Payments (6 Months)", bounced_6m)

                            weighted_score_6m = calculate_weighted_score(metrics_6m, directors_score, sector_risk, industry_thresholds, weights, company_age_months, personal_default_12m, business_ccj, director_ccj, website_or_social_outdated, uses_generic_email, no_online_presence, penalties)
                            st.write(f"Weighted Score (6 Months): {weighted_score_6m}")

                            probability_6m = predict_score(model, metrics_6m, directors_score, sector_risk, scaler, company_age_months)
                            st.write(f"Repayment Probability (6 Months): {probability_6m:.2f}")

                            industry_score_6m = calculate_industry_score(metrics_6m, directors_score, sector_risk, industry_thresholds, company_age_months)
                            st.write(f"Financial Score (6 Months): {industry_score_6m}")

                            avg_rev_6m = avg_revenue(data_6m)
                            loan_risk_6m = calculate_risk(requested_loan, avg_rev_6m)
                            st.write(f"Loan Risk Level (6 Months): {loan_risk_6m}")
                        else:
                            st.warning("No transaction data available for the last 6 months.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.info("Please upload a JSON file to view financial analysis.")

    
    with main_tab2:
        # Create subtabs for Bank Account and Payment Processing
        subtab5, subtab6 = st.tabs(["Bank Account Information", "Daily MCA Payment Processing"])
        
        with subtab5:
            st.header("Bank Account Information")

            st.subheader("Data Source Selection")
            data_source = st.radio("Choose data source:", ["Plaid API", "Upload File"], horizontal=True)

            submit_button = False  # Prevent UnboundLocalError

            if data_source == "Upload File":
                uploaded_file = st.file_uploader("Upload Transaction JSON", type=["json"], key="bank_tab_file_upload")
                account_df, categorized_data = get_data_from_uploaded_file(uploaded_file)

                if account_df is not None and categorized_data is not None:
                    st.success("Transaction data successfully loaded.")
                    st.dataframe(categorized_data)  # Show all rows

            elif data_source == "Plaid API":
                companies = COMPANY_ACCESS_TOKENS

                with st.form("simple_transaction_form"):
                    st.subheader("Select Company")
                    selected_company = st.selectbox("Select Company", list(companies.keys()), key="simple_company_selector")
                    submit_button = st.form_submit_button("View Information")

            if submit_button:
                st.info(f"Selected Company: {selected_company}")
                access_token = companies[selected_company]

                try:
                    with st.spinner('Fetching transaction data...'):
                        end_date = datetime.now().date()
                        start_date = end_date - timedelta(days=30)

                        _, transaction_data = get_plaid_data_by_company(
                            selected_company,
                            access_token,
                            start_date,
                            end_date
                        )

                    if not transaction_data.empty:
                        transaction_data['date'] = pd.to_datetime(transaction_data['date'])
                        sorted_transactions = transaction_data.sort_values('date', ascending=False)

                        actual_min_date = transaction_data['date'].min().date()
                        actual_max_date = transaction_data['date'].max().date()
                        st.success(f"Showing transactions from {actual_min_date} to {actual_max_date}")

                        csv = sorted_transactions[['date', 'name', 'amount', 'category', 'is_authorised_account', 'sort_code', 'account_number', 'account_name']].to_csv(index=False)
                        st.download_button(
                             "Download Transactions as CSV",
                             data=csv,
                             file_name=f"{selected_company}_transactions.csv",
                             mime="text/csv"
                        )

                        st.subheader("Transactions")
                        st.dataframe(sorted_transactions[['date', 'name', 'amount', 'category', 'is_authorised_account', 'sort_code', 'account_number', 'account_name', 'subcategory', 'personal_finance_category.detailed']])
                    else:
                        st.warning(f"No transaction data found for company: {selected_company}")

                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")

        
        with subtab6:
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

    with main_tab3:
        st.header("Upload Transaction File")

        st.subheader("Select Date Range Before Uploading")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=date.today())

        uploaded_file = st.file_uploader("Upload Transaction JSON", type=["json"], key="upload_tab_file_upload")

        if uploaded_file:
            account_df, categorized_data = get_data_from_uploaded_file(uploaded_file, start_date, end_date)

            if account_df is not None and categorized_data is not None:
                st.success("Transaction data successfully loaded.")

                if not categorized_data.empty and 'subcategory' in categorized_data.columns:
                    available_subcategories = categorized_data['subcategory'].dropna().unique().tolist()
                    selected_subcategories = st.multiselect(
                        "Filter by Subcategory (e.g. Income, Special Inflow, Expenses, etc.)",
                        options=available_subcategories,
                        default=available_subcategories
                    )
                    filtered_data = categorized_data[categorized_data['subcategory'].isin(selected_subcategories)]
                    st.dataframe(filtered_data)

                    csv_data = filtered_data.to_csv(index=False)
                    st.download_button(
                        label="Download Filtered Transactions as CSV",
                        data=csv_data,
                        file_name="categorized_transactions.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No usable transactions or 'subcategory' column missing from processed data.")

if __name__ == "__main__":
        main()
