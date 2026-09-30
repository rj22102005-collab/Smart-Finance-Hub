"""
SMART FINANCE HUB - Data Layer & Loader
========================================
Centralized data access module:
- Reads structured CSVs from the data/ directory
- Provides cached DataFrames to Streamlit
- Includes robust in-memory fallbacks if files are missing
- Contains filtering helpers and Excel/CSV export functions
"""

import os
import io
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
import openpyxl.styles as styles
import streamlit as st
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

DISCLAIMER_TEXT = (
    "Rates and charges are indicative and subject to change. Please verify with the official "
    "bank website before making financial decisions."
)

LAST_UPDATED_LABEL = "September 2024"


# ==============================================================================
# 1. CACHED CSV LOADERS
# ==============================================================================

@st.cache_data(show_spinner=False)
def load_fd_rates() -> pd.DataFrame:
    """Loads FD interest rates for all benchmarked banks."""
    file_path = os.path.join(DATA_DIR, "fd_rates.csv")
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Ensure proper numeric typing
            df["General_Rate"] = pd.to_numeric(df["General_Rate"], errors="coerce")
            df["Senior_Citizen_Rate"] = pd.to_numeric(df["Senior_Citizen_Rate"], errors="coerce")
            df["Minimum_Deposit"] = pd.to_numeric(df["Minimum_Deposit"], errors="coerce").fillna(1000)
            return df
    except Exception as e:
        st.warning(f"Note: Loading default FD dataset (File error: {e})")
    
    # Return minimal fallback
    return pd.DataFrame([
        {"Bank": "State Bank of India", "Product": "SBI Regular Term Deposit", "Tenure_Category": "1 Year to 2 Years",
         "Tenure_Days_Min": 365, "Tenure_Days_Max": 729, "General_Rate": 6.80, "Senior_Citizen_Rate": 7.30,
         "Minimum_Deposit": 1000, "Compounding_Frequency": "Quarterly", "Premature_Withdrawal_Penalty": "0.50% - 1.00%",
         "Effective_Date": "2024-06-15", "Last_Updated": LAST_UPDATED_LABEL, "Source_URL": "https://sbi.co.in"}
    ])


@st.cache_data(show_spinner=False)
def load_savings_rates() -> pd.DataFrame:
    """Loads savings account interest rates and balance slabs."""
    file_path = os.path.join(DATA_DIR, "savings_rates.csv")
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["Interest_Rate"] = pd.to_numeric(df["Interest_Rate"], errors="coerce")
            df["Minimum_Balance_Metro"] = pd.to_numeric(df["Minimum_Balance_Metro"], errors="coerce").fillna(0)
            df["Minimum_Balance_Rural"] = pd.to_numeric(df["Minimum_Balance_Rural"], errors="coerce").fillna(0)
            return df
    except Exception as e:
        st.warning(f"Note: Loading default Savings dataset (File error: {e})")

    return pd.DataFrame([
        {"Bank": "State Bank of India", "Product": "SBI Regular Savings Account", "Balance_Slab": "Up to Rs 10 Crore",
         "Interest_Rate": 2.70, "Interest_Calculation_Basis": "Daily Product", "Credit_Frequency": "Quarterly",
         "Minimum_Balance_Metro": 0, "Minimum_Balance_Rural": 0, "Non_Maintenance_Charge": "Zero",
         "Effective_Date": "2020-05-31", "Last_Updated": LAST_UPDATED_LABEL, "Source_URL": "https://sbi.co.in"}
    ])


