import subprocess
import os
import time

RULES_FILE = "output/validation_rules.json"

# Step 1: Run pdf_parser.py
print("🔍 Running pdf_parser.py to generate validation rules...")
subprocess.run(["python", "pdf_parser.py"], check=True)

# Step 2: Wait for the rules file to be generated
while not os.path.exists(RULES_FILE):
    print("⏳ Waiting for validation rules to be generated...")
    time.sleep(2)

print("✅ Validation rules generated successfully!")

# Step 3: Run anomaly.py
print("🔍 Running anomaly.py to validate transactions...")
subprocess.run(["python", "anomaly.py"], check=True)

print("✅ Pipeline completed successfully!")
