import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. Create Architecture Diagram
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=220)
ax.axis('off')

boxes = [
    ('1. Frontline User / Retention Agent\n(Inputs Subscriber Profile & Risk Factors)', 0.5, 0.90, '#1E3A8A', '#EFF6FF'),
    ('2. Telemetry & Feature Extraction\n(Churn Risk %, Top Hazard Drivers, Monthly Charges)', 0.5, 0.73, '#1E3A8A', '#F1F5F9'),
    ('3. Dynamic Prompt Construction Layer\n(Few-Shot Context, System Persona, Business Rules)', 0.5, 0.55, '#4338CA', '#EEF2FF'),
    ('4. Generative AI Model / API Layer\n(Gemini 2.0 / GPT-4o / Contextual Inference Engine)', 0.5, 0.37, '#6D28D9', '#FAF5FF'),
    ('5. Multi-Channel Output Dispatch\n(Personalized Email, SMS Alert, Agent Script, CRM JSON)', 0.5, 0.18, '#047857', '#ECFDF5')
]

for label, x, y, border_col, bg_col in boxes:
    rect = patches.FancyBboxPatch((x - 0.35, y - 0.06), 0.7, 0.10, boxstyle='round,pad=0.03',
                                  facecolor=bg_col, edgecolor=border_col, linewidth=2.0)
    ax.add_patch(rect)
    ax.text(x, y - 0.01, label, ha='center', va='center', fontsize=9.5, fontweight='bold', color=border_col)

for y_top, y_bot in [(0.84, 0.77), (0.67, 0.60), (0.49, 0.42), (0.31, 0.23)]:
    ax.annotate('', xy=(0.5, y_bot), xytext=(0.5, y_top),
                arrowprops=dict(facecolor='#475569', edgecolor='#475569', width=1.8, headwidth=8, shrink=0.05))

plt.title('TelcoPulse GenAI End-to-End System Architecture & Workflow', fontsize=12, fontweight='bold', color='#1E3A8A', pad=15)
plt.savefig('screenshots/09_genai_system_architecture.png', bbox_inches='tight')
plt.close()

# 2. Create GenAI Copilot Mockup Screenshot figure
fig, ax = plt.subplots(figsize=(9.5, 6.0), dpi=220)
ax.axis('off')

# Outer Window
bg = patches.FancyBboxPatch((0.02, 0.02), 0.96, 0.94, boxstyle='round,pad=0.02', facecolor='#0F172A', edgecolor='#334155', linewidth=1.5)
ax.add_patch(bg)

# Header
ax.text(0.06, 0.90, '⚡ TelcoPulse AI — ✨ GenAI Customer Retention Copilot', fontsize=11, fontweight='bold', color='#38BDF8')
ax.text(0.06, 0.86, 'Generative AI-Powered Personalized Win-Back Campaign & Script Generator', fontsize=8.5, color='#94A3B8')

# Left Box: Prompt & Context
ctx_box = patches.FancyBboxPatch((0.05, 0.10), 0.42, 0.72, boxstyle='round,pad=0.02', facecolor='#1E293B', edgecolor='#475569', linewidth=1.0)
ax.add_patch(ctx_box)
ax.text(0.07, 0.78, '📋 Subscriber Context & Prompt Configuration', fontsize=9, fontweight='bold', color='#E2E8F0')
prompt_lines = [
    '• Customer: Sarah Jenkins (ID: #7590-VHVEG)',
    '• Risk Level: Critical (>60% Churn Probability)',
    '• Tenure: 4 months | Monthly Bill: $94.50/mo',
    '• Top Drivers: High Bill, Month-to-Month, No Tech Support',
    '• Persona: Empathetic, Warm & Customer-Centric',
    '• Target Channel: Personalized Email & Agent Script'
]
for i, line in enumerate(prompt_lines):
    ax.text(0.07, 0.72 - i*0.065, line, fontsize=7.5, color='#CBD5E1')

ax.text(0.07, 0.28, 'Prompt Sent to GenAI Engine (Gemini / LLM):', fontsize=8, fontweight='bold', color='#A5B4FC')
p_code = patches.FancyBboxPatch((0.065, 0.12), 0.39, 0.14, boxstyle='round,pad=0.01', facecolor='#0F172A', edgecolor='#6366F1', linewidth=1.0)
ax.add_patch(p_code)
ax.text(0.075, 0.22, 'SYSTEM: You are an expert Telecom Retention Strategist.\nTASK: Generate high-converting win-back offer email,\nagent negotiation objection script & CRM JSON.', fontsize=6.5, color='#E0E7FF', family='monospace')

# Right Box: Generated AI Output
out_box = patches.FancyBboxPatch((0.51, 0.10), 0.44, 0.72, boxstyle='round,pad=0.02', facecolor='#1E1B4B', edgecolor='#6366F1', linewidth=1.5)
ax.add_patch(out_box)
ax.text(0.53, 0.78, '✨ Generated AI Retention Output', fontsize=9.5, fontweight='bold', color='#A5B4FC')

ax.text(0.53, 0.72, 'Subject: Exclusive Member Benefit: Save $18.90/mo', fontsize=8, fontweight='bold', color='#38BDF8')
email_text = [
    'Dear Sarah,',
    'We know connectivity reliability and fair pricing are essential.',
    'We approved an exclusive 20% loyalty rate reduction:',
    '  ✓ Bill drops from $94.50 to $75.60/month (12 mos)',
    '  ✓ Complimentary 24/7 VIP Tech Support ($15/mo value free)',
    '  ✓ Instant $15 account credit on auto-pay switch'
]
for i, line in enumerate(email_text):
    ax.text(0.53, 0.67 - i*0.045, line, fontsize=7.2, color='#E2E8F0')

# Agent Call Script
ax.text(0.53, 0.36, '📞 Frontline Agent Objection Script:', fontsize=8, fontweight='bold', color='#FBBF24')
ax.text(0.53, 0.31, '"I see you have been with us 4 months. I have authorization\nto reduce your rate to $75.60/mo with zero contract lock-in."', fontsize=7.0, color='#FEF08A', style='italic')

# CRM JSON Box
ax.text(0.53, 0.22, '⚙️ CRM JSON Payload: QUEUED_FOR_OUTREACH', fontsize=7.5, fontweight='bold', color='#4ADE80')

plt.title('TelcoPulse GenAI Retention Copilot User Interface & Generated Assets', fontsize=11.5, fontweight='bold', color='#1E3A8A', pad=12)
plt.savefig('screenshots/10_genai_copilot_ui.png', bbox_inches='tight')
plt.close()

print('GenAI diagrams and UI screenshots generated successfully!')
