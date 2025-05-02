import pandas as pd
import numpy as np
import streamlit as st  # Make sure this import is present


# Function to predict the score using the trained Logistic Regression model
def predict_score(model, metrics, directors_score, sector_risk, scaler, company_age_months):
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
        'Company Age (Months)': company_age_months,
        
    }

    # Convert features to a DataFrame
    features_df = pd.DataFrame([features])

    # Debug: Print raw features
    st.write("📊 Raw input features:")
    st.write(features_df)

    # Show feature counts
    st.write("📦 You are passing in", features_df.shape[1], "features")
    st.write("🔍 Model expects", model.coef_.shape[1], "features")
    st.write("🧪 Scaler expects", scaler.mean_.shape[0], "features")

    # Handle infinite values and fill NaNs
    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.fillna(0, inplace=True)

    # Scale the features
    features_scaled = scaler.transform(features_df)

    # Debug: Print scaled features
    st.write("📉 Scaled input features:")
    st.write(features_scaled)

    # Predict the probability of repayment (class 1)
    probability_score = model.predict_proba(features_scaled)[:, 1]

    return probability_score[0]
