import pandas as pd
import numpy as np

# Function to predict the score using the trained Logistic Regression model
def predict_score(model, metrics, directors_score, sector_risk, scaler, company_age_months):
    # Prepare the input data as a dictionary
    features = {
        'Directors Score': directors_score,
        'Total Revenue': metrics["Total Revenue"],  
        'Total Debt': metrics["Total Debt"], 
        'Debt-to-Income Ratio': metrics["Debt-to-Income Ratio"], 
        'Operating Margin': metrics["Operating Margin"],  
        'Debt Service Coverage Ratio': metrics["Debt Service Coverage Ratio"],
        'Cash Flow Volatility': metrics["Cash Flow Volatility"],
        'Revenue Growth Rate': metrics["Revenue Growth Rate"],
        'Average Month-End Balance': metrics["Average Month-End Balance"],
        'Average Negative Balance Days per Month': metrics["Average Negative Balance Days per Month"],
        'Number of Bounced Payments': metrics["Number of Bounced Payments"],
        'Company Age (Months)': company_age_months,
        'Sector_Risk': sector_risk                             
                
        # 'Total Expenses': metrics["Total Expenses"],       
        # 'Net Income': metrics["Net Income"],               
        # 'Total Debt Repayments': metrics["Total Debt Repayments"],  
        # 'Expense-to-Revenue Ratio': metrics["Expense-to-Revenue Ratio"],
        # 'Gross Burn Rate': metrics["Gross Burn Rate"],       
        
    }

    # Convert features to a DataFrame
    features_df = pd.DataFrame([features])

    # Clean the data
    features_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    features_df.fillna(0, inplace=True)

    # Scale the features
    features_scaled = scaler.transform(features_df)

    # Predict the probability of repayment (class 1)
    probability_score = model.predict_proba(features_scaled)[:, 1] * 100

    return round(probability_score[0], 2)