@st.cache_data(show_spinner=False)
def load_bank_accounts() -> pd.DataFrame:
    """Loads detailed bank account features, limits, and charges."""
    file_path = os.path.join(DATA_DIR, "bank_accounts.csv")
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["Minimum_Balance_Metro"] = pd.to_numeric(df["Minimum_Balance_Metro"], errors="coerce").fillna(0)
            df["ATM_Limit_Per_Day"] = pd.to_numeric(df["ATM_Limit_Per_Day"], errors="coerce").fillna(25000)
            df["UPI_Limit_Per_Day"] = pd.to_numeric(df["UPI_Limit_Per_Day"], errors="coerce").fillna(100000)
            df["IMPS_Limit_Per_Day"] = pd.to_numeric(df["IMPS_Limit_Per_Day"], errors="coerce").fillna(500000)
            df["POS_Debit_Card_Limit"] = pd.to_numeric(df["POS_Debit_Card_Limit"], errors="coerce").fillna(50000)
            return df
    except Exception as e:
        st.warning(f"Note: Loading default Bank Accounts dataset (File error: {e})")

    return pd.DataFrame([
        {"Bank": "State Bank of India", "Account_Name": "SBI Regular Savings Account", "Account_Type": "Regular Savings",
         "Opening_Charges": "0", "Minimum_Balance_Metro": 0, "Annual_Maintenance_Fee": "0", "Debit_Card_Annual_Fee": "125 + GST",
         "ATM_Limit_Per_Day": 40000, "UPI_Limit_Per_Day": 100000, "IMPS_Limit_Per_Day": 500000, "NEFT_Limit_Per_Day": "No Limit",
         "RTGS_Limit_Per_Day": "No Limit", "Cash_Deposit_Limit_Free": "3 free deposits/mo",
         "Cash_Withdrawal_Charges": "Rs 50 + GST beyond free", "POS_Debit_Card_Limit": 75000,
         "Digital_Banking": "Yes", "Mobile_Banking": "Yes", "Net_Banking": "Yes",
         "Effective_Date": "2024-04-01", "Last_Updated": LAST_UPDATED_LABEL, "Source_URL": "https://sbi.co.in"}
    ])


@st.cache_data(show_spinner=False)
def load_loan_rates() -> pd.DataFrame:
    """Loads benchmark loan interest rates and fees across lenders."""
    file_path = os.path.join(DATA_DIR, "loan_rates.csv")
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df["Min_Rate"] = pd.to_numeric(df["Min_Rate"], errors="coerce")
            df["Max_Rate"] = pd.to_numeric(df["Max_Rate"], errors="coerce")
            df["Processing_Fee_Percentage"] = pd.to_numeric(df["Processing_Fee_Percentage"], errors="coerce").fillna(0.5)
            df["Processing_Fee_Min"] = pd.to_numeric(df["Processing_Fee_Min"], errors="coerce").fillna(0)
            df["Processing_Fee_Max"] = pd.to_numeric(df["Processing_Fee_Max"], errors="coerce").fillna(10000)
            return df
    except Exception as e:
        st.warning(f"Note: Loading default Loan Rates dataset (File error: {e})")

    return pd.DataFrame([
        {"Bank": "State Bank of India", "Loan_Category": "Home Loan", "Product_Name": "SBI Regular Home Loan",
         "Min_Rate": 8.50, "Max_Rate": 9.65, "Benchmark_Linked": "EBR / EBLR", "Processing_Fee_Percentage": 0.35,
         "Processing_Fee_Min": 2000, "Processing_Fee_Max": 10000, "Min_Tenure_Years": 1, "Max_Tenure_Years": 30,
         "Effective_Date": "2024-05-01", "Last_Updated": LAST_UPDATED_LABEL, "Source_URL": "https://sbi.co.in"}
    ])


# ==============================================================================
# 2. FILTERING & COMPARISON HELPERS
# ==============================================================================

def get_best_fd_rate_for_bank(bank_name: str, tenure_days: int, customer_type: str = "General") -> float:
    """
    Finds the applicable FD interest rate for a given bank and tenure in days.
    """
    df = load_fd_rates()
    bank_df = df[df["Bank"] == bank_name]
    if bank_df.empty:
        return 7.0 if customer_type == "General" else 7.5

    # Check exact matching range
    match = bank_df[(bank_df["Tenure_Days_Min"] <= tenure_days) & (bank_df["Tenure_Days_Max"] >= tenure_days)]
    rate_col = "Senior_Citizen_Rate" if customer_type == "Senior Citizen" else "General_Rate"

    if not match.empty:
        return float(match.iloc[0][rate_col])

    # If no exact match, find closest range
    closest_idx = (bank_df["Tenure_Days_Min"] - tenure_days).abs().idxmin()
    return float(bank_df.loc[closest_idx, rate_col])


