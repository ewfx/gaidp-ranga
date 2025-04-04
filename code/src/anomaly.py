import os
import pandas as pd
import json
import time
import google.generativeai as genai
import re
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import json
import pandas as pd
import numpy as np
import tiktoken
from constant import *

# Configure Gemini API Key

genai.configure(api_key=API_KEY)




def detect_anomalies_clustering2(df, anomaly_threshold=1.5):
    """
    Detect anomalies using Isolation Forest for numerical data and DBSCAN for categorical data.
    
    Parameters:
    - df (pd.DataFrame): Input DataFrame
    - anomaly_threshold (float): Minimum anomaly score to consider a row as an anomaly
    
    Returns:
    - pd.DataFrame: DataFrame containing only the anomalous rows
    """
    df_clean = df.copy()
    
    # Separate numerical and categorical columns
    numerical_cols = df_clean.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df_clean.select_dtypes(include=['object']).columns.tolist()
    
    anomaly_scores = np.zeros(len(df_clean))  # Initialize anomaly scores
    
    # Process numerical data
    if numerical_cols:
        scaler = StandardScaler()
        scaled_numerical_data = scaler.fit_transform(df_clean[numerical_cols])
        
        # Apply Isolation Forest
        iso_forest = IsolationForest(contamination='auto', random_state=42)
        num_anomaly_scores = -iso_forest.fit(scaled_numerical_data).decision_function(scaled_numerical_data)
        
        # Assign higher weight to individual extreme values
        for i, col in enumerate(numerical_cols):
            col_scores = np.abs(scaled_numerical_data[:, i]) * num_anomaly_scores
            anomaly_scores += col_scores
    
    # Process categorical data
    if categorical_cols:
        encoder = OneHotEncoder(handle_unknown='ignore')
        encoded_categorical_data = encoder.fit_transform(df_clean[categorical_cols]).toarray()
        
        # Apply DBSCAN for density-based anomaly detection
        dbscan = DBSCAN(eps=0.5, min_samples=3, metric='hamming')
        cat_anomaly_pred = dbscan.fit_predict(encoded_categorical_data)
        
        # Increase anomaly score for categorical anomalies
        for j in range(len(df_clean)):
            if cat_anomaly_pred[j] == -1:
                anomaly_scores[j] += 2  # Weight categorical anomalies
    
    # Add anomaly scores to the DataFrame
    df_clean['anomaly_score'] = anomaly_scores
    
    # Return only rows where the anomaly score exceeds the threshold
    anomalies_df = df_clean[df_clean['anomaly_score'] > anomaly_threshold]
    return anomalies_df

# Process Data file

def processData(df):
    # Tokenization
    enc = tiktoken.get_encoding("cl100k_base")
    token_count = sum(len(enc.encode(str(row))) for row in df.astype(str).values.flatten())
    
    # Free Gemini API token limit (e.g., 8k tokens per request)
    FREE_GEMINI_TOKEN_LIMIT = 8000
    
    if token_count > FREE_GEMINI_TOKEN_LIMIT:
        print("Token limit exceeded, running anomaly detection...")
        return detect_anomalies_clustering2(df)
    else:
        print("Token limit not exceeded")
        return df


# --- Load JSON Rules ---
def load_rules():
    """Load validation rules from a JSON file."""
    with open(RULES_FILE, "r") as file:
        return json.load(file)

# --- Log Gemini API Responses ---
def log_response(prompt, response):
    """Logs Gemini requests and responses to a file."""
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write("\n=== Gemini Request ===\n")
        log.write(prompt + "\n")
        log.write("\n=== Gemini Response ===\n")
        log.write(response + "\n\n")

