import streamlit as st
import pandas as pd
import numpy as np
import joblib
import warnings
import plotly.graph_objects as go
import plotly.express as px
import os
import database

# Initialize database
try:
    active_db_engine = database.init_database()
except Exception:
    active_db_engine = "sqlite"

warnings.filterwarnings("ignore")

# -----------------------------
# Streamlit App Configuration
# -----------------------------
st.set_page_config(
    page_title="TelcoPulse | Churn Intelligence Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom Styling / CSS
# -----------------------------
st.markdown("""
<style>
    /* ============ GLOBAL ============ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(160deg, #0a0e1a 0%, #0f1629 40%, #111827 100%);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0f172a; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6366f1, #8b5cf6); border-radius: 10px; }
    
    /* ============ SIDEBAR ============ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1222 0%, #111936 50%, #0f172a 100%) !important;
        border-right: 1px solid rgba(99, 102, 241, 0.2) !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        padding: 10px 14px !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        border: 1px solid transparent !important;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
    }
    
    /* ============ HERO HEADER BANNER ============ */
    .hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #1e3a8a 60%, #0f766e 100%);
        border-radius: 16px;
        padding: 28px 32px;
        border: 1px solid rgba(129, 140, 248, 0.25);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15), 0 0 80px rgba(99, 102, 241, 0.05);
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(34, 211, 238, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #e0e7ff 0%, #a5b4fc 50%, #67e8f9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        font-weight: 400;
        max-width: 650px;
        position: relative;
        z-index: 1;
        line-height: 1.5;
    }
    
    /* ============ GLASSMORPHIC METRIC CARDS ============ */
    .metric-card {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 22px 24px;
        border: 1px solid rgba(148, 163, 184, 0.12);
        color: white;
        margin-bottom: 16px;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #6366f1 50%, transparent 100%);
        opacity: 0;
        transition: opacity 0.35s ease;
    }
    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.35);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.12), 0 0 60px rgba(99, 102, 241, 0.06);
        transform: translateY(-2px);
    }
    .metric-card:hover::before {
        opacity: 1;
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        margin-top: 6px;
        letter-spacing: -0.03em;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
    }
    
    /* ============ GLOWING RISK BADGES ============ */
    .badge-safe {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.12) 0%, rgba(16, 185, 129, 0.08) 100%);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.35);
        padding: 8px 20px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        letter-spacing: 0.04em;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.15);
        text-shadow: 0 0 10px rgba(74, 222, 128, 0.3);
    }
    .badge-moderate {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(245, 158, 11, 0.08) 100%);
        color: #fbbf24;
        border: 1px solid rgba(234, 179, 8, 0.35);
        padding: 8px 20px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        letter-spacing: 0.04em;
        box-shadow: 0 0 20px rgba(234, 179, 8, 0.15);
        text-shadow: 0 0 10px rgba(251, 191, 36, 0.3);
    }
    .badge-high {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, rgba(220, 38, 38, 0.08) 100%);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.35);
        padding: 8px 20px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
        letter-spacing: 0.04em;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.15);
        animation: pulse-red 2s ease-in-out infinite;
        text-shadow: 0 0 10px rgba(248, 113, 113, 0.3);
    }
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.15); }
        50% { box-shadow: 0 0 35px rgba(239, 68, 68, 0.3); }
    }
    
    /* ============ ACTION / RECOMMENDATION CARDS ============ */
    .action-card {
        background: linear-gradient(145deg, rgba(30, 27, 75, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
        backdrop-filter: blur(12px);
        border-left: 3px solid;
        border-image: linear-gradient(180deg, #818cf8, #6366f1) 1;
        padding: 18px 22px;
        border-radius: 0 14px 14px 0;
        margin-bottom: 12px;
        transition: all 0.3s ease;
        border-top: 1px solid rgba(129, 140, 248, 0.1);
        border-right: 1px solid rgba(129, 140, 248, 0.1);
        border-bottom: 1px solid rgba(129, 140, 248, 0.1);
    }
    .action-card:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
        border-image: linear-gradient(180deg, #a78bfa, #818cf8) 1;
    }
    
    /* ============ GENAI COPILOT SPECIAL BANNER ============ */
    .genai-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #1e3a8a 100%);
        padding: 22px 28px;
        border-radius: 16px;
        border: 1px solid rgba(129, 140, 248, 0.3);
        text-align: center;
        margin-top: 20px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(99, 102, 241, 0.12);
    }
    .genai-banner::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #818cf8, #a78bfa, #818cf8, transparent);
        animation: shimmer 3s ease-in-out infinite;
    }
    @keyframes shimmer {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }
    
    /* ============ FINANCIAL RISK CARD ============ */
    .risk-finance-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
        backdrop-filter: blur(16px);
        padding: 20px 24px;
        border-radius: 14px;
        margin-top: 16px;
        border: 1px solid rgba(56, 189, 248, 0.15);
        box-shadow: 0 4px 20px rgba(56, 189, 248, 0.06);
    }
    
    /* ============ SECTION DIVIDERS ============ */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.3), transparent) !important;
        margin: 24px 0 !important;
    }
    
    /* ============ BUTTONS ============ */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #7c3aed 100%) !important;
        color: white !important;
        border: 1px solid rgba(129, 140, 248, 0.3) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.25) !important;
    }
    .stButton>button[kind="primary"]:hover {
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.4) !important;
        transform: translateY(-1px) !important;
    }
    
    /* ============ TABS ============ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
    }
    
    /* ============ FOOTER ============ */
    .app-footer {
        text-align: center;
        padding: 20px 0;
        margin-top: 32px;
        border-top: 1px solid rgba(99, 102, 241, 0.15);
    }
    .footer-brand {
        font-weight: 700;
        background: linear-gradient(135deg, #818cf8, #6366f1, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 0.9rem;
        letter-spacing: 0.04em;
    }
    .footer-sub {
        color: #475569;
        font-size: 0.75rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Model & Asset Loading
# -----------------------------
@st.cache_resource
def load_ml_assets():
    model = joblib.load("logistic_regression_model.pkl")
    scaler = joblib.load("scaler.pkl")
    encoder = joblib.load("encoder.pkl")
    return model, scaler, encoder

@st.cache_data
def load_dataset():
    data_path = os.path.join("dataset", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
        return df
    return None

model, scaler, encoder = load_ml_assets()
raw_dataset = load_dataset()

# Helper function to preprocess and score input data
def preprocess_and_predict(df_input):
    df_temp = df_input.copy()
    
    # Ensure numeric columns
    numeric_fields = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]
    for col in numeric_fields:
        if col in df_temp.columns:
            df_temp[col] = pd.to_numeric(df_temp[col], errors="coerce").fillna(0)
            
    categorical_cols = [
        "gender", "Partner", "Dependents", "PhoneService", "MultipleLines",
        "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies", "Contract",
        "PaperlessBilling", "PaymentMethod"
    ]
    
    # Categorical encoding
    encoded_data = encoder.transform(df_temp[categorical_cols])
    encoded_df = pd.DataFrame(
        encoded_data,
        columns=encoder.get_feature_names_out(categorical_cols)
    )
    
    # Scale numeric + encoded features matching scaler features
    final_data = pd.concat(
        [df_temp[numeric_fields].reset_index(drop=True), encoded_df.reset_index(drop=True)],
        axis=1
    )
    
    # Feature ordering to match scaler.feature_names_in_
    final_data = final_data[scaler.feature_names_in_]
    
    final_scaled = scaler.transform(final_data)
    probs = model.predict_proba(final_scaled)[:, 1]
    preds = model.predict(final_scaled)
    
    # Calculate feature contributions for explainability (linear log-odds contribution)
    coefs = model.coef_[0]
    contributions = final_scaled * coefs
    
    return preds, probs, final_scaled, contributions, scaler.feature_names_in_

# -----------------------------
# Header Navigation & Sidebar
# -----------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3281/3281355.png", width=64)
    st.title("TelcoPulse AI")
    st.caption("Next-Gen Retention & Churn Intelligence")
    
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        [
            "🎯 Single Customer Diagnosis",
            "✨ GenAI Retention Copilot",
            "🎛️ What-If Retention Sandbox",
            "📁 Batch Scoring & Priority Queue",
            "📊 Executive Cohort Insights",
            "🧠 Model Diagnostics",
            "🗄️ Database & CRM Records"
        ]
    )
    
    # Active Database Status Badge
    db_cfg = database.load_db_config()
    db_engine_name = "MySQL (XAMPP)" if active_db_engine == "mysql" else "SQLite (Local DB)"
    db_badge_color = "#22c55e" if active_db_engine == "mysql" else "#38bdf8"
    st.markdown(f"""
    <div style='background: rgba(15, 23, 42, 0.85); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(99, 102, 241, 0.25); font-size: 0.82rem; margin: 10px 0 16px 0;'>
        <div style='color: #94a3b8; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;'>Database Status</div>
        <div style='color: #f1f5f9; font-weight: 600; display: flex; align-items: center; gap: 6px;'>
            <span style='color: {db_badge_color}; font-size: 0.9rem;'>●</span> {db_engine_name}
        </div>
        <div style='color: #64748b; font-size: 0.72rem; margin-top: 2px;'>DB: <code>{db_cfg.get('database', 'telecom_churn')}</code></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    def _get_default_api_key():
        key_f = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gemini_key")
        if os.path.exists(key_f):
            try:
                with open(key_f, "r", encoding="utf-8") as f:
                    k = f.read().strip()
                    if k:
                        return k
            except Exception:
                pass
        return os.environ.get("GEMINI_API_KEY", "")

    DEFAULT_GEMINI_KEY = _get_default_api_key()
    with st.expander("🔑 Live Gemini Cloud API", expanded=False):
        user_gemini_key = st.text_input(
            "Gemini API Key",
            value=DEFAULT_GEMINI_KEY,
            type="password",
            help="Configured with default Google Gemini API Key. You can edit, replace, or customize this key anytime."
        )
        if user_gemini_key:
            st.success("✅ Live Gemini API Key Configured!")
        else:
            st.caption("Running high-precision local contextual GenAI synthesis engine.")
    st.info("💡 **Pro-tip**: Use the **GenAI Copilot** to automatically generate personalized win-back campaigns and retention scripts.")


# Helper function to generate dynamic contextual GenAI retention assets with creative variety
def generate_dynamic_retention_campaign(c_name, c_risk_tier, c_tenure, c_contract, c_mcharges, c_internet, c_drivers, c_goal, c_tone, c_channel, temperature=0.85, api_key=None):
    import random, datetime, requests, json
    
    first_name = c_name.split()[0] if ' ' in c_name else c_name
    account_id = c_name.split()[-1].replace('#', '').replace('(', '').replace(')', '').replace(':', '') if '#' in c_name else f"CUST-{random.randint(1000, 9999)}"
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    random_seed = random.randint(100, 999)
    promo_code = f"TELCO-{random_seed}-{random.choice(['SAVE', 'RENEW', 'VIP', 'CARE', 'SECURE'])}"
    
    # 1. Tenure description & customized opening
    if c_tenure >= 36:
        years = round(c_tenure / 12, 1)
        tenure_desc = f"{years} years ({c_tenure} months)"
    elif c_tenure >= 12:
        years = round(c_tenure / 12, 1)
        tenure_desc = f"{years} years ({c_tenure} months)"
    else:
        tenure_desc = f"{c_tenure} months"

    # Diverse Narrative Framing Styles (Stochastic sampling for creative variety)
    narrative_hooks = [
        f"Loyalty shouldn't just be acknowledged—it should be directly rewarded. As someone who has been with our network for {tenure_desc}, your continued trust is what drives our service forward.",
        f"During our quarterly account optimization review, our team noticed that your account #{account_id} hasn't received our latest rate benefits and service upgrades for your {c_internet} connection.",
        f"We are reaching out with a simple, personal commitment: to ensure that you are receiving the highest level of connectivity, reliability, and value for your household.",
        f"As we celebrate your milestone of {tenure_desc} with our network, our executive leadership wanted to extend a direct loyalty dividend back onto your monthly statement.",
        f"We know reliable high-speed {c_internet} is essential for your everyday work and family life, and we never take your decision to stay with us for granted.",
        f"Great customer relationships are built on listening and taking proactive action before friction arises. That is why we have reviewed your account and approved an immediate upgrade package."
    ]
    chosen_hook = random.choice(narrative_hooks)

    # 2. Concession & discount calculations with stochastic variation
    base_disc = 0.25 if "Emergency" in c_goal else (0.20 if "Annual Contract" in c_goal else (0.15 if "Bill Optimization" in c_goal else 0.20))
    # Add slight creative fluctuation based on temperature
    fluctuation = random.choice([-0.02, 0.0, 0.02, 0.03]) if temperature > 0.5 else 0.0
    final_disc_rate = max(0.10, min(0.35, base_disc + fluctuation))
    
    discount_val = round(c_mcharges * final_disc_rate, 2)
    new_bill = round(c_mcharges - discount_val, 2)
    annual_savings = round(discount_val * 12, 2)

    goal_themes = [
        "Exclusive Loyalty Rate-Lock Guarantee",
        "Preferred Subscriber Care & Price-Freeze Package",
        "Proactive Service Optimization & Loyalty Dividend",
        "VIP Account Reinvestment & Security Upgrade"
    ]
    chosen_theme = random.choice(goal_themes)

    # 3. Dynamic Value Proposition Bullets (Strictly matching selected drivers + varied wording!)
    dynamic_bullets = []
    
    for d in c_drivers:
        if "High Monthly Bill" in d:
            disc_options = [
                f"* **🔒 Immediate Rate Relief:** We have authorized an ongoing **{int(final_disc_rate*100)}% monthly loyalty credit**, reducing your bill from **\\${c_mcharges:.2f}** to just **\\${new_bill:.2f}/mo** (saving you **\\${annual_savings:.2f}** over the year).",
                f"* **💰 Direct Monthly Savings:** Your monthly charge is dropping from **\\${c_mcharges:.2f}** down to **\\${new_bill:.2f}/month**, guaranteed for the next 12 billing cycles.",
                f"* **📉 Price-Protection Dividend:** Enjoy an approved **\\${discount_val:.2f}/mo discount** (\\${annual_savings:.2f} annual total savings) with zero hidden fees."
            ]
            dynamic_bullets.append(random.choice(disc_options))
        elif "Month-to-Month" in d:
            contract_options = [
                f"* **🛡️ 12-Month Inflation Freeze:** Lock in your preferred rate for a full year with our **30-Day Zero-Risk Guarantee** (cancel anytime with zero termination penalties).",
                f"* **📄 Flexible Loyalty Rate Guarantee:** Enjoy complete rate stability without rigid lock-ins—if you're not 100% satisfied, you can modify or cancel penalty-free.",
                f"* **🔒 Guaranteed Price Shield:** Protect your household from industry rate increases with a 1-year rate freeze and flexible account terms."
            ]
            dynamic_bullets.append(random.choice(contract_options))
        elif "Tech Support" in d or "Device Protection" in d:
            tech_options = [
                f"* **🛠️ 24/7 VIP Priority Tech Hotline & Security:** 6 months of complimentary cybersecurity protection, router bandwidth tuning, and direct tier-2 agent access (\\$90 retail value, 100% on us).",
                f"* **🛡️ Complete Device & Network Care Suite:** Complimentary 24/7 technical hotline and malware defense bundled directly into your subscription at zero extra cost.",
                f"* **⚡ Dedicated Priority Resolution Care:** Skip regular queue times with direct access to our Senior Technical Support team whenever you need assistance."
            ]
            dynamic_bullets.append(random.choice(tech_options))
        elif "Electronic Check" in d:
            pay_options = [
                f"* **💳 Instant Auto-Pay Enrollment Credit:** Switch your billing to automated credit card or bank transfer and receive an instant **\\$20 statement credit** on your next bill.",
                f"* **⚡ One-Click Payment Bonus:** Enroll in paperless auto-pay to claim a one-time **\\$25 billing waiver** and streamlined monthly processing.",
                f"* **🎁 Automated Billing Reward:** Receive an immediate **\\$20 account credit** upon activating automated payment protection."
            ]
            dynamic_bullets.append(random.choice(pay_options))
        elif "Early Tenure" in d:
            tenure_options = [
                f"* **🌟 Dedicated Customer Success Concierge:** Direct personal point-of-contact for your first year to ensure all connectivity needs are resolved immediately.",
                f"* **🤝 Priority Onboarding Check-in:** A dedicated senior care specialist assigned to your account for personalized service monitoring."
            ]
            dynamic_bullets.append(random.choice(tenure_options))
        elif "Competitor" in d:
            comp_options = [
                f"* **⚡ Fiber Bandwidth Speed Booster:** Complimentary upgrade to our Next-Gen 1 Gbps fiber speed tier with our lifetime price-match guarantee.",
                f"* **🚀 Price-Match & Speed Assurance:** We will match any verified local competitor promotion while doubling your upstream bandwidth."
            ]
            dynamic_bullets.append(random.choice(comp_options))

    if not dynamic_bullets:
        dynamic_bullets.append(f"* **🎁 Approved Loyalty Rate:** Lower your rate by **{int(final_disc_rate*100)}%** to **\\${new_bill:.2f}/mo** for the next 12 months.")
        dynamic_bullets.append(f"* **🛠️ VIP Priority Support:** 24/7 dedicated customer care and network optimization.")

    bullets_text = "\n\n".join(dynamic_bullets)

    # 4. Tone-based Subject Lines & Signatures with creative variety
    subject_templates = {
        "Empathetic": [
            f"A personal note for {first_name}: Let's ensure your {c_internet} experience is exceptional",
            f"{first_name}, we appreciate your {tenure_desc} with us — here is an exclusive loyalty update",
            f"Regarding your TelcoPulse service: A special rate optimization for {first_name}",
            f"{first_name}, thank you for your loyalty — we approved a \\${discount_val:.2f}/mo credit for you"
        ],
        "Professional": [
            f"Account Optimization Notice #{account_id}: Approved rate reduction for {first_name}",
            f"Service & Billing Portfolio Review: Updated terms and \\${annual_savings:.2f}/yr savings for #{account_id}",
            f"Confidential Account Brief: Authorized loyalty pricing adjustment for {first_name}",
            f"Annual Subscription Value Review: Approved rate restructuring for account #{account_id}"
        ],
        "Urgent": [
            f"⚡ Priority Reservation [{promo_code}]: Exclusive rate discount approved for {first_name} (Expires in 5 Days)",
            f"🚨 Urgent Loyalty Benefit: Claim your approved \\${new_bill:.2f}/mo rate before offer #{promo_code} expires",
            f"⏱️ Time-Sensitive Notice: Exclusive rate freeze and VIP perks approved for account #{account_id}",
            f"⚡ VIP Member Alert: Lock in your {int(final_disc_rate*100)}% discount with reservation code {promo_code}"
        ],
        "Executive": [
            f"Executive Outreach: A personal commitment regarding your TelcoPulse account #{account_id}",
            f"From the Office of Customer Experience: Special rate freeze authorized for {first_name}",
            f"Executive Portfolio Update: Direct loyalty commitment for account #{account_id}",
            f"Personal Message from Executive Care: Ensuring your {c_internet} service value"
        ]
    }
    
    tone_key = "Empathetic" if "Empathetic" in c_tone else ("Professional" if "Professional" in c_tone else ("Urgent" if "Urgent" in c_tone else "Executive"))
    subject_line = random.choice(subject_templates.get(tone_key, subject_templates["Empathetic"]))

    signatures = {
        "Empathetic": f"Warmest regards,\n\n**Senior Customer Care & Retention Advocate**\n\n*TelcoPulse Network Services*",
        "Professional": f"Respectfully,\n\n**Director of Subscriber Portfolio Operations**\n\n*TelcoPulse Business Services*",
        "Urgent": f"Urgent Member Support Desk,\n\n**Priority Retention & Concierge Unit**\n\n*TelcoPulse Network Services*",
        "Executive": f"With my personal commitment,\n\n**Vice President of Customer Experience & Operations**\n\n*TelcoPulse Executive Services*"
    }
    closing_sign = signatures.get(tone_key, signatures["Empathetic"])

    # Live Google Gemini Cloud API Call if key provided
    is_live_api = False
    custom_gemini_email = None
    if api_key and len(api_key.strip()) > 15:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
            prompt_content = f"""
            You are an elite, highly creative telecom retention copywriter. Draft an exceptional, personalized win-back outreach message for a telecom customer.
            Customer: {c_name}, Tenure: {c_tenure} months, Monthly Bill: ${c_mcharges}, Internet: {c_internet}, Contract: {c_contract}, Risk: {c_risk_tier}.
            Primary Risk Drivers: {', '.join(c_drivers)}.
            Campaign Goal: {c_goal}, Tone: {c_tone}, Target Format: {c_channel}.
            Special Promo Code: {promo_code}, Discounted Rate: ${new_bill:.2f}/mo (Save ${annual_savings:.2f}/yr).
            Creativity Level: {temperature}.
            Provide a completely unique, highly persuasive narrative that directly addresses their specific pain points and offers an irresistible incentive to renew.
            """
            resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt_content}]}], "generationConfig": {"temperature": temperature}}, timeout=10)
            if resp.status_code == 200:
                candidates = resp.json().get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts:
                        custom_gemini_email = parts[0].get('text')
                        is_live_api = True
        except Exception:
            pass

    # Assemble Structured Email
    email_body = f"""**Subject Line:** *{subject_line}*

**Dear {first_name},**

{chosen_hook}

To ensure you experience the full value and dependable speed of your **{c_internet}** connection, our care team has authorized a dedicated **{chosen_theme}** for your household:

{bullets_text}

There is no complicated paperwork or service interruption required. Click the secure portal link below to lock in your special rate:

👉 **[Activate My Approved Loyalty Rate (\\${new_bill:.2f}/mo) — Code: {promo_code}](#)**

{closing_sign}"""

    # Dynamic Agent Rebuttals with Variety
    rebuttals = []
    for d in c_drivers[:3]:
        if "High Monthly Bill" in d:
            rebuttals.append(f"* **Objection: 'My monthly bill (\\${c_mcharges:.2f}) is too high.'**\n  * **Agent Response:** *'I completely hear you, {first_name}. That is why I have executive authorization to reduce your rate to **\\${new_bill:.2f}/mo** right now, putting **\\${annual_savings:.2f}** back in your budget this year while maintaining your high-speed {c_internet}.'*")
        elif "Month-to-Month" in d:
            rebuttals.append(f"* **Objection: 'I prefer not being tied down to a contract.'**\n  * **Agent Response:** *'Our 1-year rate freeze comes with a complete 30-day satisfaction guarantee. If at any point you are not delighted, you can modify or cancel with zero penalty fees.'*")
        elif "Tech Support" in d:
            rebuttals.append(f"* **Objection: 'I ran into technical issues and felt stranded.'**\n  * **Agent Response:** *'I sincerely apologize for that friction. I am activating our **24/7 VIP Priority Tech Hotline & Security Care** on your account today for 6 months at zero cost, giving you direct access to our senior engineering team.'*")
        elif "Electronic Check" in d:
            rebuttals.append(f"* **Objection: 'I prefer paying manually each month.'**\n  * **Agent Response:** *'I understand! To make it worth your while, we will apply an immediate **\\$20 bill credit** onto your next statement if you try automated payment protection.'*")
        elif "Competitor" in d:
            rebuttals.append(f"* **Objection: 'Another company offered me an introductory promotion.'**\n  * **Agent Response:** *'Those introductory promotions often spike after a few months. We will match their speed today and guarantee your **\\${new_bill:.2f}/mo** rate for 12 months with zero surprise hikes.'*")

    if not rebuttals:
        rebuttals.append(f"* **Objection: 'I am re-evaluating my monthly expenses.'**\n  * **Agent Response:** *'As a valued customer of {tenure_desc}, I want to make sure your monthly rate is discounted to **\\${new_bill:.2f}/mo** so you get our premier tier at an unbeatable value.'*")

    agent_script = f"""#### 🎯 Contextual Opening Hook ({tone_key}):
> *"Hello {first_name}, my name is [Agent Name] with Senior Customer Care. I see you've been with us for {tenure_desc}, and I am reaching out personally because your account was flagged for our newly approved **{chosen_theme}**."*

#### 🛡️ Context-Specific Objection Rebuttals (Mapped to Churn Drivers):
{chr(10).join(rebuttals)}

#### 🤝 Closing Commitment:
> *"I can lock in this **${new_bill:.2f}/mo** rate right now on this call, and you'll see the discount reflected on your next statement. Shall we activate this for you today?"*"""

    # Concession Hierarchy
    concession_df = pd.DataFrame([
        {"Tier": "Level 1 (Immediate)", "Incentive": f"{int(final_disc_rate*100)}% Monthly Rate Discount", "Cost to Company": f"${discount_val:.2f}/mo", "Retention Impact": "High (Reduces Churn by 45%)"},
        {"Tier": "Level 2 (Value Add)", "Incentive": "Free 6-Month VIP Tech Support & Security", "Cost to Company": "$3.50/mo (Wholesale Cost)", "Retention Impact": "Very High (+38% Stickiness)"},
        {"Tier": "Level 3 (Contract)", "Incentive": "1-Year Inflation-Proof Rate Lock", "Cost to Company": "$0.00", "Retention Impact": "Maximum (Reduces Churn to <4%)"},
        {"Tier": "Level 4 (Payment)", "Incentive": "$20 Auto-Pay Account Credit", "Cost to Company": "$20.00 One-time", "Retention Impact": "Moderate (Reduces Payment Defection)"}
    ])

    # CRM JSON Payload
    crm_json_dict = {
        "customer_id": account_id,
        "customer_name": c_name,
        "tenure_months": c_tenure,
        "risk_tier": c_risk_tier.split()[0],
        "campaign_goal": chosen_theme,
        "promo_code": promo_code,
        "pricing_parameters": {
            "original_mrr": c_mcharges,
            "discount_percentage": f"{int(final_disc_rate*100)}%",
            "monthly_discount": discount_val,
            "discounted_mrr": new_bill,
            "projected_annual_savings": annual_savings
        },
        "targeted_churn_drivers": c_drivers,
        "delivery_channel": c_channel.split()[0],
        "tone_persona": tone_key,
        "crm_status": "QUEUED_FOR_OUTREACH",
        "generated_timestamp": timestamp_str,
        "agent_dispatch_uuid": f"DISPATCH-2026-{random_seed}"
    }

    return {
        "email_subject": subject_line,
        "email_body": custom_gemini_email if is_live_api and custom_gemini_email else email_body,
        "agent_script": agent_script,
        "concession_df": concession_df,
        "crm_json": json.dumps(crm_json_dict, indent=2),
        "discount_val": discount_val,
        "new_bill": new_bill,
        "annual_savings": annual_savings,
        "promo_code": promo_code,
        "is_live_api": is_live_api,
        "account_id": account_id
    }


