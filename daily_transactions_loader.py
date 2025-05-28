import pandas as pd
import streamlit as st
from data_processing import process_json_data

def get_data_from_uploaded_file(uploaded_file, start_date=None, end_date=None):
    if uploaded_file is None:
        st.warning("Please upload a transaction file.")
        return None, None

    try:
        import json
        json_data = json.load(uploaded_file)

        accounts = json_data.get('accounts', [])
        transactions = json_data.get('transactions', [])

        # Filter transactions by date range if provided
        if start_date and end_date:
            transactions = [
                txn for txn in transactions
                if 'date' in txn and start_date <= pd.to_datetime(txn['date']).date() <= end_date
            ]

        # Account summary construction
        account_summaries = []
        routing_data = {}
        for acct in accounts:
            acct_id = acct['account_id']
            routing_data[acct_id] = {
                'sort_code': acct.get('sort_code', 'N/A'),
                'account_number': acct.get('account', 'N/A'),
                'account_name': acct.get('name', 'Unnamed Account')
            }
            account_summaries.append({
                'account_id': acct_id,
                'account_name': acct.get('name', 'Unknown'),
                'account_type': acct.get('type', 'Unknown'),
                'account_subtype': acct.get('subtype', 'Unknown'),
                'balance_available': acct.get('balances', {}).get('available'),
                'balance_current': acct.get('balances', {}).get('current'),
                'sort_code': acct.get('sort_code', 'N/A'),
                'account_number': acct.get('account', 'N/A'),
            })
        account_df = pd.DataFrame(account_summaries)

        try:
            categorized_data = process_json_data({
                'accounts': accounts,
                'transactions': transactions
            })

            categorized_data['is_authorised_account'] = categorized_data['account_id'].apply(
                lambda x: x in routing_data
            )
            categorized_data['sort_code'] = categorized_data['account_id'].apply(
                lambda x: routing_data.get(x, {}).get('sort_code', 'N/A')
            )
            categorized_data['account_number'] = categorized_data['account_id'].apply(
                lambda x: routing_data.get(x, {}).get('account_number', 'N/A')
            )
            categorized_data['account_name'] = categorized_data['account_id'].apply(
                lambda x: routing_data.get(x, {}).get('account_name', 'Unnamed Account')
            )

            if 'name_y' in categorized_data.columns and 'name' not in categorized_data.columns:
                categorized_data = categorized_data.rename(columns={'name_y': 'name'})

        except Exception as e:
            st.error(f"Error in processing transaction data: {str(e)}")
            txn_data = []
            for txn in transactions:
                acct_id = txn['account_id']
                route_info = routing_data.get(acct_id, {})
                txn_data.append({
                    'date': txn['date'],
                    'name': txn['name'],
                    'amount': txn['amount'],
                    'category': ", ".join(txn.get('category') or []),
                    'account_id': acct_id,
                    'is_authorised_account': acct_id in routing_data,
                    'sort_code': route_info.get('sort_code'),
                    'account_number': route_info.get('account_number'),
                    'account_name': route_info.get('account_name'),
                    'subcategory': 'Income' if txn['amount'] < 0 else 'Expenses'
                })
            categorized_data = pd.DataFrame(txn_data)

        return account_df, categorized_data

    except Exception as e:
        st.error(f"Failed to load and process uploaded file: {str(e)}")
        return None, None
