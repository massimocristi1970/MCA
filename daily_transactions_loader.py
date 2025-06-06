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

        # ✅ Filter by date
        if start_date and end_date:
            filtered_transactions = []
            for txn in transactions:
                try:
                    txn_date = pd.to_datetime(txn.get('date')).date()
                    if start_date <= txn_date <= end_date:
                        filtered_transactions.append(txn)
                except Exception as e:
                    st.warning(f"Skipping transaction due to invalid date: {txn.get('date')} ({e})")

            transactions = filtered_transactions

            
        # 🧠 Optional sanity check
        st.write(f"Transactions in date range: {len(transactions)}")
        
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

            if categorized_data is None or categorized_data.empty:
                raise ValueError("process_json_data() returned no data")

            # Add routing/account metadata
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

            # Rename for consistency
            if 'name_y' in categorized_data.columns and 'name' not in categorized_data.columns:
                categorized_data = categorized_data.rename(columns={'name_y': 'name'})

        except Exception as e:
            st.error("process_json_data() failed")
            st.exception(e)



            txn_data = []
            for txn in transactions:
                try:
                    acct_id = txn.get('account_id', 'unknown')
                    route_info = routing_data.get(acct_id, {})
                    txn_data.append({
                        'date': txn.get('date'),
                        'name': txn.get('name'),
                        'amount': txn.get('amount'),
                        'category': ", ".join(txn.get('category') or []),
                        'account_id': acct_id,
                        'is_authorised_account': acct_id in routing_data,
                        'sort_code': route_info.get('sort_code'),
                        'account_number': route_info.get('account_number'),
                        'account_name': route_info.get('account_name'),
                        'subcategory': (
                            'Income' if txn.get('amount') is not None and txn['amount'] < 0
                            else 'Expenses' if txn.get('amount') is not None
                            else None
                        )
                    })
                except Exception as txn_error:
                    st.warning(f"Skipping malformed transaction: {txn_error}")

            categorized_data = pd.DataFrame(txn_data)

            if categorized_data.empty:
                st.warning("All transactions were skipped due to formatting issues.")
            else:
                if 'subcategory' not in categorized_data.columns:
                    st.warning("Transactions loaded, but 'subcategory' could not be derived.")

        return account_df, categorized_data

    except Exception as e:
        st.error(f"Failed to load and process uploaded file: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

