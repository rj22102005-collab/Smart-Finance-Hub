"""
SMART FINANCE HUB - UI/UX Components & Visual Design System
============================================================
High-contrast, presentation-ready styling inspired by modern Indian FinTech:
- Crisp white & light-slate palette with bold deep navy (#0F172A) text
- Clean rounded cards with distinct borders and subtle shadows
- High visibility on all projectors and laptop screens
- Clickable action cards, loan health score widget & payoff journey tracker
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from calculations import format_inr, format_inr_compact


# ==============================================================================
# 1. DESIGN TOKENS & HIGH-CONTRAST CSS INJECTION
# ==============================================================================

def inject_custom_css():
    """
    Injects custom CSS tailored for crystal-clear readability and contrast.
    Guarantees dark, bold text on crisp light backgrounds.
    """
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@500;600;700&display=swap');

    :root {
        --primary-blue: #0F4C81;
        --secondary-teal: #0D9488;
        --accent-sky: #0284C7;
        --accent-emerald: #10B981;
        --accent-amber: #D97706;
        --accent-rose: #DC2626;
        --bg-main: #F8FAFC;
        --bg-card: #FFFFFF;
        --text-dark: #0F172A;
        --text-body: #1E293B;
        --text-muted: #475569;
        --border-card: #CBD5E1;
    }

    /* Base Styling - High Contrast */
    .stApp {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
        background-color: #F8FAFC;
        color: #0F172A;
    }

    /* Ensure All Streamlit Headings & Labels are Bold and Dark */
    h1, h2, h3, h4, h5, h6, .stMarkdown p, label, .stSelectbox label, .stNumberInput label {
        color: #0F172A !important;
        font-weight: 700 !important;
    }

    /* Main Container Spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1350px;
    }

    /* FinTech Presentation Cards */
    .fin-card {
        background-color: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
        margin-bottom: 1.2rem;
    }

    .fin-card-gradient {
        background: linear-gradient(135deg, #0F4C81 0%, #1E3A8A 50%, #0D9488 100%);
        color: #FFFFFF !important;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 8px 24px rgba(15, 76, 129, 0.25);
        margin-bottom: 1.5rem;
    }
    .fin-card-gradient h1, .fin-card-gradient h2, .fin-card-gradient h3, .fin-card-gradient p {
        color: #FFFFFF !important;
    }

    /* Metric Display Box */
    .metric-box {
        background: #FFFFFF;
        border: 1.5px solid #CBD5E1;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    .metric-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 5px;
        height: 100%;
        background: var(--accent-sky);
    }
    .metric-box.teal::before { background: var(--secondary-teal); }
    .metric-box.emerald::before { background: var(--accent-emerald); }
    .metric-box.amber::before { background: var(--accent-amber); }
    .metric-box.blue::before { background: var(--primary-blue); }
    .metric-box.rose::before { background: var(--accent-rose); }

    .metric-title {
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #475569;
        margin-bottom: 0.4rem;
    }
    .metric-val {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
    }
    .metric-sub {
        font-size: 0.88rem;
        color: #334155;
        font-weight: 600;
        margin-top: 0.35rem;
    }

    /* Badges & Status Pills */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .badge-green { background-color: #ECFDF5; color: #065F46; border: 1.5px solid #6EE7B7; }
    .badge-blue { background-color: #EFF6FF; color: #1E40AF; border: 1.5px solid #93C5FD; }
    .badge-teal { background-color: #F0FDFA; color: #115E59; border: 1.5px solid #5EEAD4; }
    .badge-amber { background-color: #FFFBEB; color: #92400E; border: 1.5px solid #FCD34D; }
    .badge-red { background-color: #FEF2F2; color: #991B1B; border: 1.5px solid #FCA5A5; }

    /* Custom Streamlit Tabs Styling - Big & High Contrast */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #E2E8F0;
        padding: 8px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 46px;
        border-radius: 10px;
        color: #1E293B !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0 20px;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #0F4C81 !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    }

    /* Buttons Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1.4rem;
        border: 1.5px solid #0F4C81;
        background-color: #FFFFFF;
        color: #0F4C81 !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #0F4C81;
        color: #FFFFFF !important;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 700 !important;
        font-size: 1rem !important;
        background-color: #0F4C81 !important;
        color: #FFFFFF !important;
        border: none;
        padding: 0.65rem 1.4rem;
        box-shadow: 0 4px 12px rgba(15, 76, 129, 0.25);
    }
    .stDownloadButton > button:hover {
        background-color: #1E3A8A !important;
    }

    /* Disclaimer box */
    .disclaimer-box {
        background-color: #F1F5F9;
        border-left: 5px solid #0F4C81;
        padding: 1rem 1.4rem;
        border-radius: 0 10px 10px 0;
        font-size: 0.88rem;
        color: #334155;
        line-height: 1.5;
        margin-top: 1.5rem;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


# ==============================================================================
# 2. HERO & HEADER COMPONENTS
# ==============================================================================

def render_hero_banner(title="SMART FINANCE HUB", subtitle="Calculate. Compare. Plan. Grow.", description=None):
    """Renders the top branding hero card with gradient and modern typography."""
    desc_html = f"<p style='margin-top: 0.6rem; font-size: 1.1rem; opacity: 0.95; max-width: 850px; font-weight: 500;'>{description}</p>" if description else ""
    st.markdown(f"""
    <div class="fin-card-gradient">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem;">
            <div>
                <span class="badge-pill" style="background: rgba(255,255,255,0.22); color: #fff; margin-bottom: 0.6rem; font-size: 0.85rem; border: none;">
                    ★ PERSONAL BANKING & FINANCE PLATFORM
                </span>
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.02em;">{title}</h1>
                <p style="margin: 0.4rem 0 0 0; font-size: 1.25rem; font-weight: 700; color: #99F6E4 !important;">
                    {subtitle}
                </p>
                {desc_html}
            </div>
            <div style="text-align: right; background: rgba(255,255,255,0.15); padding: 0.9rem 1.4rem; border-radius: 12px; backdrop-filter: blur(8px);">
                <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">Data Status</div>
                <div style="font-size: 1.1rem; font-weight: 800; color: #A7F3D0;">● Verified Official</div>
                <div style="font-size: 0.82rem; font-weight: 600; opacity: 0.9;">September 2024</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title, value, subtitle="", border_color="blue", icon=None):
    """Renders a single metric box with colored indicator stripe."""
    icon_html = f"<span style='float: right; font-size: 1.4rem;'>{icon}</span>" if icon else ""
    card_html = (
        f'<div class="metric-box {border_color}">'
        f'{icon_html}'
        f'<div class="metric-title">{title}</div>'
        f'<div class="metric-val">{value}</div>'
        f'<div class="metric-sub">{subtitle}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


# ==============================================================================
# 3. BONUS WIDGET 1: EDUCATIONAL LOAN HEALTH SCORE
# ==============================================================================

def render_loan_health_widget(health_data: dict):
    """
    Renders the Educational Loan Health Score bonus widget.
    High contrast and presentation clear.
    """
    score = health_data["score"]
    grade = health_data["grade"]
    color = health_data["badge_color"]
    summary = health_data["summary"]
    breakdown = health_data["breakdown"]

    st.markdown(f"""
    <div class="fin-card" style="border-left: 8px solid {color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.6rem;">
                    <span class="badge-pill badge-blue">BONUS WIDGET</span>
                    <span style="font-size: 0.95rem; font-weight: 800; color: #0F172A; text-transform: uppercase;">
                        YOUR LOAN PROFILE & FINANCIAL HEALTH
                    </span>
                </div>
                <div style="display: flex; align-items: baseline; gap: 0.9rem; margin-top: 0.5rem;">
                    <span style="font-size: 3rem; font-weight: 800; color: #0F172A; line-height: 1;">
                        {score} <span style="font-size: 1.5rem; color: #64748B; font-weight: 700;">/ 100</span>
                    </span>
                    <span class="badge-pill" style="background-color: {color}20; color: {color}; border: 2px solid {color}; font-size: 1.05rem; font-weight: 800; padding: 0.4rem 1rem;">
                        ● {grade}
                    </span>
                </div>
                <p style="margin: 0.5rem 0 0.8rem 0; font-size: 1rem; color: #1E293B; font-weight: 600;">
                    {summary}
                </p>
            </div>
            <div style="min-width: 240px; background: #F8FAFC; border: 1.5px solid #CBD5E1; padding: 1rem 1.2rem; border-radius: 12px;">
                <div style="font-size: 0.82rem; font-weight: 800; color: #0F172A; margin-bottom: 0.6rem; text-transform: uppercase;">
                    Profile Pillars
                </div>
                <div style="font-size: 0.92rem; display: flex; flex-direction: column; gap: 0.4rem;">
                    <div><strong>EMI Burden:</strong> <span style="color: #0F172A; font-weight: 700;">{breakdown['emi_burden']['status']}</span></div>
                    <div><strong>Debt Level:</strong> <span style="color: #0F172A; font-weight: 700;">{breakdown['existing_debt']['status']}</span></div>
                    <div><strong>Savings Rate:</strong> <span style="color: #0F172A; font-weight: 700;">{breakdown['savings']['status']}</span></div>
                    <div><strong>Emergency Reserve:</strong> <span style="color: #0F172A; font-weight: 700;">{breakdown['emergency_fund']['status']}</span></div>
                </div>
            </div>
        </div>

        <div style="margin-top: 1rem;">
            <div style="width: 100%; height: 12px; background: #E2E8F0; border-radius: 999px; overflow: hidden;">
                <div style="width: {score}%; height: 100%; background: linear-gradient(90deg, #0F4C81, {color}); border-radius: 999px;"></div>
            </div>
        </div>

        <div style="margin-top: 0.8rem; font-size: 0.82rem; color: #64748B; font-weight: 600;">
            * Educational / Illustrative Loan Health Score — This is NOT a credit score (e.g. CIBIL/Experian) and does not guarantee loan eligibility or bank approval.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 4. BONUS WIDGET 2: LOAN JOURNEY VISUAL MILESTONE TRACKER
# ==============================================================================

def render_loan_journey_widget(original_amount: float, paid_amount: float, remaining_amount: float, current_month: int = 12, total_months: int = 60):
    """
    Renders an attractive visual loan journey milestones widget:
    ₹10,00,000 -> ₹8,00,000 -> ₹6,00,000 -> ₹4,00,000 -> ₹2,00,000 -> ₹0 🎉
    """
    original_amount = max(1.0, original_amount)
    pct_paid = min(100.0, max(0.0, (paid_amount / original_amount) * 100.0))

    milestones = [
        format_inr_compact(original_amount),
        format_inr_compact(original_amount * 0.8),
        format_inr_compact(original_amount * 0.6),
        format_inr_compact(original_amount * 0.4),
        format_inr_compact(original_amount * 0.2),
        "₹0 Debt-Free 🎉"
    ]

    st.markdown(f"""
    <div class="fin-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.9rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <span class="badge-pill badge-teal" style="margin-bottom: 0.3rem;">BONUS WIDGET</span>
                <h4 style="margin: 0; font-size: 1.3rem; font-weight: 800; color: #0F172A;">
                    🗺️ Your Loan Payoff Journey
                </h4>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 1.5rem; font-weight: 800; color: #0D9488;">{pct_paid:.1f}% Repaid</span>
                <span style="font-size: 0.95rem; font-weight: 700; color: #334155; margin-left: 0.5rem;">({current_month} of {total_months} Months)</span>
            </div>
        </div>

        <!-- Visual Milestone Journey Path -->
        <div style="display: flex; justify-content: space-between; align-items: center; background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 12px; padding: 1.1rem; margin-bottom: 1.1rem; overflow-x: auto;">
            <div style="text-align: center; min-width: 80px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #475569;">Start</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #0F4C81;">{milestones[0]}</div>
            </div>
            <div style="color: #64748B; font-weight: 800; font-size: 1.2rem;">→</div>
            <div style="text-align: center; min-width: 80px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #475569;">Stage 1</div>
                <div style="font-weight: 700; font-size: 1rem; color: #1E293B;">{milestones[1]}</div>
            </div>
            <div style="color: #64748B; font-weight: 800; font-size: 1.2rem;">→</div>
            <div style="text-align: center; min-width: 80px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #475569;">Midpoint</div>
                <div style="font-weight: 700; font-size: 1rem; color: #1E293B;">{milestones[2]}</div>
            </div>
            <div style="color: #64748B; font-weight: 800; font-size: 1.2rem;">→</div>
            <div style="text-align: center; min-width: 80px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #475569;">Stage 3</div>
                <div style="font-weight: 700; font-size: 1rem; color: #1E293B;">{milestones[3]}</div>
            </div>
            <div style="color: #64748B; font-weight: 800; font-size: 1.2rem;">→</div>
            <div style="text-align: center; min-width: 80px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #475569;">Stage 4</div>
                <div style="font-weight: 700; font-size: 1rem; color: #1E293B;">{milestones[4]}</div>
            </div>
            <div style="color: #64748B; font-weight: 800; font-size: 1.2rem;">→</div>
            <div style="text-align: center; min-width: 110px; background: #ECFDF5; padding: 0.4rem 0.8rem; border-radius: 8px; border: 1.5px solid #6EE7B7;">
                <div style="font-size: 0.8rem; color: #065F46; font-weight: 800;">Target</div>
                <div style="font-weight: 800; font-size: 1.05rem; color: #065F46;">{milestones[5]}</div>
            </div>
        </div>

        <!-- Dynamic Multi-Stop Progress Bar -->
        <div style="width: 100%; height: 16px; background: #E2E8F0; border-radius: 999px; overflow: hidden; margin-bottom: 0.9rem;">
            <div style="width: {pct_paid}%; height: 100%; background: linear-gradient(90deg, #0F4C81, #0D9488, #10B981); border-radius: 999px;"></div>
        </div>

        <div style="display: flex; justify-content: space-between; font-size: 1rem;">
            <div>
                <span style="color: #334155; font-weight: 700;">Principal Repaid:</span>
                <strong style="color: #0F4C81; margin-left: 0.3rem;">{format_inr(paid_amount)}</strong>
            </div>
            <div>
                <span style="color: #334155; font-weight: 700;">Remaining Outstanding:</span>
                <strong style="color: #DC2626; margin-left: 0.3rem;">{format_inr(remaining_amount)}</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 5. SAVINGS GOAL TRACKER WIDGET
# ==============================================================================

def render_goal_tracker_widget(goal_data: dict):
    """Renders the attractive Savings Goal progress bar."""
    goal_name = goal_data["goal_name"]
    target = goal_data["target_amount"]
    current = goal_data["current_savings"]
    remaining = goal_data["remaining_amount"]
    pct = goal_data["progress_pct"]
    months = goal_data["months_to_goal"]
    target_dt = goal_data["completion_date"]

    st.markdown(f"""
    <div class="fin-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.9rem; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <span class="badge-pill badge-green">GOAL TRACKER</span>
                <h3 style="margin: 0.3rem 0 0 0; font-size: 1.4rem; font-weight: 800; color: #0F172A;">
                    🎯 {goal_name}
                </h3>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 2rem; font-weight: 800; color: #0D9488;">{pct:.1f}%</span>
                <span style="font-size: 0.9rem; color: #334155; font-weight: 700; display: block;">Achieved</span>
            </div>
        </div>

        <div style="width: 100%; height: 18px; background: #E2E8F0; border-radius: 999px; overflow: hidden; margin-bottom: 1.1rem;">
            <div style="width: {pct}%; height: 100%; background: linear-gradient(90deg, #0D9488, #10B981); border-radius: 999px;"></div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.9rem; background: #F8FAFC; padding: 1rem 1.2rem; border-radius: 12px; border: 1.5px solid #CBD5E1;">
            <div>
                <div style="font-size: 0.82rem; color: #475569; font-weight: 700; text-transform: uppercase;">Saved So Far</div>
                <div style="font-weight: 800; font-size: 1.2rem; color: #0D9488;">{format_inr(current)}</div>
            </div>
            <div>
                <div style="font-size: 0.82rem; color: #475569; font-weight: 700; text-transform: uppercase;">Target Goal</div>
                <div style="font-weight: 800; font-size: 1.2rem; color: #0F4C81;">{format_inr(target)}</div>
            </div>
            <div>
                <div style="font-size: 0.82rem; color: #475569; font-weight: 700; text-transform: uppercase;">Remaining</div>
                <div style="font-weight: 800; font-size: 1.2rem; color: #DC2626;">{format_inr(remaining)}</div>
            </div>
            <div>
                <div style="font-size: 0.82rem; color: #475569; font-weight: 700; text-transform: uppercase;">Estimated Finish</div>
                <div style="font-weight: 800; font-size: 1.1rem; color: #0F172A;">{target_dt} ({months} mos)</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# 6. PLOTLY CHART STYLING UTILITIES
# ==============================================================================

CHART_PALETTE = {
    "primary": "#0F4C81",
    "teal": "#0D9488",
    "sky": "#0284C7",
    "emerald": "#10B981",
    "amber": "#D97706",
    "rose": "#DC2626",
    "slate": "#475569",
    "grid": "#E2E8F0",
    "bg": "#FFFFFF"
}

def apply_clean_chart_layout(fig: go.Figure, title: str = "", x_title: str = "", y_title: str = "", height: int = 380):
    """Applies a crisp, presentation-ready light theme layout to any Plotly chart."""
    if fig is None:
        return fig
    try:
        fig.update_layout(
            title=dict(
                text=f"<b>{title}</b>" if title else "",
                font=dict(family="Plus Jakarta Sans, Inter, sans-serif", size=16, color="#0F172A"),
                x=0.01,
                y=0.96
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=40, r=20, t=55 if title else 25, b=45),
            height=height,
            font=dict(family="Plus Jakarta Sans, Inter, sans-serif", color="#0F172A", size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=12, color="#0F172A")
            )
        )
    except Exception:
        pass

    try:
        if x_title or hasattr(fig.layout, "xaxis"):
            fig.update_xaxes(
                title=dict(text=x_title, font=dict(color="#0F172A", size=12, family="Plus Jakarta Sans")),
                showgrid=True,
                gridcolor="#E2E8F0",
                linecolor="#94A3B8",
                tickfont=dict(size=12, color="#0F172A")
            )
    except Exception:
        pass

    try:
        if y_title or hasattr(fig.layout, "yaxis"):
            fig.update_yaxes(
                title=dict(text=y_title, font=dict(color="#0F172A", size=12, family="Plus Jakarta Sans")),
                showgrid=True,
                gridcolor="#E2E8F0",
                linecolor="#94A3B8",
                tickfont=dict(size=12, color="#0F172A")
            )
    except Exception:
        pass

    return fig


# ==============================================================================
# 7. FOOTER COMPONENT
# ==============================================================================

def render_footer():
    """Renders the official footer with disclaimers and last updated notice."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; color: #475569; font-size: 0.9rem;">
        <div style="font-weight: 800; font-size: 1.25rem; color: #0F4C81; letter-spacing: -0.01em;">
            SMART FINANCE HUB
        </div>
        <div style="font-weight: 700; color: #0D9488; font-size: 0.95rem; margin-top: 0.2rem;">
            Calculate. Compare. Plan. Grow.
        </div>
        <div style="max-width: 850px; margin: 0.8rem auto 0 auto; line-height: 1.5; font-size: 0.85rem; color: #334155; font-weight: 500;">
            <strong>Educational & Informational Disclaimer:</strong> This application is developed strictly for educational, illustrative, and comparative purposes. 
            It does not constitute chartered financial advice or credit guarantee. Bank interest rates, charges, limits, and product terms vary frequently based on borrower credit score, RBI policy rates, and institutional guidelines.
            Please verify all current parameters directly on official banking portals before entering financial agreements.
        </div>
        <div style="margin-top: 0.8rem; font-size: 0.85rem; font-weight: 700; color: #0F172A;">
            Data Verified From Official Portals (SBI, HDFC, ICICI, Axis, Kotak, BoB, PNB, Canara, Union Bank) • Last Updated: <strong>September 2024</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)
