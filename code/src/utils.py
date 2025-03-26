import json
import re


def clean_and_format_json(gemini_output):
    """
    Cleans and formats JSON output from Gemini by:
    1. Removing markdown artifacts (```json ... ```)
    2. Handling cases where JSON is inside an array or provided directly
    3. Ensuring valid JSON formatting
    4. Enforcing "Rules" as a list (even if it contains a single value)

    Args:
        gemini_output (list or str): JSON content, either inside an array or as a direct JSON string.

    Returns:
        str: Properly formatted JSON string.
    """
    if not gemini_output:
        return "Error: Empty input."

    # If input is a list (first case: generate rule outputs JSON inside an array)
    if isinstance(gemini_output, list):
        json_str = gemini_output[0] if gemini_output else ""
    else:
        json_str = gemini_output  # If it's already a string

    # Step 1: Remove Markdown artifacts and whitespace
    json_str = re.sub(r'```json\n|\n```', '', json_str).strip()

    try:
        # Step 2: Convert JSON string to a Python object (list or dict)
        json_obj = json.loads(json_str)

        # Ensure it's always a list
        if isinstance(json_obj, dict):
            json_obj = [json_obj]

        # Step 3: Ensure "Rules" field is always a list
        for entry in json_obj:
            if "Rules" in entry and isinstance(entry["Rules"], str):
                entry["Rules"] = [entry["Rules"]]  # Convert single string rule to a list

        # Step 4: Return properly formatted JSON string
        return json.dumps(json_obj, indent=4)

    except json.JSONDecodeError as e:
        return f"Error decoding JSON: {e}"
