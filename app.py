import streamlit as st
import pandas as pd
import numpy as np
import joblib
import warnings
import plotly.graph_objects as go
import plotly.express as px
import os

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
    /* Metric Card Styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #334155;
        color: white;
        margin-bottom: 15px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-top: 5px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Risk Badges */
    .badge-safe {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid #22c55e;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-moderate {
        background-color: rgba(234, 179, 8, 0.15);
        color: #facc15;
        border: 1px solid #eab308;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-high {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid #ef4444;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Recommendation Card */
    .action-card {
        background-color: #1e1e2f;
        border-left: 4px solid #6366f1;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
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
            "🎛️ What-If Retention Sandbox",
            "📁 Batch Scoring & Priority Queue",
            "📊 Executive Cohort Insights",
            "🧠 Model Diagnostics"
        ]
    )
    st.markdown("---")
    st.info("💡 **Pro-tip**: Use the **What-If Sandbox** to simulate retention offers and see risk drops in real time.")


# ==============================================================================
# TAB 1: Single Customer Diagnosis
# ==============================================================================
if menu == "🎯 Single Customer Diagnosis":
    st.title("🎯 Single Customer Churn Risk Diagnosis")
    st.markdown("Assess individual customer churn probability, pinpoint drivers, and prescribe instant retention workflows.")
    
    # Quick Preset Loader
    with st.expander("⚡ Load Pre-configured Customer Profiles (Quick Test)", expanded=False):
        col_p1, col_p2, col_p3 = st.columns(3)
        preset = None
        if col_p1.button("🔴 High Risk Profile (Month-to-Month, Fiber, Elec. Check)", use_container_width=True):
            preset = "high"
        if col_p2.button("🟡 Moderate Risk Profile (1-Year, DSL, Short Tenure)", use_container_width=True):
            preset = "mod"
        if col_p3.button("🟢 Loyal Customer Profile (2-Year, Auto-Pay, Long Tenure)", use_container_width=True):
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


# ==============================================================================
# TAB 2: What-If Retention Sandbox
# ==============================================================================
elif menu == "🎛️ What-If Retention Sandbox":
    st.title("🎛️ What-If Retention Strategy Simulator")
    st.markdown("Test different retention levers on an at-risk customer in real time and see how much churn probability drops!")
    
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
# TAB 3: Batch Scoring & Priority Queue
# ==============================================================================
elif menu == "📁 Batch Scoring & Priority Queue":
    st.title("📁 Batch Customer Risk Scoring & Outreach Priority Queue")
    st.markdown("Upload a customer CSV or load a cohort sample to automatically rank and prioritize high-risk churn interventions.")
    
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
        
        # Download Action Plan CSV
        csv_download = filtered_view.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Prioritized Outreach Campaign (CSV)",
            data=csv_download,
            file_name="telecom_prioritized_churn_leads.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("👆 Upload a CSV or click 'Load 250 Sample Records' to preview batch scoring.")


# ==============================================================================
# TAB 4: Executive Cohort Insights
# ==============================================================================
elif menu == "📊 Executive Cohort Insights":
    st.title("📊 Executive Cohort & Retention Analytics")
    st.markdown("Explore macroeconomic patterns, driver distributions, and customer lifecycles across the historical customer base.")
    
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
# TAB 5: Model Diagnostics
# ==============================================================================
elif menu == "🧠 Model Diagnostics":
    st.title("🧠 AI Model Diagnostics & Feature Weights")
    st.markdown("Inspect underlying model architecture, global feature importance weights, and inference pipelines.")
    
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

st.markdown("---")
st.caption("⚡ TelcoPulse AI Suite • Built with Streamlit, Scikit-Learn & Plotly")
