import fitz  # PyMuPDF for PDF extraction
import re
import google.generativeai as genai  # Gemini API
import os
import json
import time
import google.api_core.exceptions
from constant import *
from utils import clean_and_format_json

# 🔹 Configure Google Gemini API Key
genai.configure(api_key="")


def extract_text_from_pdf(pdf_path):
    """Extracts text from the given PDF file."""
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        text += page.get_text("text") + "\n"

    return text


def chunk_text_dynamically(text, max_chunk_size=3000):
    """
    Dynamically split text into manageable chunks based on field patterns.
    Ensures chunks stay within the token limit (~3000 characters per chunk).
    """
    chunks = re.split(r'\n\s*\d+\s+', text)  # Split by numbers indicating field sections
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]  # Remove empty sections

    # Further split into smaller chunks if any are too large
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            sub_chunks = [chunk[i:i + max_chunk_size] for i in range(0, len(chunk), max_chunk_size)]
            final_chunks.extend(sub_chunks)
        else:
            final_chunks.append(chunk)

    return final_chunks


def generate_rules_with_gemini(chunks):
    """
    Calls Gemini API to generate validation rules for extracted field descriptions.
    Implements retries for quota handling.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")  # Using the latest Gemini model
    rules = []
    
    for chunk in chunks:
        prompt = RULE_GENERATION_PROMPT_TEMPLATE.format(field_description=chunk)

        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt)
                generated_rules = response.text.strip() if response.text else "No rules generated."
                rules.append(generated_rules)  # Only storing the response as rules
                break  # Exit retry loop on success

            except google.api_core.exceptions.ResourceExhausted:
                print(f"Quota exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            except Exception as e:
                print(f"Error generating rules: {e}")
                rules.append("Error occurred")

    return clean_and_format_json(rules)


def update_rules(existing_rules, user_prompt, max_retries=5):
    """
    Updates validation rules dynamically based on user modifications.
    Implements retries for handling API errors.
    """

    prompt = RULE_MODIFICATION_PROMPT_TEMPLATE.format(
        existing_rules=json.dumps(existing_rules, indent=2), 
        user_prompt=user_prompt
    )
    model = genai.GenerativeModel("gemini-2.0-flash")

    for attempt in range(max_retries):
        try:
            response = model.generate_content([prompt])
            updated_rules = response.text.strip() if response.text else "No rules generated."
            return clean_and_format_json(updated_rules) # Return updated JSON rules

        except google.api_core.exceptions.ResourceExhausted:
            print(f"Quota exceeded. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Error updating rules: {e}")
            return "Error occurred"

    return "Failed to update rules after multiple retries."



# 🔹 Full Execution

def process_pdf_and_generate_rules(pdf_path):
    """
    Extracts text from a PDF, splits it into field-based chunks, 
    and generates validation rules using Gemini.

    Args:
        pdf_path (str or file-like object): Path to the PDF file or uploaded file object.

    Returns:
        list: Generated validation rules in JSON format.
    """
    # Step 1: Extract text
    extracted_text = extract_text_from_pdf(pdf_path)

    # Step 2: Dynamically split into field-based chunks
    field_chunks = chunk_text_dynamically(extracted_text)

    # Step 3: Pass chunks to Gemini for rule generation
    validation_rules = generate_rules_with_gemini(field_chunks)

    return validation_rules
