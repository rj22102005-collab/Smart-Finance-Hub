"""
SMART FINANCE HUB - Financial Calculations Engine
==================================================
Clean, precise, validated financial mathematics for:
1. Loan EMI, Amortization, What-If, and Total Cost
2. Prepayment simulation (tenure reduction vs EMI reduction)
3. Loan Affordability & Educational Loan Health Score
4. Fixed Deposit maturity (Cumulative, Monthly, Quarterly), TDS & Laddering
5. Savings account compounding & Goal Tracker
6. Indian currency formatting (INR ₹)
"""

import math
import pandas as pd
import numpy as np
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


# ==============================================================================
# 1. CURRENCY & NUMBER FORMATTING (INDIAN SYSTEM)
# ==============================================================================

def format_inr(value, decimals=0, symbol="₹"):
    """
    Formats a number according to the Indian number system (Lakhs, Crores).
    Example:
        format_inr(500000) -> "₹5,00,000"
        format_inr(12345678) -> "₹1,23,45,678"
        format_inr(-1500) -> "-₹1,500"
    """
    if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
        return f"{symbol}0"
    
    try:
        num = float(value)
    except (ValueError, TypeError):
        return f"{symbol}0"

    is_negative = num < 0
    num = abs(num)

    if decimals > 0:
        formatted_dec = f"{num:.{decimals}f}".split(".")[1]
    else:
        formatted_dec = ""

    int_part = int(round(num)) if decimals == 0 else int(num)
    s = str(int_part)

    if len(s) <= 3:
        res = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        chunks = []
        while len(remaining) > 2:
            chunks.append(remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            chunks.append(remaining)
        res = ",".join(reversed(chunks)) + "," + last3

    if decimals > 0 and formatted_dec:
        res = f"{res}.{formatted_dec}"

    sign = "-" if is_negative else ""
    return f"{sign}{symbol}{res}"


def format_inr_compact(value, symbol="₹"):
    """
    Compact readable format for large Indian numbers:
    100000 -> ₹1.00 Lakh
    15000000 -> ₹1.50 Cr
    """
    if value is None or (isinstance(value, float) and (np.isnan(value) or np.isinf(value))):
        return f"{symbol}0"
    try:
        num = float(value)
    except (ValueError, TypeError):
        return f"{symbol}0"

    is_negative = num < 0
    num = abs(num)
    sign = "-" if is_negative else ""

    if num >= 1e7:
        return f"{sign}{symbol}{num / 1e7:.2f} Cr"
    elif num >= 1e5:
        return f"{sign}{symbol}{num / 1e5:.2f} Lakh"
    elif num >= 1e3:
        return f"{sign}{symbol}{num / 1e3:.1f}k"
    else:
        return f"{sign}{symbol}{num:.0f}"


# ==============================================================================
# 2. LOAN CALCULATIONS
# ==============================================================================

def calculate_emi(principal, annual_rate, tenure_years=0, tenure_months=0,
                  processing_fee_pct=0.0, processing_fee_flat=0.0, other_charges=0.0):
    """
    Standard Equated Monthly Installment (EMI) Formula:
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    Handles zero rate, zero tenure, and processing fee.
    """
    principal = max(0.0, float(principal))
    annual_rate = max(0.0, float(annual_rate))
    total_months = int(tenure_years * 12 + tenure_months)

    if principal <= 0 or total_months <= 0:
        return {
            "emi": 0.0,
            "principal": principal,
            "total_interest": 0.0,
            "total_payment": 0.0,
            "processing_fee": 0.0,
            "other_charges": float(other_charges),
            "total_cost": float(other_charges),
            "interest_ratio": 0.0,
            "months": total_months
        }

    monthly_rate = (annual_rate / 100.0) / 12.0

    if monthly_rate == 0:
        emi = principal / total_months
        total_interest = 0.0
    else:
        factor = math.pow(1.0 + monthly_rate, total_months)
        emi = principal * monthly_rate * factor / (factor - 1.0)
        total_payment = emi * total_months
        total_interest = max(0.0, total_payment - principal)

    total_payment = emi * total_months
    proc_fee = (principal * (processing_fee_pct / 100.0)) + processing_fee_flat
    total_cost = total_payment + proc_fee + other_charges
    interest_ratio = (total_interest / total_cost * 100.0) if total_cost > 0 else 0.0

    return {
        "emi": emi,
        "principal": principal,
        "total_interest": total_interest,
        "total_payment": total_payment,
        "processing_fee": proc_fee,
        "other_charges": float(other_charges),
        "total_cost": total_cost,
        "interest_ratio": interest_ratio,
        "months": total_months
    }


def generate_amortization_schedule(principal, annual_rate, tenure_months, start_date=None):
    """
    Generates monthly and year-wise amortization schedules.
    """
    principal = max(0.0, float(principal))
    annual_rate = max(0.0, float(annual_rate))
    tenure_months = int(tenure_months)

    if principal <= 0 or tenure_months <= 0:
        empty_monthly = pd.DataFrame(columns=[
            "Month", "Payment_Date", "Opening_Balance", "EMI",
            "Principal_Repaid", "Interest_Paid", "Closing_Balance",
            "Cumulative_Principal", "Cumulative_Interest"
        ])
        empty_yearly = pd.DataFrame(columns=[
            "Year", "Opening_Balance", "Total_EMI",
            "Principal_Repaid", "Interest_Paid", "Closing_Balance"
        ])
        return empty_monthly, empty_yearly

    calc = calculate_emi(principal, annual_rate, tenure_months=tenure_months)
    emi = calc["emi"]
    monthly_rate = (annual_rate / 100.0) / 12.0

    if start_date is None:
        start_date = date.today()

    rows = []
    opening = principal
    cum_principal = 0.0
    cum_interest = 0.0

    for m in range(1, tenure_months + 1):
        pay_date = start_date + relativedelta(months=m - 1)
        interest_comp = opening * monthly_rate
        principal_comp = emi - interest_comp

        # Adjust for last month rounding
        if m == tenure_months or principal_comp > opening:
            principal_comp = opening
            emi_actual = principal_comp + interest_comp
            closing = 0.0
        else:
            emi_actual = emi
            closing = max(0.0, opening - principal_comp)

        cum_principal += principal_comp
        cum_interest += interest_comp

        rows.append({
            "Month": m,
            "Payment_Date": pay_date.strftime("%b %Y"),
            "Opening_Balance": round(opening, 2),
            "EMI": round(emi_actual, 2),
            "Principal_Repaid": round(principal_comp, 2),
            "Interest_Paid": round(interest_comp, 2),
            "Closing_Balance": round(closing, 2),
            "Cumulative_Principal": round(cum_principal, 2),
            "Cumulative_Interest": round(cum_interest, 2)
        })

        opening = closing
        if opening <= 0:
            break

    monthly_df = pd.DataFrame(rows)

    # Generate Yearly summary
    monthly_df["Year_Num"] = ((monthly_df["Month"] - 1) // 12) + 1
    yearly_rows = []
    for y, group in monthly_df.groupby("Year_Num"):
        yearly_rows.append({
            "Year": f"Year {y}",
            "Opening_Balance": group.iloc[0]["Opening_Balance"],
            "Total_EMI": round(group["EMI"].sum(), 2),
            "Principal_Repaid": round(group["Principal_Repaid"].sum(), 2),
            "Interest_Paid": round(group["Interest_Paid"].sum(), 2),
            "Closing_Balance": group.iloc[-1]["Closing_Balance"]
        })
    yearly_df = pd.DataFrame(yearly_rows)
    monthly_df.drop(columns=["Year_Num"], inplace=True)

    return monthly_df, yearly_df


def simulate_prepayment(principal, annual_rate, tenure_months, current_month,
                        prepayment_amount, prepayment_mode="reduce_tenure"):
    """
    Simulates the impact of a lump-sum prepayment at a specific month.
    Modes:
      - 'reduce_tenure': Keep EMI same, shorten loan duration.
      - 'reduce_emi': Keep remaining tenure same, reduce monthly EMI.
    """
    principal = float(principal)
    annual_rate = float(annual_rate)
    tenure_months = int(tenure_months)
    current_month = min(int(current_month), tenure_months - 1)
    prepayment_amount = float(prepayment_amount)

    base_monthly, _ = generate_amortization_schedule(principal, annual_rate, tenure_months)
    base_emi = base_monthly.iloc[0]["EMI"] if not base_monthly.empty else 0.0
    base_total_interest = base_monthly["Interest_Paid"].sum() if not base_monthly.empty else 0.0
    base_total_payment = base_monthly["EMI"].sum() if not base_monthly.empty else 0.0

    if current_month <= 0 or current_month >= len(base_monthly):
        balance_at_event = principal
    else:
        balance_at_event = base_monthly.iloc[current_month - 1]["Closing_Balance"]

    # Cap prepayment to balance
    actual_prepayment = min(prepayment_amount, balance_at_event)
    revised_balance = max(0.0, balance_at_event - actual_prepayment)

    monthly_rate = (annual_rate / 100.0) / 12.0
    remaining_months = tenure_months - current_month

    if revised_balance <= 0:
        revised_months = current_month
        revised_emi = 0.0
        interest_after = 0.0
        months_saved = tenure_months - current_month
        new_schedule = base_monthly.iloc[:current_month].copy()
    elif prepayment_mode == "reduce_tenure":
        # Keep EMI identical to base_emi
        if monthly_rate == 0:
            months_left = math.ceil(revised_balance / base_emi)
        else:
            # Solve for n: P * r / (1 - (1+r)^-n) = EMI
            # 1 - P*r/EMI = (1+r)^-n
            denom = 1.0 - (revised_balance * monthly_rate / base_emi)
            if denom <= 0:
                months_left = remaining_months
            else:
                months_left = math.ceil(-math.log(denom) / math.log(1.0 + monthly_rate))

        months_saved = max(0, remaining_months - months_left)
        revised_months = current_month + months_left
        revised_emi = base_emi

        # Build revised amortization schedule
        head = base_monthly.iloc[:current_month].copy()
        tail, _ = generate_amortization_schedule(revised_balance, annual_rate, months_left)
        tail["Month"] = tail["Month"] + current_month
        new_schedule = pd.concat([head, tail], ignore_index=True)
    else:
        # Prepayment mode: reduce_emi
        calc = calculate_emi(revised_balance, annual_rate, tenure_months=remaining_months)
        revised_emi = calc["emi"]
        months_saved = 0
        revised_months = tenure_months

        head = base_monthly.iloc[:current_month].copy()
        tail, _ = generate_amortization_schedule(revised_balance, annual_rate, remaining_months)
        tail["Month"] = tail["Month"] + current_month
        new_schedule = pd.concat([head, tail], ignore_index=True)

    new_total_interest = new_schedule["Interest_Paid"].sum()
    interest_saved = max(0.0, base_total_interest - new_total_interest)
    new_total_payment = new_schedule["EMI"].sum() + actual_prepayment

    return {
        "base_emi": base_emi,
        "base_tenure_months": tenure_months,
        "base_total_interest": base_total_interest,
        "base_total_payment": base_total_payment,
        "actual_prepayment": actual_prepayment,
        "balance_before_prepayment": balance_at_event,
        "balance_after_prepayment": revised_balance,
        "revised_emi": revised_emi,
        "revised_tenure_months": revised_months,
        "months_saved": months_saved,
        "years_saved": round(months_saved / 12.0, 1),
        "interest_saved": interest_saved,
        "new_total_interest": new_total_interest,
        "new_total_payment": new_total_payment,
        "new_schedule": new_schedule,
        "base_schedule": base_monthly
    }


def calculate_affordability(monthly_income, existing_emis, monthly_expenses,
                            proposed_principal, annual_rate, tenure_years):
    """
    Educational / Illustrative Loan Affordability Calculator.
    FOIR = Fixed Obligation to Income Ratio
    """
    income = max(1.0, float(monthly_income))
    existing_debt = max(0.0, float(existing_emis))
    expenses = max(0.0, float(monthly_expenses))
    principal = max(0.0, float(proposed_principal))
    rate = max(0.0, float(annual_rate))
    tenure_m = max(1, int(tenure_years * 12))

    calc = calculate_emi(principal, rate, tenure_months=tenure_m)
    proposed_emi = calc["emi"]
    total_emi = existing_debt + proposed_emi
    foir_pct = (total_emi / income) * 100.0
    total_outflow = total_emi + expenses
    disposable_income = income - total_outflow

    # Recommended max EMI is usually 40% - 50% of net income
    max_recommended_emi = income * 0.40
    avail_emi_capacity = max(0.0, max_recommended_emi - existing_debt)

    # Reverse calculate max loan capacity for available EMI
    monthly_rate = (rate / 100.0) / 12.0
    if monthly_rate == 0:
        max_loan_capacity = avail_emi_capacity * tenure_m
    else:
        factor = math.pow(1.0 + monthly_rate, tenure_m)
        max_loan_capacity = avail_emi_capacity * (factor - 1.0) / (monthly_rate * factor)

    if foir_pct <= 35:
        status = "Comfortable"
        status_color = "#10b981"  # Emerald
        note = "Your total EMI obligation is well within the comfortable range (< 35% of income)."
    elif foir_pct <= 50:
        status = "Moderate / Manageable"
        status_color = "#f59e0b"  # Amber
        note = "Your debt obligations represent a substantial portion (35% - 50%) of your monthly income."
    else:
        status = "High Burden"
        status_color = "#ef4444"  # Rose
        note = "Total EMI exceeds 50% of monthly income. This poses a cash-flow risk in case of unforeseen emergencies."

    return {
        "monthly_income": income,
        "existing_emis": existing_debt,
        "monthly_expenses": expenses,
        "proposed_emi": proposed_emi,
        "total_emi": total_emi,
        "foir_pct": foir_pct,
        "disposable_income": disposable_income,
        "status": status,
        "status_color": status_color,
        "note": note,
        "max_recommended_emi": max_recommended_emi,
        "max_loan_capacity": max_loan_capacity
    }


def calculate_loan_health_score(monthly_income, existing_emis, proposed_emi,
                                monthly_expenses, savings_balance, emergency_fund_months):
    """
    Educational / Illustrative Loan Health Score (0 to 100).
    Explicitly labeled as an educational model, NOT a credit/CIBIL score.
    Breakdown:
      - EMI Burden (Max 30 pts)
      - Existing Debt Burden (Max 25 pts)
      - Monthly Savings Rate (Max 25 pts)
      - Emergency Fund Coverage (Max 20 pts)
    """
    income = max(1.0, float(monthly_income))
    existing = max(0.0, float(existing_emis))
    prop_emi = max(0.0, float(proposed_emi))
    expenses = max(0.0, float(monthly_expenses))
    total_emi = existing + prop_emi

    # 1. Total EMI Burden (30 points)
    emi_ratio = total_emi / income
    if emi_ratio <= 0.25:
        emi_score = 30
        emi_status = "✓ Low EMI Burden"
    elif emi_ratio <= 0.40:
        emi_score = 22
        emi_status = "✓ Moderate EMI Burden"
    elif emi_ratio <= 0.50:
        emi_score = 12
        emi_status = "⚠ Elevated EMI Burden"
    else:
        emi_score = 4
        emi_status = "✕ Heavy Debt Obligation"

    # 2. Existing Debt (25 points)
    existing_ratio = existing / income
    if existing_ratio == 0:
        debt_score = 25
        debt_status = "✓ Debt Free Prior"
    elif existing_ratio <= 0.15:
        debt_score = 20
        debt_status = "✓ Light Existing Debt"
    elif existing_ratio <= 0.30:
        debt_score = 12
        debt_status = "⚠ Notable Existing Debt"
    else:
        debt_score = 5
        debt_status = "✕ High Existing Debt"

    # 3. Monthly Savings / Buffer (25 points)
    surplus = income - (total_emi + expenses)
    savings_ratio = surplus / income
    if savings_ratio >= 0.25:
        savings_score = 25
        savings_status = "✓ Strong Savings Buffer (>25%)"
    elif savings_ratio >= 0.15:
        savings_score = 18
        savings_status = "✓ Adequate Savings Buffer"
    elif savings_ratio > 0:
        savings_score = 10
        savings_status = "⚠ Slim Savings Buffer"
    else:
        savings_score = 2
        savings_status = "✕ Deficit / Zero Savings"

    # 4. Emergency Fund Coverage (20 points)
    # Target: 6 months of expenses + EMIs
    monthly_burn = expenses + total_emi
    effective_months = (savings_balance / monthly_burn) if monthly_burn > 0 else emergency_fund_months
    effective_months = max(effective_months, emergency_fund_months)

    if effective_months >= 6.0:
        ef_score = 20
        ef_status = "✓ 6+ Months Emergency Cushion"
    elif effective_months >= 3.0:
        ef_score = 14
        ef_status = "✓ 3-5 Months Emergency Cushion"
    elif effective_months >= 1.0:
        ef_score = 8
        ef_status = "⚠ Minimal 1-2 Months Cushion"
    else:
        ef_score = 2
        ef_status = "✕ Negligible Emergency Fund"

    total_score = int(emi_score + debt_score + savings_score + ef_score)
    total_score = max(5, min(100, total_score))

    if total_score >= 80:
        grade = "EXCELLENT"
        badge_color = "#10b981"  # Emerald
        summary = "Your financial profile shows solid liquidity, healthy debt coverage, and a disciplined buffer."
    elif total_score >= 65:
        grade = "GOOD"
        badge_color = "#0284c7"  # Sky/Blue
        summary = "Well-balanced profile with manageable commitments. Maintain consistent savings discipline."
    elif total_score >= 50:
        grade = "MODERATE"
        badge_color = "#f59e0b"  # Amber
        summary = "Fair profile. Consider boosting your liquid emergency reserve or prepaying high-interest debt."
    else:
        grade = "NEEDS ATTENTION"
        badge_color = "#ef4444"  # Red
        summary = "Debt obligations are stretched relative to disposable income. High sensitivity to cash-flow shocks."

    return {
        "score": total_score,
        "grade": grade,
        "badge_color": badge_color,
        "summary": summary,
        "breakdown": {
            "emi_burden": {"score": emi_score, "max": 30, "status": emi_status},
            "existing_debt": {"score": debt_score, "max": 25, "status": debt_status},
            "savings": {"score": savings_score, "max": 25, "status": savings_status},
            "emergency_fund": {"score": ef_score, "max": 20, "status": ef_status}
        }
    }


def compare_tenures(principal, annual_rate, tenures_list=[3, 5, 7, 10]):
    """
    Compares loan metrics across standard tenure brackets.
    """
    records = []
    for yrs in tenures_list:
        calc = calculate_emi(principal, annual_rate, tenure_years=yrs)
        records.append({
            "Tenure": f"{yrs} Years ({yrs*12} Months)",
            "Tenure_Years": yrs,
            "Monthly_EMI": round(calc["emi"], 2),
            "Total_Interest": round(calc["total_interest"], 2),
            "Total_Payment": round(calc["total_payment"], 2),
            "Total_Cost": round(calc["total_cost"], 2),
            "Interest_to_Principal_Ratio": round((calc["total_interest"] / principal) * 100, 1) if principal > 0 else 0
        })
    return pd.DataFrame(records)


# ==============================================================================
# 3. FIXED DEPOSIT (FD) CALCULATIONS
# ==============================================================================

def calculate_fd_maturity(principal, annual_rate, tenure_days=None, tenure_years=None,
                          payout_type="Cumulative", compounding_freq=4):
    """
    Calculates FD maturity values, payouts, and estimated interest.
    - Cumulative: Quarterly compounding A = P * (1 + r/(n*100))^(n*t)
    - Monthly: Simple interest paid monthly: P * r / 1200
    - Quarterly: Simple interest paid quarterly: P * r / 400
    """
    principal = max(0.0, float(principal))
    annual_rate = max(0.0, float(annual_rate))

    if tenure_days is not None:
        t_years = float(tenure_days) / 365.0
        days = int(tenure_days)
    elif tenure_years is not None:
        t_years = float(tenure_years)
        days = int(tenure_years * 365)
    else:
        t_years = 1.0
        days = 365

    if principal <= 0 or t_years <= 0 or annual_rate <= 0:
        return {
            "principal": principal,
            "annual_rate": annual_rate,
            "tenure_days": days,
            "tenure_years": t_years,
            "interest_earned": 0.0,
            "maturity_amount": principal,
            "periodic_payout": 0.0,
            "effective_yield": annual_rate,
            "tds_applicable": False,
            "estimated_tds": 0.0
        }

    payout_clean = payout_type.lower()

    if "monthly" in payout_clean:
        periodic_payout = principal * (annual_rate / 1200.0)
        total_payout_count = t_years * 12.0
        total_interest = periodic_payout * total_payout_count
        maturity_amount = principal  # Principal returned at maturity
        effective_yield = annual_rate
    elif "quarterly" in payout_clean:
        periodic_payout = principal * (annual_rate / 400.0)
        total_payout_count = t_years * 4.0
        total_interest = periodic_payout * total_payout_count
        maturity_amount = principal
        effective_yield = annual_rate
    else:
        # Standard Cumulative Quarterly Compounding (Indian banking standard)
        n = float(compounding_freq)
        maturity_amount = principal * math.pow(1.0 + (annual_rate / (100.0 * n)), n * t_years)
        total_interest = maturity_amount - principal
        periodic_payout = 0.0
        effective_yield = ((maturity_amount - principal) / (principal * t_years)) * 100.0 if t_years > 0 else annual_rate

    # TDS Check (Section 194A): Threshold is ₹40,000 for General, ₹50,000 for Senior Citizens per financial year
    # Estimated assuming 1-year window
    annualized_interest = total_interest / max(1.0, t_years)
    tds_applicable = annualized_interest > 40000.0
    estimated_tds = annualized_interest * 0.10 if tds_applicable else 0.0

    return {
        "principal": principal,
        "annual_rate": annual_rate,
        "tenure_days": days,
        "tenure_years": round(t_years, 2),
        "interest_earned": round(total_interest, 2),
        "maturity_amount": round(maturity_amount, 2),
        "periodic_payout": round(periodic_payout, 2),
        "effective_yield": round(effective_yield, 2),
        "tds_applicable": tds_applicable,
        "estimated_tds": round(estimated_tds, 2)
    }


def calculate_fd_ladder(total_investment, ladder_years=[1, 2, 3, 4, 5],
                        base_rate=6.8, step_rate=0.15, customer_type="General"):
    """
    Generates an educational FD laddering strategy.
    Splits total investment across multiple maturity terms.
    """
    num_rungs = len(ladder_years)
    per_rung = total_investment / num_rungs
    rungs = []
    start_dt = date.today()

    senior_bonus = 0.50 if customer_type == "Senior Citizen" else 0.0

    for i, yrs in enumerate(ladder_years):
        # Slightly increasing rate curve for longer tenures
        rate = base_rate + (i * step_rate) + senior_bonus
        res = calculate_fd_maturity(per_rung, rate, tenure_years=yrs, payout_type="Cumulative")
        mat_dt = start_dt + relativedelta(years=yrs)

        rungs.append({
            "Rung": f"Bucket {i+1} ({yrs} Yr)",
            "Tenure_Years": yrs,
            "Investment": round(per_rung, 2),
            "Interest_Rate": round(rate, 2),
            "Start_Date": start_dt.strftime("%Y-%m-%d"),
            "End_Date": mat_dt.strftime("%Y-%m-%d"),
            "Maturity_Date": mat_dt.strftime("%d %b %Y"),
            "Maturity_Amount": res["maturity_amount"],
            "Interest_Earned": res["interest_earned"]
        })

    df = pd.DataFrame(rungs)
    total_mature = df["Maturity_Amount"].sum()
    total_interest = df["Interest_Earned"].sum()

    return df, total_mature, total_interest


# ==============================================================================
# 4. SAVINGS CALCULATOR & GOAL TRACKER
# ==============================================================================

def calculate_savings_growth(initial_balance, monthly_deposit, annual_rate, duration_years):
    """
    Projects recurring savings account balance with monthly additions
    and quarterly compounding interest.
    """
    initial = max(0.0, float(initial_balance))
    monthly = max(0.0, float(monthly_deposit))
    rate = max(0.0, float(annual_rate))
    total_months = max(1, int(duration_years * 12))

    monthly_rate = (rate / 100.0) / 12.0

    records = []
    balance = initial
    total_deposited = initial
    total_interest = 0.0

    for m in range(1, total_months + 1):
        interest_this_month = balance * monthly_rate
        balance += interest_this_month + monthly
        total_deposited += monthly
        total_interest += interest_this_month

        records.append({
            "Month": m,
            "Year": round(m / 12.0, 1),
            "Total_Deposited": round(total_deposited, 2),
            "Interest_Earned": round(total_interest, 2),
            "Current_Balance": round(balance, 2)
        })

    df = pd.DataFrame(records)
    return {
        "final_balance": round(balance, 2),
        "total_deposited": round(total_deposited, 2),
        "total_interest": round(total_interest, 2),
        "projection_df": df
    }


def calculate_goal_tracker(goal_name, target_amount, current_savings, monthly_contribution, annual_rate=3.0):
    """
    Goal progress tracker with estimated completion timeline.
    """
    target = max(1.0, float(target_amount))
    current = max(0.0, float(current_savings))
    monthly = max(0.0, float(monthly_contribution))

    progress_pct = min(100.0, (current / target) * 100.0)
    remaining_amount = max(0.0, target - current)

    if remaining_amount <= 0:
        months_to_goal = 0
        completion_date = date.today()
    elif monthly <= 0:
        months_to_goal = -1  # Cannot reach without contributions
        completion_date = None
    else:
        # Estimate with modest compounding
        monthly_rate = (annual_rate / 100.0) / 12.0
        bal = current
        m = 0
        while bal < target and m < 600:  # Max 50 years cap
            bal += (bal * monthly_rate) + monthly
            m += 1
        months_to_goal = m
        completion_date = date.today() + relativedelta(months=months_to_goal)

    return {
        "goal_name": goal_name,
        "target_amount": target,
        "current_savings": current,
        "remaining_amount": remaining_amount,
        "progress_pct": progress_pct,
        "months_to_goal": months_to_goal,
        "completion_date": completion_date.strftime("%B %Y") if completion_date else "N/A"
    }
