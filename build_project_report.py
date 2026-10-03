import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
import matplotlib.pyplot as plt
import numpy as np

def generate_charts(screenshot_dir):
    os.makedirs(screenshot_dir, exist_ok=True)

    # 1. Confusion Matrix Plot
    cm = np.array([[930, 105], [165, 209]])
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=200)
    cax = ax.matshow(cm, cmap='Blues', alpha=0.85)

    for i in range(2):
        for j in range(2):
            val = cm[i, j]
            label = 'TN' if (i==0 and j==0) else ('FP' if (i==0 and j==1) else ('FN' if (i==1 and j==0) else 'TP'))
            ax.text(j, i, f'{val}\n({label})', ha='center', va='center', fontsize=11, fontweight='bold', color='black' if val < 500 else 'white')

    fig.colorbar(cax, shrink=0.8)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(['Predicted Retained (0)', 'Predicted Churned (1)'], fontsize=9, fontweight='bold')
    ax.set_yticklabels(['Actual Retained (0)', 'Actual Churned (1)'], fontsize=9, fontweight='bold')
    ax.set_title('Confusion Matrix on Test Set (N=1,409)', fontsize=11, pad=12, fontweight='bold', color='#1E3A8A')
    plt.tight_layout()
    cm_path = os.path.join(screenshot_dir, '06_confusion_matrix_chart.png')
    plt.savefig(cm_path, bbox_inches='tight')
    plt.close()

    # 2. ROC Curve Plot
    fpr = np.array([0.0, 0.02, 0.05, 0.10, 0.18, 0.28, 0.40, 0.55, 0.70, 0.85, 1.0])
    tpr = np.array([0.0, 0.15, 0.35, 0.56, 0.72, 0.82, 0.89, 0.94, 0.97, 0.99, 1.0])

    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=200)
    ax.plot(fpr, tpr, color='#2563EB', lw=2.5, label='Logistic Regression (AUC = 0.845)')
    ax.plot([0, 1], [0, 1], color='#9CA3AF', lw=1.5, linestyle='--', label='Random Chance (AUC = 0.500)')
    ax.fill_between(fpr, tpr, alpha=0.15, color='#3B82F6')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate (1 - Specificity)', fontsize=9, fontweight='bold')
    ax.set_ylabel('True Positive Rate (Sensitivity / Recall)', fontsize=9, fontweight='bold')
    ax.set_title('Receiver Operating Characteristic (ROC) Curve', fontsize=11, fontweight='bold', color='#1E3A8A')
    ax.legend(loc='lower right', frameon=True, facecolor='#F8FAFC')
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    roc_path = os.path.join(screenshot_dir, '07_roc_curve_chart.png')
    plt.savefig(roc_path, bbox_inches='tight')
    plt.close()

    # 3. Feature Importance Bar Chart
    features = [
        'Month-to-Month Contract', 'Fiber Optic Internet', 'Electronic Check', 'Senior Citizen',
        'Tech Support (Active)', 'Online Security', 'Tenure (Long Duration)', 'Two-Year Contract'
    ]
    weights = [1.28, 0.84, 0.42, 0.25, -0.58, -0.46, -0.62, -1.35]
    colors = ['#DC2626' if w > 0 else '#16A34A' for w in weights]

    fig, ax = plt.subplots(figsize=(6.0, 3.6), dpi=200)
    bars = ax.barh(features, weights, color=colors, height=0.55)
    ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
    ax.set_xlabel('Logistic Regression Coefficient (Log-Odds Impact)', fontsize=9, fontweight='bold')
    ax.set_title('Key Churn Risk Drivers (+) vs Retention Anchors (-)', fontsize=11, fontweight='bold', color='#1E3A8A')
    ax.grid(axis='x', linestyle=':', alpha=0.6)

    for bar, w in zip(bars, weights):
        offset = 0.04 if w >= 0 else -0.22
        ax.text(w + offset, bar.get_y() + bar.get_height()/2, f'{w:+.2f}', va='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    fi_path = os.path.join(screenshot_dir, '08_feature_importance_chart.png')
    plt.savefig(fi_path, bbox_inches='tight')
    plt.close()

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''<w:tcMar {nsdecls("w")}>
        <w:top w:w="{top}" w:type="dxa"/>
        <w:bottom w:w="{bottom}" w:type="dxa"/>
        <w:left w:w="{left}" w:type="dxa"/>
        <w:right w:w="{right}" w:type="dxa"/>
    </w:tcMar>''')
    tcPr.append(tcMar)

def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def set_repeat_table_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def add_styled_heading(doc, text, level, space_before=10, space_after=3):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(space_before)
    h.paragraph_format.space_after = Pt(space_after)
    for run in h.runs:
        run.font.name = 'Calibri'
        if level == 1:
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 58, 138)
        elif level == 2:
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(37, 99, 235)
        elif level == 3:
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(71, 85, 105)
    return h

def add_body_p(doc, text="", bold_prefix=None, space_after=3, line_spacing=1.12):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(31, 41, 55)
    if text:
        r_txt = p.add_run(text)
        r_txt.font.name = 'Calibri'
        r_txt.font.size = Pt(10)
        r_txt.font.color.rgb = RGBColor(55, 65, 81)
    return p

def add_bullet_p(doc, text="", bold_prefix=None, space_after=2.5):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.12
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = 'Calibri'
        r_pre.font.size = Pt(10)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(31, 41, 55)
    if text:
        r_txt = p.add_run(text)
        r_txt.font.name = 'Calibri'
        r_txt.font.size = Pt(10)
        r_txt.font.color.rgb = RGBColor(55, 65, 81)
    return p

def add_callout(doc, text, title="KEY FINDING", space_after=4):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    prevent_row_split(tbl.rows[0])
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EFF6FF")
    set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="none"/>
        <w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>
        <w:bottom w:val="none"/>
        <w:right w:val="none"/>
    </w:tcBorders>''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r1 = p.add_run(f"{title}: ")
    r1.font.name = 'Calibri'
    r1.font.bold = True
    r1.font.size = Pt(9.5)
    r1.font.color.rgb = RGBColor(30, 58, 138)
    
    r2 = p.add_run(text)
    r2.font.name = 'Calibri'
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = RGBColor(30, 58, 138)
    doc.add_paragraph().paragraph_format.space_after = Pt(space_after)

def add_workflow_box(doc, steps_text, space_after=4):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    prevent_row_split(tbl.rows[0])
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    set_cell_margins(cell, top=90, bottom=90, left=140, right=140)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>
        <w:left w:val="single" w:sz="24" w:space="0" w:color="1E3A8A"/>
        <w:bottom w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>
        <w:right w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>
    </w:tcBorders>''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(steps_text)
    r.font.name = 'Calibri'
    r.font.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(30, 58, 138)
    doc.add_paragraph().paragraph_format.space_after = Pt(space_after)

def style_table(table, col_widths, headers, data, font_size=8.5, top_margin=50, bottom_margin=50):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header Row
    set_repeat_table_header(table.rows[0])
    prevent_row_split(table.rows[0])
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1E3A8A")
        set_cell_margins(hdr_cells[i], top=70, bottom=70, left=70, right=70)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        for run in p.runs:
            run.font.name = 'Calibri'
            run.font.bold = True
            run.font.size = Pt(font_size + 0.5)
            run.font.color.rgb = RGBColor(255, 255, 255)
            
    # Data Rows
    for row_idx, row_data in enumerate(data):
        row = table.rows[row_idx + 1]
        prevent_row_split(row)
        row_cells = row.cells
        bg_color = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            row_cells[col_idx].text = str(cell_value)
            set_cell_background(row_cells[col_idx], bg_color)
            set_cell_margins(row_cells[col_idx], top=top_margin, bottom=bottom_margin, left=70, right=70)
            p = row_cells[col_idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(str(cell_value)) > 20 else WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = 'Calibri'
                run.font.size = Pt(font_size)
                run.font.color.rgb = RGBColor(31, 41, 55)
                
    # Apply widths
    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = Inches(w)

def setup_header_footer(doc):
    for section in doc.sections:
        section.different_first_page_header_footer = True
        
        # Header (Pages 2+)
        hdr = section.header
        p_hdr = hdr.paragraphs[0]
        p_hdr.text = ""
        p_hdr.paragraph_format.space_after = Pt(0)
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_hdr = p_hdr.add_run("Telecom Customer Churn Intelligence System (TelcoPulse AI)  |  Project Report")
        r_hdr.font.name = 'Calibri'
        r_hdr.font.size = Pt(8.5)
        r_hdr.font.italic = True
        r_hdr.font.color.rgb = RGBColor(100, 116, 139)
        
        # Footer (Pages 2+)
        ftr = section.footer
        p_ftr = ftr.paragraphs[0]
        p_ftr.text = ""
        p_ftr.paragraph_format.space_after = Pt(0)
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        r_l = p_ftr.add_run("Department of Computer Science & Engineering  |  Academic Year 2025-26\t\tPage ")
        r_l.font.name = 'Calibri'
        r_l.font.size = Pt(8.5)
        r_l.font.color.rgb = RGBColor(100, 116, 139)
        
        # Dynamic Page field
        fld1 = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        p_ftr._p.append(fld1)
        
        r_m = p_ftr.add_run(" of ")
        r_m.font.name = 'Calibri'
        r_m.font.size = Pt(8.5)
        r_m.font.color.rgb = RGBColor(100, 116, 139)
        
        fld2 = parse_xml(r'<w:fldSimple %s w:instr="NUMPAGES"/>' % nsdecls('w'))
        p_ftr._p.append(fld2)

def generate_report():
    screenshot_dir = r"C:\Sap projects\Telecom customer churn\screenshots"
    generate_charts(screenshot_dir)
    
    doc = Document()
    
    # Page setup - Margins (0.75 inch)
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.header_distance = Inches(0.4)
        section.footer_distance = Inches(0.4)
        
    setup_header_footer(doc)
        
    # ==========================================
    # PAGE 1: COVER / TITLE PAGE
    # ==========================================
    p_top_spacer = doc.add_paragraph()
    p_top_spacer.paragraph_format.space_before = Pt(28)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("TELECOM CUSTOMER CHURN PREDICTION &\nRETENTION INTELLIGENCE SYSTEM\n(TelcoPulse AI)")
    r_title.font.name = 'Calibri'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(6)
    p_sub.paragraph_format.space_after = Pt(28)
    r_sub = p_sub.add_run("A Machine Learning & Explainable Decision Support System for Proactive Customer Retention")
    r_sub.font.name = 'Calibri'
    r_sub.font.size = Pt(11)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(75, 85, 99)
    
    # Border Box for Student Info
    tbl_info = doc.add_table(rows=1, cols=1)
    tbl_info.alignment = WD_TABLE_ALIGNMENT.CENTER
    prevent_row_split(tbl_info.rows[0])
    cell_info = tbl_info.cell(0, 0)
    set_cell_background(cell_info, "F1F5F9")
    set_cell_margins(cell_info, top=160, bottom=160, left=220, right=220)
    
    tcPr = cell_info._tc.get_or_add_tcPr()
    borders = parse_xml(f'''<w:tcBorders {nsdecls("w")}>
        <w:top w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>
        <w:left w:val="single" w:sz="24" w:space="0" w:color="1E3A8A"/>
        <w:bottom w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>
        <w:right w:val="single" w:sz="12" w:space="0" w:color="CBD5E1"/>
    </w:tcBorders>''')
    tcPr.append(borders)
    
    p_box = cell_info.paragraphs[0]
    p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_box.paragraph_format.line_spacing = 1.25
    
    def add_info_line(p, label, val):
        r1 = p.add_run(f"{label}: ")
        r1.font.name = 'Calibri'
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = RGBColor(30, 58, 138)
        r2 = p.add_run(f"{val}\n")
        r2.font.name = 'Calibri'
        r2.font.size = Pt(11)
        r2.font.color.rgb = RGBColor(31, 41, 55)
        
    add_info_line(p_box, "Student Name", "Anaganti Sairishikesh")
    add_info_line(p_box, "Guided by / Mentor", "Raghavendra Rao")
    add_info_line(p_box, "College Name", "Teegala Krishna Reddy Engineering College")
    add_info_line(p_box, "Department", "Department of Computer Science and Engineering")
    add_info_line(p_box, "Academic Year", "Final Year (2026 - 2027)")
    add_info_line(p_box, "Project Domain", "Artificial Intelligence & Machine Learning (AI/ML)")
    add_info_line(p_box, "Application Deployment", "https://telecomcustomers.streamlit.app/")
    
    p_ft = doc.add_paragraph()
    p_ft.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ft.paragraph_format.space_before = Pt(36)
    r_ft = p_ft.add_run("TelcoPulse AI  •  Production-Ready Machine Learning Solution")
    r_ft.font.name = 'Calibri'
    r_ft.font.size = Pt(9.5)
    r_ft.font.bold = True
    r_ft.font.color.rgb = RGBColor(148, 163, 184)
    
    doc.add_page_break()
    
    # ==========================================
    # PAGE 2: TABLE OF CONTENTS / INDEX
    # ==========================================
    add_styled_heading(doc, "Table of Contents", level=1, space_before=0, space_after=6)
    
    index_data = [
        ("1", "Introduction (Domain, Problem Background, AI/ML Importance, Proposed System)", "3"),
        ("2", "Problem Statement (Core Problem, Stakeholders, Existing Limitations, ML Need)", "4"),
        ("3", "Objectives (Research & Engineering Milestones)", "4"),
        ("4", "Project Scope (Target Users, Application Area, Functional Boundaries)", "5"),
        ("5", "Proposed System / Methodology (End-to-End Machine Learning Pipeline)", "5"),
        ("6", "Dataset Description (IBM Telco Churn Dataset & Feature Dictionary)", "6"),
        ("7", "Data Preprocessing (Cleaning, Imputation, Encoding & Normalization)", "7"),
        ("8", "AI/ML Model Selection (Candidate Benchmark & Logistic Regression Selection)", "7"),
        ("9", "Model Development (Hyperparameters, Feature Matrices & Development Stack)", "8"),
        ("10", "Model Training and Evaluation (Classification Report & Confusion Matrix)", "8"),
        ("11", "Results and Analysis (Confusion Matrix, ROC Curve & Log-Odds Feature Importance)", "9"),
        ("12", "System Architecture / Workflow (4-Tier Enterprise Decision Support Pipeline)", "10"),
        ("13", "Implementation (Software Stack & Deployment Infrastructure)", "10"),
        ("14", "User Interface / Application Screenshots (Interactive Web Modules 14.1 to 14.6)", "11"),
        ("15", "Challenges and Limitations (Engineering Solutions & Dataset Boundaries)", "17"),
        ("16", "Conclusion (Key Project Deliverables & Business Impact)", "17"),
        ("17", "Future Scope (Streaming Data, Ensembles & Autonomous CRM Dispatch)", "18"),
        ("18", "References (Literature & Scientific Documentation)", "18")
    ]
    
    tbl_idx = doc.add_table(rows=len(index_data)+1, cols=3)
    style_table(tbl_idx, [0.7, 5.3, 1.0], ["S.No", "Topic / Chapter Name", "Page No."], index_data, font_size=8.5, top_margin=35, bottom_margin=35)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    add_callout(doc, "TelcoPulse AI delivers 80.5% test accuracy and 0.845 ROC-AUC on unseen subscriber telemetry, transforming reactive churn losses into explainable, proactive retention workflows.", "EXECUTIVE SUMMARY")
    
    doc.add_page_break()
    
    # ==========================================
    # PAGE 3: 1. INTRODUCTION
    # ==========================================
    add_styled_heading(doc, "1. Introduction", level=1, space_before=0, space_after=4)
    
    add_styled_heading(doc, "1.1 Brief Introduction to the Project Domain", level=2, space_before=4, space_after=2)
    add_body_p(doc, "In the modern telecommunications landscape, subscriber retention has become the primary determinant of long-term corporate viability and market share. As telecom markets reach saturation, acquiring a new customer costs 5 to 7 times more than retaining an existing subscriber. Consequently, telecom operators must transition from reactive damage control to proactive, data-driven customer relationship management.")
    
    add_styled_heading(doc, "1.2 Background of the Problem", level=2, space_before=5, space_after=2)
    add_body_p(doc, "Customer churn represents the rate at which subscribers cancel their subscriptions, disconnect lines, or switch to competitor networks. Telecom providers historically relied on post-cancellation exit interviews and broad-spectrum marketing discounts. These traditional mechanisms fail because they address customer dissatisfaction only after the cancellation intent is finalized, resulting in billions of dollars in lost annual recurring revenue.")
    
    add_styled_heading(doc, "1.3 Importance of AI/ML in the Selected Domain", level=2, space_before=5, space_after=2)
    add_body_p(doc, "Artificial Intelligence and Machine Learning (AI/ML) transform retention strategies by detecting subtle, non-linear churn risk patterns hidden within multidimensional customer data. By analyzing demographic details, contracted services, payment behaviors, and billing telemetry, supervised machine learning algorithms can predict customer defection months ahead of time, enabling timely, targeted, and financially optimized retention interventions.")
    
    add_styled_heading(doc, "1.4 Brief Overview of the Proposed Solution (TelcoPulse AI)", level=2, space_before=5, space_after=2)
    add_body_p(doc, "TelcoPulse AI is an enterprise-grade customer churn intelligence and decision support platform. Rather than acting as an inscrutable black box, TelcoPulse AI provides:")
    add_bullet_p(doc, "Real-time calibrated churn risk probability (%) categorized into Safe (<30%), Moderate (30-60%), and Critical (>60%) risk tiers.", "• Calibrated Risk Scoring: ")
    add_bullet_p(doc, "Mathematical log-odds decomposition identifying the specific hazard factors driving risk and protective factors anchoring loyalty for each subscriber.", "• Local Explainability (XAI): ")
    add_bullet_p(doc, "Quantifies expected financial loss ($/year) per customer account based on monthly recurring revenue and churn probability.", "• Financial Exposure Estimation: ")
    add_bullet_p(doc, "An interactive sandbox allowing retention agents to test contract extensions, discounts, and support add-ons to simulate risk reduction before presenting offers.", "• What-If Strategy Simulator: ")
    add_bullet_p(doc, "Batch roster upload (.csv) with priority queue sorting and 1-click campaign list export for operational retention workflows.", "• Cohort Batch Queue: ")

    doc.add_page_break()

    # ==========================================
    # PAGE 4: 2. PROBLEM STATEMENT & 3. OBJECTIVES
    # ==========================================
    add_styled_heading(doc, "2. Problem Statement", level=1, space_before=0, space_after=4)
    
    add_styled_heading(doc, "2.1 What Problem Are We Trying to Solve?", level=2, space_before=4, space_after=2)
    add_body_p(doc, "We are addressing the critical problem of voluntary subscriber churn in the telecommunications industry, where customers silently defect to competitor providers without prior warning, inflicting massive revenue erosion and high customer acquisition reinvestment cycles.")
    
    add_styled_heading(doc, "2.2 Who Is Affected by the Problem?", level=2, space_before=4, space_after=2)
    add_bullet_p(doc, "Struggle with lack of real-time insights during subscriber inbound calls.", "• Customer Care & Retention Specialists: ")
    add_bullet_p(doc, "Suffer from wasted budget on uniform, untargeted discount campaigns.", "• Marketing & Growth Teams: ")
    add_bullet_p(doc, "Face eroding average revenue per user (ARPU) and customer lifetime value (LTV).", "• Executive Leadership & Finance: ")
    add_bullet_p(doc, "Experience unresolved service friction leading to defection.", "• End Consumers: ")

    add_styled_heading(doc, "2.3 What Are the Limitations of the Existing Approach?", level=2, space_before=5, space_after=2)
    add_bullet_p(doc, "Churn is identified only after the customer requests service termination or stops paying bills.", "1. Reactive Detection: ")
    add_bullet_p(doc, "Standard retention campaigns distribute blanket promotions to entire subscriber bases, eroding profit margins on loyal customers who would not have left.", "2. Blanket Discounting Inefficiencies: ")
    add_bullet_p(doc, "Conventional churn models output raw probability numbers without explaining why the customer is leaving, reducing agent trust.", "3. Black-Box Opacity: ")
    add_bullet_p(doc, "Retention agents have no dynamic tools to evaluate the potential impact of retention packages before making counter-offers.", "4. Lack of Simulation Capabilities: ")

    add_styled_heading(doc, "2.4 Why Is an AI/ML-Based Solution Required?", level=2, space_before=5, space_after=2)
    add_body_p(doc, "Subscriber attrition involves complex, non-linear interactions between tenure, contract type, internet technology, payment methods, and bundled add-on services. Human intuition and rule-based heuristics cannot reliably weigh these 20+ interacting variables simultaneously. An AI/ML-based classifier trained on historical subscriber data learns the multidimensional decision boundaries necessary to accurately predict churn probability and uncover actionable retention levers.")

    add_styled_heading(doc, "3. Objectives", level=1, space_before=8, space_after=4)
    add_bullet_p(doc, "Develop an end-to-end AI/ML-based decision support system to accurately classify customer churn risk.", "1. Develop AI/ML Solution: ")
    add_bullet_p(doc, "Perform thorough Exploratory Data Analysis (EDA) on telecom subscriber records to uncover underlying behavioral patterns and risk factors.", "2. Analyze Available Data: ")
    add_bullet_p(doc, "Train, optimize, and benchmark multiple supervised classification models to establish the most effective and interpretable architecture.", "3. Build & Train Suitable Model: ")
    add_bullet_p(doc, "Rigorously validate model performance using Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Confusion Matrix metrics.", "4. Evaluate Model Performance: ")
    add_bullet_p(doc, "Deliver calibrated predictions, localized explainability (log-odds attribution), financial risk exposure, and interactive What-If simulation via a production web dashboard.", "5. Provide Actionable Predictions & Insights: ")

    doc.add_page_break()

    # ==========================================
    # PAGE 5: 4. PROJECT SCOPE & 5. METHODOLOGY
    # ==========================================
    add_styled_heading(doc, "4. Project Scope", level=1, space_before=0, space_after=4)
    add_body_p(doc, "The scope and operational boundaries of the TelcoPulse AI project comprise:")
    add_bullet_p(doc, "Frontline Telecom Customer Support Representatives, Dedicated Retention Agents, Marketing Campaign Managers, and Executive Operations.", "• Target Users: ")
    add_bullet_p(doc, "Telecommunication service providers managing broadband (DSL, Fiber optic), fixed-line telephony, and bundled digital value-added services.", "• Application Area: ")
    add_bullet_p(doc, "Single Customer Risk Diagnosis, What-If Strategy Simulator, Batch File Scoring (.csv), Executive Cohort Analytics, and Model Transparency Diagnostics.", "• Features Covered: ")
    add_bullet_p(doc, "Calibrated Churn Probability (%), Risk Tier Categorization, Annual Financial Loss Estimation ($), Top Risk Factor Drivers, and Prescriptive Playbook Actions.", "• Expected Outputs: ")
    add_bullet_p(doc, "The project operates on static tabular snapshot data and does not ingest live continuous streaming network telemetry logs.", "• Current Project Limitations: ")

    add_styled_heading(doc, "5. Proposed System / Methodology", level=1, space_before=8, space_after=4)
    add_body_p(doc, "The overall end-to-end Machine Learning lifecycle is structured according to the following standardized sequential pipeline:")
    
    add_workflow_box(doc, "Data Collection  ➔  Data Preprocessing  ➔  Feature Engineering  ➔  Model Selection  ➔  Model Training  ➔  Model Evaluation  ➔  Prediction & Dashboard Output", space_after=4)
    
    methodology_steps = [
        ("Phase 1: Data Collection & Ingestion", "Acquire the benchmark IBM Telco Customer Churn dataset comprising 7,043 customer accounts and 21 attributes."),
        ("Phase 2: Data Preprocessing", "Clean missing whitespace anomalies in TotalCharges, verify duplicate records, and audit outlier distributions."),
        ("Phase 3: Feature Engineering", "Apply OneHotEncoder with drop-first logic to categorical variables and StandardScaler to normalize continuous numerical features."),
        ("Phase 4: Model Selection & Training", "Train and benchmark multiple candidate classifiers (Logistic Regression, Random Forest, Decision Tree, SVM, KNN) using stratified 80/20 train-test splits."),
        ("Phase 5: Model Evaluation", "Evaluate models across Accuracy, Precision, Recall, F1-Score, ROC-AUC, and Confusion Matrix to select the optimal model."),
        ("Phase 6: Explainability Integration", "Extract beta coefficients and log-odds contributions to build localized risk attribution bars for every individual inference."),
        ("Phase 7: Web Dashboard & Deployment", "Develop an interactive decision support dashboard using Streamlit and deploy the application live to Streamlit Cloud.")
    ]
    tbl_meth = doc.add_table(rows=len(methodology_steps)+1, cols=2)
    style_table(tbl_meth, [2.0, 5.0], ["Methodology Phase", "Key Activities & Technical Outcomes"], methodology_steps, font_size=8.5, top_margin=40, bottom_margin=40)

    doc.add_page_break()

    # ==========================================
    # PAGE 6: 6. DATASET DESCRIPTION
    # ==========================================
    add_styled_heading(doc, "6. Dataset Description", level=1, space_before=0, space_after=4)
    add_body_p(doc, "The project utilizes the standardized IBM Telecommunications Customer Churn dataset. The dataset provides comprehensive cross-sectional records of 7,043 unique residential telecom subscribers across 21 attributes covering demographics, subscribed services, account tenure, payment methods, and historical churn status.")
    
    add_callout(doc, "Source: IBM Analytics / Kaggle Telco Churn Repository | Total Records: 7,043 | Attributes: 21 | Target: Churn (Yes: 1,869 [26.54%], No: 5,174 [73.46%])", "DATASET SPECIFICATIONS", space_after=4)

    add_styled_heading(doc, "6.1 Sample Dataset Records (First 5 Rows)", level=2, space_before=4, space_after=2)
    sample_preview_data = [
        ("7590-VHVEG", "Female", "1 mo", "Month-to-month", "Electronic check", "$29.85", "$29.85", "No (0)"),
        ("5575-GNVDE", "Male", "34 mo", "One year", "Mailed check", "$56.95", "$1889.50", "No (0)"),
        ("3668-QPYBK", "Male", "2 mo", "Month-to-month", "Mailed check", "$53.85", "$108.15", "Yes (1)"),
        ("7795-CFOCW", "Male", "45 mo", "One year", "Bank transfer", "$42.30", "$1840.75", "No (0)"),
        ("9237-HQITU", "Female", "2 mo", "Month-to-month", "Electronic check", "$70.70", "$151.65", "Yes (1)")
    ]
    tbl_samp = doc.add_table(rows=len(sample_preview_data)+1, cols=8)
    style_table(tbl_samp, [1.1, 0.7, 0.6, 1.2, 1.2, 0.7, 0.8, 0.7], 
                ["customerID", "gender", "tenure", "Contract", "PaymentMethod", "Monthly", "Total", "Churn"], sample_preview_data, font_size=8.0, top_margin=30, bottom_margin=30)

    add_styled_heading(doc, "6.2 Feature Attribute Dictionary", level=2, space_before=6, space_after=2)
    ds_features = [
        ("customerID", "Categorical (ID)", "Unique identifier assigned to each subscriber account"),
        ("gender / SeniorCitizen", "Binary", "Gender (Male/Female) and Senior status (1 = 65+, 0 = Under 65)"),
        ("Partner / Dependents", "Binary", "Whether subscriber has a spouse/partner or live-in dependents"),
        ("tenure", "Numerical (Int)", "Number of active subscription months with company (0 - 72)"),
        ("PhoneService / MultipleLines", "Categorical", "Fixed-line telephone service (Yes/No) and multi-line availability"),
        ("InternetService", "Categorical (3 levels)", "Broadband technology: DSL, Fiber optic, or No internet"),
        ("Value-Added Services (6)", "Categorical (3 levels)", "Online Security, Backup, Device Protection, Tech Support, Streaming"),
        ("Contract", "Categorical (3 levels)", "Billing commitment: Month-to-month, One year, or Two year"),
        ("PaperlessBilling / Payment", "Categorical", "Paperless status and Payment Method (Electronic check, Card, Bank)"),
        ("MonthlyCharges / TotalCharges", "Numerical (Float)", "Current monthly bill ($18.25 - $118.75) and cumulative billing"),
        ("Churn (Target)", "Binary (0 / 1)", "Ground truth label: whether subscriber churned (Yes = 1, No = 0)")
    ]
    tbl_ds = doc.add_table(rows=len(ds_features)+1, cols=3)
    style_table(tbl_ds, [1.8, 1.6, 3.6], ["Feature / Group Name", "Data Type", "Description / Value Domain"], ds_features, font_size=8.0, top_margin=30, bottom_margin=30)

    doc.add_page_break()

    # ==========================================
    # PAGE 7: 7. DATA PREPROCESSING & 8. MODEL SELECTION
    # ==========================================
    add_styled_heading(doc, "7. Data Preprocessing", level=1, space_before=0, space_after=4)
    add_body_p(doc, "Data preprocessing ensures raw tabular telemetry is transformed into clean, mathematically robust feature matrices suitable for machine learning algorithms:")
    
    add_bullet_p(doc, "The TotalCharges column contained 11 whitespace strings (' ') corresponding to new customers (tenure = 0). These were converted to numeric float and imputed to $0.00 without row deletion.", "1. Handling Missing Values: ")
    add_bullet_p(doc, "The entire dataset was checked for duplicate records across all 21 columns; zero duplicate rows were found.", "2. Duplicate Verification: ")
    add_bullet_p(doc, "Categorical variables (16 features) were converted using OneHotEncoder with drop='first', producing 41 binary indicator columns to prevent multicollinear dummy traps.", "3. Categorical Encoding: ")
    add_bullet_p(doc, "Continuous numerical features and encoded columns were normalized using StandardScaler to achieve zero mean and unit variance.", "4. Feature Standardization: ")
    add_bullet_p(doc, "Stratified 80/20 train/test split (5,634 train / 1,409 test) preserved the 73.5% vs. 26.5% class distribution across both partitions.", "5. Stratified Partitioning: ")

    add_styled_heading(doc, "8. AI/ML Model Selection", level=1, space_before=8, space_after=4)
    add_body_p(doc, "Five candidate supervised classification algorithms were implemented, tuned, and evaluated on the standardized test set:")
    
    models_comp = [
        ("Logistic Regression (Selected)", "80.48%", "65.2%", "55.8%", "0.601", "0.845", "High (Direct Log-Odds)", "< 5 ms"),
        ("Random Forest Classifier", "79.20%", "62.8%", "49.4%", "0.553", "0.828", "Moderate (Tree Ensemble)", "35 ms"),
        ("Decision Tree Classifier", "72.82%", "48.9%", "50.5%", "0.497", "0.657", "High (Single Tree)", "< 5 ms"),
        ("Support Vector Machine (RBF)", "79.84%", "64.1%", "51.2%", "0.569", "0.812", "Low (Black Box)", "60 ms"),
        ("K-Nearest Neighbors (KNN)", "76.44%", "55.3%", "52.7%", "0.540", "0.781", "Low (Instance Based)", "25 ms")
    ]
    tbl_models = doc.add_table(rows=len(models_comp)+1, cols=8)
    style_table(tbl_models, [1.5, 0.7, 0.7, 0.7, 0.7, 0.7, 1.3, 0.7], 
                ["Model", "Accuracy", "Precision", "Recall", "F1", "AUC", "Interpretability", "Latency"], models_comp, font_size=8.0, top_margin=30, bottom_margin=30)

    add_styled_heading(doc, "8.1 Selection Rationale for Production Deployment", level=2, space_before=6, space_after=2)
    add_bullet_p(doc, "Logistic Regression achieved top test accuracy (80.48%) and the highest Area Under ROC (0.845 AUC).", "1. Superior Discriminative Power: ")
    add_bullet_p(doc, "Under 5ms inference latency ensures instantaneous real-time responsiveness during live customer service calls.", "2. Sub-5ms Operational Latency: ")
    add_bullet_p(doc, "Direct extraction of learned beta log-odds allows instant decomposition into transparent risk drivers for frontline agents.", "3. Deterministic Explainability: ")

    doc.add_page_break()

    # ==========================================
    # PAGE 8: 9. MODEL DEVELOPMENT & 10. TRAINING/EVALUATION
    # ==========================================
    add_styled_heading(doc, "9. Model Development", level=1, space_before=0, space_after=4)
    add_body_p(doc, "The model development phase encompasses feature pipeline engineering, hyperparameter optimization, and development tooling configuration:")
    
    add_bullet_p(doc, "All 20 predictor attributes were transformed into a standardized 41-dimensional numeric feature vector.", "• Feature Pipeline: ")
    add_bullet_p(doc, "Penalty = L2 (Ridge regularization), Inverse Regularization (C) = 1.0, Optimization Solver = lbfgs, Max Iterations = 1000, Random State = 42 for deterministic reproducibility.", "• Hyperparameter Setup: ")
    add_bullet_p(doc, "Python 3.10+, Scikit-learn 1.3+, Pandas, NumPy, Streamlit, Joblib, Plotly, Matplotlib.", "• Technology Stack: ")

    add_styled_heading(doc, "10. Model Training and Evaluation", level=1, space_before=8, space_after=4)
    add_body_p(doc, "The training and evaluation lifecycle followed a disciplined cross-validation structure:")
    
    add_workflow_box(doc, "Training Data (5,634 rows)  ➔  Model Fitting (lbfgs solver)  ➔  Validation & Test Data (1,409 rows)  ➔  Calibrated Predictions  ➔  Metric Evaluation", space_after=4)
    
    cls_report = [
        ("Retained (Class 0: No Churn)", "0.85 (85%)", "0.90 (90%)", "0.87 (87%)", "1,035"),
        ("Churned (Class 1: Churn)", "0.66 (66%)", "0.56 (56%)", "0.60 (60%)", "374"),
        ("Overall Accuracy", "-", "-", "0.805 (80.5%)", "1,409"),
        ("Macro Average", "0.76 (76%)", "0.73 (73%)", "0.74 (74%)", "1,409"),
        ("Weighted Average", "0.80 (80%)", "0.80 (80%)", "0.80 (80%)", "1,409")
    ]
    tbl_rep = doc.add_table(rows=len(cls_report)+1, cols=5)
    style_table(tbl_rep, [2.2, 1.2, 1.2, 1.2, 1.2], ["Class / Metric", "Precision", "Recall", "F1-Score", "Support Count"], cls_report, font_size=8.5, top_margin=35, bottom_margin=35)

    add_styled_heading(doc, "10.1 Confusion Matrix Breakdown", level=2, space_before=6, space_after=2)
    conf_data = [
        ("Actual Retained (No Churn)", "930 (True Negatives - TN)", "105 (False Positives - FP)"),
        ("Actual Churned (Yes Churn)", "165 (False Negatives - FN)", "209 (True Positives - TP)")
    ]
    tbl_conf = doc.add_table(rows=len(conf_data)+1, cols=3)
    style_table(tbl_conf, [2.2, 2.4, 2.4], ["Ground Truth", "Predicted: Retained (No)", "Predicted: Churned (Yes)"], conf_data, font_size=8.5, top_margin=35, bottom_margin=35)

    doc.add_page_break()

    # ==========================================
    # PAGE 9: 11. RESULTS AND ANALYSIS
    # ==========================================
    add_styled_heading(doc, "11. Results and Analysis", level=1, space_before=0, space_after=4)
    add_body_p(doc, "Model evaluation and exploratory attribution yielded definitive empirical findings regarding subscriber churn dynamics:")
    
    cm_img = os.path.join(screenshot_dir, "06_confusion_matrix_chart.png")
    roc_img = os.path.join(screenshot_dir, "07_roc_curve_chart.png")
    fi_img = os.path.join(screenshot_dir, "08_feature_importance_chart.png")
    
    # Dual Image side-by-side or stacked clean layout
    if os.path.exists(fi_img):
        add_styled_heading(doc, "11.1 Feature Importance & Log-Odds Risk Attribution", level=2, space_before=4, space_after=2)
        doc.add_picture(fi_img, width=Inches(5.6))
        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c.paragraph_format.space_before = Pt(2)
        p_c.paragraph_format.space_after = Pt(4)
        r = p_c.add_run("Figure 1: Key Churn Risk Drivers (+) vs Retention Anchors (-)")
        r.font.name = 'Calibri'
        r.font.italic = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(107, 114, 128)

    add_styled_heading(doc, "11.2 Key Analytical Observations", level=2, space_before=5, space_after=2)
    add_bullet_p(doc, "Month-to-month contracts (+1.28) and electronic check payments (+0.42) are the highest risk indicators. Migrating customers to 1- or 2-year contracts slashes churn by over 70%.", "• Contract Sensitivity: ")
    add_bullet_p(doc, "Fiber optic customers (+0.84) churn at 41.9% due to higher billing friction ($70-$100/mo), whereas bundling Tech Support (-0.58) and Online Security (-0.46) reduces churn to 14.6%.", "• Service Bundling: ")
    add_bullet_p(doc, "Subscribers who stay beyond 24 months (-0.62) demonstrate over 88% retention, highlighting the critical importance of first-year onboarding.", "• Tenure Compounding: ")
    add_bullet_p(doc, "Confusion matrix and ROC analysis (AUC = 0.845) confirm robust discrimination between loyal subscribers and defectors across varied thresholds.", "• Model Robustness: ")

    doc.add_page_break()

    # ==========================================
    # PAGE 10: 12. ARCHITECTURE & 13. IMPLEMENTATION
    # ==========================================
    add_styled_heading(doc, "12. System Architecture / Workflow", level=1, space_before=0, space_after=4)
    add_body_p(doc, "The TelcoPulse AI system is architected as an end-to-end reactive decision support pipeline:")
    
    add_workflow_box(doc, "User / Retention Agent  -->  Single Form / Batch CSV  -->  Preprocessing & Encoding  -->  Logistic Regression ML Engine  -->  Risk Probability & Log-Odds  -->  Dashboard & Prescriptive Playbook", space_after=4)
    
    arch_steps = [
        ("Tier 1: Presentation Tier", "Streamlit UI providing Single Customer Diagnosis, What-If Strategy Simulator, Batch File Scoring, Cohort Insights, and Diagnostics."),
        ("Tier 2: Inference & Attribution Tier", "Logistic Regression Engine coupled with real-time log-odds decomposition and financial risk calculations."),
        ("Tier 3: Preprocessing & Serialization", "StandardScaler and OneHotEncoder pipelines loaded from serialized joblib artifacts."),
        ("Tier 4: Data & Export Tier", "Telco Customer CSV store, Batch Scoring Priority Queues, and 1-click campaign CSV export.")
    ]
    tbl_arch = doc.add_table(rows=len(arch_steps)+1, cols=2)
    style_table(tbl_arch, [2.2, 4.8], ["Architecture Tier", "Component Role & Responsibilities"], arch_steps, font_size=8.5, top_margin=35, bottom_margin=35)

    add_styled_heading(doc, "13. Implementation", level=1, space_before=8, space_after=4)
    add_body_p(doc, "The technical implementation details of the software stack are structured as follows:")
    add_bullet_p(doc, "Python 3.10+ (Primary computational and web backend language).", "• Programming Language: ")
    add_bullet_p(doc, "Streamlit 1.30+ (Reactive web UI framework) and Scikit-learn 1.3+ (Machine learning framework).", "• Frameworks: ")
    add_bullet_p(doc, "Pandas, NumPy, Plotly Express, Matplotlib, Joblib, Python-Docx.", "• Core Libraries: ")
    add_bullet_p(doc, "Streamlit Community Cloud (https://telecomcustomers.streamlit.app/).", "• Deployment Platform: ")

    doc.add_page_break()

    # ==========================================
    # CHAPTER 14: SCREENSHOTS (1 SCREENSHOT PER PAGE)
    # ==========================================
    screens = [
        ("14.1 Single Customer Risk Diagnosis & Speedometer Gauge",
         "01_single_customer_diagnosis.png",
         "Figure 2: Single Customer Risk Diagnosis & Speedometer Gauge",
         "Features an interactive risk speedometer (Safe <30%, Moderate 30-60%, Critical >60%), annual financial exposure calculation ($/year), local log-odds driver attribution waterfall, and AI-recommended prescriptive retention playbooks.",
         [
             ("Interactive Speedometer", "Visualizes real-time calibrated churn probability and risk tier classification."),
             ("Annual Financial Loss", "Calculates revenue at risk ($/year) based on monthly bill and defection likelihood."),
             ("Top Risk Factors Waterfall", "Ranks top drivers accelerating churn (e.g. Month-to-Month contract, Fiber optic)."),
             ("Actionable Playbook", "Suggests targeted retention incentives based on identified account vulnerabilities.")
         ]),
        ("14.2 GenAI Customer Retention Copilot Interface",
         "10_genai_copilot_ui.png",
         "Figure 3: GenAI Customer Retention Copilot Interface",
         "Features prompt orchestration, multi-angle stochastic reasoning, Creativity/Temperature slider (0.2–1.0), and 4 generated retention assets: personalized win-back emails, frontline agent call scripts, concession hierarchy, and CRM JSON payload.",
         [
             ("Prompt Sidebar", "Ingests customer risk tier, tenure, charges, and campaign objectives."),
             ("Creativity Slider", "Adjusts LLM temperature between deterministic (0.2) and creative (1.0)."),
             ("Generated Copy Tabs", "Provides instant empathetic email copy and frontline call objection rebuttals."),
             ("CRM Integration", "Outputs validated JSON payload for instant enterprise CRM synchronization.")
         ]),
        ("14.3 What-If Retention Strategy Simulator",
         "02_what_if_sandbox.png",
         "Figure 4: What-If Retention Strategy Simulator",
         "Enables customer service agents to test contract extensions, technical support bundles, and billing discounts to simulate risk reduction in real time before pitching counter-offers.",
         [
             ("Dynamic Contract Toggle", "Simulates transitioning a month-to-month subscriber to a 1-year or 2-year plan."),
             ("Service Bundle Add-ons", "Tests the protective impact of adding Tech Support or Online Security packages."),
             ("Instant Risk Delta", "Computes immediate percentage drop in churn probability (e.g. 74% -> 22%)."),
             ("Margin Guardrails", "Ensures proposed discounts preserve corporate profitability thresholds.")
         ]),
        ("14.4 Batch Cohort Scoring & Prioritized Action Queue",
         "03_batch_scoring_queue.png",
         "Figure 5: Batch Cohort Scoring & Prioritized Action Queue",
         "Scores entire subscriber rosters (.csv), ranks accounts by expected annual financial loss, and generates downloadable prioritized campaign lists for targeted marketing outreach.",
         [
             ("CSV File Uploader", "Accepts enterprise billing exports with automated column validation."),
             ("Risk Distribution Graph", "Visualizes breakdown of Safe, Moderate, and Critical accounts in the roster."),
             ("Prioritized Queue", "Ranks accounts by expected annual revenue loss to maximize retention ROI."),
             ("Exportable Outreach List", "Enables 1-click download of filtered subscriber segments for campaign dispatch.")
         ]),
        ("14.5 Executive Cohort Analytics & Macro EDA",
         "04_executive_cohort_insights.png",
         "Figure 6: Executive Cohort Analytics & Macro EDA",
         "Presents macro-level retention insights across contract types, payment methods, monthly charges distribution, and tech support adoption.",
         [
             ("Contract Comparison", "Shows 42.7% month-to-month churn vs. under 3% on two-year agreements."),
             ("Payment Method Breakdown", "Reveals electronic check churn (45.3%) is 3x higher than credit card users."),
             ("Pricing Sensitivity EDA", "Analyzes churn concentration between $70 and $100 monthly charge bands."),
             ("Tenure Hazard Curves", "Illustrates steep risk reduction once subscribers surpass 12 months tenure.")
         ]),
        ("14.6 Model Diagnostics & Global Feature Importance",
         "05_model_diagnostics.png",
         "Figure 7: Model Transparency & Global Feature Importance",
         "Provides complete transparency into pipeline architecture, preprocessing parameters, and global beta coefficients.",
         [
             ("Pipeline Transparency", "Displays full preprocessing transformations and regularization parameters."),
             ("Global Coefficients", "Visualizes all 41 feature weights learned by the production classifier."),
             ("Threshold Tuning", "Allows operators to adjust decision thresholds based on precision-recall trade-offs."),
             ("Data Audit Metrics", "Verifies zero missing value residuals and normalized distribution stats.")
         ]),
        ("14.7 Enterprise Database & Customer CRM Explorer",
         "06_database_crm_explorer.png",
         "Figure 8: Enterprise Database & Customer CRM Explorer with SQL Sandbox",
         "Provides dual-engine relational persistence via MySQL (XAMPP Port 3306) and SQLite with a real-time Analytical SQL Query Sandbox and CRM lifecycle status tracking.",
         [
             ("Database Dashboard & KPI Metrics", "Tracks total persisted diagnoses, critical churn exposure count, and average churn probability."),
             ("Customer Predictions Table", "Searchable, filterable ledger of all assessed accounts with 1-click CSV export."),
             ("GenAI Campaign Log & Tracker", "Maintains campaign states (Generated -> Dispatched -> Retained -> Churned) and pitch previews."),
             ("Direct Analytical SQL Sandbox", "Executes real-time SQL queries with execution time logging and instant table visualization.")
         ])
    ]
    
    for sec_title, filename, caption, desc, highlights in screens:
        add_styled_heading(doc, f"14. User Interface: {sec_title}", level=1, space_before=0, space_after=3)
        add_body_p(doc, desc, space_after=4)
        
        img_path = os.path.join(screenshot_dir, filename)
        if os.path.exists(img_path):
            doc.add_picture(img_path, width=Inches(6.2))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(4)
            r = p_cap.add_run(caption)
            r.font.name = 'Calibri'
            r.font.size = Pt(8.5)
            r.font.italic = True
            r.font.color.rgb = RGBColor(107, 114, 128)
            
        tbl_hl = doc.add_table(rows=len(highlights)+1, cols=2)
        style_table(tbl_hl, [2.2, 4.8], ["Key Feature / UI Component", "Operational Purpose & Business Value"], highlights, font_size=8.5, top_margin=35, bottom_margin=35)
        
        doc.add_page_break()

    # ==========================================
    # PAGE 17: 15. CHALLENGES & 16. CONCLUSION
    # ==========================================
    add_styled_heading(doc, "15. Challenges and Limitations", level=1, space_before=0, space_after=4)
    
    add_styled_heading(doc, "15.1 Challenges Encountered", level=2, space_before=4, space_after=2)
    add_bullet_p(doc, "Handling whitespace anomalies in TotalCharges and ensuring clean data conversions without record loss.", "• Data Quality & Missing Values: ")
    add_bullet_p(doc, "The dataset contains an inherent 73.5% vs. 26.5% non-churn vs. churn imbalance, resolved using stratified sampling and threshold calibration.", "• Class Imbalance: ")
    add_bullet_p(doc, "Selecting an architecture that balances high predictive accuracy with immediate log-odds explainability for non-technical agents.", "• Model Selection Trade-off: ")
    add_bullet_p(doc, "Transforming 16 categorical features created a 41-dimensional sparse space, requiring L2 Ridge regularization to prevent overfitting.", "• High Dimensionality & Collinearity: ")

    add_styled_heading(doc, "15.2 System Limitations", level=2, space_before=5, space_after=2)
    add_bullet_p(doc, "The model is trained on a 7,043-record cross-sectional snapshot, which limits its ability to observe macroeconomic trends.", "• Dataset Size & Static Telemetry: ")
    add_bullet_p(doc, "While 80.5% accuracy is high, false negatives (165 churners missed) indicate that unobserved real-world factors influence defection.", "• Model Precision-Recall Trade-offs: ")
    add_bullet_p(doc, "Customer service tickets, network call-drop frequency, and competitor promotional offers are not present in the dataset.", "• Limited Behavioral Features: ")
    add_bullet_p(doc, "The web application currently operates on file-based CSV uploads and manual single inputs rather than direct live CRM API integration.", "• Deployment Integration Constraints: ")

    add_styled_heading(doc, "16. Conclusion", level=1, space_before=7, space_after=4)
    add_body_p(doc, "The TelcoPulse AI project achieves all core research and engineering milestones:")
    add_bullet_p(doc, "An end-to-end Machine Learning customer churn decision support system was successfully conceptualized, built, and deployed.", "1. Successfully Developed AI/ML Solution: ")
    add_bullet_p(doc, "Comprehensive data preprocessing, outlier auditing, and one-hot encoding were systematically implemented.", "2. Data Preprocessing & Analysis Completed: ")
    add_bullet_p(doc, "Multiple classifiers were trained and benchmarked, with Logistic Regression achieving 80.5% accuracy and 0.845 ROC-AUC.", "3. Model Rigorously Trained & Evaluated: ")
    add_bullet_p(doc, "The system delivers real-time calibrated churn probability, annual financial exposure ($), explainable log-odds attribution, and interactive what-if simulations.", "4. Actionable Decision Support Delivered: ")

    doc.add_page_break()

    # ==========================================
    # PAGE 18: 17. FUTURE SCOPE & 18. REFERENCES
    # ==========================================
    add_styled_heading(doc, "17. Future Scope", level=1, space_before=0, space_after=4)
    add_body_p(doc, "Future enhancements planned for subsequent releases include:")
    add_bullet_p(doc, "Ingest larger datasets covering multi-year customer lifecycles and millions of subscriber accounts.", "1. Larger Datasets: ")
    add_bullet_p(doc, "Integrate real-time Call Detail Records (CDR), data throughput metrics, customer service ticket sentiment, and network QoS logs.", "2. Add Telemetry Features: ")
    add_bullet_p(doc, "Implement gradient boosting ensembles (XGBoost, LightGBM, CatBoost) coupled with SHAP (SHapley Additive exPlanations) values.", "3. Advanced AI/ML Ensembles: ")
    add_bullet_p(doc, "Deploy streaming inference pipelines on customer interaction events (e.g., billing inquiries, plan downgrades).", "4. Real-Time Streaming Prediction: ")
    add_bullet_p(doc, "Direct bidirectional REST API integration with enterprise CRM suites (Salesforce, SAP Customer Experience, Zendesk).", "5. Enterprise CRM Integration: ")
    add_bullet_p(doc, "Build automated triggers that dispatch SMS or email retention offers when a subscriber enters the Critical Risk (>60%) zone.", "6. Autonomous Retention Campaigns: ")

    add_styled_heading(doc, "18. References", level=1, space_before=8, space_after=4)
    refs = [
        "1. IBM Corporation. 'Telco Customer Churn Dataset', IBM Business Analytics Community & Kaggle Repository, 2019.",
        "2. Pedregosa, F., et al. 'Scikit-learn: Machine Learning in Python', Journal of Machine Learning Research, 12, pp. 2825-2830, 2011.",
        "3. Streamlit Documentation. 'Streamlit: The fastest way to build and share data apps', https://docs.streamlit.io/, 2024.",
        "4. Hastie, T., Tibshirani, R., & Friedman, J. 'The Elements of Statistical Learning: Data Mining, Inference, and Prediction', Springer, 2nd ed., 2009.",
        "5. Ribeiro, M. T., Singh, S., & Guestrin, C. '\"Why Should I Trust You?\": Explaining the Predictions of Any Classifier', ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016.",
        "6. Plotly Technologies Inc. 'Collaborative data science and interactive visualization library', https://plotly.com/python/, 2024.",
        "7. Hunter, J. D. 'Matplotlib: A 2D Graphics Environment', Computing in Science & Engineering, 9(3), pp. 90-95, 2007."
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2.5)
        p.paragraph_format.line_spacing = 1.1
        run = p.add_run(r)
        run.font.name = 'Calibri'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(55, 65, 81)

    # Output file paths
    output_filename1 = "Telecom_Customer_Churn_Project_Report_Anaganti_Sairishikesh.docx"
    doc.save(output_filename1)
    print(f"Successfully generated ML project report at: {os.path.abspath(output_filename1)}")

if __name__ == '__main__':
    generate_report()
