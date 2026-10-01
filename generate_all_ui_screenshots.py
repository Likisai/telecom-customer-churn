import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('screenshots', exist_ok=True)

# Common styling helper
def create_window_frame(ax, title_text, subtitle_text):
    ax.axis('off')
    # Dark modern canvas
    bg = patches.FancyBboxPatch((0.01, 0.01), 0.98, 0.98, boxstyle='round,pad=0.015',
                                facecolor='#0B0F19', edgecolor='#1E293B', linewidth=1.5)
    ax.add_patch(bg)
    
    # Header Banner
    banner = patches.FancyBboxPatch((0.03, 0.88), 0.94, 0.09, boxstyle='round,pad=0.01',
                                   facecolor='#1E1B4B', edgecolor='#4338CA', linewidth=1.2)
    ax.add_patch(banner)
    ax.text(0.05, 0.935, f"⚡ {title_text}", fontsize=11, fontweight='bold', color='#E0E7FF')
    ax.text(0.05, 0.900, subtitle_text, fontsize=8, color='#94A3B8')

# 1. Single Customer Diagnosis
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
create_window_frame(ax, "TelcoPulse AI — 🎯 Single Customer Churn Risk Diagnosis",
                    "Real-Time Churn Risk Classification, Log-Odds Explainability & Prescriptive Playbook")

