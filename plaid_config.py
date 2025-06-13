# Import Plaid libraries
import pandas as pd
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from datetime import datetime, timedelta
from data_processing import process_json_data
import streamlit as st


COMPANY_ACCESS_TOKENS = dict(sorted({
    "Bound Studios": "access-production-c96f81d2-206f-4e6a-b442-a18d102b3870",
    "Moving Ewe": "access-production-31009602-a97b-42db-bf7c-ca7db185eac1",
    "Sanitaire Ltd": "access-production-9d27e5a4-3f09-4deb-8d7c-58b2ea014578",
    "Ellevate limited": "access-production-a93de1cc-4c56-4e4f-a92d-6dd000d00d85",
    "Boiler Solution Cover UK": "access-production-b8b19025-2c67-4364-b7ee-ac6c236764f1"
}.items()))



def get_plaid_data_by_company(company_name, access_token, start_date, end_date):
    # Plaid credentials
    PLAID_CLIENT_ID = "649ec08315ff560018b268cd"
    PLAID_SECRET = "1759b2f1f5a085506186f1396430fa"
    PLAID_ENV = "production"

    # Environment setup
    host_url = {
        "sandbox": "https://sandbox.plaid.com",
        "development": "https://development.plaid.com",
        "production": "https://production.plaid.com"
    }[PLAID_ENV]
 
    config = Configuration(
        host=host_url,
        api_key={
            'clientId': PLAID_CLIENT_ID,
            'secret': PLAID_SECRET
        }
    )
    api_client = ApiClient(config)
    client = plaid_api.PlaidApi(api_client)

    # --- STEP 1: Get Auth Info ---
    auth_request = AuthGetRequest(access_token=access_token)
    auth_response = client.auth_get(auth_request)
    auth_data = auth_response.to_dict()

    accounts = auth_data['accounts']
    bacs_info = auth_data.get('numbers', {}).get('bacs', [])

    # Build a mapping of account_id
    routing_data = {
        item['account_id']: {
            'sort_code': item['sort_code'],
            'account_number': item['account']
        }
        for item in bacs_info
    }

    # Add account name to routing_data
    for acct in accounts:
        acct_id = acct['account_id']
        if acct_id in routing_data:
            routing_data[acct_id]['account_name'] = acct.get('name', 'Unnamed Account')

    # --- STEP 2: Get Transactions for the Specified Date Range ---
    txn_request = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date
    )
    txn_response = client.transactions_get(txn_request)
    transactions = txn_response.to_dict()['transactions']

    # --- STEP 3: Format Account Summary Data ---
    account_summaries = []
    for acct in accounts:
        acct_id = acct['account_id']
        routing = routing_data.get(acct_id, {})
        account_summaries.append({
            'account_id': acct_id,
            'account_name': acct.get('name', 'Unknown'),
            'account_type': acct.get('type', 'Unknown'),
            'account_subtype': acct.get('subtype', 'Unknown'),
            'balance_available': acct.get('balances', {}).get('available'),
            'balance_current': acct.get('balances', {}).get('current'),
            'sort_code': routing.get('sort_code', 'N/A'),
            'account_number': routing.get('account_number', 'N/A'),
        })

    account_df = pd.DataFrame(account_summaries)
    
    # Create JSON structure for process_json_data function
    json_structure = {
        'accounts': accounts,
        'transactions': transactions
    }
    
    # Process data using the existing process_json_data function
    try:
        categorized_data = process_json_data(json_structure)
        if 'is_authorised_account' not in categorized_data.columns:
            categorized_data['is_authorised_account'] = categorized_data['account_id'].apply(
                lambda x: x in routing_data
            )
            
        if 'sort_code' not in categorized_data.columns:
            categorized_data['sort_code'] = categorized_data['account_id'].apply(
                lambda x: routing_data.get(x, {}).get('sort_code', 'N/A')
            )
            
        if 'account_number' not in categorized_data.columns:
            categorized_data['account_number'] = categorized_data['account_id'].apply(
                lambda x: routing_data.get(x, {}).get('account_number', 'N/A')
            )
            
        if 'account_name' not in categorized_data.columns:
            categorized_data['account_name'] = categorized_data['account_id'].apply(
                lambda x: routing_data.get(x, {}).get('account_name', 'Unnamed Account')
            )

        if 'name_y' in categorized_data.columns and 'name' not in categorized_data.columns:
            categorized_data = categorized_data.rename(columns={'name_y': 'name'})
            
    except Exception as e:
        st.error(f"Error in process_json_data: {str(e)}")
        
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
                # Simple subcategory fallback
                'subcategory': 'Income' if txn['amount'] < 0 else 'Expenses'
            })
            
        categorized_data = pd.DataFrame(txn_data)

    return account_df, categorized_data
