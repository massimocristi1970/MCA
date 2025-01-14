import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from sklearn.linear_model import LinearRegression

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

def plot_loan_vs_expense_graph(data, loan_dates):
    loans_received = data[data['subcategory'] == 'Loans']
    selected_categories = ['Expenses', 'Debt Repayments', 'Special Outflow', 'Failed Payment']
    expenses = data[data['subcategory'].isin(selected_categories)]

    # Aggregate loans by date
    loans_grouped = loans_received.groupby('date')['amount'].sum().reset_index()
    expenses_grouped = expenses.groupby('date')['amount'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(loans_grouped['date'], loans_grouped['amount'], label='Loans Received', color='green', marker='o')
    ax.plot(expenses_grouped['date'], expenses_grouped['amount'], label='Total Expenses', color='red', marker='o')

    # Set plot labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount')
    ax.set_title('Loans vs Total Expenses')
    ax.legend()
    st.pyplot(fig)


def plot_transaction_graphs(data, input_date):
    input_date = pd.to_datetime(input_date)
    filtered_data = data[data['date'] >= input_date]

    # Group data by day for inflow and outflow
    daily_data = filtered_data.groupby(filtered_data['date'].dt.date).agg(
        Daily_Inflow=('amount', lambda x: x[filtered_data['is_revenue']].sum()),
        Daily_Outflow=('amount', lambda x: x[filtered_data['is_expense']].sum())
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(daily_data['date'], daily_data['Daily_Inflow'], label='Daily Inflow', color='green')
    ax.plot(daily_data['date'], daily_data['Daily_Outflow'], label='Daily Outflow', color='red')

    ax.set_xlabel('Date')
    ax.set_ylabel('Amount')
    ax.set_title('Daily Inflow and Outflow')
    ax.legend()

    st.pyplot(fig)
    # Group data by day for Revenue vs Expenses
    revenue_expense_data = filtered_data.groupby(filtered_data['date'].dt.date).agg(
        Revenue=('amount', lambda x: x[filtered_data['is_revenue']].sum()),
        Expenses=('amount', lambda x: x[filtered_data['is_expense']].sum())
    ).reset_index()