def get_all_bank_fd_comparison(principal: float, tenure_days: int, customer_type: str = "General", payout_type: str = "Cumulative"):
    """
    Returns a comparison DataFrame across all banks for a specific tenure.
    """
    from calculations import calculate_fd_maturity

    fd_df = load_fd_rates()
    banks = fd_df["Bank"].unique()
    rows = []

    for b in banks:
        rate = get_best_fd_rate_for_bank(b, tenure_days, customer_type)
        calc = calculate_fd_maturity(principal, rate, tenure_days=tenure_days, payout_type=payout_type)
        
        # Grab source url
        sample_row = fd_df[fd_df["Bank"] == b].iloc[0]
        source_url = sample_row.get("Source_URL", "")

        rows.append({
            "Bank": b,
            "Interest_Rate": rate,
            "Investment": principal,
            "Interest_Earned": calc["interest_earned"],
            "Maturity_Amount": calc["maturity_amount"],
            "Periodic_Payout": calc["periodic_payout"],
            "Effective_Yield": calc["effective_yield"],
            "Source_URL": source_url
        })

    comp_df = pd.DataFrame(rows)
    comp_df.sort_values(by="Maturity_Amount", ascending=False, inplace=True)
    comp_df.reset_index(drop=True, inplace=True)
    return comp_df


def filter_bank_accounts(low_balance: bool = False,
                         low_charges: bool = False,
                         high_atm_limit: bool = False,
                         high_upi_limit: bool = False,
                         digital_only: bool = False,
                         account_type_filter: list = None) -> pd.DataFrame:
    """
    Applies multi-criteria smart filtering to bank accounts dataset.
    """
    df = load_bank_accounts().copy()

    if account_type_filter and len(account_type_filter) > 0 and "All" not in account_type_filter:
        df = df[df["Account_Type"].isin(account_type_filter)]

    if low_balance:
        # Zero balance or max ₹2,000
        df = df[df["Minimum_Balance_Metro"] <= 2000]

    if low_charges:
        # Debit card fee <= ₹150
        df = df[df["Debit_Card_Annual_Fee"].str.contains("0|125|150|Free|Waived", case=False, na=False)]

    if high_atm_limit:
        df = df[df["ATM_Limit_Per_Day"] >= 40000]

    if high_upi_limit:
        df = df[df["UPI_Limit_Per_Day"] >= 100000]

    if digital_only:
        df = df[df["Account_Type"] == "Digital Savings"]

    return df


# ==============================================================================
# 3. EXCEL / CSV REPORT GENERATOR
# ==============================================================================

def generate_excel_download(dataframes_dict: dict, report_title: str = "Smart Finance Hub Report") -> bytes:
    """
    Creates a professionally formatted Excel workbook with multiple tabs using openpyxl.
    dataframes_dict format: {"Sheet_Name": df, ...}
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, df in dataframes_dict.items():
            # Clean sheet name (max 31 chars)
            clean_name = sheet_name[:31]
            df.to_excel(writer, sheet_name=clean_name, index=False)

            workbook = writer.book
            worksheet = writer.sheets[clean_name]

            # Style header row
            import openpyxl.styles as styles
            header_fill = styles.PatternFill(start_color="0F4C81", end_color="0F4C81", fill_type="solid")
            header_font = styles.Font(color="FFFFFF", bold=True, name="Calibri", size=11)
            thin_border = styles.Border(
                left=styles.Side(style='thin', color='DDDDDD'),
                right=styles.Side(style='thin', color='DDDDDD'),
                top=styles.Side(style='thin', color='DDDDDD'),
                bottom=styles.Side(style='thin', color='DDDDDD')
            )

            for col_idx, col in enumerate(worksheet.columns, start=1):
                cell = col[0]
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = styles.Alignment(horizontal="center", vertical="center")

                # Auto fit column widths
                max_len = max(len(str(c.value or "")) for c in col)
                col_letter = openpyxl.utils.get_column_letter(col_idx)
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

                # Add light border to cells
                for c in col[1:]:
                    c.border = thin_border

    output.seek(0)
    return output.getvalue()


def generate_csv_download(df: pd.DataFrame) -> bytes:
    """Converts a DataFrame into downloadable CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")