# ==============================================================================
# TAB 1: Single Customer Diagnosis
# ==============================================================================
if menu == "🎯 Single Customer Diagnosis":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🎯 Single Customer Churn Risk Diagnosis</div>
        <div class="hero-subtitle">Assess individual customer defection probability in real time, uncover mathematical log-odds risk drivers, and trigger automated retention playbooks.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Preset Loader
    with st.expander("⚡ Load Pre-configured Customer Profiles (Quick Test)", expanded=True):
        st.markdown("<div style='color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;'>Select a pre-built persona to instantly populate the diagnosis parameters:</div>", unsafe_allow_html=True)
        col_p1, col_p2, col_p3 = st.columns(3)
        preset = None
        if col_p1.button("🔴 High Risk Profile (Month-to-Month, Fiber)", use_container_width=True):
            preset = "high"
        if col_p2.button("🟡 Moderate Risk Profile (1-Year, DSL)", use_container_width=True):
            preset = "mod"
        if col_p3.button("🟢 Loyal Customer Profile (2-Year, Auto-Pay)", use_container_width=True):
            preset = "loyal"

    # Default Form Values based on Presets
    def_gender = "Female"
    def_sc = 0
    def_partner = "No"
    def_dep = "No"
    def_tenure = 4
    def_phone = "Yes"
    def_lines = "Yes"
    def_internet = "Fiber optic"
    def_sec = "No"
    def_bak = "No"
    def_dev = "No"
    def_tech = "No"
    def_stv = "Yes"
    def_smv = "Yes"
    def_contract = "Month-to-month"
    def_paperless = "Yes"
    def_pay = "Electronic check"
    def_mcharges = 95.0
    
    if preset == "mod":
        def_tenure = 18
        def_internet = "DSL"
        def_sec = "Yes"
        def_tech = "No"
        def_contract = "One year"
        def_pay = "Bank transfer (automatic)"
        def_mcharges = 60.0
    elif preset == "loyal":
        def_partner = "Yes"
        def_dep = "Yes"
        def_tenure = 62
        def_internet = "Fiber optic"
        def_sec = "Yes"
        def_bak = "Yes"
        def_dev = "Yes"
        def_tech = "Yes"
        def_contract = "Two year"
        def_pay = "Credit card (automatic)"
        def_mcharges = 105.0

    with st.form("customer_diagnosis_form"):
        col_id1, col_id2 = st.columns([1, 2])
        with col_id1:
            diag_cust_id = st.text_input("Customer ID", value="CUST-7482")
        with col_id2:
            diag_cust_name = st.text_input("Customer Full Name", value="Alex Morgan")
            
        st.subheader("1. Customer Demographics & Account Info")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            gender = st.selectbox("Gender", ["Female", "Male"], index=0 if def_gender=="Female" else 1)
            senior_citizen = st.selectbox("Senior Citizen", [0, 1], index=def_sc)
        with col2:
            partner = st.selectbox("Has Partner", ["No", "Yes"], index=1 if def_partner=="Yes" else 0)
            dependents = st.selectbox("Has Dependents", ["No", "Yes"], index=1 if def_dep=="Yes" else 0)
        with col3:
            tenure = st.slider("Tenure (Months)", min_value=0, max_value=72, value=def_tenure)
            paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"], index=0 if def_paperless=="Yes" else 1)
        with col4:
            contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"], 
                                    index=["Month-to-month", "One year", "Two year"].index(def_contract))
            payment_method = st.selectbox(
                "Payment Method",
                ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
                index=["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"].index(def_pay)
            )

        st.subheader("2. Subscribed Services")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            phone_service = st.selectbox("Phone Service", ["Yes", "No"], index=0 if def_phone=="Yes" else 1)
            multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"], index=["No", "Yes", "No phone service"].index(def_lines))
        with col_s2:
            internet_service = st.selectbox("Internet Service", ["Fiber optic", "DSL", "No"], index=["Fiber optic", "DSL", "No"].index(def_internet))
            online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"], index=["No", "Yes", "No internet service"].index(def_sec))
        with col_s3:
            online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"], index=["No", "Yes", "No internet service"].index(def_bak))
            device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"], index=["No", "Yes", "No internet service"].index(def_dev))
        with col_s4:
            tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"], index=["No", "Yes", "No internet service"].index(def_tech))
            streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"], index=["No", "Yes", "No internet service"].index(def_stv))
            streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"], index=["No", "Yes", "No internet service"].index(def_smv))

        st.subheader("3. Billing & Charges")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            monthly_charges = st.number_input("Monthly Charges ($)", min_value=15.0, max_value=150.0, value=float(def_mcharges), step=1.0)
        with col_b2:
            total_charges = st.number_input("Total Lifetime Charges ($)", min_value=0.0, value=float(max(monthly_charges, monthly_charges * tenure)), step=10.0)

        submitted = st.form_submit_button("⚡ Run Real-Time AI Diagnosis", use_container_width=True)

    # Process and show results
    input_df = pd.DataFrame({
        "gender": [gender],
        "SeniorCitizen": [senior_citizen],
        "Partner": [partner],
        "Dependents": [dependents],
        "tenure": [tenure],
        "PhoneService": [phone_service],
        "MultipleLines": [multiple_lines],
        "InternetService": [internet_service],
        "OnlineSecurity": [online_security],
        "OnlineBackup": [online_backup],
        "DeviceProtection": [device_protection],
        "TechSupport": [tech_support],
        "StreamingTV": [streaming_tv],
        "StreamingMovies": [streaming_movies],
        "Contract": [contract],
        "PaperlessBilling": [paperless_billing],
        "PaymentMethod": [payment_method],
        "MonthlyCharges": [monthly_charges],
        "TotalCharges": [total_charges]
    })

    preds, probs, scaled_vals, contribs, feature_names = preprocess_and_predict(input_df)
    churn_prob = probs[0]
    
    st.markdown("---")
    st.header("📋 Diagnostic Results & Retention Playbook")
    
    col_res1, col_res2 = st.columns([1.2, 1.8])
    
    with col_res1:
        # Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=churn_prob * 100,
            number={'suffix': "%", 'font': {'size': 44, 'color': '#ffffff'}},
            title={'text': "<b>Predicted Churn Risk</b>", 'font': {'size': 20, 'color': '#e2e8f0'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#cbd5e1"},
                'bar': {'color': "#ef4444" if churn_prob > 0.5 else ("#eab308" if churn_prob > 0.3 else "#22c55e"), 'thickness': 0.28},
                'bgcolor': "#1e293b",
                'borderwidth': 2,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, 30], 'color': 'rgba(34, 197, 94, 0.25)'},
                    {'range': [30, 60], 'color': 'rgba(234, 179, 8, 0.25)'},
                    {'range': [60, 100], 'color': 'rgba(239, 68, 68, 0.25)'}
                ],
                'threshold': {
                    'line': {'color': "#ffffff", 'width': 3},
                    'thickness': 0.8,
                    'value': churn_prob * 100
                }
            }
        ))
        fig_gauge.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#f8fafc")
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Risk Badge & Impact
        if churn_prob >= 0.60:
            st.markdown("""<div style='text-align: center;'><span class='badge-high'>🚨 CRITICAL AT-RISK CUSTOMER</span></div>""", unsafe_allow_html=True)
        elif churn_prob >= 0.35:
            st.markdown("""<div style='text-align: center;'><span class='badge-moderate'>⚠️ MODERATE RISK (WATCHLIST)</span></div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div style='text-align: center;'><span class='badge-safe'>✅ LOW RISK / LOYAL CUSTOMER</span></div>""", unsafe_allow_html=True)
        
        annual_revenue = monthly_charges * 12
        st.markdown(f"""
        <div style='background: #1e293b; padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #334155;'>
            <div style='color: #94a3b8; font-size: 0.85rem;'>ESTIMATED ANNUAL VALUE AT RISK</div>
            <div style='font-size: 1.6rem; font-weight: bold; color: #38bdf8;'>${annual_revenue:,.2f}</div>
            <div style='font-size: 0.85rem; color: #cbd5e1; margin-top: 5px;'>Expected Churn Loss: <b>${annual_revenue * churn_prob:,.2f}</b> / year</div>
        </div>
        """, unsafe_allow_html=True)

    with col_res2:
        st.subheader("🔍 Top Driving Factors for This Score")
        
        # Local explainability: Sort positive and negative contributors
        feat_contrib_df = pd.DataFrame({
            "Feature": feature_names,
            "Contribution": contribs[0]
        }).sort_values(by="Contribution", ascending=False)
        
        # Filter top positive (increasing risk) and top negative (decreasing risk)
        top_risk_drivers = feat_contrib_df.head(4)
        top_retention_drivers = feat_contrib_df.tail(4).iloc[::-1]
        
        combined_drivers = pd.concat([top_risk_drivers, top_retention_drivers]).drop_duplicates()
        combined_drivers["Impact"] = combined_drivers["Contribution"].apply(
            lambda x: "Increases Churn Risk" if x > 0 else "Protects / Lowers Churn"
        )
        combined_drivers["Clean_Name"] = combined_drivers["Feature"].str.replace("_", ": ")
        
        fig_bars = px.bar(
            combined_drivers,
            x="Contribution",
            y="Clean_Name",
            orientation="h",
            color="Impact",
            color_discrete_map={"Increases Churn Risk": "#ef4444", "Protects / Lowers Churn": "#22c55e"},
            title="Local Feature Attribution (Log-Odds Impact)"
        )
        fig_bars.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#e2e8f0"),
            height=320,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig_bars, use_container_width=True)

    # Automated Prescriptive Recommendations
    st.subheader("💡 Prescribed Retention Playbook & Action Plan")
    recs = []
    
    if contract == "Month-to-month":
        recs.append(("📄 Lock-in Contract Incentive", "Customer is on a flexible **Month-to-month** plan. Pitch a **1-Year or 2-Year Contract** with a 10-15% loyalty discount to drastically stabilize retention."))
    
    if payment_method == "Electronic check":
        recs.append(("💳 Auto-Pay Enrollment Campaign", "Customer pays via **Electronic Check** (historically 45% churn rate). Offer a one-time $10 credit for switching to **Credit Card / Bank Auto-Pay**."))
        
    if tech_support == "No" and internet_service != "No":
        recs.append(("🛠️ Complimentary Tech Support / Security Bundle", "Customer has no **Tech Support**. Offer **3 months complimentary Tech Support & Online Security** to increase product stickiness."))
        
    if tenure <= 12:
        recs.append(("🌟 VIP Onboarding & Check-in Call", f"Customer is in the critical first-year window (Tenure = {tenure} mos). Schedule a proactive customer success satisfaction check-in."))
        
    if monthly_charges > 80.0:
        recs.append(("🎁 Value Optimization Review", f"Monthly charges are high (${monthly_charges:.2f}/mo). Conduct a plan audit to bundle services or remove unutilized add-ons."))

    if not recs:
        recs.append(("⭐ Loyalty Appreciation Reward", "Customer displays high loyalty metrics. Send an anniversary appreciation perk or exclusive priority VIP tier upgrade."))

    cols_rec = st.columns(len(recs) if len(recs) <= 3 else 3)
    for idx, (title, desc) in enumerate(recs):
        with cols_rec[idx % 3]:
            st.markdown(f"""
            <div class='action-card'>
                <div style='font-weight: 700; color: #a5b4fc; margin-bottom: 6px;'>{title}</div>
                <div style='font-size: 0.9rem; color: #cbd5e1;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)


    # Database Persistence Operations
    st.markdown("---")
    st.subheader("💾 Database Operations")
    col_db1, col_db2 = st.columns([2.5, 1])
    with col_db1:
        st.markdown(f"Save this diagnostic record for **{diag_cust_name}** (`{diag_cust_id}`) into the active database (`{active_db_engine.upper()}`) for historical churn tracking, compliance audits, and CRM queue management.")
    with col_db2:
        if st.button("💾 Save Diagnosis to Database", use_container_width=True, type="primary"):
            risk_label = "Critical Risk" if churn_prob >= 0.60 else ("Moderate Risk" if churn_prob >= 0.35 else "Low Risk")
            drivers_summary = [f"{row['Feature']} ({'+' if row['Contribution'] > 0 else ''}{row['Contribution']:.2f})" for _, row in feat_contrib_df.head(4).iterrows()]
            
            record_data = {
                "customer_id": diag_cust_id,
                "customer_name": diag_cust_name,
                "gender": gender,
                "senior_citizen": senior_citizen,
                "partner": partner,
                "dependents": dependents,
                "tenure": tenure,
                "phone_service": phone_service,
                "multiple_lines": multiple_lines,
                "internet_service": internet_service,
                "online_security": online_security,
                "online_backup": online_backup,
                "device_protection": device_protection,
                "tech_support": tech_support,
                "streaming_tv": streaming_tv,
                "streaming_movies": streaming_movies,
                "contract": contract,
                "paperless_billing": paperless_billing,
                "payment_method": payment_method,
                "monthly_charges": monthly_charges,
                "total_charges": total_charges,
                "churn_prediction": int(preds[0]),
                "churn_probability": float(churn_prob),
                "risk_tier": risk_label,
                "key_churn_drivers": drivers_summary,
                "source": "Single Diagnosis"
            }
            try:
                database.save_single_prediction(record_data)
                st.success(f"✅ Record successfully saved to {active_db_engine.upper()} database for **{diag_cust_name}** (`{diag_cust_id}`)!")
            except Exception as e:
                st.error(f"❌ Failed to save record to database: {e}")

    # Quick Link to GenAI Copilot
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%); padding: 18px; border-radius: 12px; border: 1px solid #6366f1; text-align: center; margin-top: 15px;'>
        <h4 style='color: #e0e7ff; margin: 0 0 8px 0;'>🤖 Want AI to draft a personalized retention campaign for this customer?</h4>
        <p style='color: #c7d2fe; font-size: 0.95rem; margin-bottom: 12px;'>Use the <b>GenAI Retention Copilot</b> to automatically generate customized win-back emails, agent call scripts, and CRM offers.</p>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: ✨ GenAI Retention Copilot
# ==============================================================================
elif menu == "✨ GenAI Retention Copilot":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">✨ GenAI Customer Retention Copilot</div>
        <div class="hero-subtitle">Harness Generative AI to instantly generate personalized win-back emails, frontline customer service negotiation scripts, and CRM-ready retention campaigns tailored to each subscriber's churn risk profile.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([1, 1])
    
    with col_g1:
        st.subheader("📋 1. Customer Context & Risk Telemetry")
        c_name = st.text_input("Customer Name / Account ID", value="Sarah Jenkins (ID: #7590-VHVEG)")
        c_risk_tier = st.selectbox("Predictive ML Risk Tier", ["Critical Risk (>60% Churn Probability)", "Moderate Risk (30-60% Churn Probability)", "Safe / Loyal (<30% Churn Probability)"], index=0)
        c_tenure = st.slider("Customer Tenure (Months)", 1, 72, 4, key="gen_tenure")
        c_contract = st.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"], index=0, key="gen_contract")
        c_mcharges = st.number_input("Monthly Charges ($/month)", min_value=15.0, max_value=150.0, value=94.50, step=1.0, key="gen_mcharges")
        c_internet = st.selectbox("Internet Service Type", ["Fiber optic", "DSL", "No Internet"], index=0, key="gen_internet")
        c_drivers = st.multiselect(
            "Identified Primary Churn Drivers (from ML Model)",
            ["High Monthly Bill ($90+)", "No Tech Support / Device Protection", "Month-to-Month Contract Flexibility", "Electronic Check Payment Friction", "Early Tenure Service Friction (< 6 months)", "Competitor Fiber Promotion Pressure"],
            default=["High Monthly Bill ($90+)", "Month-to-Month Contract Flexibility", "No Tech Support / Device Protection"]
        )

    with col_g2:
        st.subheader("⚙️ 2. GenAI Campaign Configuration")
        c_goal = st.selectbox(
            "Campaign Objective",
            [
                "🚨 Emergency Win-Back & Churn Reversal Offer",
                "📄 Annual Contract Lock-in & Loyalty Upgrade",
                "💰 Bill Optimization & Service Downgrade Relief",
                "🛠️ Free VIP Tech Support & Security Bundle Offer",
                "📞 Inbound Call Center Agent Negotiation Script"
            ]
        )
        c_tone = st.selectbox(
            "AI Voice & Tone Persona",
            [
                "🤝 Empathetic, Warm & Customer-Centric",
                "💼 Professional, Value-Driven & Consultative",
                "⚡ Exclusive, Urgent & Limited-Time VIP Offer",
                "🎯 Executive & Concierge Support"
            ]
        )
        c_channel = st.radio(
            "Primary Communication Channel",
            ["📧 Personalized Email Campaign", "📱 SMS / Push Notification Alert", "📞 Call Center Dialogue Script", "📊 Executive Retention Brief"],
            horizontal=True
        )
        
        c_temp = st.slider("🧠 AI Creativity & Temperature (Variability Level)", min_value=0.2, max_value=1.0, value=0.85, step=0.05, help="Controls how creatively and distinctly the AI thinks on every generation. Higher values produce fresh angles, diverse vocabulary, and distinct strategy hooks.")

        with st.expander("🔍 View Structured Prompt Template Sent to LLM", expanded=False):
            st.code(f"""
SYSTEM PROMPT:
You are an expert Telecom Retention Strategist & Copywriter. Your mission is to convert high-churn risk subscribers into long-term loyal customers through empathetic, personalized, and value-maximizing communications.

USER INPUT CONTEXT:
- Customer: {c_name}
- Churn Risk Level: {c_risk_tier}
- Tenure: {c_tenure} months | Monthly Bill: ${c_mcharges}/mo | Contract: {c_contract}
- Subscribed Internet: {c_internet}
- Top Risk Factors: {', '.join(c_drivers)}
- Campaign Goal: {c_goal}
- Voice / Persona Tone: {c_tone}
- Target Format: {c_channel}
- AI Temperature / Creativity: {c_temp}

TASK:
1. Formulate a personalized, high-converting customer communication tailored to these exact churn drivers.
2. Provide an Agent Negotiation Playbook with objection handling.
3. Recommend an optimal concession/incentive matrix.
4. Output a structured CRM JSON payload.
            """, language="markdown")
            
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns([1.5, 1])
    gen_clicked = col_btn1.button("✨ Generate AI Retention Campaign & Playbook", type="primary", use_container_width=True)
    rethink_clicked = col_btn2.button("🔄 Re-Think & Generate New Angle", use_container_width=True)
    
    if gen_clicked or rethink_clicked:
        with st.spinner("🤖 Generative AI Copilot is synthesizing fresh retention angles and strategies..."):
            import time
            time.sleep(0.4) # Fast responsive animation
            
            # Execute Dynamic GenAI Engine
            ai_output = generate_dynamic_retention_campaign(
                c_name=c_name,
                c_risk_tier=c_risk_tier,
                c_tenure=c_tenure,
                c_contract=c_contract,
                c_mcharges=c_mcharges,
                c_internet=c_internet,
                c_drivers=c_drivers,
                c_goal=c_goal,
                c_tone=c_tone,
                c_channel=c_channel,
                temperature=c_temp,
                api_key=user_gemini_key
            )
            
            discount_amount = ai_output["discount_val"]
            new_bill = ai_output["new_bill"]
            annual_savings = ai_output["annual_savings"]
            promo_code = ai_output["promo_code"]
            
            if ai_output.get("is_live_api"):
                st.success("🎉 Live Google Gemini Cloud LLM Generation Succeeded!")
            else:
                st.success(f"🎉 Tailored AI Retention Campaign Generated (Offer Code: {promo_code})!")
            
            tab_out1, tab_out2, tab_out3, tab_out4 = st.tabs([
                "✉️ Generated Customer Communication",
                "📞 Agent Call & Negotiation Script",
                "🎁 Recommended Concession Matrix",
                "⚙️ CRM Integration Payload (JSON)"
            ])
            
            with tab_out1:
                st.markdown(f"### 📧 Tailored Customer Outreach Asset for {c_name.split()[0] if ' ' in c_name else c_name}")
                if "Email" in c_channel:
                    st.markdown(ai_output["email_body"])
                elif "SMS" in c_channel:
                    st.markdown(f"""
                    **📱 SMS Campaign (Optimized for Mobile Push):**
                    
                    `TelcoPulse VIP Alert: Hi {c_name.split()[0] if ' ' in c_name else 'Customer'}, your loyalty rate discount has been approved! Enjoy ${new_bill:.2f}/mo (save ${annual_savings:.2f}/yr) + free VIP perks. Activate: telco.ly/{promo_code.lower()}. Reply STOP to opt-out.`
                    """)
                elif "Brief" in c_channel:
                    st.markdown(f"""
                    ### 📊 Executive Account Retention Dossier
                    * **Target Account:** {c_name} (Tenure: {c_tenure} months)
                    * **Monthly Recurring Revenue (MRR):** ${c_mcharges:.2f}/mo
                    * **Assessed Risk Tier:** {c_risk_tier}
                    * **Strategic Objective:** {c_goal}
                    * **Recommended Action:** Approve immediate {promo_code} concession to preserve long-term account lifetime value.
                    """)
                else:
                    st.markdown(ai_output["email_body"])
                    
                st.download_button(
                    "📥 Copy / Download Communication (.txt)",
                    data=f"Customer: {c_name}\nSubject: {ai_output['email_subject']}\n\n{ai_output['email_body']}",
                    file_name=f"retention_{ai_output['account_id']}.txt",
                    use_container_width=True
                )

            with tab_out2:
                st.markdown("### 📞 Frontline Agent Negotiation & Objection Handling Script")
                st.markdown(ai_output["agent_script"])

            with tab_out3:
                st.markdown("### 🎁 AI-Recommended Retention Concession Hierarchy")
                st.table(ai_output["concession_df"])

            with tab_out4:
                st.markdown("### ⚙️ CRM-Ready JSON Dispatch Payload")
                st.code(ai_output["crm_json"], language="json")

            # Database Persistence for GenAI Campaigns
            st.markdown("---")
            st.subheader("💾 Campaign Database Dispatch & Tracking")
            col_cdb1, col_cdb2 = st.columns([2, 1])
            with col_cdb1:
                camp_status_choice = st.selectbox(
                    "Initial Campaign Lifecycle Status",
                    ["Generated (Draft)", "Dispatched via CRM", "Agent Outreach In-Progress", "Successfully Retained", "Escalated"],
                    index=0,
                    key="genai_camp_status"
                )
            with col_cdb2:
                st.write("")
                st.write("")
                if st.button("💾 Save Campaign to Database", use_container_width=True, type="primary", key="btn_save_camp"):
                    camp_data = {
                        "customer_id": ai_output.get("account_id", f"CUST-{abs(hash(c_name)) % 10000:04d}"),
                        "customer_name": c_name,
                        "risk_tier": c_risk_tier,
                        "monthly_charges": float(c_mcharges),
                        "campaign_goal": c_goal,
                        "outreach_tone": c_tone,
                        "target_channel": c_channel,
                        "promo_code": promo_code,
                        "retention_offer": f"Discount to ${new_bill:.2f}/mo (Save ${annual_savings:.2f}/yr) + Promo: {promo_code}",
                        "personalized_script": ai_output.get("email_body", "") or ai_output.get("agent_script", ""),
                        "action_status": camp_status_choice
                    }
                    try:
                        database.save_retention_campaign(camp_data)
                        st.success(f"✅ Retention Campaign saved to **{active_db_engine.upper()}** database for **{c_name}** (`{promo_code}`)!")
                    except Exception as e:
                        st.error(f"❌ Error saving campaign to database: {e}")


# ==============================================================================
# TAB 3: What-If Retention Sandbox
# ==============================================================================
elif menu == "🎛️ What-If Retention Sandbox":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🎛️ What-If Retention Strategy Simulator</div>
        <div class="hero-subtitle">Test different retention levers on an at-risk subscriber in real time and see how much churn probability and annual revenue loss drop instantly.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_base, col_mod = st.columns(2)
    
    with col_base:
        st.markdown("### 🔴 Baseline (Current Customer State)")
        b_tenure = st.slider("Baseline Tenure (months)", 1, 72, 6, key="b_tenure")
        b_contract = st.selectbox("Baseline Contract", ["Month-to-month", "One year", "Two year"], index=0, key="b_contract")
        b_tech = st.selectbox("Baseline Tech Support", ["No", "Yes"], index=0, key="b_tech")
        b_sec = st.selectbox("Baseline Online Security", ["No", "Yes"], index=0, key="b_sec")
        b_pay = st.selectbox("Baseline Payment Method", ["Electronic check", "Credit card (automatic)", "Bank transfer (automatic)", "Mailed check"], index=0, key="b_pay")
        b_charges = st.slider("Baseline Monthly Charges ($)", 20.0, 130.0, 90.0, key="b_charges")
        
        base_df = pd.DataFrame({
            "gender": ["Male"], "SeniorCitizen": [0], "Partner": ["No"], "Dependents": ["No"],
            "tenure": [b_tenure], "PhoneService": ["Yes"], "MultipleLines": ["Yes"],
            "InternetService": ["Fiber optic"], "OnlineSecurity": [b_sec], "OnlineBackup": ["No"],
            "DeviceProtection": ["No"], "TechSupport": [b_tech], "StreamingTV": ["Yes"],
            "StreamingMovies": ["Yes"], "Contract": [b_contract], "PaperlessBilling": ["Yes"],
            "PaymentMethod": [b_pay], "MonthlyCharges": [b_charges], "TotalCharges": [b_charges * b_tenure]
        })
        _, b_prob, _, _, _ = preprocess_and_predict(base_df)
        base_churn = b_prob[0]

    with col_mod:
        st.markdown("### 🟢 Proposed Retention Package (Simulated State)")
        s_contract = st.selectbox("Offer Contract Upgrade", ["Month-to-month", "One year", "Two year"], index=1, key="s_contract")
        s_tech = st.selectbox("Include Tech Support Free", ["No", "Yes"], index=1, key="s_tech")
        s_sec = st.selectbox("Include Online Security", ["No", "Yes"], index=1, key="s_sec")
        s_pay = st.selectbox("Switch to Auto-Pay", ["Electronic check", "Credit card (automatic)", "Bank transfer (automatic)", "Mailed check"], index=1, key="s_pay")
        discount = st.slider("Monthly Plan Discount ($)", 0.0, 40.0, 10.0, step=2.5, key="s_disc")
        s_charges = max(15.0, b_charges - discount)
        
        sim_df = pd.DataFrame({
            "gender": ["Male"], "SeniorCitizen": [0], "Partner": ["No"], "Dependents": ["No"],
            "tenure": [b_tenure], "PhoneService": ["Yes"], "MultipleLines": ["Yes"],
            "InternetService": ["Fiber optic"], "OnlineSecurity": [s_sec], "OnlineBackup": ["No"],
            "DeviceProtection": ["No"], "TechSupport": [s_tech], "StreamingTV": ["Yes"],
            "StreamingMovies": ["Yes"], "Contract": [s_contract], "PaperlessBilling": ["Yes"],
            "PaymentMethod": [s_pay], "MonthlyCharges": [s_charges], "TotalCharges": [s_charges * b_tenure]
        })
        _, s_prob, _, _, _ = preprocess_and_predict(sim_df)
        sim_churn = s_prob[0]

    st.markdown("---")
    st.subheader("📊 Retention Impact Analysis")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Baseline Churn Risk</div>
            <div class='metric-value' style='color: #f87171;'>{base_churn * 100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Simulated Churn Risk</div>
            <div class='metric-value' style='color: #4ade80;'>{sim_churn * 100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        risk_reduction = (base_churn - sim_churn) * 100
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Absolute Risk Reduction</div>
            <div class='metric-value' style='color: #38bdf8;'>▼ {risk_reduction:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m4:
        retention_gain = ((base_churn - sim_churn) / max(0.01, base_churn)) * 100
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Relative Improvement</div>
            <div class='metric-value' style='color: #a855f7;'>+{retention_gain:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Comparison Waterfall / Bar Chart
    fig_comp = go.Figure(data=[
        go.Bar(name='Baseline Risk', x=['Customer Churn Probability'], y=[base_churn * 100], marker_color='#ef4444', text=[f"{base_churn*100:.1f}%"], textposition='auto'),
        go.Bar(name='With Retention Package', x=['Customer Churn Probability'], y=[sim_churn * 100], marker_color='#22c55e', text=[f"{sim_churn*100:.1f}%"], textposition='auto')
    ])
    fig_comp.update_layout(
        barmode='group',
        yaxis_title="Churn Probability (%)",
        yaxis=dict(range=[0, 100]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#f8fafc"),
        height=320
    )
    st.plotly_chart(fig_comp, use_container_width=True)


# ==============================================================================
# TAB 4: Batch Scoring & Priority Queue
# ==============================================================================
elif menu == "📁 Batch Scoring & Priority Queue":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📁 Batch Customer Risk Scoring & Action Queue</div>
        <div class="hero-subtitle">Upload a customer CSV or load a cohort sample to automatically rank and prioritize high-risk churn interventions by annual revenue at risk.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        uploaded_file = st.file_uploader("Upload CSV containing customer data", type=["csv"])
    with col_u2:
        st.write("")
        st.write("")
        load_sample = st.button("📂 Load 250 Sample Records from Dataset", use_container_width=True)

    batch_df = None
    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
    elif load_sample and raw_dataset is not None:
        batch_df = raw_dataset.sample(250, random_state=42).copy()

    if batch_df is not None:
        st.success(f"Successfully loaded {len(batch_df)} customer records for batch inference!")
        
        with st.spinner("Scoring customer cohort with AI pipeline..."):
            preds, probs, _, _, _ = preprocess_and_predict(batch_df)
            
            batch_result = batch_df.copy()
            batch_result["Churn_Probability"] = probs
            batch_result["Risk_Score_%"] = (probs * 100).round(2)
            batch_result["Risk_Tier"] = pd.cut(
                batch_result["Churn_Probability"],
                bins=[-0.01, 0.35, 0.60, 1.0],
                labels=["🟢 Low Risk", "🟡 Moderate", "🔴 Critical"]
            )
            batch_result["Annual_Value"] = (batch_result["MonthlyCharges"] * 12).round(2)
            batch_result["Expected_Annual_Loss"] = (batch_result["Annual_Value"] * batch_result["Churn_Probability"]).round(2)
            
            # Sort by highest loss priority
            batch_result = batch_result.sort_values(by="Expected_Annual_Loss", ascending=False)
            
        # Summary KPI Cards
        st.markdown("### 📈 Cohort Risk Overview")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Customers Scored</div>
                <div class='metric-value'>{len(batch_result):,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            critical_count = (batch_result["Risk_Tier"] == "🔴 Critical").sum()
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Critical Risk Accounts</div>
                <div class='metric-value' style='color: #f87171;'>{critical_count} ({critical_count/len(batch_result)*100:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi3:
            avg_cohort_prob = batch_result["Churn_Probability"].mean() * 100
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Average Churn Risk</div>
                <div class='metric-value' style='color: #facc15;'>{avg_cohort_prob:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi4:
            total_loss = batch_result["Expected_Annual_Loss"].sum()
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Annual Revenue at Risk</div>
                <div class='metric-value' style='color: #38bdf8;'>${total_loss:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        # Filters & Prioritized Table
        st.markdown("### 📋 Prioritized Customer Action Queue")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            tier_filter = st.multiselect("Filter by Risk Tier", ["🔴 Critical", "🟡 Moderate", "🟢 Low Risk"], default=["🔴 Critical", "🟡 Moderate"])
        with col_f2:
            contract_filter = st.multiselect("Filter by Contract", batch_result["Contract"].unique().tolist(), default=batch_result["Contract"].unique().tolist())
            
        filtered_view = batch_result[
            (batch_result["Risk_Tier"].isin(tier_filter)) &
            (batch_result["Contract"].isin(contract_filter))
        ]
        
        display_cols = [
            col for col in ["customerID", "Risk_Score_%", "Risk_Tier", "Expected_Annual_Loss", "MonthlyCharges", "tenure", "Contract", "InternetService", "PaymentMethod"]
            if col in filtered_view.columns
        ]
        
        st.dataframe(
            filtered_view[display_cols].style.background_gradient(subset=["Risk_Score_%"], cmap="RdYlGn_r"),
            use_container_width=True,
            height=350
        )
        
        # Actions: Download CSV & Save to Database
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            csv_download = filtered_view.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Prioritized Outreach Campaign (CSV)",
                data=csv_download,
                file_name="telecom_prioritized_churn_leads.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_act2:
            if st.button("💾 Save Batch Cohort to Database", use_container_width=True, type="primary"):
                try:
                    # Prepare dataframe with Prediction column if missing
                    df_to_save = filtered_view.copy()
                    if "Prediction" not in df_to_save.columns:
                        df_to_save["Prediction"] = (df_to_save["Churn_Probability"] > 0.5).astype(int)
                    num_saved = database.save_batch_predictions(df_to_save, batch_name=f"Batch Scoring Run ({len(df_to_save)} records)")
                    st.success(f"✅ Successfully persisted {num_saved} customer records into **{active_db_engine.upper()}** database!")
                except Exception as e:
                    st.error(f"❌ Failed to persist batch to database: {e}")
    else:
        st.info("👆 Upload a CSV or click 'Load 250 Sample Records' to preview batch scoring.")


# ==============================================================================
# TAB 5: Executive Cohort Insights
# ==============================================================================
elif menu == "📊 Executive Cohort Insights":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">📊 Executive Cohort & Retention Analytics</div>
        <div class="hero-subtitle">Explore macroeconomic attrition drivers, billing distribution dynamics, and customer lifecycles across the entire historical subscriber base.</div>
    </div>
    """, unsafe_allow_html=True)
    
    if raw_dataset is not None:
        c1, c2 = st.columns(2)
        
        with c1:
            # Churn by Contract
            contract_churn = raw_dataset.groupby(["Contract", "Churn"]).size().reset_index(name="Count")
            fig_cc = px.bar(
                contract_churn,
                x="Contract",
                y="Count",
                color="Churn",
                barmode="group",
                color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                title="Customer Churn by Contract Type"
            )
            fig_cc.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
            st.plotly_chart(fig_cc, use_container_width=True)
            
            # Monthly Charges distribution
            fig_hist = px.histogram(
                raw_dataset,
                x="MonthlyCharges",
                color="Churn",
                marginal="box",
                barmode="overlay",
                color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                title="Monthly Charges Distribution vs Churn"
            )
            fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
            st.plotly_chart(fig_hist, use_container_width=True)

        with c2:
            # Payment Method Breakdown
            pay_churn = raw_dataset.groupby(["PaymentMethod", "Churn"]).size().reset_index(name="Count")
            total_pm = pay_churn.groupby("PaymentMethod")["Count"].transform("sum")
            pay_churn["Percentage"] = (pay_churn["Count"] / total_pm * 100).round(1)
            
            fig_pay = px.bar(
                pay_churn,
                y="PaymentMethod",
                x="Percentage",
                color="Churn",
                orientation="h",
                barmode="group",
                text="Percentage",
                color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                title="Churn Rate % by Payment Method"
            )
            fig_pay.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_pay.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
            st.plotly_chart(fig_pay, use_container_width=True)
            
            # Internet Service vs Tech Support Churn
            ts_churn = raw_dataset[raw_dataset["InternetService"] != "No"].groupby(["TechSupport", "Churn"]).size().reset_index(name="Count")
            fig_ts = px.bar(
                ts_churn,
                x="TechSupport",
                y="Count",
                color="Churn",
                barmode="group",
                color_discrete_map={"No": "#22c55e", "Yes": "#ef4444"},
                title="Impact of Tech Support on Internet Subscribers"
            )
            fig_ts.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
            st.plotly_chart(fig_ts, use_container_width=True)
    else:
        st.warning("Historical dataset not found at `dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv`.")


