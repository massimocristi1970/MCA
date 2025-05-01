# Function to calculate weighted score
import pandas as pd
import streamlit as st
from config import months_threshold, calculate_risk
from financial_metrics import avg_revenue

def calculate_weighted_score(metrics, directors_score, sector_risk, thresholds, weights, company_age_months):
    weighted_score = 0
    # Debt Service Coverage Ratio
    if metrics["Debt Service Coverage Ratio"] >= thresholds["Debt Service Coverage Ratio"]:
        weighted_score += weights["Debt Service Coverage Ratio"]

    # Net Income
    if metrics["Net Income"] >= thresholds["Net Income"]:
        weighted_score += weights["Net Income"]

    # Operating Margin
    if metrics["Operating Margin"] >= thresholds["Operating Margin"]:
        weighted_score += weights["Operating Margin"]

    # Expense-to-Revenue Ratio (lower is better)
    if metrics["Expense-to-Revenue Ratio"] <= thresholds["Expense-to-Revenue Ratio"]:
        weighted_score += weights["Expense-to-Revenue Ratio"]

    # Revenue Growth Rate
    if metrics["Revenue Growth Rate"] >= thresholds["Revenue Growth Rate"]:
        weighted_score += weights["Revenue Growth Rate"]

    # Cash Flow Volatility (lower is better)
    if metrics["Cash Flow Volatility"] <= thresholds["Cash Flow Volatility"]:
        weighted_score += weights["Cash Flow Volatility"]

    # Burn Rate (lower is better)
    if metrics["Gross Burn Rate"] <= thresholds["Gross Burn Rate"]:
        weighted_score += weights["Gross Burn Rate"]

    # Company Age (passed manually)
    if company_age_months >= months_threshold:
        weighted_score += weights["Months"]

    # Directors Score
    if directors_score >= thresholds["Directors Score"]:
        weighted_score += weights["Directors Score"]

    # Sector Risk (Industry Risk) adjustment based on input
    # Add weight for Sector Risk if it's low
    if sector_risk <= thresholds["Sector Risk"]:
        weighted_score += weights["Sector Risk"]

    # Average Month-End Balance
    if "Average Month-End Balance" in metrics and "Average Month-End Balance" in thresholds:
        if metrics["Average Month-End Balance"] >= thresholds["Average Month-End Balance"]:
            weighted_score += weights["Average Month-End Balance"]

    # Average Negative Balance Days per Month (lower is better)
    if "Average Negative Balance Days per Month" in metrics and "Average Negative Balance Days per Month" in thresholds:
        if metrics["Average Negative Balance Days per Month"] <= thresholds["Average Negative Balance Days per Month"]:
            weighted_score += weights["Average Negative Balance Days per Month"]

    # Number of Bounced Payments (lower is better)
    if "Number of Bounced Payments" in metrics and "Number of Bounced Payments" in thresholds:
        if metrics["Number of Bounced Payments"] <= thresholds["Number of Bounced Payments"]:
            weighted_score += weights["Number of Bounced Payments"]

            
    return weighted_score


