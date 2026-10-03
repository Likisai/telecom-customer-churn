"""
Database Management Module for TelcoPulse AI
Supports MySQL (via XAMPP / PyMySQL / SQLAlchemy) with seamless SQLite fallback.
Provides complete CRUD, persistence for Single Diagnosis, GenAI Campaigns, and Batch Scores.
"""

import os
import datetime
import json
import sqlite3
import warnings
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_config.json")
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telecom_churn.db")

# Default connection settings
DEFAULT_CONFIG = {
    "engine": "mysql",  # "mysql" or "sqlite"
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "telecom_churn",
    "use_fallback": True
}


def load_db_config():
    """Loads database configuration from json file or defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return {**DEFAULT_CONFIG, **cfg}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_db_config(cfg):
    """Saves database configuration to json file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        return True
    except Exception:
        return False


def test_db_connection(config=None):
    """
    Tests connection to MySQL or SQLite.
    Returns (success: bool, message: str, active_engine: str)
    """
    cfg = config or load_db_config()
    
    if cfg.get("engine") == "mysql":
        try:
            import pymysql
            # Connect to server
            conn = pymysql.connect(
                host=cfg.get("host", "localhost"),
                port=int(cfg.get("port", 3306)),
                user=cfg.get("user", "root"),
                password=cfg.get("password", ""),
                charset='utf8mb4',
                connect_timeout=3
            )
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg.get('database', 'telecom_churn')}` CHARACTER SET utf8mb4;")
            conn.close()
            return True, f"Successfully connected to MySQL server on {cfg.get('host')}:{cfg.get('port')}", "mysql"
        except Exception as e:
            err_msg = str(e)
            if "Access denied" in err_msg:
                return False, f"MySQL Authentication Failed: Check your username and password. Details: {err_msg}", "mysql"
            return False, f"MySQL Connection Error: {err_msg}", "mysql"
    else:
        try:
            conn = sqlite3.connect(SQLITE_DB_PATH)
            conn.close()
            return True, f"Connected to local SQLite database ({SQLITE_DB_PATH})", "sqlite"
        except Exception as e:
            return False, f"SQLite Error: {str(e)}", "sqlite"


def get_db_connection(config=None):
    """
    Connects to the configured database.
    If MySQL fails and use_fallback is True, falls back to SQLite.
    Returns (conn, active_engine)
    """
    cfg = config or load_db_config()
    
    if cfg.get("engine") == "mysql":
        try:
            import pymysql
            # Ensure DB exists
            server_conn = pymysql.connect(
                host=cfg.get("host", "localhost"),
                port=int(cfg.get("port", 3306)),
                user=cfg.get("user", "root"),
                password=cfg.get("password", ""),
                autocommit=True,
                charset='utf8mb4',
                connect_timeout=3
            )
            with server_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{cfg.get('database', 'telecom_churn')}` CHARACTER SET utf8mb4;")
            server_conn.close()
            
            conn = pymysql.connect(
                host=cfg.get("host", "localhost"),
                port=int(cfg.get("port", 3306)),
                user=cfg.get("user", "root"),
                password=cfg.get("password", ""),
                database=cfg.get("database", "telecom_churn"),
                autocommit=True,
                charset='utf8mb4'
            )
            return conn, "mysql"
        except Exception as e:
            if not cfg.get("use_fallback", True):
                raise e

    # SQLite fallback
    conn = sqlite3.connect(SQLITE_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def init_database(config=None):
    """Initializes tables in database."""
    conn, db_type = get_db_connection(config)
    
    if db_type == "mysql":
        table_predictions = """
        CREATE TABLE IF NOT EXISTS customer_predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            customer_name VARCHAR(100) DEFAULT 'Customer',
            gender VARCHAR(20),
            senior_citizen INT,
            partner VARCHAR(10),
            dependents VARCHAR(10),
            tenure INT,
            phone_service VARCHAR(10),
            multiple_lines VARCHAR(25),
            internet_service VARCHAR(25),
            online_security VARCHAR(25),
            online_backup VARCHAR(25),
            device_protection VARCHAR(25),
            tech_support VARCHAR(25),
            streaming_tv VARCHAR(25),
            streaming_movies VARCHAR(25),
            contract VARCHAR(25),
            paperless_billing VARCHAR(10),
            payment_method VARCHAR(50),
            monthly_charges FLOAT,
            total_charges FLOAT,
            churn_prediction INT,
            churn_probability FLOAT,
            risk_tier VARCHAR(20),
            key_churn_drivers TEXT,
            source VARCHAR(30) DEFAULT 'Single Diagnosis',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (customer_id),
            INDEX (risk_tier),
            INDEX (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        table_campaigns = """
        CREATE TABLE IF NOT EXISTS retention_campaigns (
            id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id VARCHAR(50) NOT NULL,
            customer_name VARCHAR(100),
            risk_tier VARCHAR(20),
            monthly_charges FLOAT,
            campaign_goal VARCHAR(100),
            outreach_tone VARCHAR(50),
            target_channel VARCHAR(50),
            promo_code VARCHAR(50),
            retention_offer TEXT,
            personalized_script TEXT,
            action_status VARCHAR(30) DEFAULT 'Generated',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (customer_id),
            INDEX (action_status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        table_batch = """
        CREATE TABLE IF NOT EXISTS batch_scoring_runs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            batch_name VARCHAR(100),
            total_records INT,
            high_risk_count INT,
            medium_risk_count INT,
            low_risk_count INT,
            avg_churn_prob FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
    else:
        table_predictions = """
        CREATE TABLE IF NOT EXISTS customer_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            customer_name TEXT DEFAULT 'Customer',
            gender TEXT,
            senior_citizen INTEGER,
            partner TEXT,
            dependents TEXT,
            tenure INTEGER,
            phone_service TEXT,
            multiple_lines TEXT,
            internet_service TEXT,
            online_security TEXT,
            online_backup TEXT,
            device_protection TEXT,
            tech_support TEXT,
            streaming_tv TEXT,
            streaming_movies TEXT,
            contract TEXT,
            paperless_billing TEXT,
            payment_method TEXT,
            monthly_charges REAL,
            total_charges REAL,
            churn_prediction INTEGER,
            churn_probability REAL,
            risk_tier TEXT,
            key_churn_drivers TEXT,
            source TEXT DEFAULT 'Single Diagnosis',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        table_campaigns = """
        CREATE TABLE IF NOT EXISTS retention_campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT NOT NULL,
            customer_name TEXT,
            risk_tier TEXT,
            monthly_charges REAL,
            campaign_goal TEXT,
            outreach_tone TEXT,
            target_channel TEXT,
            promo_code TEXT,
            retention_offer TEXT,
            personalized_script TEXT,
            action_status TEXT DEFAULT 'Generated',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        table_batch = """
        CREATE TABLE IF NOT EXISTS batch_scoring_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_name TEXT,
            total_records INTEGER,
            high_risk_count INTEGER,
            medium_risk_count INTEGER,
            low_risk_count INTEGER,
            avg_churn_prob REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

    cursor = conn.cursor()
    cursor.execute(table_predictions)
    cursor.execute(table_campaigns)
    cursor.execute(table_batch)
    conn.commit()
    conn.close()
    return db_type


def save_single_prediction(data_dict, config=None):
    """Saves a single customer prediction into customer_predictions table."""
    conn, db_type = get_db_connection(config)
    cursor = conn.cursor()
    
    cols = [
        "customer_id", "customer_name", "gender", "senior_citizen", "partner", "dependents",
        "tenure", "phone_service", "multiple_lines", "internet_service", "online_security",
        "online_backup", "device_protection", "tech_support", "streaming_tv", "streaming_movies",
        "contract", "paperless_billing", "payment_method", "monthly_charges", "total_charges",
        "churn_prediction", "churn_probability", "risk_tier", "key_churn_drivers", "source"
    ]
    
    drivers_str = data_dict.get("key_churn_drivers", "")
    if isinstance(drivers_str, (list, dict)):
        drivers_str = json.dumps(drivers_str)
        
    values = [
        str(data_dict.get("customer_id", "CUST-XXXX")),
        str(data_dict.get("customer_name", "Customer")),
        str(data_dict.get("gender", "")),
        int(data_dict.get("senior_citizen", 0)),
        str(data_dict.get("partner", "")),
        str(data_dict.get("dependents", "")),
        int(data_dict.get("tenure", 0)),
        str(data_dict.get("phone_service", "")),
        str(data_dict.get("multiple_lines", "")),
        str(data_dict.get("internet_service", "")),
        str(data_dict.get("online_security", "")),
        str(data_dict.get("online_backup", "")),
        str(data_dict.get("device_protection", "")),
        str(data_dict.get("tech_support", "")),
        str(data_dict.get("streaming_tv", "")),
        str(data_dict.get("streaming_movies", "")),
        str(data_dict.get("contract", "")),
        str(data_dict.get("paperless_billing", "")),
        str(data_dict.get("payment_method", "")),
        float(data_dict.get("monthly_charges", 0.0)),
        float(data_dict.get("total_charges", 0.0)),
        int(data_dict.get("churn_prediction", 0)),
        float(data_dict.get("churn_probability", 0.0)),
        str(data_dict.get("risk_tier", "Low Risk")),
        str(drivers_str),
        str(data_dict.get("source", "Single Diagnosis"))
    ]
    
    ph = "%s" if db_type == "mysql" else "?"
    placeholders = ", ".join([ph] * len(cols))
    col_names = ", ".join(cols)
    
    query = f"INSERT INTO customer_predictions ({col_names}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True


def save_retention_campaign(camp_dict, config=None):
    """Saves a generated GenAI retention campaign into retention_campaigns table."""
    conn, db_type = get_db_connection(config)
    cursor = conn.cursor()
    
    cols = [
        "customer_id", "customer_name", "risk_tier", "monthly_charges",
        "campaign_goal", "outreach_tone", "target_channel", "promo_code",
        "retention_offer", "personalized_script", "action_status"
    ]
    
    values = [
        str(camp_dict.get("customer_id", "CUST-XXXX")),
        str(camp_dict.get("customer_name", "Customer")),
        str(camp_dict.get("risk_tier", "Unknown")),
        float(camp_dict.get("monthly_charges", 0.0)),
        str(camp_dict.get("campaign_goal", "")),
        str(camp_dict.get("outreach_tone", "")),
        str(camp_dict.get("target_channel", "")),
        str(camp_dict.get("promo_code", "")),
        str(camp_dict.get("retention_offer", "")),
        str(camp_dict.get("personalized_script", "")),
        str(camp_dict.get("action_status", "Generated"))
    ]
    
    ph = "%s" if db_type == "mysql" else "?"
    placeholders = ", ".join([ph] * len(cols))
    col_names = ", ".join(cols)
    
    query = f"INSERT INTO retention_campaigns ({col_names}) VALUES ({placeholders})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True


def save_batch_predictions(df_batch, batch_name="Batch Upload", config=None):
    """Saves multiple batch scored customer records and creates a batch summary record."""
    conn, db_type = get_db_connection(config)
    cursor = conn.cursor()
    
    total = len(df_batch)
    high = int((df_batch["Risk_Tier"].astype(str).str.contains("Critical", case=False)).sum() if "Risk_Tier" in df_batch.columns else 0)
    med = int((df_batch["Risk_Tier"].astype(str).str.contains("Moderate", case=False)).sum() if "Risk_Tier" in df_batch.columns else 0)
    low = int((df_batch["Risk_Tier"].astype(str).str.contains("Low", case=False)).sum() if "Risk_Tier" in df_batch.columns else 0)
    avg_p = float(df_batch["Churn_Probability"].mean() if "Churn_Probability" in df_batch.columns else 0.0)
    
    ph = "%s" if db_type == "mysql" else "?"
    cursor.execute(
        f"INSERT INTO batch_scoring_runs (batch_name, total_records, high_risk_count, medium_risk_count, low_risk_count, avg_churn_prob) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})",
        [batch_name, total, high, med, low, avg_p]
    )
    
    cols = [
        "customer_id", "customer_name", "gender", "senior_citizen", "partner", "dependents",
        "tenure", "phone_service", "multiple_lines", "internet_service", "online_security",
        "online_backup", "device_protection", "tech_support", "streaming_tv", "streaming_movies",
        "contract", "paperless_billing", "payment_method", "monthly_charges", "total_charges",
        "churn_prediction", "churn_probability", "risk_tier", "source"
    ]
    
    insert_cols = ", ".join(cols)
    placeholders = ", ".join([ph] * len(cols))
    query = f"INSERT INTO customer_predictions ({insert_cols}) VALUES ({placeholders})"
    
    rows_to_insert = []
    for _, row in df_batch.iterrows():
        cust_id = str(row.get("customerID", row.get("customer_id", f"BATCH-{_}")))
        rows_to_insert.append([
            cust_id,
            f"Customer {cust_id[:8]}",
            str(row.get("gender", "Female")),
            int(row.get("SeniorCitizen", 0)),
            str(row.get("Partner", "No")),
            str(row.get("Dependents", "No")),
            int(row.get("tenure", 0)),
            str(row.get("PhoneService", "Yes")),
            str(row.get("MultipleLines", "No")),
            str(row.get("InternetService", "DSL")),
            str(row.get("OnlineSecurity", "No")),
            str(row.get("OnlineBackup", "No")),
            str(row.get("DeviceProtection", "No")),
            str(row.get("TechSupport", "No")),
            str(row.get("StreamingTV", "No")),
            str(row.get("StreamingMovies", "No")),
            str(row.get("Contract", "Month-to-month")),
            str(row.get("PaperlessBilling", "Yes")),
            str(row.get("PaymentMethod", "Electronic check")),
            float(row.get("MonthlyCharges", 0.0)),
            float(row.get("TotalCharges", 0.0) if pd.notnull(row.get("TotalCharges")) and str(row.get("TotalCharges")).strip() != "" else 0.0),
            int(row.get("Prediction", 0)),
            float(row.get("Churn_Probability", 0.0)),
            str(row.get("Risk_Tier", "Low Risk")),
            "Batch Scoring"
        ])
    
    cursor.executemany(query, rows_to_insert)
    conn.commit()
    conn.close()
    return total


def get_predictions_df(limit=300, risk_filter=None, config=None):
    """Retrieves customer predictions as a Pandas DataFrame."""
    conn, db_type = get_db_connection(config)
    query = "SELECT * FROM customer_predictions"
    params = []
    
    if risk_filter and risk_filter != "All":
        query += " WHERE risk_tier LIKE ?" if db_type == "sqlite" else " WHERE risk_tier LIKE %s"
        params.append(f"%{risk_filter}%")
        
    query += " ORDER BY id DESC LIMIT " + str(int(limit))
    
    try:
        if params:
            df = pd.read_sql(query, conn, params=params)
        else:
            df = pd.read_sql(query, conn)
    finally:
        conn.close()
        
    if not df.empty:
        # Explicitly coerce numeric columns to avoid pandas object dtype issues
        numeric_floats = ["monthly_charges", "total_charges", "churn_probability"]
        for c in numeric_floats:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype(float)
                
        numeric_ints = ["id", "tenure", "senior_citizen", "churn_prediction"]
        for c in numeric_ints:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
        
    return df


def get_campaigns_df(limit=200, config=None):
    """Retrieves retention campaigns as a Pandas DataFrame."""
    conn, db_type = get_db_connection(config)
    query = f"SELECT * FROM retention_campaigns ORDER BY id DESC LIMIT {int(limit)}"
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
        
    if not df.empty and "monthly_charges" in df.columns:
        df["monthly_charges"] = pd.to_numeric(df["monthly_charges"], errors="coerce").fillna(0.0).astype(float)
        
    return df


def get_db_summary_stats(config=None):
    """Returns high-level statistics for the database dashboard."""
    conn, db_type = get_db_connection(config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as cnt FROM customer_predictions")
        row = cursor.fetchone()
        total_preds = row["cnt"] if isinstance(row, dict) else (row[0] if row else 0)
        
        cursor.execute("SELECT COUNT(*) as cnt FROM customer_predictions WHERE risk_tier LIKE '%Critical%'")
        row = cursor.fetchone()
        critical_count = row["cnt"] if isinstance(row, dict) else (row[0] if row else 0)
        
        cursor.execute("SELECT COUNT(*) as cnt FROM retention_campaigns")
        row = cursor.fetchone()
        campaigns_count = row["cnt"] if isinstance(row, dict) else (row[0] if row else 0)
        
        cursor.execute("SELECT AVG(churn_probability) as avg_p FROM customer_predictions")
        row = cursor.fetchone()
        avg_p = row["avg_p"] if isinstance(row, dict) else (row[0] if row else 0.0)
        avg_churn = float(avg_p) if avg_p is not None else 0.0
    except Exception:
        total_preds, critical_count, campaigns_count, avg_churn = 0, 0, 0, 0.0
    finally:
        conn.close()
        
    return {
        "db_type": db_type,
        "total_predictions": total_preds,
        "critical_risk_count": critical_count,
        "campaigns_count": campaigns_count,
        "avg_churn_rate": avg_churn
    }


def update_campaign_status(campaign_id, new_status, config=None):
    """Updates status of a retention campaign."""
    conn, db_type = get_db_connection(config)
    cursor = conn.cursor()
    ph = "%s" if db_type == "mysql" else "?"
    cursor.execute(f"UPDATE retention_campaigns SET action_status = {ph} WHERE id = {ph}", [new_status, campaign_id])
    conn.commit()
    conn.close()
    return True


def delete_prediction_record(record_id, config=None):
    """Deletes a prediction record by ID."""
    conn, db_type = get_db_connection(config)
    cursor = conn.cursor()
    ph = "%s" if db_type == "mysql" else "?"
    cursor.execute(f"DELETE FROM customer_predictions WHERE id = {ph}", [record_id])
    conn.commit()
    conn.close()
    return True


def execute_custom_query(sql_query, config=None):
    """Safely executes a custom SQL query for the explorer UI."""
    conn, db_type = get_db_connection(config)
    try:
        df = pd.read_sql(sql_query, conn)
        return True, df, db_type
    except Exception as e:
        return False, str(e), db_type
    finally:
        conn.close()


def seed_demo_data(predict_fn=None, limit=50, config=None):
    """Loads records from WA_Fn-UseC_-Telco-Customer-Churn.csv into the database."""
    dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "WA_Fn-UseC_-Telco-Customer-Churn.csv")
    if not os.path.exists(dataset_path):
        return 0
        
    df = pd.read_csv(dataset_path).head(limit)
    
    if predict_fn:
        preds, probs, _, _, _ = predict_fn(df)
        df["Prediction"] = preds
        df["Churn_Probability"] = probs
        df["Risk_Tier"] = df["Churn_Probability"].apply(
            lambda p: "Critical Risk" if p > 0.6 else ("Moderate Risk" if p > 0.3 else "Low Risk")
        )
    else:
        df["Prediction"] = (df["Churn"] == "Yes").astype(int) if "Churn" in df.columns else 0
        df["Churn_Probability"] = df["Prediction"].astype(float) * 0.75 + 0.15
        df["Risk_Tier"] = df["Churn_Probability"].apply(
            lambda p: "Critical Risk" if p > 0.6 else ("Moderate Risk" if p > 0.3 else "Low Risk")
        )
        
    return save_batch_predictions(df, batch_name=f"Initial Seed Data ({len(df)} records)", config=config)
