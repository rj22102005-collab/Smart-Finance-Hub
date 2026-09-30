"""
SMART FINANCE HUB
==================================================
Calculate. Compare. Plan. Grow.
A comprehensive Personal Banking & Finance Platform built with Streamlit, Pandas, NumPy, and Plotly.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date

# Local Modular Imports
from calculations import (
    format_inr,
    format_inr_compact,
    calculate_emi,
    generate_amortization_schedule,
    simulate_prepayment,
    calculate_affordability,
    compare_tenures,
    calculate_fd_maturity,
    calculate_fd_ladder,
    calculate_savings_growth,
    calculate_goal_tracker
)

from data_loader import (
    load_fd_rates,
    load_savings_rates,
    load_bank_accounts,
    load_loan_rates,
    get_best_fd_rate_for_bank,
    get_all_bank_fd_comparison,
    filter_bank_accounts,
    generate_excel_download,
    generate_csv_download,
    DISCLAIMER_TEXT,
    LAST_UPDATED_LABEL
)

from ui_components import (
    inject_custom_css,
    render_hero_banner,
    render_metric_card,
    render_goal_tracker_widget,
    apply_clean_chart_layout,
    render_footer,
    CHART_PALETTE
)

# ==============================================================================
# 1. STREAMLIT PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Smart Finance Hub | Personal Banking & Finance Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject high-contrast FinTech CSS
inject_custom_css()

# ==============================================================================
# 2. SESSION STATE INITIALIZATION
# ==============================================================================

def init_session_state():
    """Initializes default calculation values so the app looks populated immediately."""
    defaults = {
        "nav_tab": "🏠 Overview",
        # Loan Defaults
        "loan_amount": 500000.0,
        "loan_rate": 8.50,
        "loan_tenure_years": 5,
        "loan_tenure_months": 0,
        "loan_proc_fee_pct": 0.5,
        "loan_proc_fee_flat": 1000.0,
        "loan_other_charges": 500.0,
        "loan_calc_result": None,
        "loan_schedule_df": None,
        "loan_yearly_df": None,

        # Prepayment Defaults
        "prepay_month": 12,
        "prepay_amount": 100000.0,
        "prepay_mode": "reduce_tenure",

        # Affordability Defaults
        "user_income": 75000.0,
        "user_existing_emis": 0.0,
        "user_expenses": 25000.0,
        "user_savings_bal": 0.0,
        "user_emergency_months": 0,

        # FD Defaults
        "fd_investment": 500000.0,
        "fd_tenure_days": 365,
        "fd_customer_type": "General",
        "fd_payout": "Cumulative",

        # Savings Defaults
        "savings_initial": 100000.0,
        "savings_monthly": 10000.0,
        "savings_duration_years": 3,
        "savings_rate_manual": 3.0,

        # Goal Defaults
        "goal_name": "Emergency Cushion & Downpayment",
        "goal_target": 500000.0,
        "goal_current": 320000.0,
        "goal_monthly": 15000.0
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Perform initial loan calculation for immediate display
    if st.session_state["loan_calc_result"] is None:
        calc = calculate_emi(
            st.session_state["loan_amount"],
            st.session_state["loan_rate"],
            st.session_state["loan_tenure_years"],
            st.session_state["loan_tenure_months"],
            st.session_state["loan_proc_fee_pct"],
            st.session_state["loan_proc_fee_flat"],
            st.session_state["loan_other_charges"]
        )
        st.session_state["loan_calc_result"] = calc
        m_df, y_df = generate_amortization_schedule(
            st.session_state["loan_amount"],
            st.session_state["loan_rate"],
            st.session_state["loan_tenure_years"] * 12
        )
        st.session_state["loan_schedule_df"] = m_df
        st.session_state["loan_yearly_df"] = y_df

init_session_state()

# ==============================================================================
# 3. TOP HORIZONTAL NAVIGATION (3 PRIMARY TABS + OVERVIEW)
# ==============================================================================

# Render Hero Branding Banner
render_hero_banner(
    title="SMART FINANCE HUB",
    subtitle="Calculate. Compare. Plan. Grow.",
    description="Your all-in-one personal banking decision companion. Compare official rates across 9 top Indian banks, simulate loans, and track savings."
)

NAV_OPTIONS = [
    "🏠 Overview",
    "💳 Loans",
    "💰 Fixed Deposits",
    "💵 Savings & Banking",
    "⚔️ Compare & Analytics"
]

# Ensure valid nav_tab
if st.session_state.get("nav_tab") not in NAV_OPTIONS:
    st.session_state["nav_tab"] = "🏠 Overview"

current_nav_index = NAV_OPTIONS.index(st.session_state["nav_tab"])

# Horizontal segmented navigation bar
st.markdown("<div style='margin-bottom: 0.5rem;'>", unsafe_allow_html=True)
selected_nav = st.radio(
    "Navigation Tabs",
    options=NAV_OPTIONS,
    index=current_nav_index,
    horizontal=True,
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# Update state if radio changed
if selected_nav != st.session_state["nav_tab"]:
    st.session_state["nav_tab"] = selected_nav
    st.rerun()

# Sidebar information badge
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
        <div style="background: linear-gradient(135deg, #0F4C81, #0D9488); color: white; width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold;">
            ₹
        </div>
        <div>
            <div style="font-weight: 800; font-size: 1.2rem; color: #0F172A; line-height: 1.1;">SMART FINANCE</div>
            <div style="font-size: 0.85rem; font-weight: 700; color: #0D9488; letter-spacing: 0.05em;">HUB INDIA</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1.5px solid #CBD5E1; border-radius: 10px; padding: 1rem; font-size: 0.88rem; color: #1E293B;">
        <div style="font-weight: 800; color: #0F172A; margin-bottom: 0.3rem;">● Verified Bank Data</div>
        <div>9 Major Indian Banks Covered</div>
        <div style="margin-top: 0.4rem; font-size: 0.8rem; font-weight: 700; color: #0D9488;">Status: September 2024</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"""
    <div style="font-size: 0.8rem; color: #475569; line-height: 1.4;">
        {DISCLAIMER_TEXT}
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# SECTION 1: OVERVIEW & DASHBOARD
# ==============================================================================