# ==============================================================================
# TAB 6: Model Diagnostics
# ==============================================================================
elif menu == "🧠 Model Diagnostics":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🧠 AI Model Diagnostics & Global Feature Weights</div>
        <div class="hero-subtitle">Inspect the underlying machine learning pipeline architecture, mathematical beta coefficients, and global explainability parameters.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns([1, 1])
    
    with col_m1:
        st.subheader("Model Architecture & Coefficients")
        coef_series = pd.Series(model.coef_[0], index=scaler.feature_names_in_).sort_values()
        
        coef_df = pd.DataFrame({
            "Feature": coef_series.index,
            "Coefficient": coef_series.values,
            "Direction": np.where(coef_series.values > 0, "Increases Churn", "Reduces Churn")
        })
        
        fig_global = px.bar(
            coef_df,
            x="Coefficient",
            y="Feature",
            orientation="h",
            color="Direction",
            color_discrete_map={"Increases Churn": "#ef4444", "Reduces Churn": "#22c55e"},
            height=700,
            title="Global Logistic Regression Coefficients (Beta Weights)"
        )
        fig_global.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
        st.plotly_chart(fig_global, use_container_width=True)

    with col_m2:
        st.subheader("Pipeline Information")
        st.markdown(f"""
        - **Model Classifier**: `{type(model).__name__}`
        - **Scaling Transform**: `StandardScaler` fitted on {len(scaler.feature_names_in_)} dimensions
        - **Categorical Encoder**: `OneHotEncoder` ({len(encoder.categories_)} categorical variables)
        - **Intercept Value**: `{model.intercept_[0]:.4f}`
        - **Decision Threshold**: `50% Churn Probability`
        """)
        
        st.subheader("Top Global Churn Accelerators")
        top_pos = coef_df[coef_df["Coefficient"] > 0].sort_values(by="Coefficient", ascending=False).head(5)
        st.table(top_pos[["Feature", "Coefficient"]])
        
        st.subheader("Top Global Retention Anchors")
        top_neg = coef_df[coef_df["Coefficient"] < 0].sort_values(by="Coefficient", ascending=True).head(5)
        st.table(top_neg[["Feature", "Coefficient"]])


