# Business Finance Application Scorecard

This Streamlit-based application is designed to analyse business bank transactions and evaluate loan applications by calculating repayment probability and financial health using a logistic regression model.

---

## 🔑 Key Features

- Upload transaction data (JSON from Plaid or manual upload)
- Automatically categorises revenue, expenses, loans, and debt repayments
- Computes financial metrics including:
  - Debt Service Coverage Ratio (DSCR)
  - Net Income
  - Operating Margin
  - Revenue Growth Rate
  - Cash Flow Volatility
  - Gross Burn Rate
  - Average Month-End Balance
  - Average Negative Balance Days
  - Number of Bounced Payments
- Generates:
  - Weighted Score (based on sector-specific thresholds)
  - Repayment Probability (from trained ML model)
  - Industry Score (threshold checks)
  - Loan Risk Classification (based on requested amount vs revenue)
- Includes anomaly and pattern visualisations (pre/post loan expenses, inflows vs outflows)

---

## 🏗️ File Structure

├── app.py # Main Streamlit app
├── analysis.py # Financial plots and visualisations
├── config.py # Industry thresholds, weights, penalty definitions
├── daily_transactions_loader.py # Upload & preprocess JSON transaction files
├── data_processing.py # JSON normalisation, transaction categorisation
├── extract_scaler_info.py # Inspect scaler used in model
├── financial_metrics.py # Core metric computations
├── model_utils.py # Predict repayment probability using model
├── plaid_config.py # Connects to Plaid API
├── score_calculation.py # Weighted and binary scoring functions
├── model.pkl # Trained logistic regression model
├── scaler.pkl # StandardScaler used for model input
├── requirements.txt # All Python dependencies


---

## ⚙️ Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt

streamlit run app.py

{
  "accounts": [...],
  "transactions": [...]
}

📊 Output Scores Explained
Weighted Score – Custom score out of 100 based on financial metrics, sector, director score, company age, and penalties

Repayment Probability – ML-predicted probability of repayment using logistic regression

Industry Score – Number of thresholds met across key financial metrics

Loan Risk – Classification from Low to High Risk based on the loan amount vs monthly revenue

🛑 Risk Flags & Penalties
Negative adjustments may apply for:

Personal or business CCJs

Recent credit defaults

Weak online presence

Use of generic email domains



