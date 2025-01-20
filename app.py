import pandas as pd
import streamlit as st
import joblib
from model_utils import predict_score
from data_processing import process_json_data, categorize_transactions, calculate_monthly_summary
from financial_metrics import calculate_metrics, avg_revenue
from score_calculation import calculate_weighted_score, calculate_industry_score
from config import weights, calculate_risk, industry_thresholds as industry_thresholds_config
from analysis import plot_revenue_vs_expense, plot_outflow_transactions, plot_transaction_graphs, plot_loan_vs_expense_graph
import json

# Load the model and scaler
model = joblib.load('model.pkl')
scaler = joblib.load('scaler.pkl')

# Streamlit App
def main():
    st.title("Financial Metrics Scoring Tool")
    requested_loan = st.number_input("Enter the requested loan amount:", min_value=0.0)
    industry = st.selectbox("Select Industry", list(industry_thresholds_config.keys()))
    industry_thresholds = industry_thresholds_config[industry]
    sector_risk = industry_thresholds['Sector Risk']
    directors_score = st.number_input("Director Score", min_value=0)
    # input_date = st.date_input("Select Date", pd.to_datetime("2022-01-01"))
    uploaded_file = st.file_uploader("Upload a JSON file", type="json")
    
    if uploaded_file:
        try:
            # Load and process JSON data
            json_data = json.load(uploaded_file)
            data = process_json_data(json_data)
            if data is not None:
                # Create tabs for different sections
                tab1, tab2 = st.tabs(["Overview", "Analysis"])
                
                with tab1:
                    st.write("Transaction Data", data)
                
                    # Categorize transactions
                    data = categorize_transactions(data) 

                    # Calculate financial metrics
                    metrics = calculate_metrics(data)
                    st.write("Calculated Financial Metrics", metrics)

                    # Calculate the weighted score
                    revised_weighted_d_score = calculate_weighted_score(metrics, directors_score, sector_risk, industry_thresholds, weights)
                    st.write(f"Weighted Score: {revised_weighted_d_score}")

                    probability_score = predict_score(model, metrics, directors_score, sector_risk, scaler)
                    st.write(f"Repayment Probability: {probability_score:.2f}")

                    # Calculate the revised score based on industry thresholds
                    industry_d_score = calculate_industry_score(metrics, directors_score, sector_risk, industry_thresholds)
                    st.write(f"Financial Score: {industry_d_score}")

                    monthly_avg_revenue = avg_revenue(data)
                    loan_risk = calculate_risk(requested_loan, monthly_avg_revenue)
                    st.write(f"Loan Risk Level: {loan_risk}")

                with tab2:
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

if __name__ == "__main__":
    main()