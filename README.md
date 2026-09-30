# SMART FINANCE HUB
### Calculate. Compare. Plan. Grow.
**A Presentation-Ready Personal Banking & Finance Comparison Platform**

---

## 📌 Executive Summary

**Smart Finance Hub** is a decision companion for Indian retail banking and personal finance. It goes far beyond a conventional EMI calculator by providing:
1. Multi-bank benchmark comparison across **9 major Indian banks** (SBI, HDFC Bank, ICICI Bank, Axis Bank, Kotak Mahindra Bank, Bank of Baroda, Punjab National Bank, Canara Bank, and Union Bank of India).
2. Advanced loan tools including prepayment simulations, tenure sensitivity, and total cost decomposition.
3. An **Educational Loan Health Score (0–100)** evaluating debt-to-income and cash reserves.
4. A visual **Loan Journey Milestone Tracker** mapping loan progress down to ₹0.
5. Fixed Deposit maturity modeling (Cumulative, Monthly, and Quarterly payout modes) with premature penalty calculations and an **FD Laddering Strategy**.
6. Balance-slab savings account modeling and a visual **Savings Goal Tracker**.
7. Distinct transaction limit comparisons (ATM, UPI, IMPS, NEFT, RTGS, Cash Deposit, and POS Spends).
8. A universal **Product A vs. Product B** comparison engine.
9. Interactive **Plotly** visual analytics.
10. One-click **Excel (.xlsx)** and **CSV** export center with multi-tab formatted workbooks.

---

## 🏗️ Project Structure

```
smart_finance_hub/
│
├── app.py                  # Main Streamlit application & interactive UI
├── calculations.py         # Financial mathematics, compounding formulas & formatters
├── data_loader.py          # Cached data layer, filtering queries & Excel generator
├── ui_components.py        # Light-mode FinTech design system, CSS & widgets
├── requirements.txt        # Python package dependencies
├── README.md               # Documentation & presentation walkthrough guide
│
└── data/                   # Verified bank datasets (easy to update)
    ├── fd_rates.csv        # Fixed deposit rates across tenure brackets & senior citizen slabs
    ├── savings_rates.csv   # Savings account interest rates, tiers & AMB requirements
    ├── bank_accounts.csv   # Separate ATM, UPI, IMPS, NEFT, RTGS, Cash limits & charges
    └── loan_rates.csv      # Benchmark-linked lending rates (EBLR/RLLR) & processing fees
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
Ensure Python 3.10+ is installed on your system.

### 2. Clone or Navigate to the Directory
```bash
cd "d:/Python adv itt/Presentation"
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🎯 Step-by-Step Presentation Walkthrough

Follow this 20-step flow for demonstrations and evaluations:

1. **Dashboard Launch**: Open `http://localhost:8501`. Notice the light-mode UI, gradient hero banner, verified bank data status, and 4 capability cards.
2. **Review Snapshot Metrics**: View the dynamic cards for *Monthly EMI*, *Total Interest*, *FD Maturity*, *Savings Growth*, and *Goal Progress*.
3. **Navigate to Loans**: Click **💳 Loans** in the sidebar.
4. **Calculate Loan**: Under **1. EMI Calculator**, review the pre-populated ₹5,00,000 loan at 8.5% for 5 years. View the calculated Monthly EMI (₹10,258), Total Interest, and Total Cost.
5. **Inspect Bonus Widgets**:
   - Check the **Educational Loan Health Score** (e.g. `89 / 100 🟢 EXCELLENT`) with breakdown of EMI burden, existing debt, savings buffer, and emergency reserves.