# Function to calculate revised score based on financial metrics, thresholds, and binary scoring
def calculate_industry_score(metrics, directors_score, sector_risk, thresholds, company_age_months):
    industry_score = 0
    feedback = []  # List to store feedback for each metric

    # Debt Service Coverage Ratio
    if metrics["Debt Service Coverage Ratio"] >= thresholds["Debt Service Coverage Ratio"]:
        industry_score += 1
        feedback.append(f"✅ Debt Service Coverage Ratio is {metrics['Debt Service Coverage Ratio']}, which meets the threshold of {thresholds['Debt Service Coverage Ratio']}.")
    else:
        feedback.append(f"❌ Debt Service Coverage Ratio is {metrics['Debt Service Coverage Ratio']}, below the threshold of {thresholds['Debt Service Coverage Ratio']}.")

    # Net Income
    if metrics["Net Income"] >= thresholds["Net Income"]:
        industry_score += 1
        feedback.append(f"✅ Net Income is {metrics['Net Income']}, which meets or exceeds the threshold of {thresholds['Net Income']}.")
    else:
        feedback.append(f"❌ Net Income is {metrics['Net Income']}, which is negative, indicating more expenses than revenue.")

    # Operating Margin
    if metrics["Operating Margin"] >= thresholds["Operating Margin"]:
        industry_score += 1
        feedback.append(f"✅ Operating Margin is {metrics['Operating Margin']}, which meets or exceeds the threshold of {thresholds['Operating Margin']}.")
    else:
        feedback.append(f"❌ Operating Margin is {metrics['Operating Margin']}, below the threshold of {thresholds['Operating Margin']}.")

    # Expense-to-Revenue Ratio (lower is better)
    if metrics["Expense-to-Revenue Ratio"] <= thresholds["Expense-to-Revenue Ratio"]:
        industry_score += 1
        feedback.append(f"✅ Expense-to-Revenue Ratio is {metrics['Expense-to-Revenue Ratio']}, which is within the acceptable range (threshold is {thresholds['Expense-to-Revenue Ratio']}).")
    else:
        feedback.append(f"❌ Expense-to-Revenue Ratio is {metrics['Expense-to-Revenue Ratio']}, exceeding the threshold of {thresholds['Expense-to-Revenue Ratio']}.")

    # Revenue Growth Rate
    if metrics["Revenue Growth Rate"] >= thresholds["Revenue Growth Rate"]:
        industry_score += 1
        feedback.append(f"✅ Revenue Growth Rate is {metrics['Revenue Growth Rate']}%, which exceeds the threshold of {thresholds['Revenue Growth Rate']}%.")
    else:
        feedback.append(f"❌ Revenue Growth Rate is {metrics['Revenue Growth Rate']}%, below the threshold.")

    # Cash Flow Volatility (lower is better)
    if metrics["Cash Flow Volatility"] <= thresholds["Cash Flow Volatility"]:
        industry_score += 1
        feedback.append(f"✅ Cash Flow Volatility is {metrics['Cash Flow Volatility']}, which is stable (threshold is {thresholds['Cash Flow Volatility']}).")
    else:
        feedback.append(f"❌ Cash Flow Volatility is {metrics['Cash Flow Volatility']}, indicating instability.")

    # Gross Burn Rate (lower is better)
    if metrics["Gross Burn Rate"] <= thresholds["Gross Burn Rate"]:
        industry_score += 1
        feedback.append(f"✅ Gross Burn Rate is {metrics['Gross Burn Rate']}, which is below the threshold of {thresholds['Gross Burn Rate']}.")
    else:
        feedback.append(f"❌ Gross Burn Rate is {metrics['Gross Burn Rate']}, which is too high.")

    # Company Age (Months) — passed manually
    if company_age_months >= months_threshold:
        industry_score += 1
        feedback.append(f"✅ Company Age is {company_age_months} months, meeting the threshold of {months_threshold} months.")
    else:
        feedback.append(f"❌ Company Age is {company_age_months} months, which is below the threshold.")

    # Directors Score
    if directors_score >= thresholds["Directors Score"]:
        industry_score += 1
        feedback.append(f"✅ Directors Score is {directors_score}, meeting the threshold of {thresholds['Directors Score']}.")
    else:
        feedback.append(f"❌ Directors Score is {directors_score}, which is below the threshold of {thresholds['Directors Score']}.")

    # Sector Risk (lower is better, 0 is low risk, 1 is high risk)
    if sector_risk == 0:
        industry_score += 1
        feedback.append("✅ Sector Risk is low.")
    else:
        feedback.append("❌ Sector Risk is high.")

    # Average Month-End Balance
    if "Average Month-End Balance" in metrics and "Average Month-End Balance" in thresholds:
        if metrics["Average Month-End Balance"] >= thresholds["Average Month-End Balance"]:
            industry_score += 1
            feedback.append(
                f"✅ Average Month-End Balance is {metrics['Average Month-End Balance']}, meeting the threshold of {thresholds['Average Month-End Balance']}."
            )
        else:
            feedback.append(
                f"❌ Average Month-End Balance is {metrics['Average Month-End Balance']}, below the threshold of {thresholds['Average Month-End Balance']}."
            )

    # Average Negative Balance Days per Month
    if "Average Negative Balance Days per Month" in metrics and "Average Negative Balance Days per Month" in thresholds:
        if metrics["Average Negative Balance Days per Month"] <= thresholds["Average Negative Balance Days per Month"]:
            industry_score += 1
            feedback.append(
                f"✅ Average Negative Balance Days per Month is {metrics['Average Negative Balance Days per Month']}, within the acceptable limit of {thresholds['Average Negative Balance Days per Month']}."
            )
        else:
            feedback.append(
                f"❌ Average Negative Balance Days per Month is {metrics['Average Negative Balance Days per Month']}, which exceeds the threshold of {thresholds['Average Negative Balance Days per Month']}."
            )

    # Number of Bounced Payments
    if "Number of Bounced Payments" in metrics and "Number of Bounced Payments" in thresholds:
        if metrics["Number of Bounced Payments"] <= thresholds["Number of Bounced Payments"]:
            industry_score += 1
            feedback.append(
                f"✅ Number of Bounced Payments is {metrics['Number of Bounced Payments']}, which is within the acceptable threshold of {thresholds['Number of Bounced Payments']}."
            )
        else:
            feedback.append(
                f"❌ Number of Bounced Payments is {metrics['Number of Bounced Payments']}, which exceeds the threshold of {thresholds['Number of Bounced Payments']}."
            )

    # Display the feedback as a list
    st.write("### Scoring Breakdown:")
    for line in feedback:
        st.write(line)

    return industry_score
