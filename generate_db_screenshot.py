"""
Generates visual diagrams and mock interface renders for Database & CRM Explorer
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_db_explorer_image(output_path):
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=200)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Top Header Banner
    banner = patches.FancyBboxPatch((3, 86), 94, 11, boxstyle="round,pad=0.5", fc="#1E1B4B", ec="#6366F1", lw=1.5)
    ax.add_patch(banner)
    ax.text(6, 92.5, "🗄️ Enterprise Database & Customer CRM Explorer", fontsize=14, fontweight='bold', color='#FFFFFF', va='center')
    ax.text(6, 88.5, "Unified persistent data layer supporting MySQL (XAMPP Port 3306) and SQLite with Live SQL Sandbox", fontsize=9.5, color='#A5B4FC', va='center')

    # Status Pill
    pill = patches.FancyBboxPatch((78, 89), 17, 5, boxstyle="round,pad=0.3", fc="#064E3B", ec="#10B981", lw=1.2)
    ax.add_patch(pill)
    ax.text(86.5, 91.5, "● MYSQL CONNECTED (3306)", fontsize=8, fontweight='bold', color='#34D399', ha='center', va='center')

    # KPI Metric Cards
    metrics = [
        ("Total Persisted Records", "7,043", "#A5B4FC", 3),
        ("Critical Churn Risk", "1,869", "#EF4444", 27.5),
        ("Active GenAI Campaigns", "342", "#38BDF8", 52),
        ("Database Avg Churn Rate", "26.5%", "#F59E0B", 76.5)
    ]
    for title, val, col, x in metrics:
        card = patches.FancyBboxPatch((x, 70), 20.5, 13, boxstyle="round,pad=0.4", fc="#111827", ec="#374151", lw=1)
        ax.add_patch(card)
        ax.text(x + 2, 79.5, title.upper(), fontsize=7.5, fontweight='bold', color='#9CA3AF')
        ax.text(x + 2, 73.5, val, fontsize=16, fontweight='bold', color=col)

    # Customer Records Table Box
    tbl_box = patches.FancyBboxPatch((3, 22), 94, 45, boxstyle="round,pad=0.5", fc="#111827", ec="#374151", lw=1)
    ax.add_patch(tbl_box)
    ax.text(5, 63, "📋 Persisted Customer Predictions & Live CRM Ledger", fontsize=11, fontweight='bold', color='#F3F4F6')

    # Table Header
    tbl_hdr = patches.Rectangle((4, 55), 92, 4.5, fc="#1F2937")
    ax.add_patch(tbl_hdr)
    cols = ["Customer ID", "Name", "Contract", "Tenure", "Monthly ($)", "Churn Prob", "Risk Tier", "Source", "Action Status"]
    col_x = [5, 16, 28, 38, 46, 56, 68, 79, 89]
    for c, x in zip(cols, col_x):
        ax.text(x, 57.2, c, fontsize=8, fontweight='bold', color='#9CA3AF', va='center')

    # Sample Table Rows
    rows = [
        ("7590-VHVEG", "Alex Morgan", "Month-to-month", "4 mos", "$95.00", "74.2%", "Critical Risk", "Single Diagnosis", "Generated"),
        ("5575-GNVDE", "Sarah Connor", "One year", "34 mos", "$56.95", "18.5%", "Low Risk", "Batch Scoring", "Retained"),
        ("3668-QPYBK", "Marcus Vance", "Month-to-month", "2 mos", "$89.50", "81.0%", "Critical Risk", "Single Diagnosis", "Dispatched"),
        ("7795-CFOCW", "Elena Rostova", "Two year", "62 mos", "$42.30", "8.2%", "Low Risk", "Batch Scoring", "Active"),
        ("9237-HQITU", "David Kim", "Month-to-month", "8 mos", "$70.70", "64.8%", "Critical Risk", "GenAI Copilot", "Dispatched"),
        ("9305-CDSKC", "Chloe Bennett", "Month-to-month", "12 mos", "$99.65", "68.3%", "Critical Risk", "Batch Scoring", "Generated")
    ]
    y_pos = 49.5
    for r in rows:
        r_box = patches.Rectangle((4, y_pos - 1.5), 92, 5, fc="#182234" if int(y_pos)%2==0 else "#131C2E")
        ax.add_patch(r_box)
        for val, x in zip(r, col_x):
            txt_color = '#EF4444' if 'Critical' in val or ('%' in val and float(val.replace('%','')) > 60) else ('#34D399' if 'Low' in val or 'Retained' in val else '#E5E7EB')
            ax.text(x, y_pos + 1, val, fontsize=7.8, color=txt_color, va='center')
        y_pos -= 5.5

    # Bottom SQL Sandbox Bar
    sql_box = patches.FancyBboxPatch((3, 3), 94, 16, boxstyle="round,pad=0.5", fc="#1E1B4B", ec="#4338CA", lw=1)
    ax.add_patch(sql_box)
    ax.text(5, 15.5, "⚡ Direct Analytical SQL Sandbox (Live MySQL / SQLite Execution)", fontsize=9.5, fontweight='bold', color='#E0E7FF')
    
    code_box = patches.Rectangle((5, 5), 75, 7.5, fc="#0A0E1A", ec="#312E81")
    ax.add_patch(code_box)
    ax.text(6.5, 9, "SELECT risk_tier, COUNT(*) as users, ROUND(AVG(monthly_charges),2) as avg_mrr FROM customer_predictions GROUP BY risk_tier;", fontsize=7.5, fontfamily='monospace', color='#38BDF8')

    btn = patches.FancyBboxPatch((82, 5), 13, 7.5, boxstyle="round,pad=0.3", fc="#4F46E5", ec="#818CF8", lw=1)
    ax.add_patch(btn)
    ax.text(88.5, 8.75, "EXECUTE SQL", fontsize=8, fontweight='bold', color='#FFFFFF', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', facecolor='#0B0F19')
    plt.close()
    print(f"Generated Database CRM Explorer screenshot at: {output_path}")

if __name__ == '__main__':
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    out_file = os.path.join(out_dir, "06_database_crm_explorer.png")
    generate_db_explorer_image(out_file)