6. **Amortization Schedule**: Open **2. Amortization Schedule**, switch between *Monthly Schedule* and *Year-wise Summary*, and inspect the interactive Plotly principal vs. interest chart.
7. **Rate Comparison & Detailed Scheme Breakdown**: Open **3. Rate Comparison**, select any category (e.g. *Home Loan*, *Personal Loan*). Click on any bank row (e.g., **State Bank of India**) or select from the dropdown to instantly view its detailed **Repayment Schedule**, **Yearly EMI Pay**, **Interest Paid (Inter Pay)**, and year-by-year principal vs. interest charts.
8. **Prepayment Simulator**: Open **4. Prepayment Simulator**, enter a lump-sum of ₹1,00,000 at Month 12, and see interest savings (₹34,000+) and 13 months saved off the loan duration.
9. **Affordability Analysis**: Open **5. Affordability**, check the FOIR percentage and disposable income donut chart.
10. **What-If Simulator**: Open **6. What-If Simulator**, move the sliders for loan amount, rate, and tenure to see immediate sensitivity updates.
11. **Total Cost Breakdown**: Open **8. Total Cost Breakdown** to see the interactive donut chart dividing principal, interest, and processing fees.
12. **EMI vs. Tenure**: Open **9. EMI vs Tenure** to compare 3, 5, 7, and 10-year repayment commitments.
13. **Download Reports**: Open **10. Reports & Export**, download the complete **Excel (.xlsx)** multi-tab workbook and CSV amortization schedule.
14. **Navigate to Fixed Deposits**: Click **💰 Fixed Deposits** in the sidebar.
15. **Multi-Bank FD Comparison**: Under **1. Multi-Bank Comparison**, view the bar charts and table comparing maturity values across all 9 banks for ₹5,00,000.
16. **FD Ladder Calculator**: Open **7. FD Ladder Calculator**, view the 5-year laddering strategy splitting capital with staggered annual liquidity and timeline visualization.
17. **Navigate to Savings**: Click **💵 Savings** in the sidebar. Set a financial milestone in **3. Savings Goal Tracker** and view the real-time progress bar.
18. **Navigate to Bank Accounts**: Click **🏦 Bank Accounts** in the sidebar. Apply smart filters (e.g., *Low Min Balance*, *High ATM Limit*) and view accounts matching criteria. Note separate limits for ATM, UPI, IMPS, NEFT, RTGS, and Cash deposits.
19. **Universal Comparison**: Click **⚔️ Compare** in the sidebar. Select *Product A vs Product B* across Loans, FDs, Savings, or Bank Accounts to view side-by-side differences.
20. **Interactive Analytics**: Click **📊 Analytics** to demonstrate the unified Plotly dashboard.

---

## 🏛️ Updating Bank Rates & Charges

All institutional bank data is decoupled from the user interface logic. To update data when the RBI revises the repo rate or banks change fees:

1. **`data/fd_rates.csv`**:
   - `Bank`: Institution name
   - `Product`: Scheme / deposit title
   - `Tenure_Days_Min` / `Tenure_Days_Max`: Duration boundaries
   - `General_Rate`: Rate for standard depositors (%)
   - `Senior_Citizen_Rate`: Rate for senior citizens (%)
   - `Premature_Withdrawal_Penalty`: Penalty guidelines
   - `Source_URL`: Official web source link

2. **`data/savings_rates.csv`**:
   - `Balance_Slab`: Balance tier (e.g., Up to ₹10 Crore)
   - `Interest_Rate`: Annual savings rate (%)
   - `Minimum_Balance_Metro`: Minimum Average Monthly Balance (AMB)

3. **`data/bank_accounts.csv`**:
   - Separate columns for `ATM_Limit_Per_Day`, `UPI_Limit_Per_Day`, `IMPS_Limit_Per_Day`, `NEFT_Limit_Per_Day`, `RTGS_Limit_Per_Day`, `Cash_Deposit_Limit_Free`, and `Debit_Card_Annual_Fee`.

4. **`data/loan_rates.csv`**:
   - Minimum and maximum benchmark-linked rates (EBLR/RLLR) and processing fee caps.

Streamlit automatically refreshes cached data when CSV files are modified.

---

## ⚖️ Legal & Educational Disclaimer

*Rates and charges displayed in this application are benchmarked from official publicly available bank portals as of **September 2024**. They are indicative and subject to change based on RBI monetary policies, individual credit underwriting, and institutional revisions. This application is developed strictly for educational, illustrative, and comparative purposes and does not constitute chartered financial advice.*