if st.session_state["nav_tab"] == "🏠 Overview":

    # 3 Large Actionable Financial Capability Cards (Clickable buttons to navigate)
    st.markdown("### 🌟 Financial Capabilities — Select a Hub")
    f_col1, f_col2, f_col3 = st.columns(3)

    with f_col1:
        st.markdown("""
        <div class="fin-card">
            <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">💳</div>
            <h3 style="margin: 0; color: #0F172A; font-weight: 800; font-size: 1.35rem;">LOANS</h3>
            <p style="margin: 0.5rem 0 1rem 0; font-size: 0.95rem; color: #334155; line-height: 1.45;">
                Calculate monthly EMI, complete amortization, lump-sum prepayment savings & visual payoff journey.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👉 Open Loans Hub", key="btn_open_loans", use_container_width=True):
            st.session_state["nav_tab"] = "💳 Loans"
            st.rerun()

    with f_col2:
        st.markdown("""
        <div class="fin-card">
            <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">💰</div>
            <h3 style="margin: 0; color: #0F172A; font-weight: 800; font-size: 1.35rem;">FIXED DEPOSITS</h3>
            <p style="margin: 0.5rem 0 1rem 0; font-size: 0.95rem; color: #334155; line-height: 1.45;">
                Compare returns across 9 commercial banks, calculate senior citizen benefits & 5-year FD Ladder.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👉 Open FD Hub", key="btn_open_fd", use_container_width=True):
            st.session_state["nav_tab"] = "💰 Fixed Deposits"
            st.rerun()

    with f_col3:
        st.markdown("""
        <div class="fin-card">
            <div style="font-size: 2.2rem; margin-bottom: 0.3rem;">💵</div>
            <h3 style="margin: 0; color: #0F172A; font-weight: 800; font-size: 1.35rem;">SAVINGS & BANKING</h3>
            <p style="margin: 0.5rem 0 1rem 0; font-size: 0.95rem; color: #334155; line-height: 1.45;">
                Simulate savings compounding, compare ATM/UPI daily limits, and track milestone goals.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("👉 Open Savings & Banking", key="btn_open_savings", use_container_width=True):
            st.session_state["nav_tab"] = "💵 Savings & Banking"
            st.rerun()

    # Quick Financial Metrics
    st.markdown("### 📈 Live Snapshot Metrics")
    loan_calc = st.session_state["loan_calc_result"]
    fd_calc = calculate_fd_maturity(
        st.session_state["fd_investment"],
        7.10,
        tenure_days=st.session_state["fd_tenure_days"],
        payout_type=st.session_state["fd_payout"]
    )
    sav_calc = calculate_savings_growth(
        st.session_state["savings_initial"],
        st.session_state["savings_monthly"],
        3.0,
        st.session_state["savings_duration_years"]
    )
    goal_res = calculate_goal_tracker(
        st.session_state["goal_name"],
        st.session_state["goal_target"],
        st.session_state["goal_current"],
        st.session_state["goal_monthly"]
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        render_metric_card("Monthly EMI", format_inr(loan_calc["emi"]), f"Tenure: {loan_calc['months']} Mos", "blue", "💳")
    with m2:
        render_metric_card("Total Interest", format_inr(loan_calc["total_interest"]), f"Principal: {format_inr_compact(loan_calc['principal'])}", "amber", "📊")
    with m3:
        render_metric_card("FD Maturity", format_inr(fd_calc["maturity_amount"]), f"Gain: +{format_inr(fd_calc['interest_earned'])}", "teal", "💰")
    with m4:
        render_metric_card("Savings Growth", format_inr(sav_calc["final_balance"]), f"After {st.session_state['savings_duration_years']} Yrs", "emerald", "💵")
    with m5:
        render_metric_card("Goal Progress", f"{goal_res['progress_pct']:.0f}%", f"{goal_res['months_to_goal']} Mos Left", "blue", "🎯")

    # Visualizations
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.markdown("#### ⚡ Loan Payoff Trajectory")
        m_df = st.session_state["loan_schedule_df"]
        if m_df is not None and not m_df.empty:
            fig_traj = go.Figure()
            fig_traj.add_trace(go.Scatter(
                x=m_df["Month"],
                y=m_df["Closing_Balance"],
                mode="lines",
                name="Outstanding Balance",
                line=dict(color=CHART_PALETTE["primary"], width=3.5),
                fill="tozeroy",
                fillcolor="rgba(15, 76, 129, 0.08)"
            ))
            apply_clean_chart_layout(fig_traj, "Loan Amortization Balance Curve", "Month", "Balance (₹)", height=320)
            st.plotly_chart(fig_traj, use_container_width=True)

    with col_right:
        st.markdown("#### 🏛️ Key Banking Benchmarks (Verified)")
        st.markdown("""
        <div class="fin-card" style="border-left: 6px solid #0F4C81;">
            <h5 style="color: #0F4C81; margin-bottom: 0.8rem; font-size: 1.15rem; font-weight: 800;">Official Rate Highlights</h5>
            <div style="display: flex; flex-direction: column; gap: 0.7rem; font-size: 0.95rem; color: #1E293B;">
                <div style="display: flex; justify-content: space-between; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 0.45rem;">
                    <span><strong>Top 1-Year FD Rate:</strong></span>
                    <span style="color: #0D9488; font-weight: 800;">7.25% – 7.40% p.a.</span>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 0.45rem;">
                    <span><strong>Senior Citizen FD Bonus:</strong></span>
                    <span style="color: #0F4C81; font-weight: 800;">+0.50% extra yield</span>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 0.45rem;">
                    <span><strong>Lowest Repo Home Loan:</strong></span>
                    <span style="color: #10B981; font-weight: 800;">8.40% – 8.50% (EBLR)</span>
                </div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1.5px solid #E2E8F0; padding-bottom: 0.45rem;">
                    <span><strong>Zero Balance Savings:</strong></span>
                    <span style="color: #0F4C81; font-weight: 800;">SBI & Kotak 811 (Nil MAB)</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding-top: 0.2rem;">
                    <span><strong>Standard UPI Daily Limit:</strong></span>
                    <span style="color: #334155; font-weight: 800;">₹1,00,000 / day</span>
                </div>
            </div>
            <div style="margin-top: 1rem; font-size: 0.82rem; color: #475569; font-weight: 600;">
                * Sourced directly from official bank portals (SBI, HDFC, ICICI, BoB, etc.) as of September 2024.
            </div>
        </div>
        """, unsafe_allow_html=True)

    render_footer()


# ==============================================================================
# SECTION 2: LOANS
# ==============================================================================

elif st.session_state["nav_tab"] == "💳 Loans":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; margin-bottom: 0.8rem;">
        <div>
            <h2 style="margin: 0; font-weight: 800; color: #0F172A; font-size: 2rem;">💳 Professional Loan Command Center</h2>
            <p style="margin: 0.2rem 0 0 0; color: #334155; font-size: 1rem; font-weight: 600;">Complete EMI calculations, 60-month amortization, prepayments & payoff journey.</p>
        </div>
        <div>
            <span class="badge-pill badge-blue" style="font-size: 0.9rem;">10 Core Interactive Tools</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    loan_tabs = st.tabs([
        "1. EMI Calculator",
        "2. Amortization Schedule",
        "3. Rate Comparison",
        "4. Prepayment Simulator",
        "5. Affordability",
        "6. What-If Simulator",
        "7. Outstanding Tracker",
        "8. Total Cost Breakdown",
        "9. EMI vs Tenure",
        "10. Reports & Export"
    ])

    # ----------------------------------------------------
    # TAB 1: EMI CALCULATOR
    # ----------------------------------------------------
    with loan_tabs[0]:
        st.markdown("#### 📐 Loan Parameter Inputs & Calculation")
        c1, c2, c3 = st.columns([1, 1, 1.2])

        with c1:
            p_input = st.number_input("Loan Amount (₹)", min_value=1000.0, max_value=100000000.0,
                                      value=float(st.session_state["loan_amount"]), step=25000.0)
            r_input = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=40.0,
                                      value=float(st.session_state["loan_rate"]), step=0.1)
            t_yrs = st.number_input("Loan Tenure (Years)", min_value=0, max_value=35,
                                    value=int(st.session_state["loan_tenure_years"]), step=1)
            t_mos = st.number_input("Additional Months", min_value=0, max_value=11,
                                    value=int(st.session_state["loan_tenure_months"]), step=1)

        with c2:
            fee_pct = st.number_input("Processing Fee (%)", min_value=0.0, max_value=5.0,
                                      value=float(st.session_state["loan_proc_fee_pct"]), step=0.1)
            fee_flat = st.number_input("Flat Processing Fee (₹)", min_value=0.0, max_value=50000.0,
                                       value=float(st.session_state["loan_proc_fee_flat"]), step=500.0)
            other_chg = st.number_input("Documentation / Other Charges (₹)", min_value=0.0, max_value=50000.0,
                                        value=float(st.session_state["loan_other_charges"]), step=500.0)

        # Update session state
        st.session_state["loan_amount"] = p_input
        st.session_state["loan_rate"] = r_input
        st.session_state["loan_tenure_years"] = t_yrs
        st.session_state["loan_tenure_months"] = t_mos
        st.session_state["loan_proc_fee_pct"] = fee_pct
        st.session_state["loan_proc_fee_flat"] = fee_flat
        st.session_state["loan_other_charges"] = other_chg

        # Recalculate
        calc = calculate_emi(p_input, r_input, t_yrs, t_mos, fee_pct, fee_flat, other_chg)
        st.session_state["loan_calc_result"] = calc
        m_sched, y_sched = generate_amortization_schedule(p_input, r_input, (t_yrs * 12 + t_mos))
        st.session_state["loan_schedule_df"] = m_sched
        st.session_state["loan_yearly_df"] = y_sched

        with c3:
            st.markdown(f"""
            <div class="fin-card" style="background: #FFFFFF; border: 2px solid #0F4C81; padding: 1.3rem;">
                <div style="font-size: 0.9rem; font-weight: 800; color: #0F4C81; text-transform: uppercase;">CALCULATED EMI</div>
                <div style="font-size: 2.4rem; font-weight: 800; color: #0F4C81; margin: 0.3rem 0;">
                    {format_inr(calc['emi'])}
                    <span style="font-size: 1.05rem; color: #475569; font-weight: 700;">/ Month</span>
                </div>
                <hr style="border: 0; border-top: 1.5px solid #CBD5E1; margin: 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 0.4rem;">
                    <span style="color: #334155; font-weight: 600;">Total Principal:</span>
                    <strong style="color: #0F172A;">{format_inr(calc['principal'])}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 0.4rem;">
                    <span style="color: #334155; font-weight: 600;">Total Interest:</span>
                    <strong style="color: #D97706;">{format_inr(calc['total_interest'])}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 0.4rem;">
                    <span style="color: #334155; font-weight: 600;">Processing & Fees:</span>
                    <strong style="color: #0F172A;">{format_inr(calc['processing_fee'] + calc['other_charges'])}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 1.05rem; font-weight: 800; margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1.5px dashed #94A3B8;">
                    <span style="color: #0F172A;">Total Loan Outflow:</span>
                    <strong style="color: #0D9488;">{format_inr(calc['total_cost'])}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)



    # ----------------------------------------------------
    # TAB 2: AMORTIZATION SCHEDULE
    # ----------------------------------------------------
    with loan_tabs[1]:
        st.markdown("#### 📅 Repayment Amortization Schedule")
        view_mode = st.radio("Select Schedule View:", ["Monthly Schedule", "Year-wise Summary"], horizontal=True)

        m_sched = st.session_state["loan_schedule_df"]
        y_sched = st.session_state["loan_yearly_df"]

        if m_sched is not None and not m_sched.empty:
            if view_mode == "Monthly Schedule":
                disp_df = m_sched.copy()
                for col in ["Opening_Balance", "EMI", "Principal_Repaid", "Interest_Paid", "Closing_Balance", "Cumulative_Principal", "Cumulative_Interest"]:
                    disp_df[col] = disp_df[col].apply(lambda x: format_inr(x))
                st.dataframe(disp_df, use_container_width=True, height=400)
            else:
                disp_y = y_sched.copy()
                for col in ["Opening_Balance", "Total_EMI", "Principal_Repaid", "Interest_Paid", "Closing_Balance"]:
                    disp_y[col] = disp_y[col].apply(lambda x: format_inr(x))
                st.dataframe(disp_y, use_container_width=True, height=350)

            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                fig_pi = go.Figure()
                fig_pi.add_trace(go.Bar(
                    x=y_sched["Year"],
                    y=y_sched["Principal_Repaid"],
                    name="Principal Repaid",
                    marker_color=CHART_PALETTE["primary"]
                ))
                fig_pi.add_trace(go.Bar(
                    x=y_sched["Year"],
                    y=y_sched["Interest_Paid"],
                    name="Interest Paid",
                    marker_color=CHART_PALETTE["amber"]
                ))
                fig_pi.update_layout(barmode="stack")
                apply_clean_chart_layout(fig_pi, "Yearly Principal vs Interest Split", "Year", "Amount (₹)")
                st.plotly_chart(fig_pi, use_container_width=True)

            with c_chart2:
                fig_bal = go.Figure()
                fig_bal.add_trace(go.Scatter(
                    x=m_sched["Month"],
                    y=m_sched["Closing_Balance"],
                    mode="lines",
                    name="Outstanding Balance",
                    line=dict(color=CHART_PALETTE["teal"], width=3.5)
                ))
                apply_clean_chart_layout(fig_bal, "Declining Outstanding Balance Curve", "Month", "Balance (₹)")
                st.plotly_chart(fig_bal, use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: LOAN RATE COMPARISON
    # ----------------------------------------------------
    with loan_tabs[2]:
        st.markdown("#### ⚖️ Compare Across Major Lenders & Detailed Scheme Breakdown")
        loan_df = load_loan_rates()
        categories = loan_df["Loan_Category"].unique().tolist()
        sel_cat = st.selectbox("Select Loan Category", categories, index=0)

        cat_loans = loan_df[loan_df["Loan_Category"] == sel_cat].copy().reset_index(drop=True)

        comp_records = []
        p_val = st.session_state["loan_amount"]
        t_val = st.session_state["loan_tenure_years"]

        for _, row in cat_loans.iterrows():
            r = row["Min_Rate"]
            f_pct = row["Processing_Fee_Percentage"]
            calc_b = calculate_emi(p_val, r, t_val, 0, processing_fee_pct=f_pct)
            comp_records.append({
                "Bank / Lender": row["Bank"],
                "Product": row["Product_Name"],
                "Indicative Rate": f"{r:.2f}%",
                "Monthly EMI": calc_b["emi"],
                "Total Interest": calc_b["total_interest"],
                "Processing Fee": calc_b["processing_fee"],
                "Total Cost": calc_b["total_cost"],
                "Benchmark": row["Benchmark_Linked"],
                "_raw_rate": r,
                "_raw_fee_pct": f_pct,
                "_calc_obj": calc_b
            })

        res_comp_df = pd.DataFrame(comp_records)
        min_emi_idx = res_comp_df["Monthly EMI"].idxmin()
        min_int_idx = res_comp_df["Total Interest"].idxmin()

        st.info(f"💡 **Neutral Insight:** Lowest calculated EMI for selected inputs: **{res_comp_df.loc[min_emi_idx, 'Bank / Lender']}** ({format_inr(res_comp_df.loc[min_emi_idx, 'Monthly EMI'])}) • Lowest calculated total interest: **{res_comp_df.loc[min_int_idx, 'Bank / Lender']}** ({format_inr(res_comp_df.loc[min_int_idx, 'Total Interest'])}).")

        st.markdown(
            '<div style="background: #F1F5F9; border-left: 4px solid #0F4C81; padding: 0.65rem 1rem; border-radius: 6px; margin: 0.6rem 0; font-size: 0.92rem; color: #1E293B;">'
            '👆 <strong>Click on any Bank / Scheme row in the table below</strong> (or select from the dropdown) to instantly see its <strong>Complete Repayment Schedule</strong> and <strong>Yearly EMI & Interest Pay Breakdown</strong>!'
            '</div>',
            unsafe_allow_html=True
        )

        disp_comp = res_comp_df[["Bank / Lender", "Product", "Indicative Rate", "Monthly EMI", "Total Interest", "Processing Fee", "Total Cost", "Benchmark"]].copy()
        for c in ["Monthly EMI", "Total Interest", "Processing Fee", "Total Cost"]:
            disp_comp[c] = disp_comp[c].apply(lambda x: format_inr(x))

        # Interactive Table with single-row selection
        table_key = f"rate_comp_table_{sel_cat}"
        selection = st.dataframe(
            disp_comp,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=table_key
        )

        state_key = f"rate_comp_idx_{sel_cat}"
        # Detect table selection
        table_selected_idx = None
        if selection:
            if hasattr(selection, "selection") and hasattr(selection.selection, "rows") and selection.selection.rows:
                table_selected_idx = selection.selection.rows[0]
            elif isinstance(selection, dict) and "selection" in selection and selection["selection"].get("rows"):
                table_selected_idx = selection["selection"]["rows"][0]

        if table_selected_idx is not None and 0 <= table_selected_idx < len(cat_loans):
            active_idx = table_selected_idx
            st.session_state[state_key] = active_idx
        else:
            active_idx = st.session_state.get(state_key, 0)
            if active_idx >= len(cat_loans):
                active_idx = 0
                st.session_state[state_key] = 0

        # Dropdown selection in sync
        scheme_options = [
            f"{row['Bank']} — {row['Product_Name']} (Rate: {row['Min_Rate']:.2f}%)"
            for _, row in cat_loans.iterrows()
        ]

        col_s1, col_s2 = st.columns([3, 1])
        with col_s1:
            chosen_scheme_str = st.selectbox(
                "🔍 Selected Scheme for Detailed Repayment & Yearly Breakdown:",
                options=scheme_options,
                index=active_idx,
                key=f"scheme_dropdown_{sel_cat}_{active_idx}"
            )
            chosen_idx = scheme_options.index(chosen_scheme_str)
            if chosen_idx != active_idx:
                st.session_state[state_key] = chosen_idx
                st.rerun()
        with col_s2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.caption(f"Inspecting: **{cat_loans.loc[active_idx, 'Bank']}**")

        # Extract selected bank data
        sel_row = cat_loans.iloc[active_idx]
        sel_comp = res_comp_df.iloc[active_idx]
        sel_calc = sel_comp["_calc_obj"]
        bank_name = sel_row["Bank"]
        product_name = sel_row["Product_Name"]
        bank_rate = sel_row["Min_Rate"]

        # Generate Amortization & Yearly Breakdown for selected bank
        m_bank_sched, y_bank_sched = generate_amortization_schedule(
            principal=p_val,
            annual_rate=bank_rate,
            tenure_months=int(t_val * 12)
        )

        bank_header_html = (
            f'<div style="background: linear-gradient(135deg, #0F4C81, #1E3A8A); color: white; padding: 1.2rem 1.5rem; border-radius: 12px; margin-top: 1rem; margin-bottom: 1.2rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">'
            f'<div>'
            f'<span style="background: rgba(255,255,255,0.22); padding: 4px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;">'
            f'Detailed Scheme Breakdown'
            f'</span>'
            f'<h3 style="margin: 0.4rem 0 0.1rem 0; font-size: 1.65rem; font-weight: 800; color: #FFFFFF;">'
            f'🏛️ {bank_name}'
            f'</h3>'
            f'<div style="font-size: 0.98rem; color: #E2E8F0; font-weight: 600;">'
            f'{product_name} &nbsp;•&nbsp; Benchmark: <strong>{sel_row["Benchmark_Linked"]}</strong>'
            f'</div>'
            f'</div>'
            f'<div style="text-align: right;">'
            f'<div style="font-size: 0.85rem; color: #CBD5E1; font-weight: 600;">Monthly EMI Outflow</div>'
            f'<div style="font-size: 2rem; font-weight: 800; color: #38BDF8;">'
            f'{format_inr(sel_calc["emi"])}<span style="font-size: 1rem; color: #E2E8F0;">/mo</span>'
            f'</div>'
            f'</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(bank_header_html, unsafe_allow_html=True)

        # Detailed Breakdown Tabs for this specific bank
        detail_view_tab1, detail_view_tab2, detail_view_tab3 = st.tabs([
            f"📊 Yearly EMI & Interest Pay ({bank_name})",
            f"📅 Full Repayment Schedule (Monthly - {int(t_val*12)} Months)",
            f"📈 Category Cost Comparison Chart"
        ])

        with detail_view_tab1:
            st.markdown(f"##### 📊 Year-wise Breakdown — {bank_name} ({product_name})")
            st.caption("Detailed view of yearly total EMI paid, principal repaid, interest paid (inter pay), and remaining closing balance.")

            disp_y_bank = y_bank_sched.copy()
            disp_y_bank_formatted = pd.DataFrame({
                "Year": disp_y_bank["Year"].apply(lambda y: f"Year {y}"),
                "Opening Balance": disp_y_bank["Opening_Balance"].apply(lambda x: format_inr(x)),
                "Yearly EMI Pay": disp_y_bank["Total_EMI"].apply(lambda x: format_inr(x)),
                "Principal Repaid": disp_y_bank["Principal_Repaid"].apply(lambda x: format_inr(x)),
                "Interest Pay (Inter Pay)": disp_y_bank["Interest_Paid"].apply(lambda x: format_inr(x)),
                "Closing Balance": disp_y_bank["Closing_Balance"].apply(lambda x: format_inr(x))
            })
            st.dataframe(disp_y_bank_formatted, use_container_width=True)

            # Chart of Yearly Principal vs Interest for this bank
            fig_bank_y = go.Figure()
            fig_bank_y.add_trace(go.Bar(
                x=[f"Year {y}" for y in y_bank_sched["Year"]],
                y=y_bank_sched["Principal_Repaid"],
                name="Principal Repaid",
                marker_color=CHART_PALETTE["primary"]
            ))
            fig_bank_y.add_trace(go.Bar(
                x=[f"Year {y}" for y in y_bank_sched["Year"]],
                y=y_bank_sched["Interest_Paid"],
                name="Interest Paid (Inter Pay)",
                marker_color=CHART_PALETTE["amber"]
            ))
            fig_bank_y.update_layout(barmode="stack")
            apply_clean_chart_layout(fig_bank_y, f"{bank_name} — Yearly Principal vs Interest Paid", "Tenure Year", "Amount (₹)")
            st.plotly_chart(fig_bank_y, use_container_width=True)

        with detail_view_tab2:
            st.markdown(f"##### 📋 Complete Monthly Repayment Schedule — {bank_name}")
            st.caption(f"Month-by-month repayment schedule for loan of {format_inr(p_val)} at {bank_rate:.2f}% for {t_val} years.")

            disp_m_bank = m_bank_sched.copy()
            disp_m_bank_formatted = pd.DataFrame({
                "Month": disp_m_bank["Month"].apply(lambda m: f"Month {m}"),
                "Opening Balance": disp_m_bank["Opening_Balance"].apply(lambda x: format_inr(x)),
                "Monthly EMI": disp_m_bank["EMI"].apply(lambda x: format_inr(x)),
                "Principal Repaid": disp_m_bank["Principal_Repaid"].apply(lambda x: format_inr(x)),
                "Interest Paid": disp_m_bank["Interest_Paid"].apply(lambda x: format_inr(x)),
                "Closing Balance": disp_m_bank["Closing_Balance"].apply(lambda x: format_inr(x)),
                "Cumulative Principal": disp_m_bank["Cumulative_Principal"].apply(lambda x: format_inr(x)),
                "Cumulative Interest": disp_m_bank["Cumulative_Interest"].apply(lambda x: format_inr(x))
            })
            st.dataframe(disp_m_bank_formatted, use_container_width=True, height=380)

            # Download CSV button for this specific bank
            csv_bank_data = m_bank_sched.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {bank_name} Repayment Schedule (CSV)",
                data=csv_bank_data,
                file_name=f"{bank_name.replace(' ', '_')}_{sel_cat.replace(' ', '_')}_amortization.csv",
                mime="text/csv",
                key=f"dl_csv_{sel_cat}_{bank_name}_{active_idx}"
            )

        with detail_view_tab3:
            st.markdown(f"##### 📊 Comparison of Total Loan Cost Across All Lenders ({sel_cat})")
            fig_l_comp = px.bar(
                res_comp_df,
                x="Bank / Lender",
                y="Total Cost",
                color="Total Interest",
                color_continuous_scale="Blues",
                title=f"Comparison of Total Loan Cost ({sel_cat})"
            )
            apply_clean_chart_layout(fig_l_comp, f"Total Loan Cost Across Lenders ({sel_cat})", "Lender", "Total Cost (₹)")
            st.plotly_chart(fig_l_comp, use_container_width=True)

    # ----------------------------------------------------
    # TAB 4: PREPAYMENT SIMULATOR
    # ----------------------------------------------------
    with loan_tabs[3]:
        st.markdown("#### 🚀 Loan Prepayment Impact Simulator")
        pp_c1, pp_c2, pp_c3 = st.columns(3)
        with pp_c1:
            prepay_amt = st.number_input("Prepayment Lump Sum (₹)", min_value=5000.0, max_value=50000000.0,
                                         value=float(st.session_state["prepay_amount"]), step=25000.0)
        with pp_c2:
            max_m = max(2, st.session_state["loan_tenure_years"] * 12 - 1)
            prepay_m = st.slider("Month of Prepayment", min_value=1, max_value=max_m,
                                 value=int(min(st.session_state["prepay_month"], max_m)))
        with pp_c3:
            prepay_mode = st.radio("Prepayment Strategy:", [
                ("reduce_tenure", "Shorten Tenure (Keep EMI Same)"),
                ("reduce_emi", "Lower Monthly EMI (Keep Tenure Same)")
            ], format_func=lambda x: x[1])

        st.session_state["prepay_amount"] = prepay_amt
        st.session_state["prepay_month"] = prepay_m

        p_res = simulate_prepayment(
            st.session_state["loan_amount"],
            st.session_state["loan_rate"],
            st.session_state["loan_tenure_years"] * 12,
            prepay_m,
            prepay_amt,
            prepayment_mode=prepay_mode[0]
        )

        w1, w2, w3, w4 = st.columns(4)
        with w1:
            render_metric_card("Interest Saved", format_inr(p_res["interest_saved"]), "Direct Savings", "emerald", "💰")
        with w2:
            if prepay_mode[0] == "reduce_tenure":
                render_metric_card("Tenure Reduced", f"{p_res['months_saved']} Months", f"≈ {p_res['years_saved']} Years Early", "teal", "⏳")
            else:
                diff_emi = p_res["base_emi"] - p_res["revised_emi"]
                render_metric_card("Revised EMI", format_inr(p_res["revised_emi"]), f"Saves {format_inr(diff_emi)}/mo", "blue", "📉")
        with w3:
            render_metric_card("Revised Total Interest", format_inr(p_res["new_total_interest"]), f"Was {format_inr(p_res['base_total_interest'])}", "blue", "📊")
        with w4:
            render_metric_card("Prepayment Applied", format_inr(p_res["actual_prepayment"]), f"At Month {prepay_m}", "amber", "⚡")

        fig_pre = go.Figure()
        fig_pre.add_trace(go.Scatter(
            x=p_res["base_schedule"]["Month"],
            y=p_res["base_schedule"]["Closing_Balance"],
            mode="lines",
            name="Regular Schedule (Without Prepayment)",
            line=dict(color="#DC2626", dash="dash", width=2.5)
        ))
        fig_pre.add_trace(go.Scatter(
            x=p_res["new_schedule"]["Month"],
            y=p_res["new_schedule"]["Closing_Balance"],
            mode="lines",
            name=f"With Prepayment ({format_inr_compact(prepay_amt)})",
            line=dict(color="#10B981", width=3.5),
            fill="tozeroy",
            fillcolor="rgba(16, 185, 129, 0.08)"
        ))
        apply_clean_chart_layout(fig_pre, "Outstanding Balance: Base vs Prepayment Path", "Month", "Balance (₹)")
        st.plotly_chart(fig_pre, use_container_width=True)

    # ----------------------------------------------------
    # TAB 5: AFFORDABILITY
    # ----------------------------------------------------
    with loan_tabs[4]:
        st.markdown("#### 🧮 Educational Loan Affordability Calculator")
        aff_c1, aff_c2 = st.columns([1, 1.2])
        with aff_c1:
            u_inc = st.number_input("Net Monthly Income (₹)", min_value=10000.0, max_value=5000000.0,
                                    value=float(st.session_state["user_income"]), step=5000.0)
            u_ex_emi = st.number_input("Existing Monthly Debt / EMIs (₹) [0 if Nil]", min_value=0.0, max_value=2000000.0,
                                       value=float(st.session_state["user_existing_emis"]), step=1000.0)
            u_exp = st.number_input("Monthly Living Expenses (₹)", min_value=0.0, max_value=2000000.0,
                                    value=float(st.session_state["user_expenses"]), step=2000.0)

            st.session_state["user_income"] = u_inc
            st.session_state["user_existing_emis"] = u_ex_emi
            st.session_state["user_expenses"] = u_exp

        aff_res = calculate_affordability(
            u_inc, u_ex_emi, u_exp,
            st.session_state["loan_amount"],
            st.session_state["loan_rate"],
            st.session_state["loan_tenure_years"]
        )

        with aff_c2:
            st.markdown(f"""
            <div class="fin-card" style="border-left: 8px solid {aff_res['status_color']};">
                <div style="font-size: 0.85rem; font-weight: 800; color: #475569; text-transform: uppercase;">
                    Affordability & Debt Obligation (FOIR)
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.8rem; margin: 0.4rem 0;">
                    <span style="font-size: 2.5rem; font-weight: 800; color: #0F172A;">{aff_res['foir_pct']:.1f}%</span>
                    <span class="badge-pill" style="background: {aff_res['status_color']}20; color: {aff_res['status_color']}; border: 1.5px solid {aff_res['status_color']}; font-weight: 800;">
                        ● {aff_res['status']}
                    </span>
                </div>
                <p style="font-size: 0.95rem; color: #1E293B; font-weight: 600;">
                    {aff_res['note']}
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; font-size: 0.9rem; background: #F8FAFC; padding: 0.9rem; border-radius: 10px; border: 1.5px solid #CBD5E1;">
                    <div><strong>Proposed EMI:</strong> {format_inr(aff_res['proposed_emi'])}</div>
                    <div><strong>Total EMI:</strong> {format_inr(aff_res['total_emi'])}</div>
                    <div><strong>Disposable Surplus:</strong> <span style="color: {'#10B981' if aff_res['disposable_income']>0 else '#DC2626'}; font-weight: 800;">{format_inr(aff_res['disposable_income'])}</span></div>
                    <div><strong>Est. Max Capacity:</strong> {format_inr_compact(aff_res['max_loan_capacity'])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 6: WHAT-IF SIMULATOR
    # ----------------------------------------------------
    with loan_tabs[5]:
        st.markdown("#### 🎛️ Interactive What-If Loan Simulator")
        w_col1, w_col2, w_col3 = st.columns(3)
        with w_col1:
            sim_p = st.slider("Loan Amount (₹)", 50000, 20000000, int(st.session_state["loan_amount"]), step=50000, key="sim_p_slider")
        with w_col2:
            sim_r = st.slider("Interest Rate (%)", 6.0, 18.0, float(st.session_state["loan_rate"]), step=0.25, key="sim_r_slider")
        with w_col3:
            sim_t = st.slider("Tenure (Years)", 1, 30, int(st.session_state["loan_tenure_years"]), step=1, key="sim_t_slider")

        sim_calc = calculate_emi(sim_p, sim_r, sim_t, 0)

        sm1, sm2, sm3, sm4 = st.columns(4)
        with sm1:
            render_metric_card("Simulated EMI", format_inr(sim_calc["emi"]), "Per Month", "blue", "💳")
        with sm2:
            render_metric_card("Total Interest", format_inr(sim_calc["total_interest"]), f"{sim_calc['interest_ratio']:.1f}% of Outflow", "amber", "📈")
        with sm3:
            render_metric_card("Total Payment", format_inr(sim_calc["total_payment"]), f"Principal: {format_inr_compact(sim_p)}", "teal", "💰")
        with sm4:
            base_calc = st.session_state["loan_calc_result"]
            diff_emi = sim_calc["emi"] - base_calc["emi"]
            sign = "+" if diff_emi > 0 else ""
            render_metric_card("EMI Variance", f"{sign}{format_inr(diff_emi)}", "vs Base Calculation", "emerald" if diff_emi <= 0 else "rose", "⚖️")

    # ----------------------------------------------------
    # TAB 7: OUTSTANDING BALANCE TRACKER
    # ----------------------------------------------------
    with loan_tabs[6]:
        st.markdown("#### 📉 Outstanding Balance Payoff Tracker")
        m_df = st.session_state["loan_schedule_df"]
        if m_df is not None and not m_df.empty:
            sel_month = st.slider("Track Repayment at Month #", 1, len(m_df), min(12, len(m_df)), key="track_m_slider")
            row_snap = m_df.iloc[sel_month - 1]

            t1, t2, t3, t4 = st.columns(4)
            with t1:
                render_metric_card("Current Balance", format_inr(row_snap["Closing_Balance"]), f"At Month {sel_month}", "rose", "📉")
            with t2:
                render_metric_card("Amount Repaid", format_inr(row_snap["Cumulative_Principal"]), "Principal Paid", "emerald", "✅")
            with t3:
                pct_done = (row_snap["Cumulative_Principal"] / st.session_state["loan_amount"]) * 100
                render_metric_card("Percentage Paid", f"{pct_done:.1f}%", f"{len(m_df) - sel_month} Months Left", "teal", "📊")
            with t4:
                render_metric_card("Interest Paid So Far", format_inr(row_snap["Cumulative_Interest"]), "To Lender", "amber", "🏦")

    # ----------------------------------------------------
    # TAB 8: TOTAL COST BREAKDOWN
    # ----------------------------------------------------
    with loan_tabs[7]:
        st.markdown("#### 🍰 Total Cost of Loan Decomposition")
        calc_curr = st.session_state["loan_calc_result"]

        tc_c1, tc_c2 = st.columns([1, 1.2])
        with tc_c1:
            cost_items = pd.DataFrame([
                {"Component": "Principal Borrowed", "Amount": calc_curr["principal"]},
                {"Component": "Total Interest Payable", "Amount": calc_curr["total_interest"]},
                {"Component": "Processing Fee", "Amount": calc_curr["processing_fee"]},
                {"Component": "Other Charges & Taxes", "Amount": calc_curr["other_charges"]}
            ])
            cost_items["Percentage"] = (cost_items["Amount"] / calc_curr["total_cost"]) * 100.0

            disp_cost = cost_items.copy()
            disp_cost["Amount"] = disp_cost["Amount"].apply(lambda x: format_inr(x))
            disp_cost["Percentage"] = disp_cost["Percentage"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(disp_cost, use_container_width=True)

        with tc_c2:
            fig_donut = px.pie(
                cost_items,
                names="Component",
                values="Amount",
                hole=0.55,
                color="Component",
                color_discrete_map={
                    "Principal Borrowed": "#0F4C81",
                    "Total Interest Payable": "#D97706",
                    "Processing Fee": "#0D9488",
                    "Other Charges & Taxes": "#64748B"
                },
                title="Decomposition of Total Loan Cost"
            )
            apply_clean_chart_layout(fig_donut, "Total Outflow Components", height=320)
            st.plotly_chart(fig_donut, use_container_width=True)

    # ----------------------------------------------------
    # TAB 9: EMI VS TENURE ANALYSIS
    # ----------------------------------------------------
    with loan_tabs[8]:
        st.markdown("#### ⏳ EMI vs Tenure Comparison (3, 5, 7, 10 Years)")
        tenure_df = compare_tenures(st.session_state["loan_amount"], st.session_state["loan_rate"], [3, 5, 7, 10])

        disp_t = tenure_df.copy()
        for col in ["Monthly_EMI", "Total_Interest", "Total_Payment", "Total_Cost"]:
            disp_t[col] = disp_t[col].apply(lambda x: format_inr(x))
        disp_t["Interest_to_Principal_Ratio"] = disp_t["Interest_to_Principal_Ratio"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(disp_t.drop(columns=["Tenure_Years"]), use_container_width=True)

    # ----------------------------------------------------
    # TAB 10: REPORTS & EXPORT
    # ----------------------------------------------------
    with loan_tabs[9]:
        st.markdown("#### 📥 Download Official Loan Reports")
        calc_curr = st.session_state["loan_calc_result"]
        summary_export_df = pd.DataFrame([
            {"Parameter": "Principal Loan Amount", "Value": format_inr(calc_curr["principal"])},
            {"Parameter": "Annual Interest Rate", "Value": f"{st.session_state['loan_rate']:.2f}%"},
            {"Parameter": "Tenure", "Value": f"{calc_curr['months']} Months ({calc_curr['months']//12} Yrs)"},
            {"Parameter": "Calculated Monthly EMI", "Value": format_inr(calc_curr["emi"])},
            {"Parameter": "Total Interest Payable", "Value": format_inr(calc_curr["total_interest"])},
            {"Parameter": "Total Outflow Cost", "Value": format_inr(calc_curr["total_cost"])},
            {"Parameter": "Generated On", "Value": datetime.now().strftime("%d %b %Y, %I:%M %p")}
        ])

        m_sched = st.session_state["loan_schedule_df"]
        y_sched = st.session_state["loan_yearly_df"]

        exp_c1, exp_c2 = st.columns(2)
        with exp_c1:
            st.markdown("""
            <div class="fin-card">
                <h4 style="color: #0F4C81;">📊 Complete Excel Workbook (.xlsx)</h4>
                <p style="font-size: 0.92rem; color: #334155;">
                    Includes 3 clean tabs: <strong>Loan_Summary</strong>, <strong>Monthly_Amortization</strong>, and <strong>Yearly_Summary</strong>.
                </p>
            </div>
            """, unsafe_allow_html=True)
            excel_bytes = generate_excel_download({
                "Loan_Summary": summary_export_df,
                "Monthly_Amortization": m_sched,
                "Yearly_Summary": y_sched
            })
            st.download_button(
                label="📥 Download Loan Report (Excel .xlsx)",
                data=excel_bytes,
                file_name=f"SmartFinance_Loan_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_dl_excel"
            )

        with exp_c2:
            st.markdown("""
            <div class="fin-card">
                <h4 style="color: #0F4C81;">📄 Amortization Schedule (.csv)</h4>
                <p style="font-size: 0.92rem; color: #334155;">
                    Lightweight CSV file with month-by-month opening balance, EMI, principal, interest, and closing balances.
                </p>
            </div>
            """, unsafe_allow_html=True)
            csv_bytes = generate_csv_download(m_sched)
            st.download_button(
                label="📥 Download Amortization Schedule (CSV)",
                data=csv_bytes,
                file_name=f"Amortization_Schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="btn_dl_csv"
            )

    render_footer()


# ==============================================================================
# SECTION 3: FIXED DEPOSITS
# ==============================================================================

elif st.session_state["nav_tab"] == "💰 Fixed Deposits":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; margin-bottom: 0.8rem;">
        <div>
            <h2 style="margin: 0; font-weight: 800; color: #0F172A; font-size: 2rem;">💰 Fixed Deposit Comparator</h2>
            <p style="margin: 0.2rem 0 0 0; color: #334155; font-size: 1rem; font-weight: 600;">Compare FD rates, maturity values and returns across 9 benchmarked banks.</p>
        </div>
        <div>
            <span class="badge-pill badge-teal" style="font-size: 0.9rem;">Official Bank Portals • Sept 2024</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fd_tabs = st.tabs([
        "1. Multi-Bank Comparison",
        "2. FD Calculator",
        "3. General vs Senior Citizen",
        "4. Payout Modes",
        "5. Premature Penalty",
        "6. TDS & Tax Guidelines",
        "7. FD Ladder Calculator"
    ])

    with st.expander("⚙️ Adjust FD Parameters", expanded=True):
        f_in1, f_in2, f_in3, f_in4 = st.columns(4)
        with f_in1:
            fd_inv = st.number_input("Investment Amount (₹)", min_value=1000.0, max_value=50000000.0,
                                     value=float(st.session_state["fd_investment"]), step=25000.0, key="fd_inv_in")
        with f_in2:
            fd_tenure_sel = st.selectbox("Tenure Bracket", [
                ("365", "1 Year (365 Days)"),
                ("399", "Special 399-444 Days"),
                ("730", "2 Years (730 Days)"),
                ("1095", "3 Years (1095 Days)"),
                ("1825", "5 Years (1825 Days)")
            ], format_func=lambda x: x[1], key="fd_tenure_sel_in")
            fd_days = int(fd_tenure_sel[0])
        with f_in3:
            cust_type = st.radio("Customer Type", ["General", "Senior Citizen"], horizontal=True, key="fd_cust_in")
        with f_in4:
            payout_sel = st.selectbox("Payout Mode", ["Cumulative (Quarterly Compounding)", "Monthly Payout", "Quarterly Payout"], key="fd_payout_in")

        st.session_state["fd_investment"] = fd_inv
        st.session_state["fd_tenure_days"] = fd_days
        st.session_state["fd_customer_type"] = cust_type
        st.session_state["fd_payout"] = payout_sel

    # 1. Multi-bank comparison
    with fd_tabs[0]:
        st.markdown("#### 🏦 Multi-Bank FD Comparison Table")
        comp_fd_df = get_all_bank_fd_comparison(fd_inv, fd_days, customer_type=cust_type, payout_type=payout_sel)

        highest_bank = comp_fd_df.iloc[0]
        st.info(f"💡 **Top Maturity Yield:** Highest calculated maturity value for the selected criteria is offered by **{highest_bank['Bank']}** at **{highest_bank['Interest_Rate']:.2f}%** yielding **{format_inr(highest_bank['Maturity_Amount'])}** (Interest: {format_inr(highest_bank['Interest_Earned'])}).")

        disp_comp_fd = comp_fd_df.copy()
        disp_comp_fd["Interest_Rate"] = disp_comp_fd["Interest_Rate"].apply(lambda x: f"{x:.2f}%")
        disp_comp_fd["Investment"] = disp_comp_fd["Investment"].apply(lambda x: format_inr(x))
        disp_comp_fd["Interest_Earned"] = disp_comp_fd["Interest_Earned"].apply(lambda x: format_inr(x))
        disp_comp_fd["Maturity_Amount"] = disp_comp_fd["Maturity_Amount"].apply(lambda x: format_inr(x))
        disp_comp_fd["Effective_Yield"] = disp_comp_fd["Effective_Yield"].apply(lambda x: f"{x:.2f}%")

        st.dataframe(disp_comp_fd.drop(columns=["Periodic_Payout", "Source_URL"]), use_container_width=True)

        bc1, bc2 = st.columns(2)
        with bc1:
            fig_mat = px.bar(
                comp_fd_df,
                x="Bank",
                y="Maturity_Amount",
                color="Interest_Rate",
                color_continuous_scale="Teal",
                title=f"Maturity Value Comparison ({fd_tenure_sel[1]})"
            )
            apply_clean_chart_layout(fig_mat, "Estimated Maturity Value (₹)", "Bank", "Maturity (₹)")
            st.plotly_chart(fig_mat, use_container_width=True)

        with bc2:
            fig_int = px.bar(
                comp_fd_df,
                x="Bank",
                y="Interest_Earned",
                color="Interest_Earned",
                color_continuous_scale="Blues",
                title=f"Total Interest Earned Comparison"
            )
            apply_clean_chart_layout(fig_int, "Estimated Interest Earned (₹)", "Bank", "Interest (₹)")
            st.plotly_chart(fig_int, use_container_width=True)

    # 2. Detailed Single Bank
    with fd_tabs[1]:
        st.markdown("#### 🔍 Single Bank Return Calculator")
        fd_banks = comp_fd_df["Bank"].tolist()
        sel_bank = st.selectbox("Select Benchmark Bank", fd_banks, index=0, key="fd_bank_pick")
        bank_rate = get_best_fd_rate_for_bank(sel_bank, fd_days, cust_type)
        res_single = calculate_fd_maturity(fd_inv, bank_rate, tenure_days=fd_days, payout_type=payout_sel)

        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            render_metric_card("Applicable Rate", f"{bank_rate:.2f}%", f"{cust_type} Slab", "blue", "🏷️")
        with s_col2:
            render_metric_card("Maturity Amount", format_inr(res_single["maturity_amount"]), "At End of Tenure", "teal", "💰")
        with s_col3:
            render_metric_card("Total Interest", format_inr(res_single["interest_earned"]), f"Yield: {res_single['effective_yield']:.2f}%", "emerald", "📈")

    # 3. General vs Senior
    with fd_tabs[2]:
        st.markdown("#### 👵 General Citizen vs Senior Citizen Differential")
        gen_comp = get_all_bank_fd_comparison(fd_inv, fd_days, customer_type="General", payout_type=payout_sel)
        sen_comp = get_all_bank_fd_comparison(fd_inv, fd_days, customer_type="Senior Citizen", payout_type=payout_sel)
        merged_c = pd.merge(gen_comp, sen_comp, on="Bank", suffixes=("_General", "_Senior"))
        merged_c["Extra_Interest"] = merged_c["Interest_Earned_Senior"] - merged_c["Interest_Earned_General"]

        disp_m = pd.DataFrame({
            "Bank": merged_c["Bank"],
            "General Rate": merged_c["Interest_Rate_General"].apply(lambda x: f"{x:.2f}%"),
            "Senior Rate": merged_c["Interest_Rate_Senior"].apply(lambda x: f"{x:.2f}%"),
            "General Maturity": merged_c["Maturity_Amount_General"].apply(lambda x: format_inr(x)),
            "Senior Maturity": merged_c["Maturity_Amount_Senior"].apply(lambda x: format_inr(x)),
            "Additional Senior Gain": merged_c["Extra_Interest"].apply(lambda x: format_inr(x))
        })
        st.dataframe(disp_m, use_container_width=True)

    # 4. Payout Modes
    with fd_tabs[3]:
        st.markdown("#### ⚖️ Cumulative vs Periodic Payout Analysis")
        res_cum = calculate_fd_maturity(fd_inv, 7.10, tenure_days=fd_days, payout_type="Cumulative")
        res_mth = calculate_fd_maturity(fd_inv, 7.10, tenure_days=fd_days, payout_type="Monthly")
        res_qtr = calculate_fd_maturity(fd_inv, 7.10, tenure_days=fd_days, payout_type="Quarterly")

        p_comp = pd.DataFrame([
            {"Payout Mode": "Cumulative (Quarterly Compounding)", "Total Interest": format_inr(res_cum["interest_earned"]), "Maturity Proceeds": format_inr(res_cum["maturity_amount"]), "Periodic Payout": "Compounded", "Advantage": "Maximum wealth growth"},
            {"Payout Mode": "Quarterly Payout", "Total Interest": format_inr(res_qtr["interest_earned"]), "Maturity Proceeds": format_inr(res_qtr["maturity_amount"]), "Periodic Payout": format_inr(res_qtr["periodic_payout"]), "Advantage": "Quarterly cash-flow buffer"},
            {"Payout Mode": "Monthly Payout", "Total Interest": format_inr(res_mth["interest_earned"]), "Maturity Proceeds": format_inr(res_mth["maturity_amount"]), "Periodic Payout": format_inr(res_mth["periodic_payout"]), "Advantage": "Monthly living income"}
        ])
        st.dataframe(p_comp, use_container_width=True)

    # 5. Premature Penalty
    with fd_tabs[4]:
        st.markdown("#### ⚠️ Premature FD Withdrawal Penalty Simulator")
        pw_c1, pw_c2 = st.columns(2)
        with pw_c1:
            contracted_rate = st.number_input("Contracted Rate (%)", 4.0, 10.0, 7.25, 0.25, key="pw_rate")
            penalty_pct = st.slider("Penalty Deducted (%)", 0.25, 1.50, 1.00, 0.25, key="pw_pen")
            withdrawn_months = st.slider("Broken After (Months)", 1, 36, 6, key="pw_mos")

        eff_rate = max(0.0, contracted_rate - penalty_pct)
        pw_reg = calculate_fd_maturity(fd_inv, contracted_rate, tenure_days=withdrawn_months*30)
        pw_pen = calculate_fd_maturity(fd_inv, eff_rate, tenure_days=withdrawn_months*30)
        loss = pw_reg["interest_earned"] - pw_pen["interest_earned"]

        with pw_c2:
            st.markdown(f"""
            <div class="fin-card" style="border-left: 8px solid #DC2626;">
                <div style="font-size: 0.85rem; font-weight: 800; color: #475569;">PENALTY LOSS</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #DC2626; margin: 0.3rem 0;">
                    -{format_inr(loss)}
                </div>
                <div style="font-size: 0.95rem; color: #1E293B; font-weight: 600;">
                    <div>Contracted Yield: <strong>{format_inr(pw_reg['interest_earned'])}</strong> ({contracted_rate:.2f}%)</div>
                    <div>Post-Penalty Yield: <strong>{format_inr(pw_pen['interest_earned'])}</strong> ({eff_rate:.2f}%)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 6. TDS Guidelines
    with fd_tabs[5]:
        st.markdown("#### 📑 TDS (Tax Deducted at Source) & Income Tax Rules")
        st.markdown("""
        <div class="fin-card">
            <h4 style="color: #0F4C81;">Indian Income Tax Act — Section 194A Guidelines</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.8rem; font-size: 0.95rem;">
                <div style="background: #F8FAFC; padding: 1.1rem; border-radius: 10px; border: 1.5px solid #CBD5E1;">
                    <strong style="color: #0F172A; font-size: 1.05rem;">General Citizens:</strong>
                    <ul style="margin: 0.5rem 0 0 1rem; padding: 0; color: #334155; line-height: 1.6;">
                        <li>TDS exemption threshold: <strong>₹40,000</strong> per financial year per bank.</li>
                        <li>TDS rate with valid PAN: <strong>10%</strong>.</li>
                        <li>TDS rate without PAN: <strong>20%</strong>.</li>
                        <li>Submit <strong>Form 15G</strong> if total annual taxable income is nil.</li>
                    </ul>
                </div>
                <div style="background: #F8FAFC; padding: 1.1rem; border-radius: 10px; border: 1.5px solid #CBD5E1;">
                    <strong style="color: #0F172A; font-size: 1.05rem;">Senior Citizens (Section 80TTB):</strong>
                    <ul style="margin: 0.5rem 0 0 1rem; padding: 0; color: #334155; line-height: 1.6;">
                        <li>TDS exemption threshold: <strong>₹50,000</strong> per financial year.</li>
                        <li>Deduction under Section 80TTB up to <strong>₹50,000</strong> on interest income.</li>
                        <li>Submit <strong>Form 15H</strong> if total tax liability is nil.</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 7. FD Ladder Calculator
    with fd_tabs[6]:
        st.markdown("#### 🪜 FD Laddering Strategy Calculator")
        ladder_df, tot_mature, tot_int = calculate_fd_ladder(
            fd_inv, ladder_years=[1, 2, 3, 4, 5], base_rate=6.8, step_rate=0.15, customer_type=cust_type
        )

        lad_c1, lad_c2 = st.columns([1.2, 1])
        with lad_c1:
            disp_lad = ladder_df.copy()
            disp_lad["Investment"] = disp_lad["Investment"].apply(lambda x: format_inr(x))
            disp_lad["Interest_Rate"] = disp_lad["Interest_Rate"].apply(lambda x: f"{x:.2f}%")
            disp_lad["Maturity_Amount"] = disp_lad["Maturity_Amount"].apply(lambda x: format_inr(x))
            disp_lad["Interest_Earned"] = disp_lad["Interest_Earned"].apply(lambda x: format_inr(x))
            st.dataframe(disp_lad[["Rung", "Investment", "Interest_Rate", "Maturity_Date", "Maturity_Amount", "Interest_Earned"]], use_container_width=True)

        with lad_c2:
            st.markdown(f"""
            <div class="fin-card">
                <h4 style="color: #0F4C81;">🪜 Ladder Strategy Summary</h4>
                <div style="font-size: 0.9rem; color: #475569;">Total Capital Split:</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: #0F172A;">{format_inr(fd_inv)}</div>
                <hr style="border: 0; border-top: 1.5px solid #CBD5E1; margin: 0.6rem 0;">
                <div style="font-size: 1rem;">Total Interest: <strong style="color: #0D9488;">{format_inr(tot_int)}</strong></div>
                <div style="font-size: 1rem;">Realized Maturity: <strong style="color: #0F172A;">{format_inr(tot_mature)}</strong></div>
            </div>
            """, unsafe_allow_html=True)

        fig_ladder = px.timeline(
            ladder_df,
            x_start="Start_Date",
            x_end="End_Date",
            y="Rung",
            color="Interest_Rate",
            color_continuous_scale="Viridis",
            title="Staggered FD Maturity Timeline"
        )
        fig_ladder.update_yaxes(autorange="reversed")
        apply_clean_chart_layout(fig_ladder, "Staggered Maturity Horizon Timeline", height=280)
        st.plotly_chart(fig_ladder, use_container_width=True)

    render_footer()


# ==============================================================================
# SECTION 4: SAVINGS & BANKING ACCOUNTS
# ==============================================================================

elif st.session_state["nav_tab"] == "💵 Savings & Banking":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; margin-bottom: 0.8rem;">
        <div>
            <h2 style="margin: 0; font-weight: 800; color: #0F172A; font-size: 2rem;">💵 Savings & Banking Command Center</h2>
            <p style="margin: 0.2rem 0 0 0; color: #334155; font-size: 1rem; font-weight: 600;">Project compounding savings growth, evaluate bank balance slabs, and compare transaction limits.</p>
        </div>
        <div>
            <span class="badge-pill badge-green" style="font-size: 0.9rem;">Compounding & Limits Engine</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sb_tabs = st.tabs([
        "1. Savings Growth Calculator",
        "2. Savings Slabs Comparison",
        "3. Milestone Goal Tracker",
        "4. Bank Accounts & Transaction Limits"
    ])

    # 1. Savings Calculator
    with sb_tabs[0]:
        st.markdown("#### 📈 Compounding Savings Growth Projector")
        sc_1, sc_2, sc_3, sc_4 = st.columns(4)
        with sc_1:
            init_bal = st.number_input("Initial Balance (₹)", min_value=0.0, max_value=10000000.0,
                                       value=float(st.session_state["savings_initial"]), step=10000.0, key="sav_init_in")
        with sc_2:
            m_dep = st.number_input("Monthly Deposit (₹)", min_value=0.0, max_value=1000000.0,
                                    value=float(st.session_state["savings_monthly"]), step=2000.0, key="sav_mdep_in")
        with sc_3:
            dur_yrs = st.number_input("Duration (Years)", min_value=1, max_value=30,
                                      value=int(st.session_state["savings_duration_years"]), step=1, key="sav_dur_in")
        with sc_4:
            s_rate = st.number_input("Savings Rate (%)", min_value=1.0, max_value=10.0,
                                     value=float(st.session_state["savings_rate_manual"]), step=0.25, key="sav_rate_in")

        st.session_state["savings_initial"] = init_bal
        st.session_state["savings_monthly"] = m_dep
        st.session_state["savings_duration_years"] = dur_yrs
        st.session_state["savings_rate_manual"] = s_rate

        growth_res = calculate_savings_growth(init_bal, m_dep, s_rate, dur_yrs)
        proj_df = growth_res["projection_df"]

        sg1, sg2, sg3 = st.columns(3)
        with sg1:
            render_metric_card("Total Deposited", format_inr(growth_res["total_deposited"]), "Your Contributions", "blue", "💵")
        with sg2:
            render_metric_card("Estimated Interest", format_inr(growth_res["total_interest"]), "Compounded Return", "emerald", "🌱")
        with sg3:
            render_metric_card("Final Projected Balance", format_inr(growth_res["final_balance"]), f"After {dur_yrs} Years", "teal", "💰")

        fig_sav = go.Figure()
        fig_sav.add_trace(go.Scatter(
            x=proj_df["Month"],
            y=proj_df["Total_Deposited"],
            mode="lines",
            name="Cumulative Contributions",
            line=dict(color=CHART_PALETTE["primary"], width=2.5)
        ))
        fig_sav.add_trace(go.Scatter(
            x=proj_df["Month"],
            y=proj_df["Current_Balance"],
            mode="lines",
            name="Total Balance (With Interest)",
            line=dict(color=CHART_PALETTE["emerald"], width=3.5),
            fill="tonexty",
            fillcolor="rgba(16, 185, 129, 0.12)"
        ))
        apply_clean_chart_layout(fig_sav, "Savings Growth Trajectory", "Month", "Amount (₹)")
        st.plotly_chart(fig_sav, use_container_width=True)

    # 2. Savings Bank Comparison
    with sb_tabs[1]:
        st.markdown("#### 🏦 Official Bank Savings Rates & Balance Slabs")
        s_rates_df = load_savings_rates()
        disp_s_rates = s_rates_df.copy()
        disp_s_rates["Interest_Rate"] = disp_s_rates["Interest_Rate"].apply(lambda x: f"{x:.2f}%")
        disp_s_rates["Minimum_Balance_Metro"] = disp_s_rates["Minimum_Balance_Metro"].apply(lambda x: format_inr(x))
        disp_s_rates["Minimum_Balance_Rural"] = disp_s_rates["Minimum_Balance_Rural"].apply(lambda x: format_inr(x))

        st.dataframe(disp_s_rates.drop(columns=["Source_URL"]), use_container_width=True)

    # 3. Savings Goal Tracker
    with sb_tabs[2]:
        st.markdown("#### 🎯 Interactive Savings Goal Tracker")
        g_c1, g_c2, g_c3, g_c4 = st.columns(4)
        with g_c1:
            g_name = st.text_input("Goal Name", st.session_state["goal_name"], key="goal_name_in")
        with g_c2:
            g_target = st.number_input("Target Amount (₹)", 10000.0, 50000000.0, float(st.session_state["goal_target"]), 25000.0, key="goal_tgt_in")
        with g_c3:
            g_curr = st.number_input("Current Savings (₹)", 0.0, 50000000.0, float(st.session_state["goal_current"]), 10000.0, key="goal_cur_in")
        with g_c4:
            g_mth = st.number_input("Monthly Contribution (₹)", 500.0, 1000000.0, float(st.session_state["goal_monthly"]), 2000.0, key="goal_mth_in")

        st.session_state["goal_name"] = g_name
        st.session_state["goal_target"] = g_target
        st.session_state["goal_current"] = g_curr
        st.session_state["goal_monthly"] = g_mth

        goal_data = calculate_goal_tracker(g_name, g_target, g_curr, g_mth)
        render_goal_tracker_widget(goal_data)

    # 4. Bank Accounts & Transaction Limits
    with sb_tabs[3]:
        st.markdown("#### 🏦 Which Bank Account Fits Your Needs?")
        flt_col1, flt_col2, flt_col3 = st.columns(3)
        with flt_col1:
            f_low_bal = st.checkbox("☑ Zero / Low Min Balance (≤ ₹2,000)", value=False, key="flt_low_bal")
            f_low_chg = st.checkbox("☑ Low / Waived Card Charges", value=False, key="flt_low_chg")
        with flt_col2:
            f_high_atm = st.checkbox("☑ High ATM Daily Limit (≥ ₹40,000)", value=False, key="flt_atm")
            f_high_upi = st.checkbox("☑ Full ₹1,00,000 UPI Daily Limit", value=False, key="flt_upi")
        with flt_col3:
            f_digital = st.checkbox("☑ Digital Account Only", value=False, key="flt_dig")

        filtered_accounts = filter_bank_accounts(
            low_balance=f_low_bal,
            low_charges=f_low_chg,
            high_atm_limit=f_high_atm,
            high_upi_limit=f_high_upi,
            digital_only=f_digital
        )

        st.markdown(f"##### 📋 Matching Accounts ({len(filtered_accounts)} Found)")
        disp_acc = filtered_accounts.copy()
        for col in ["Minimum_Balance_Metro", "ATM_Limit_Per_Day", "UPI_Limit_Per_Day", "IMPS_Limit_Per_Day", "POS_Debit_Card_Limit"]:
            disp_acc[col] = disp_acc[col].apply(lambda x: format_inr(x))

        show_cols = [
            "Bank", "Account_Name", "Account_Type", "Minimum_Balance_Metro",
            "Debit_Card_Annual_Fee", "ATM_Limit_Per_Day", "UPI_Limit_Per_Day",
            "IMPS_Limit_Per_Day", "POS_Debit_Card_Limit"
        ]
        st.dataframe(disp_acc[show_cols], use_container_width=True)

    render_footer()


# ==============================================================================
# SECTION 5: COMPARE & ANALYTICS
# ==============================================================================

elif st.session_state["nav_tab"] == "⚔️ Compare & Analytics":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; margin-bottom: 0.8rem;">
        <div>
            <h2 style="margin: 0; font-weight: 800; color: #0F172A; font-size: 2rem;">⚔️ Universal Comparison & Analytics</h2>
            <p style="margin: 0.2rem 0 0 0; color: #334155; font-size: 1rem; font-weight: 600;">Head-to-head neutral comparison of any two financial instruments plus visual telemetry.</p>
        </div>
        <div>
            <span class="badge-pill badge-blue" style="font-size: 0.9rem;">Product A vs Product B</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ca_tabs = st.tabs(["1. Compare Any Two Products", "2. Interactive Analytics"])

    with ca_tabs[0]:
        compare_category = st.radio(
            "Choose Domain to Compare:",
            ["Loan vs Loan", "Fixed Deposit vs Fixed Deposit", "Bank Account vs Bank Account"],
            horizontal=True,
            key="cmp_domain_radio"
        )

        if compare_category == "Loan vs Loan":
            l_col1, l_col2 = st.columns(2)
            with l_col1:
                st.markdown("##### 🟦 Product A")
                p_a = st.number_input("Loan Amount A (₹)", 10000.0, 50000000.0, 500000.0, 25000.0, key="cmp_la_p")
                r_a = st.number_input("Rate A (%)", 5.0, 25.0, 8.5, 0.1, key="cmp_la_r")
                t_a = st.number_input("Tenure A (Years)", 1, 30, 5, 1, key="cmp_la_t")
                calc_a = calculate_emi(p_a, r_a, t_a, 0)
            with l_col2:
                st.markdown("##### 🟩 Product B")
                p_b = st.number_input("Loan Amount B (₹)", 10000.0, 50000000.0, 500000.0, 25000.0, key="cmp_lb_p")
                r_b = st.number_input("Rate B (%)", 5.0, 25.0, 9.2, 0.1, key="cmp_lb_r")
                t_b = st.number_input("Tenure B (Years)", 1, 30, 5, 1, key="cmp_lb_t")
                calc_b = calculate_emi(p_b, r_b, t_b, 0)

            diff_emi = calc_b["emi"] - calc_a["emi"]
            diff_int = calc_b["total_interest"] - calc_a["total_interest"]

            comp_loan_table = pd.DataFrame([
                {"Selected Criteria": "Principal Amount", "Product A": format_inr(p_a), "Product B": format_inr(p_b), "Difference (B - A)": format_inr(p_b - p_a)},
                {"Selected Criteria": "Interest Rate", "Product A": f"{r_a:.2f}%", "Product B": f"{r_b:.2f}%", "Difference (B - A)": f"{(r_b - r_a):+.2f}%"},
                {"Selected Criteria": "Tenure", "Product A": f"{t_a} Years", "Product B": f"{t_b} Years", "Difference (B - A)": f"{t_b - t_a} Years"},
                {"Selected Criteria": "Monthly EMI", "Product A": format_inr(calc_a["emi"]), "Product B": format_inr(calc_b["emi"]), "Difference (B - A)": format_inr(diff_emi)},
                {"Selected Criteria": "Total Interest", "Product A": format_inr(calc_a["total_interest"]), "Product B": format_inr(calc_b["total_interest"]), "Difference (B - A)": format_inr(diff_int)},
                {"Selected Criteria": "Total Cost", "Product A": format_inr(calc_a["total_cost"]), "Product B": format_inr(calc_b["total_cost"]), "Difference (B - A)": format_inr(calc_b["total_cost"] - calc_a["total_cost"])}
            ])
            st.dataframe(comp_loan_table, use_container_width=True)

        elif compare_category == "Fixed Deposit vs Fixed Deposit":
            fd_col1, fd_col2 = st.columns(2)
            fd_df = load_fd_rates()
            banks = fd_df["Bank"].unique().tolist()
            with fd_col1:
                st.markdown("##### 🟦 Option A")
                b_a = st.selectbox("Bank A", banks, index=0, key="cmp_fda_b")
                inv_a = st.number_input("Investment A (₹)", 5000.0, 50000000.0, 500000.0, 25000.0, key="cmp_fda_inv")
                t_days_a = st.selectbox("Tenure A", [365, 399, 730, 1095, 1825], index=0, key="cmp_fda_t")
                rate_a = get_best_fd_rate_for_bank(b_a, t_days_a, "General")
                fd_res_a = calculate_fd_maturity(inv_a, rate_a, tenure_days=t_days_a)
            with fd_col2:
                st.markdown("##### 🟩 Option B")
                b_b = st.selectbox("Bank B", banks, index=min(1, len(banks)-1), key="cmp_fdb_b")
                inv_b = st.number_input("Investment B (₹)", 5000.0, 50000000.0, 500000.0, 25000.0, key="cmp_fdb_inv")
                t_days_b = st.selectbox("Tenure B", [365, 399, 730, 1095, 1825], index=0, key="cmp_fdb_t")
                rate_b = get_best_fd_rate_for_bank(b_b, t_days_b, "General")
                fd_res_b = calculate_fd_maturity(inv_b, rate_b, tenure_days=t_days_b)

            diff_mat = fd_res_b["maturity_amount"] - fd_res_a["maturity_amount"]
            diff_int = fd_res_b["interest_earned"] - fd_res_a["interest_earned"]

            comp_fd_table = pd.DataFrame([
                {"Selected Criteria": "Bank Name", "Option A": b_a, "Option B": b_b, "Difference": "Institutional offering"},
                {"Selected Criteria": "Interest Rate", "Option A": f"{rate_a:.2f}%", "Option B": f"{rate_b:.2f}%", "Difference": f"{(rate_b - rate_a):+.2f}%"},
                {"Selected Criteria": "Estimated Interest", "Option A": format_inr(fd_res_a["interest_earned"]), "Option B": format_inr(fd_res_b["interest_earned"]), "Difference": format_inr(diff_int)},
                {"Selected Criteria": "Maturity Proceeds", "Option A": format_inr(fd_res_a["maturity_amount"]), "Option B": format_inr(fd_res_b["maturity_amount"]), "Difference": format_inr(diff_mat)}
            ])
            st.dataframe(comp_fd_table, use_container_width=True)

        elif compare_category == "Bank Account vs Bank Account":
            b_df = load_bank_accounts()
            acc_list = b_df["Account_Name"].tolist()
            ba_c1, ba_c2 = st.columns(2)
            with ba_c1:
                sel_a = st.selectbox("Select Account A", acc_list, index=0, key="cmp_ba_sel_a")
                row_a = b_df[b_df["Account_Name"] == sel_a].iloc[0]
            with ba_c2:
                sel_b = st.selectbox("Select Account B", acc_list, index=min(3, len(acc_list)-1), key="cmp_ba_sel_b")
                row_b = b_df[b_df["Account_Name"] == sel_b].iloc[0]

            comp_ba_table = pd.DataFrame([
                {"Selected Criteria": "Bank", "Account A": row_a["Bank"], "Account B": row_b["Bank"]},
                {"Selected Criteria": "Account Type", "Account A": row_a["Account_Type"], "Account B": row_b["Account_Type"]},
                {"Selected Criteria": "Minimum Balance (Metro)", "Account A": format_inr(row_a["Minimum_Balance_Metro"]), "Account B": format_inr(row_b["Minimum_Balance_Metro"])},
                {"Selected Criteria": "Debit Card Annual Fee", "Account A": row_a["Debit_Card_Annual_Fee"], "Account B": row_b["Debit_Card_Annual_Fee"]},
                {"Selected Criteria": "ATM Withdrawal Limit / Day", "Account A": format_inr(row_a["ATM_Limit_Per_Day"]), "Account B": format_inr(row_b["ATM_Limit_Per_Day"])},
                {"Selected Criteria": "UPI Daily Limit", "Account A": format_inr(row_a["UPI_Limit_Per_Day"]), "Account B": format_inr(row_b["UPI_Limit_Per_Day"])},
                {"Selected Criteria": "IMPS Daily Limit", "Account A": format_inr(row_a["IMPS_Limit_Per_Day"]), "Account B": format_inr(row_b["IMPS_Limit_Per_Day"])}
            ])
            st.dataframe(comp_ba_table, use_container_width=True)

    with ca_tabs[1]:
        st.markdown("#### 📊 Interactive Cross-Domain Analytics")
        an_c1, an_c2 = st.columns(2)
        with an_c1:
            m_df = st.session_state["loan_schedule_df"]
            if m_df is not None and not m_df.empty:
                fig_a1 = go.Figure()
                fig_a1.add_trace(go.Scatter(
                    x=m_df["Month"],
                    y=m_df["Cumulative_Principal"],
                    mode="lines",
                    name="Principal Repaid",
                    line=dict(color=CHART_PALETTE["primary"], width=3)
                ))
                fig_a1.add_trace(go.Scatter(
                    x=m_df["Month"],
                    y=m_df["Cumulative_Interest"],
                    mode="lines",
                    name="Interest Paid",
                    line=dict(color=CHART_PALETTE["amber"], width=3)
                ))
                apply_clean_chart_layout(fig_a1, "Cumulative Principal Repaid vs Interest Paid", "Month", "Amount (₹)")
                st.plotly_chart(fig_a1, use_container_width=True)

        with an_c2:
            fd_comp_df = get_all_bank_fd_comparison(st.session_state["fd_investment"], 365)
            fig_a2 = px.bar(
                fd_comp_df,
                x="Bank",
                y="Interest_Earned",
                color="Interest_Rate",
                color_continuous_scale="Viridis",
                title="1-Year FD Interest Yield Across 9 Banks"
            )
            apply_clean_chart_layout(fig_a2, "Bank-wise FD Interest Yield", "Bank", "Interest (₹)")
            st.plotly_chart(fig_a2, use_container_width=True)

    render_footer()
