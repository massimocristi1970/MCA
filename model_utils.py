import pandas as pd
import numpy as np


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
        'Company Age (Months)': metrics["Company Age (Months)"],
        
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
