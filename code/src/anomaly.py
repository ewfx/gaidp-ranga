import pandas as pd
import json
import time
import google.generativeai as genai
import re

# Configure Gemini API Key
GEMINI_API_KEY = "AIzaSyAVd0JIXEGcOiFx_DmCoHMfHfaD2n0LoGU"
genai.configure(api_key=GEMINI_API_KEY)

# Load CSV file
df = pd.read_csv("output/data.csv")

# Load JSON rules
with open("output/validation_rules.json", "r") as file:
    rules = json.load(file)

# Initialize new columns
df["Validation Status"] = "Valid"
df["Anomaly Reason"] = ""
df["Remediation"] = ""

# Log file for Gemini responses
LOG_FILE = "gemini_log.txt"

# Function to log Gemini responses
def log_response(prompt, response):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write("\n=== Gemini Request ===\n")
        log.write(prompt + "\n")
        log.write("\n=== Gemini Response ===\n")
        log.write(response + "\n\n")

# Function to query Gemini API with validation and remediation
def interpret_rules_batch(batch_data):
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

# Function to parse Gemini's response
def parse_response(response_text):
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

# Batch processing
batch_size = 5
batch_data = []

for index, row in df.iterrows():
    for rule in rules:
        column = rule["Column Name"]
        rule_text = rule["Rules"]

        if column in df.columns:
            batch_data.append((index, column, rule_text, row[column]))

        # Process batch
        if len(batch_data) >= batch_size:
            response_text = interpret_rules_batch(batch_data)
            parsed_results = parse_response(response_text)

            for idx, result in parsed_results.items():
                if result["status"] == "Anomaly":
                    df.at[idx, "Validation Status"] = "Anomaly"
                    df.at[idx, "Anomaly Reason"] += "; ".join(result["reasons"]) + "; "
                    df.at[idx, "Remediation"] += result["remediation"]  # Ensure remediation appends

            batch_data.clear()

# Process remaining data (ensures last batch is not skipped)
if batch_data:
    response_text = interpret_rules_batch(batch_data)
    parsed_results = parse_response(response_text)

    for idx, result in parsed_results.items():
        if result["status"] == "Anomaly":
            df.at[idx, "Validation Status"] = "Anomaly"
            df.at[idx, "Anomaly Reason"] += "; ".join(result["reasons"]) + "; "
            df.at[idx, "Remediation"] += result["remediation"]  # Ensure remediation appends

# Save results
df.to_csv("output/validated_data.csv", index=False)
print("✅ Validation completed. Results saved to validated_data.csv.")
print(f"🔍 Check {LOG_FILE} for Gemini responses.")
