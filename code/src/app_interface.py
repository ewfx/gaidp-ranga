import base64
import json
import streamlit as st
from google.generativeai import GenerativeModel, configure
import os
from constant import API_KEY, MODEL
from anomaly import start_validation_process
from pdf_parser import process_pdf_and_generate_rules, update_rules

# --- Google Model Key from secrets ---
configure(api_key=API_KEY)
model = GenerativeModel(model_name=MODEL)

    

# --- Functions ---

def create_download_link(file_path, link_text="📥 Click here to download"):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        ext = os.path.splitext(file_path)[-1].replace(".", "")
        return f'<a href="data:file/{ext};base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'
    
def process_data_upload(data_file):
    st.toast(f"📊 Parsing new data file: {data_file.name}")
    output=start_validation_process(data_file)
    download_link = create_download_link(output, "📥 Download processed data")
    st.markdown(download_link, unsafe_allow_html=True)
    st.session_state.chat_history.append({"role": "assistant", "message": "Download Processed file from the side bar"})
    

def process_profile_rules_upload(rules_file):
    st.toast(f"📁 Processing profiling rules: {rules_file.name}")
    
    # Ensure temp directory exists
    temp_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "temp"))
    os.makedirs(temp_dir, exist_ok=True)

    # Get the file extension
    extension = os.path.splitext(rules_file.name)[1].lower()
    if extension not in [".pdf"]:
        st.error(f"Unsupported file type: {extension}")
        return None

    # Save the file
    save_path = os.path.join(temp_dir, f"profiles{extension}")
    with open(save_path, "wb") as f:
        f.write(rules_file.getbuffer())
    
    # Extract rules from the PDF
    validation_rules = process_pdf_and_generate_rules(save_path)
    
    try:
        parsed_json = json.loads(validation_rules)
        pretty_json = json.dumps(parsed_json, indent=2)
        chat_message_text = f"```json\n{pretty_json}\n```"
    except:
        chat_message_text = validation_rules

    st.session_state.chat_history.append({"role": "assistant", "message": chat_message_text})
    st.session_state.validation_rules = validation_rules

def file_changed(file1, file2):
    if not file1 or not file2:
        return True
    return file1.getvalue() != file2.getvalue()

# -- Session State Init --
if "rules_file" not in st.session_state:
    st.session_state.rules_file = None
if "data_file" not in st.session_state:
    st.session_state.data_file = None
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "rules_uploaded_once" not in st.session_state:
    st.session_state.rules_uploaded_once = False
if "data_uploaded_once" not in st.session_state:
    st.session_state.data_uploaded_once = False

# -- Sidebar Uploads (Only shown in chat mode) --
if st.session_state.chat_mode:
    with st.sidebar:
        st.markdown("### ⚙️ Upload Options")

        rules_file_sidebar = st.file_uploader(
            "📋 Upload Data Profiling Rules",
            type=["pdf"],
            key="rules_sidebar"
        )
        if rules_file_sidebar:
            if (
                not st.session_state.rules_file
                or file_changed(rules_file_sidebar, st.session_state.rules_file)
            ):
                st.session_state.rules_file = rules_file_sidebar
                saved_path = process_profile_rules_upload(rules_file_sidebar)
                st.session_state.rules_uploaded_once = True

        data_file = st.file_uploader(
            "📊 Upload Data File",
            type=["csv", "xlsx", "json"],
            key="data_sidebar"
        )
        if data_file:
            if (
                not st.session_state.data_uploaded_once or
                file_changed(data_file, st.session_state.rules_file)
            ):
                st.session_state.data_file = data_file
                process_data_upload(data_file)
                st.session_state.data_uploaded_once = True

# -- Initial Screen: Only Profiling Rules Upload --
if not st.session_state.chat_mode:
    st.title("📋 Upload Data Profiling Rules")
    rules_file = st.file_uploader(
        "Upload Data Profiling Rules",
        type=["txt", "pdf", "json", "csv"],
        key="rules_upload_main"
    )

    if rules_file:
        if (
            not st.session_state.rules_uploaded_once or
            file_changed(rules_file, st.session_state.rules_file)
        ):
            st.session_state.rules_file = rules_file
            saved_path = process_profile_rules_upload(rules_file)
            st.session_state.rules_uploaded_once = True
            st.session_state.chat_mode = True
            st.rerun()

# -- Chat Interface --
if st.session_state.chat_mode:
    st.markdown("## 💬 Team Ranga's Data Profiler")

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["message"])

    prompt = st.chat_input("Ask anything about profiling rules or data...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "message": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Model is thinking..."):
                try:
                    response = update_rules(st.session_state.validation_rules, prompt)
                    try:
                        parsed_json = json.loads(response)
                        pretty_json = json.dumps(parsed_json, indent=2)
                        chat_message_text = f"```json\n{pretty_json}\n```"
                    except:
                        chat_message_text = response
                    st.session_state.validation_rules = response
                except Exception as e:
                    answer = f"❌ Error from Model: {e}"

                st.markdown(chat_message_text)
                st.session_state.chat_history.append({"role": "assistant", "message": chat_message_text})
