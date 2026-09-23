# ⚡ TelcoPulse AI: Telecom Customer Churn & Retention Intelligence Suite

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TelcoPulse AI** is an enterprise-grade AI decision support system designed for telecom customer retention teams. Going beyond basic churn probability predictions, TelcoPulse provides **real-time local risk explainability**, **prescriptive action playbooks**, **interactive "What-If" contract simulations**, and **cohort-level batch prioritization**.

---

## 🌟 Key Features

### 1. 🎯 Individual Customer Churn Diagnosis & Explainability
- **Real-Time Risk Gauge**: Visual speedometer mapping churn risk into actionable tiers (*Safe <30%*, *Moderate 30-60%*, *Critical >60%*).
- **Local Feature Attribution (Log-Odds Decomposition)**: Diverging waterfall bars showing the top drivers increasing vs protecting against churn for every specific customer.
- **Financial Risk Exposure**: Automatically calculates **Estimated Annual Revenue at Risk ($/yr)**.
- **Prescriptive Retention Playbook**: Generates targeted business actions (e.g., contract extension incentives, auto-pay discounts, free tech support trials).
- **1-Click Profile Presets**: Quickly load High Risk, Moderate, or Loyal customer personas.

### 2. 🎛️ What-If Retention Strategy Simulator
- Interactive sandbox allowing retention specialists to test retention packages (contract extensions, bundling security/support, fee discounts).
- Live recalculation showing **Absolute Risk Reduction (▼ %)** and **Relative Improvement (+%)** before making an offer to the customer.

### 3. 📁 Batch Cohort Scoring & Prioritized Action Queue
- Upload any customer `.csv` or load a sample cohort.
- Scores all accounts simultaneously and ranks them by **Expected Annual Loss**.
- Multi-criteria filtering by Risk Tier and Contract type.
- 1-click export of prioritized outreach campaign lists (`.csv`).

### 4. 📊 Executive Cohort Insights & Macro EDA
- Interactive Plotly visualizations for macro patterns:
  - Churn rates across Contract Types & Payment Methods.
  - Monthly charge density distribution vs churn status.
  - Value-added services (Tech Support, Online Security) impact analysis.

### 5. 🧠 Model Diagnostics & Transparency
- Complete visibility into ML pipeline architecture, data scalers, one-hot encoders, and global beta coefficients.

---

## 📸 Screenshots

| 1. Single Customer Diagnosis & Playbook | 2. What-If Retention Sandbox |
|:---:|:---:|
| ![Single Customer Diagnosis](screenshots/01_single_customer_diagnosis.png) | ![What-If Sandbox](screenshots/02_what_if_sandbox.png) |

| 3. Batch Scoring & Priority Queue | 4. Executive Cohort Analytics |
|:---:|:---:|
| ![Batch Scoring Queue](screenshots/03_batch_scoring_queue.png) | ![Executive Cohort Insights](screenshots/04_executive_cohort_insights.png) |

| 5. AI Model Diagnostics |
|:---:|
| ![Model Diagnostics](screenshots/05_model_diagnostics.png) |

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10 or higher
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <YOUR_REPO_URL>
   cd "Telecom customer churn"
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit App:**
   ```bash
   streamlit run app.py
   ```
   *Open [http://localhost:8501](http://localhost:8501) in your browser.*

---

## 🌐 Deploy as a Live Demo (Streamlit Community Cloud)

You can host this application for free on **Streamlit Community Cloud**:
1. Push this repository to GitHub.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/).
3. Click **"New app"**, select your repository, branch `main`, and main file `app.py`.
4. Click **Deploy** — your live demo URL will be ready in under a minute!

---

## 🛠️ Tech Stack
- **Framework**: [Streamlit](https://streamlit.io/)
- **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/), [Joblib](https://joblib.readthedocs.io/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Visualizations**: [Plotly](https://plotly.com/python/)

---

## 📄 License
This project is licensed under the MIT License.