# Left: Gauge Card
g_box = patches.FancyBboxPatch((0.04, 0.32), 0.44, 0.53, boxstyle='round,pad=0.02',
                              facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(g_box)
ax.text(0.06, 0.81, "Predicted Churn Probability", fontsize=9, fontweight='bold', color='#E5E7EB')
ax.text(0.26, 0.65, "61.3%", fontsize=26, fontweight='bold', color='#EF4444', ha='center')

# Badge
badge = patches.FancyBboxPatch((0.14, 0.54), 0.24, 0.06, boxstyle='round,pad=0.01',
                              facecolor='#7F1D1D', edgecolor='#EF4444', linewidth=1.0)
ax.add_patch(badge)
ax.text(0.26, 0.57, "🚨 CRITICAL RISK", fontsize=8.5, fontweight='bold', color='#FCA5A5', ha='center')

# Revenue at Risk Card
rev_box = patches.FancyBboxPatch((0.06, 0.35), 0.40, 0.15, boxstyle='round,pad=0.01',
                                facecolor='#1E293B', edgecolor='#0284C7', linewidth=1.0)
ax.add_patch(rev_box)
ax.text(0.08, 0.46, "ESTIMATED ANNUAL VALUE AT RISK", fontsize=7.5, color='#94A3B8', fontweight='bold')
ax.text(0.08, 0.40, "$1,140.00 / yr  (Expected Loss: $698.82)", fontsize=9.5, fontweight='bold', color='#38BDF8')

# Right: Feature Attribution Bar Chart
attr_box = patches.FancyBboxPatch((0.52, 0.32), 0.44, 0.53, boxstyle='round,pad=0.02',
                                 facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(attr_box)
ax.text(0.54, 0.81, "🔍 Local Feature Attribution (Log-Odds Impact)", fontsize=9, fontweight='bold', color='#E5E7EB')

features = [
    ("Contract: Month-to-month", 1.28, '#EF4444'),
    ("Internet: Fiber optic", 0.84, '#EF4444'),
    ("Payment: Electronic check", 0.42, '#EF4444'),
    ("Tenure: 4 Months", 0.35, '#EF4444'),
    ("Online Security: Yes", -0.46, '#10B981'),
    ("Contract: Two year", -1.35, '#10B981')
]
for i, (feat, val, col) in enumerate(features):
    ax.text(0.54, 0.74 - i*0.065, feat, fontsize=7.5, color='#CBD5E1')
    bar_w = abs(val) * 0.08
    bx = 0.80 if val > 0 else 0.80 - bar_w
    bar = patches.Rectangle((bx, 0.73 - i*0.065), bar_w, 0.025, facecolor=col)
    ax.add_patch(bar)

# Bottom: Prescriptive Playbook Cards
p1 = patches.FancyBboxPatch((0.04, 0.05), 0.29, 0.23, boxstyle='round,pad=0.01', facecolor='#1E1B4B', edgecolor='#6366F1', linewidth=1.0)
p2 = patches.FancyBboxPatch((0.36, 0.05), 0.29, 0.23, boxstyle='round,pad=0.01', facecolor='#1E1B4B', edgecolor='#6366F1', linewidth=1.0)
p3 = patches.FancyBboxPatch((0.68, 0.05), 0.28, 0.23, boxstyle='round,pad=0.01', facecolor='#1E1B4B', edgecolor='#6366F1', linewidth=1.0)
ax.add_patch(p1); ax.add_patch(p2); ax.add_patch(p3)

ax.text(0.06, 0.23, "📄 1-Year Rate Lock Incentive", fontsize=8, fontweight='bold', color='#A5B4FC')
ax.text(0.06, 0.14, "Offer 1-Year agreement with\n15% discount to stabilize churn.", fontsize=7, color='#CBD5E1')

ax.text(0.38, 0.23, "🛠️ Free Tech Support Bundle", fontsize=8, fontweight='bold', color='#A5B4FC')
ax.text(0.38, 0.14, "Bundle 6-Month 24/7 Tech Care\nto boost product stickiness.", fontsize=7, color='#CBD5E1')

ax.text(0.70, 0.23, "💳 Auto-Pay $20 Credit", fontsize=8, fontweight='bold', color='#A5B4FC')
ax.text(0.70, 0.14, "Offer $20 statement credit for\ncredit card/bank auto-pay.", fontsize=7, color='#CBD5E1')

plt.savefig('screenshots/01_single_customer_diagnosis.png', bbox_inches='tight')
plt.close()

# 2. What-If Retention Sandbox
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
create_window_frame(ax, "TelcoPulse AI — 🎛️ What-If Retention Strategy Simulator",
                    "Simulate Retention Offers in Real Time & Measure Probability Drops")

# KPI Cards Top
metrics = [
    ("BASELINE CHURN RISK", "83.6%", '#EF4444', 0.04),
    ("SIMULATED CHURN RISK", "28.4%", '#10B981', 0.28),
    ("ABSOLUTE RISK REDUCTION", "▼ 55.2%", '#38BDF8', 0.52),
    ("RELATIVE IMPROVEMENT", "+66.0%", '#C084FC', 0.76)
]
for lbl, val, col, x in metrics:
    box = patches.FancyBboxPatch((x, 0.68), 0.20, 0.17, boxstyle='round,pad=0.01',
                                facecolor='#111827', edgecolor='#374151', linewidth=1.0)
    ax.add_patch(box)
    ax.text(x+0.02, 0.81, lbl, fontsize=6.5, color='#94A3B8', fontweight='bold')
    ax.text(x+0.02, 0.73, val, fontsize=16, fontweight='bold', color=col)

# Left: Baseline vs Simulated Inputs
in_box = patches.FancyBboxPatch((0.04, 0.06), 0.44, 0.58, boxstyle='round,pad=0.015',
                               facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(in_box)
ax.text(0.06, 0.59, "🎛️ Strategy Parameter Configuration", fontsize=9, fontweight='bold', color='#E5E7EB')

sim_params = [
    ("Contract Upgrade:", "Month-to-month  ➔  One year (Annual Lock)"),
    ("Tech Support Add-on:", "No Tech Support  ➔  Included Free (6 Mos)"),
    ("Payment Method:", "Electronic Check  ➔  Credit Card (Auto-Pay)"),
    ("Monthly Plan Discount:", "$0.00/mo  ➔  -$15.00/mo Loyalty Credit"),
    ("Resulting Bill:", "$95.00/mo  ➔  $80.00/mo")
]
for i, (k, v) in enumerate(sim_params):
    ax.text(0.06, 0.51 - i*0.08, k, fontsize=7.5, color='#94A3B8', fontweight='bold')
    ax.text(0.06, 0.47 - i*0.08, v, fontsize=7.5, color='#38BDF8')

# Right: Waterfall Comparison Bar
out_box = patches.FancyBboxPatch((0.52, 0.06), 0.44, 0.58, boxstyle='round,pad=0.015',
                                facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(out_box)
ax.text(0.54, 0.59, "📊 Risk Probability Comparison", fontsize=9, fontweight='bold', color='#E5E7EB')

# Bars
bar1 = patches.Rectangle((0.60, 0.15), 0.12, 0.38, facecolor='#EF4444')
bar2 = patches.Rectangle((0.78, 0.15), 0.12, 0.13, facecolor='#10B981')
ax.add_patch(bar1); ax.add_patch(bar2)

ax.text(0.66, 0.55, "83.6%", fontsize=10, fontweight='bold', color='#FCA5A5', ha='center')
ax.text(0.84, 0.30, "28.4%", fontsize=10, fontweight='bold', color='#86EFAC', ha='center')
ax.text(0.66, 0.10, "Baseline", fontsize=8, color='#94A3B8', ha='center')
ax.text(0.84, 0.10, "With Package", fontsize=8, color='#94A3B8', ha='center')

plt.savefig('screenshots/02_what_if_sandbox.png', bbox_inches='tight')
plt.close()

# 3. Batch Scoring Queue
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
create_window_frame(ax, "TelcoPulse AI — 📁 Batch Customer Risk Scoring & Action Queue",
                    "Score Entire Cohorts (.csv), Prioritize Interventions & Export Action Lists")

kpis = [
    ("TOTAL CUSTOMERS", "250", '#F3F4F6', 0.04),
    ("CRITICAL ACCOUNTS", "39 (15.6%)", '#EF4444', 0.28),
    ("AVG CHURN RISK", "26.0%", '#FBBF24', 0.52),
    ("ANNUAL REVENUE AT RISK", "$59,804", '#38BDF8', 0.76)
]
for lbl, val, col, x in kpis:
    box = patches.FancyBboxPatch((x, 0.68), 0.20, 0.17, boxstyle='round,pad=0.01',
                                facecolor='#111827', edgecolor='#374151', linewidth=1.0)
    ax.add_patch(box)
    ax.text(x+0.02, 0.81, lbl, fontsize=6.5, color='#94A3B8', fontweight='bold')
    ax.text(x+0.02, 0.73, val, fontsize=14, fontweight='bold', color=col)

# Table Representation
tbl_box = patches.FancyBboxPatch((0.04, 0.06), 0.92, 0.58, boxstyle='round,pad=0.015',
                                facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(tbl_box)
ax.text(0.06, 0.59, "📋 Prioritized Customer Outreach Queue (Ranked by Expected Annual Loss)", fontsize=8.5, fontweight='bold', color='#E5E7EB')

rows = [
    ("CUST-9061", "80.5%", "🔴 Critical", "$920.60", "$95.25", "13 mo", "Month-to-month", "Fiber optic"),
    ("CUST-2725", "78.9%", "🔴 Critical", "$859.41", "$90.75", "1 mo", "Month-to-month", "Fiber optic"),
    ("CUST-5421", "76.2%", "🔴 Critical", "$812.30", "$88.90", "4 mo", "Month-to-month", "Fiber optic"),
    ("CUST-1049", "64.1%", "🔴 Critical", "$734.20", "$95.40", "8 mo", "Month-to-month", "Fiber optic"),
    ("CUST-8832", "42.3%", "🟡 Moderate", "$420.50", "$82.60", "22 mo", "One year", "DSL"),
    ("CUST-3910", "12.4%", "🟢 Low Risk", "$112.00", "$75.20", "55 mo", "Two year", "Fiber optic")
]
headers = ["Account ID", "Risk %", "Risk Tier", "Expected Loss", "Monthly Charges", "Tenure", "Contract", "Internet"]
for j, h in enumerate(headers):
    ax.text(0.06 + j*0.115, 0.52, h, fontsize=7.2, color='#A5B4FC', fontweight='bold')

for i, r in enumerate(rows):
    y_pos = 0.45 - i*0.065
    for j, val in enumerate(r):
        col = '#EF4444' if 'Critical' in val or (j==1 and float(val.replace('%',''))>60) else ('#10B981' if 'Low' in val else '#E5E7EB')
        ax.text(0.06 + j*0.115, y_pos, val, fontsize=7.0, color=col)

plt.savefig('screenshots/03_batch_scoring_queue.png', bbox_inches='tight')
plt.close()

# 4. Executive Cohort Analytics
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
create_window_frame(ax, "TelcoPulse AI — 📊 Executive Cohort & Retention Analytics",
                    "Macroeconomic Trends, Billing Distributions & Churn Velocity")

# 4 Chart Sub-Cards
c1 = patches.FancyBboxPatch((0.04, 0.48), 0.44, 0.38, boxstyle='round,pad=0.01', facecolor='#111827', edgecolor='#374151', linewidth=1.0)
c2 = patches.FancyBboxPatch((0.52, 0.48), 0.44, 0.38, boxstyle='round,pad=0.01', facecolor='#111827', edgecolor='#374151', linewidth=1.0)
c3 = patches.FancyBboxPatch((0.04, 0.06), 0.44, 0.38, boxstyle='round,pad=0.01', facecolor='#111827', edgecolor='#374151', linewidth=1.0)
c4 = patches.FancyBboxPatch((0.52, 0.06), 0.44, 0.38, boxstyle='round,pad=0.01', facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(c1); ax.add_patch(c2); ax.add_patch(c3); ax.add_patch(c4)

ax.text(0.06, 0.81, "Customer Churn by Contract Type", fontsize=8.5, fontweight='bold', color='#E5E7EB')
ax.text(0.06, 0.74, "• Month-to-Month: 42.7% Churn (High Risk)\n• One Year: 11.2% Churn\n• Two Year: 2.8% Churn (High Retention)", fontsize=7.2, color='#CBD5E1')

ax.text(0.54, 0.81, "Churn Rate % by Payment Method", fontsize=8.5, fontweight='bold', color='#E5E7EB')
ax.text(0.54, 0.74, "• Electronic Check: 45.3% Churn (Friction)\n• Bank Transfer (Auto): 16.7% Churn\n• Credit Card (Auto): 15.2% Churn", fontsize=7.2, color='#CBD5E1')

ax.text(0.06, 0.39, "Monthly Charges Distribution ($/mo)", fontsize=8.5, fontweight='bold', color='#E5E7EB')
ax.text(0.06, 0.32, "• High Risk Density: $70 - $105/mo\n• Low Risk Density: $20 - $35/mo\n• Threshold Elasticity: Spike above $80/mo", fontsize=7.2, color='#CBD5E1')

ax.text(0.54, 0.39, "Impact of Tech Support on Internet Retention", fontsize=8.5, fontweight='bold', color='#E5E7EB')
ax.text(0.54, 0.32, "• No Tech Support: 41.6% Churn\n• With Tech Support: 15.1% Churn\n• Retention Multiplier: +2.7x Stickiness", fontsize=7.2, color='#CBD5E1')

plt.savefig('screenshots/04_executive_cohort_insights.png', bbox_inches='tight')
plt.close()

# 5. Model Diagnostics
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
create_window_frame(ax, "TelcoPulse AI — 🧠 AI Model Diagnostics & Feature Weights",
                    "Model Pipeline Architecture, Calibration & Global Beta Weights")

# Left: Pipeline Specs
p_box = patches.FancyBboxPatch((0.04, 0.06), 0.44, 0.80, boxstyle='round,pad=0.015',
                              facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(p_box)
ax.text(0.06, 0.81, "⚙️ Pipeline Specifications", fontsize=9, fontweight='bold', color='#E5E7EB')
specs = [
    ("Classifier:", "Logistic Regression (L2 Ridge)"),
    ("Scaler:", "StandardScaler (45 Dimensions)"),
    ("Encoder:", "OneHotEncoder (15 Categories)"),
    ("Accuracy:", "80.48% (Test Set)"),
    ("ROC-AUC:", "0.845 (High Discrimination)"),
    ("Decision Threshold:", "50.0% Churn Probability"),
    ("Inference Latency:", "< 5 ms per inference")
]
for i, (k, v) in enumerate(specs):
    ax.text(0.06, 0.73 - i*0.075, k, fontsize=8, color='#94A3B8', fontweight='bold')
    ax.text(0.06, 0.69 - i*0.075, v, fontsize=8, color='#38BDF8')

# Right: Top Global Weights
w_box = patches.FancyBboxPatch((0.52, 0.06), 0.44, 0.80, boxstyle='round,pad=0.015',
                              facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(w_box)
ax.text(0.54, 0.81, "Top Global Churn Accelerators (+ Beta)", fontsize=8.5, fontweight='bold', color='#EF4444')
pos_weights = [
    ("TotalCharges (Collinear)", "+0.5264"),
    ("Internet: Fiber Optic", "+0.4426"),
    ("Contract: Month-to-Month", "+0.3061"),
    ("Streaming TV: Yes", "+0.1888")
]
for i, (feat, w) in enumerate(pos_weights):
    ax.text(0.54, 0.74 - i*0.055, feat, fontsize=7.5, color='#CBD5E1')
    ax.text(0.86, 0.74 - i*0.055, w, fontsize=7.5, color='#EF4444', fontweight='bold')

ax.text(0.54, 0.48, "Top Global Retention Anchors (- Beta)", fontsize=8.5, fontweight='bold', color='#10B981')
neg_weights = [
    ("Tenure (Loyalty Length)", "-1.2490"),
    ("MonthlyCharges (Baseline)", "-1.0098"),
    ("Internet: DSL Service", "-0.3540"),
    ("Contract: Two-Year", "-0.3226")
]
for i, (feat, w) in enumerate(neg_weights):
    ax.text(0.54, 0.41 - i*0.055, feat, fontsize=7.5, color='#CBD5E1')
    ax.text(0.86, 0.41 - i*0.055, w, fontsize=7.5, color='#10B981', fontweight='bold')

plt.savefig('screenshots/05_model_diagnostics.png', bbox_inches='tight')
plt.close()

# 6. GenAI Copilot UI
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
create_window_frame(ax, "TelcoPulse AI — ✨ GenAI Customer Retention Copilot",
                    "Multi-Angle Stochastic Retention Copywriter & Agent Negotiation Assistant")

# Left Box: Prompt & Context
ctx_box = patches.FancyBboxPatch((0.04, 0.06), 0.44, 0.80, boxstyle='round,pad=0.015',
                                facecolor='#111827', edgecolor='#374151', linewidth=1.0)
ax.add_patch(ctx_box)
ax.text(0.06, 0.81, "📋 Telemetry & Multi-Angle Parameters", fontsize=9, fontweight='bold', color='#E5E7EB')

prompt_lines = [
    ("Customer:", "Waheed (ID: #CUST-5795)"),
    ("Risk Level:", "Critical (>60% Churn Probability)"),
    ("Tenure:", "15 months (1.2 years) | Monthly: $94.50"),
    ("Target Channel:", "Personalized Email Campaign"),
    ("Persona Tone:", "Professional, Value-Driven"),
    ("AI Temperature:", "0.85 (High Creative Variety)")
]
for i, (lbl, val) in enumerate(prompt_lines):
    ax.text(0.06, 0.74 - i*0.065, lbl, fontsize=7.5, color='#94A3B8', fontweight='bold')
    ax.text(0.06, 0.70 - i*0.065, val, fontsize=7.5, color='#38BDF8')

ax.text(0.06, 0.28, "🧠 Reasoning Strategy Sampled:", fontsize=8, fontweight='bold', color='#A5B4FC')
p_code = patches.FancyBboxPatch((0.055, 0.09), 0.41, 0.16, boxstyle='round,pad=0.01',
                               facecolor='#0F172A', edgecolor='#6366F1', linewidth=1.0)
ax.add_patch(p_code)
ax.text(0.07, 0.20, "STRATEGY: Proactive Value Audit & Rate Relief\nPERKS: 20% Monthly Credit ($75.60/mo)\n+ Free 6-Mo VIP Security + $20 Auto-Pay Credit\nREBUTTALS: Custom Rebuttals for High Bill & Contract", fontsize=6.2, color='#E0E7FF', family='monospace')

# Right Box: Generated AI Output
out_box = patches.FancyBboxPatch((0.52, 0.06), 0.44, 0.80, boxstyle='round,pad=0.015',
                                facecolor='#1E1B4B', edgecolor='#6366F1', linewidth=1.2)
ax.add_patch(out_box)
ax.text(0.54, 0.81, "✉️ AI-Crafted Personalized Outreach", fontsize=9, fontweight='bold', color='#A5B4FC')
ax.text(0.54, 0.75, "Subject: Account Review #CUST-5795: Approved Rate Relief", fontsize=7.5, fontweight='bold', color='#38BDF8')

email_preview = [
    "Dear Waheed,",
    "You have been a cornerstone subscriber for 1.2 years (15 mos).",
    "We specially approved an Annual Loyalty Rate-Lock Guarantee:",
    "  • Guaranteed Rate Reduction: $94.50 ➔ $75.60/mo ($226.80/yr savings)",
    "  • Flexible Price-Lock: 1-Year freeze with 30-Day trial guarantee",
    "  • Free 24/7 VIP Tech Support: 6 months complimentary ($90 value)",
    "👉 [Claim My Approved Loyalty Rate ($75.60/mo) — Code: TELCO-631-SAVE]",
    "Sincerely, Subscriber Portfolio Management • TelcoPulse"
]
for i, line in enumerate(email_preview):
    ax.text(0.54, 0.69 - i*0.045, line, fontsize=6.5, color='#E0E7FF')

# Script preview
ax.text(0.54, 0.30, "📞 Frontline Agent Negotiation Rebuttal:", fontsize=7.5, fontweight='bold', color='#FBBF24')
ax.text(0.54, 0.24, "\"I hear you, Waheed. I have special authorization to reduce your\nmonthly bill to $75.60/mo right now, saving you $226.80/year.\"", fontsize=6.5, color='#FEF08A', style='italic')

# CRM payload preview
ax.text(0.54, 0.12, "⚙️ CRM JSON Payload: QUEUED_FOR_OUTREACH", fontsize=7.2, fontweight='bold', color='#4ADE80')

plt.savefig('screenshots/10_genai_copilot_ui.png', bbox_inches='tight')
plt.close()

print("All updated dark-mode UI screenshots generated successfully!")
