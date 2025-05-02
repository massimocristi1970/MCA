import pandas as pd
import numpy as np
import streamlit as st  # Make sure this import is present
import os


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

    # ✅ 🔍 Add diagnostics here
    st.write("📦 Model path:", os.path.abspath("model.pkl"))
    st.write("🧪 Scaler path:", os.path.abspath("scaler.pkl"))

    st.write("📊 Raw input features:")
    st.write(features_df)

    st.write("📈 Model coefficients shape:", model.coef_.shape)
    st.write("📏 Scaler mean shape:", scaler.mean_.shape)
    st.write("📋 Scaler expected features (if available):", getattr(scaler, 'feature_names_in_', 'Not available'))

    # Handle infinite values and fill NaNs
    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.fillna(0, inplace=True)

    # ✅ Check the order of columns
    st.write("🧭 Order of columns in features_df:", list(features_df.columns))
    st.write("🎯 Order expected by scaler:", list(getattr(scaler, 'feature_names_in_', [])))

    # Scale the features
    features_scaled = scaler.transform(features_df)

    # ✅ More diagnostics after scaling
    st.write("📉 Final scaled input to model:")
    st.write(features_scaled)

    st.write("⚙️ Model coefficients:")
    st.write(model.coef_)

    st.write("🚦 Model intercept:")
    st.write(model.intercept_)

    # 🧮 Manually calculate probability to confirm
    logit = np.dot(features_scaled, model.coef_.T) + model.intercept_
    probability = 1 / (1 + np.exp(-logit))
    st.write("🧮 Manually calculated probability:", probability[0][0])

    # Predict the probability of repayment (class 1)
    probability_score = model.predict_proba(features_scaled)[:, 1]

    return probability_score[0]