# --- Call Gemini API for Batch Validation ---
def interpret_rules_batch(batch_data):
    """Sends batch data to Gemini for validation and retrieves responses."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            "You are a strict data validation AI. Return responses **only** in the following format:\n"
            "Row <row_number>: Valid OR\n"
            "Row <row_number>: Anomaly - <reason>\n"
            "Remediation: <remediation action>\n\n"
            "For each row below, validate based on the given rule:\n\n"
        )

        for row_index, column_name, rule_text, column_value in batch_data:
            prompt += (
                f"Row {row_index + 1}: Column '{column_name}' Value '{column_value}' "
                f"should follow these rules: {', '.join(rule_text)}\n"
            )

        response = model.generate_content([prompt])
        response_text = response.text.strip()

        # Log response for debugging
        log_response(prompt, response_text)
        print(f"\n🔍 Gemini Response Logged:\n{response_text}\n")

        return response_text

    except Exception as e:
        print(f"API Error: {e}. Retrying in 60 seconds...")
        time.sleep(60)
        return interpret_rules_batch(batch_data)

# --- Parse Gemini's Response ---
def parse_response(response_text):
    """Parses Gemini's response into structured results."""
    parsed_results = {}
    lines = response_text.split("\n")

    for i in range(len(lines)):
        match = re.match(r"Row (\d+): (Valid|Anomaly - (.*))", lines[i].strip())
        remediation_match = (
            re.match(r"Remediation: (.*)", lines[i + 1].strip()) if (i + 1 < len(lines)) else None
        )
        
        if match:
            row_index = int(match.group(1)) - 1  # Convert to 0-based index
            status = "Valid" if match.group(2) == "Valid" else "Anomaly"
            reason = match.group(3) if status == "Anomaly" else ""
            remediation = remediation_match.group(1) if remediation_match else ""

            if row_index not in parsed_results:
                parsed_results[row_index] = {"status": "Valid", "reasons": [], "remediation": ""}

            if status == "Anomaly":
                parsed_results[row_index]["status"] = "Anomaly"
                parsed_results[row_index]["reasons"].append(reason)
                parsed_results[row_index]["remediation"] += remediation + "; "

    print(f"🚨 Parsed Results:\n{parsed_results}")  # Debugging Step
    return parsed_results

# --- Main Function to Start Validation Process ---
def start_validation_process(input_csv):
    """
    Starts the validation process:
    - Loads CSV data
    - Validates each row against rules using Gemini
    - Returns the validated DataFrame
    """
    # Load Data
    df = pd.read_csv(input_csv)
    df["Validation Status"] = "Valid"
    df["Anomaly Reason"] = ""
    df["Remediation"] = ""

    # Load Validation Rules
    rules = load_rules()
    batch_data = []

    # Batch Processing
    for index, row in df.iterrows():
        for rule in rules:
            column = rule["Column Name"]
            rule_text = rule["Rules"]

            if column in df.columns:
                batch_data.append((index, column, rule_text, row[column]))

            # Process batch
            if len(batch_data) >= BATCH_SIZE:
                response_text = interpret_rules_batch(batch_data)
                parsed_results = parse_response(response_text)

                for idx, result in parsed_results.items():
                    if result["status"] == "Anomaly":
                        df.at[idx, "Validation Status"] = "Anomaly"
                        df.at[idx, "Anomaly Reason"] += "; ".join(result["reasons"]) + "; "
                        df.at[idx, "Remediation"] += result["remediation"]

                batch_data.clear()

    # Process remaining batch
    if batch_data:
        response_text = interpret_rules_batch(batch_data)
        parsed_results = parse_response(response_text)

        for idx, result in parsed_results.items():
            if result["status"] == "Anomaly":
                df.at[idx, "Validation Status"] = "Anomaly"
                df.at[idx, "Anomaly Reason"] += "; ".join(result["reasons"]) + "; "
                df.at[idx, "Remediation"] += result["remediation"]

    # Save Validated Data
    df.to_csv(VALIDATED_CSV, index=False)
    print(f"✅ Validation completed. Results saved to {VALIDATED_CSV}.")
    print(f"🔍 Check {LOG_FILE} for Gemini responses.")
    return VALIDATED_CSV