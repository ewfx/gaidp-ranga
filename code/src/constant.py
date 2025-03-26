RULE_GENERATION_PROMPT_TEMPLATE = """
    You are given a field definition containing a column name and its description. Your task is to generate validation rules based on the description and return the output strictly in JSON format.

    ### **Instructions:**
    - Extract constraints, allowable values, formatting requirements, or any validation rules from the given field description.
    - Structure the JSON output with the following attributes:
    - `"Column Name"`: The name of the field.
    - `"Description"`: A detailed explanation of the field's purpose or meaning.
    - `"Rules"`: A **list** of validation rules (even if there's only one rule).
    - **Ensure the JSON output is clean, and contains no extra characters like `\n`, markdown (` ```json `), or explanations.**

    ### **Input:**
    {field_description}

    ### **Output Format (Strict JSON):**
    ```json
    [
        {{
            "Column Name": "<Field Name>",
            "Description": "<Brief explanation of the field>",
            "Rules": [
                "<Validation Rule 1>",
                "<Validation Rule 2>",
                "<Additional validation rules if applicable>"
            ]
        }}
    ]
    """

RULE_MODIFICATION_PROMPT_TEMPLATE = """
    You are an AI that updates **financial transaction validation rules** based on user instructions.
    Given a set of existing rules and a user request, modify the rules accordingly.
    Ensure all modifications maintain strict **data integrity, compliance, and validation** principles.

    ### **Instructions:**
    - Review the existing rules.
    - Modify or append rules based on the user request.
    - Ensure **Rules** remain a **list** (even if there's only one rule).
    - **Ensure the JSON output is clean, and contains no extra characters like `\n`, markdown (` ```json `), or explanations.**

    ### **Existing Rules:**
    {existing_rules}

    ### **User Input:**
    {user_prompt}

    ### **Output Format (Strict JSON):**
    ```json
    [
        {{
            "Column Name": "<Field Name>",
            "Description": "<Brief explanation of the field>",
            "Rules": [
                "<Updated Validation Rule 1>",
                "<Updated Validation Rule 2>",
                "<Additional validation rules if applicable>"
            ]
        }}
    ]
    """

max_retries = 5
retry_delay = 60 