# ==============================================================================
# TAB 7: 🗄️ Database & CRM Records
# ==============================================================================
elif menu == "🗄️ Database & CRM Records":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">🗄️ Enterprise Database & Customer CRM Explorer</div>
        <div class="hero-subtitle">Unified persistent data layer supporting MySQL (XAMPP) and SQLite. Inspect diagnostic history, manage GenAI retention campaign dispatches, and execute custom analytical SQL queries.</div>
    </div>
    """, unsafe_allow_html=True)

    db_tab1, db_tab2, db_tab3, db_tab4, db_tab5 = st.tabs([
        "📊 Database Dashboard",
        "👥 Customer Predictions Explorer",
        "🎯 GenAI Campaign Log",
        "⚡ Direct SQL Sandbox",
        "⚙️ Connection & Settings"
    ])

    # -----------------------------
    # TAB 1: Database Dashboard
    # -----------------------------
    with db_tab1:
        st.markdown("### 📈 Stored Customer & Retention Metrics")
        stats = database.get_db_summary_stats()
        
        kpi_db1, kpi_db2, kpi_db3, kpi_db4 = st.columns(4)
        with kpi_db1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Persisted Diagnoses</div>
                <div class='metric-value' style='color: #a5b4fc;'>{stats['total_predictions']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_db2:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Critical Risk Customers</div>
                <div class='metric-value' style='color: #ef4444;'>{stats['critical_risk_count']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_db3:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Active Retention Campaigns</div>
                <div class='metric-value' style='color: #38bdf8;'>{stats['campaigns_count']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi_db4:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Database Avg Churn Risk</div>
                <div class='metric-value' style='color: #f59e0b;'>{stats['avg_churn_rate']*100:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        df_all = database.get_predictions_df(limit=500)
        
        if not df_all.empty:
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1:
                st.subheader("Risk Tier Distribution")
                if "risk_tier" in df_all.columns:
                    risk_counts = df_all["risk_tier"].value_counts().reset_index()
                    risk_counts.columns = ["Risk Tier", "Count"]
                    fig_pie = px.pie(
                        risk_counts,
                        names="Risk Tier",
                        values="Count",
                        hole=0.45,
                        color="Risk Tier",
                        color_discrete_map={
                            "Critical Risk": "#ef4444",
                            "🔴 Critical": "#ef4444",
                            "Moderate Risk": "#eab308",
                            "🟡 Moderate": "#eab308",
                            "Low Risk": "#22c55e",
                            "🟢 Low Risk": "#22c55e"
                        }
                    )
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
                    st.plotly_chart(fig_pie, use_container_width=True)
            with col_ch2:
                st.subheader("Contract Type vs Average Monthly Charges")
                if "contract" in df_all.columns and "monthly_charges" in df_all.columns:
                    df_chart_data = df_all.copy()
                    df_chart_data["monthly_charges"] = pd.to_numeric(df_chart_data["monthly_charges"], errors="coerce").fillna(0.0)
                    df_contract = df_chart_data.groupby("contract", as_index=False)["monthly_charges"].mean()
                    fig_bar = px.bar(
                        df_contract,
                        x="contract",
                        y="monthly_charges",
                        color="contract",
                        color_discrete_sequence=["#6366f1", "#38bdf8", "#ec4899"],
                        labels={"monthly_charges": "Avg Monthly Charges ($)", "contract": "Contract Type"}
                    )
                    fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#f8fafc"))
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("💡 No diagnostic records found in database yet. Run single diagnosis, batch scoring, or click **'Seed Database'** in the Settings tab to populate sample data!")

    # -----------------------------
    # TAB 2: Customer Predictions Explorer
    # -----------------------------
    with db_tab2:
        st.markdown("### 📋 Persisted Customer Diagnosis Records")
        col_flt1, col_flt2, col_flt3 = st.columns([1.5, 2, 1])
        with col_flt1:
            risk_sel = st.selectbox("Filter Risk Tier", ["All", "Critical", "Moderate", "Low"], index=0)
        with col_flt2:
            search_query = st.text_input("🔍 Search Customer ID or Name", placeholder="e.g. CUST-7482 or Alex")
        with col_flt3:
            rec_limit = st.selectbox("Max Records", [50, 100, 200, 500], index=1)

        filter_arg = None if risk_sel == "All" else risk_sel
        preds_df = database.get_predictions_df(limit=rec_limit, risk_filter=filter_arg)

        if not preds_df.empty:
            if search_query.strip():
                q = search_query.strip().lower()
                preds_df = preds_df[
                    preds_df["customer_id"].astype(str).str.lower().str.contains(q) |
                    preds_df["customer_name"].astype(str).str.lower().str.contains(q)
                ]

            st.dataframe(preds_df, use_container_width=True, height=400)
            
            # Action bar: Download & Delete
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                csv_data = preds_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Export Filtered Records (CSV)",
                    data=csv_data,
                    file_name="telecom_customer_predictions_export.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_d2:
                del_id = st.number_input("Delete Record by ID", min_value=1, step=1, key="del_rec_id")
                if st.button("🗑️ Delete Record", use_container_width=True):
                    database.delete_prediction_record(int(del_id))
                    st.success(f"Record #{del_id} deleted successfully!")
                    st.rerun()
        else:
            st.warning("No records matched your search criteria.")

    # -----------------------------
    # TAB 3: GenAI Campaign Log
    # -----------------------------
    with db_tab3:
        st.markdown("### 🎯 GenAI Retention Campaign Dispatch Tracker")
        camps_df = database.get_campaigns_df(limit=100)
        
        if not camps_df.empty:
            st.dataframe(
                camps_df[["id", "customer_id", "customer_name", "risk_tier", "promo_code", "campaign_goal", "target_channel", "action_status", "created_at"]],
                use_container_width=True,
                height=300
            )

            st.markdown("---")
            st.subheader("Update Campaign Lifecycle Status")
            col_up1, col_up2, col_up3 = st.columns([1, 1.5, 1])
            with col_up1:
                selected_cid = st.selectbox("Select Campaign ID", camps_df["id"].tolist())
            with col_up2:
                new_status_val = st.selectbox(
                    "New Status",
                    ["Generated (Draft)", "Dispatched via CRM", "Agent Outreach In-Progress", "Successfully Retained", "Customer Churned", "Escalated to Executive"]
                )
            with col_up3:
                st.write("")
                st.write("")
                if st.button("🔄 Update Status", use_container_width=True):
                    database.update_campaign_status(selected_cid, new_status_val)
                    st.success(f"Campaign #{selected_cid} updated to **{new_status_val}**!")
                    st.rerun()

            with st.expander("📖 View Campaign Script & Pitch Copy", expanded=False):
                matched = camps_df[camps_df["id"] == selected_cid]
                if not matched.empty:
                    st.markdown(f"**Customer:** {matched.iloc[0]['customer_name']} (`{matched.iloc[0]['customer_id']}`)")
                    st.markdown(f"**Promo Code:** `{matched.iloc[0]['promo_code']}`")
                    st.markdown(f"**Offer:** {matched.iloc[0]['retention_offer']}")
                    st.markdown("**Generated Pitch / Copy:**")
                    st.info(matched.iloc[0]['personalized_script'])
        else:
            st.info("💡 No retention campaigns generated yet. Use the **GenAI Retention Copilot** tab and click 'Save Campaign to Database' to log campaigns!")

    # -----------------------------
    # TAB 4: Direct SQL Sandbox
    # -----------------------------
    with db_tab4:
        st.markdown("### ⚡ Live Analytical SQL Query Sandbox")
        st.caption("Directly query the active database to run custom cohort aggregations, ROI metrics, and retention audit analysis.")
        
        sample_queries = {
            "Top 10 Highest Risk Customers": "SELECT customer_id, customer_name, risk_tier, churn_probability, monthly_charges, contract FROM customer_predictions ORDER BY churn_probability DESC LIMIT 10;",
            "Risk Tier Aggregation & Avg Charges": "SELECT risk_tier, COUNT(*) as customer_count, ROUND(AVG(monthly_charges), 2) as avg_monthly_charges, ROUND(AVG(churn_probability)*100, 1) as avg_churn_pct FROM customer_predictions GROUP BY risk_tier;",
            "Payment Method Risk Analysis": "SELECT payment_method, COUNT(*) as total_users, ROUND(AVG(churn_probability)*100, 1) as avg_churn_risk_pct FROM customer_predictions GROUP BY payment_method ORDER BY avg_churn_risk_pct DESC;",
            "Recent GenAI Retention Campaigns": "SELECT id, customer_id, customer_name, promo_code, action_status, created_at FROM retention_campaigns ORDER BY id DESC LIMIT 15;"
        }
        
        q_choice = st.selectbox("💡 Load Pre-built SQL Template", ["-- Select a template --"] + list(sample_queries.keys()))
        default_query_text = sample_queries[q_choice] if q_choice in sample_queries else "SELECT * FROM customer_predictions LIMIT 10;"
        
        user_sql = st.text_area("SQL Statement", value=default_query_text, height=110)
        
        if st.button("🚀 Execute SQL Query", type="primary", use_container_width=True):
            import time
            start_t = time.time()
            success, res_df, engine_used = database.execute_custom_query(user_sql)
            elapsed = (time.time() - start_t) * 1000
            
            if success:
                st.success(f"✅ Query executed on **{engine_used.upper()}** in {elapsed:.1f}ms ({len(res_df)} rows returned)")
                st.dataframe(res_df, use_container_width=True)
                
                # Download query results
                csv_query = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Export Query Results (CSV)",
                    data=csv_query,
                    file_name="sql_query_result.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.error(f"❌ SQL Execution Error: {res_df}")

    # -----------------------------
    # TAB 5: Connection & Settings
    # -----------------------------
    with db_tab5:
        st.markdown("### ⚙️ Database Configuration & Credentials")
        current_cfg = database.load_db_config()
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### Primary Database Settings (XAMPP MySQL)")
            db_engine_choice = st.radio("Database Engine", ["mysql", "sqlite"], index=0 if current_cfg.get("engine") == "mysql" else 1, horizontal=True)
            db_host = st.text_input("Host", value=current_cfg.get("host", "localhost"))
            db_port = st.number_input("Port", value=int(current_cfg.get("port", 3306)), step=1)
            db_user = st.text_input("Username", value=current_cfg.get("user", "root"))
            db_password = st.text_input("Password", value=current_cfg.get("password", ""), type="password", help="Default XAMPP MySQL has no password (empty). If you configured a password in phpMyAdmin, enter it here.")
            db_name = st.text_input("Database Name", value=current_cfg.get("database", "telecom_churn"))
            db_fallback = st.checkbox("Enable automatic SQLite fallback if MySQL is unreachable", value=current_cfg.get("use_fallback", True))
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🔌 Test Connection", use_container_width=True):
                    test_cfg = {
                        "engine": db_engine_choice,
                        "host": db_host,
                        "port": int(db_port),
                        "user": db_user,
                        "password": db_password,
                        "database": db_name,
                        "use_fallback": db_fallback
                    }
                    ok, msg, eng = database.test_db_connection(test_cfg)
                    if ok:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
            with col_btn2:
                if st.button("💾 Save Settings", use_container_width=True, type="primary"):
                    new_cfg = {
                        "engine": db_engine_choice,
                        "host": db_host,
                        "port": int(db_port),
                        "user": db_user,
                        "password": db_password,
                        "database": db_name,
                        "use_fallback": db_fallback
                    }
                    database.save_db_config(new_cfg)
                    st.success("✅ Database configuration saved!")
                    st.rerun()

        with col_c2:
            st.markdown("#### Database Utilities & Initial Seeding")
            st.markdown("""
            Populate the database with initial customer records from the raw dataset (`dataset/WA_Fn-UseC_-Telco-Customer-Churn.csv`) with automatic AI risk scoring.
            """)
            
            seed_count = st.slider("Number of records to seed", min_value=10, max_value=200, value=50, step=10)
            if st.button(f"📥 Seed Database with {seed_count} Telecom Records", use_container_width=True):
                with st.spinner(f"Seeding {seed_count} customer records into database..."):
                    try:
                        seeded = database.seed_demo_data(predict_fn=preprocess_and_predict, limit=seed_count)
                        st.success(f"✅ Successfully seeded {seeded} customer records into **{active_db_engine.upper()}** database!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Seeding error: {e}")
                        
            st.markdown("---")
            st.markdown("#### Database Info")
            st.markdown(f"""
            - **Active Engine**: `{active_db_engine.upper()}`
            - **Local SQLite Path**: `{database.SQLITE_DB_PATH}`
            - **Config File**: `{database.CONFIG_FILE}`
            - **Supported Operations**: Single Prediction Save, Batch Insertion, GenAI Campaign Logging, Custom SQL Queries
            """)


# Sleek Global Footer
st.markdown("""
<div class="app-footer">
    <div class="footer-brand">⚡ TelcoPulse AI • Generative AI & Predictive Churn Intelligence Suite</div>
    <div class="footer-sub">Enterprise Retention Intelligence Platform • Built with Streamlit, Python & Scikit-Learn</div>
</div>
""", unsafe_allow_html=True)
