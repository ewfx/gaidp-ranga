import streamlit as st
from google.generativeai import GenerativeModel, configure

# --- Google Gemini API Key ---
configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = GenerativeModel("gemini-2.0-flash")

# --- Session Initialization ---
if "rules_file" not in st.session_state:
    st.session_state.rules_file = None
if "data_file" not in st.session_state:
    st.session_state.data_file = None
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Uploads (Always Enabled in Chat Mode) ---
if st.session_state.chat_mode:
    with st.sidebar:
        st.markdown("### 📂 Upload Files")
        st.session_state.rules_file = st.file_uploader(
            "📄 Data Profiling Rules", type=["txt", "pdf", "json", "csv"], key="rules_sidebar", label_visibility="visible"
        )
        st.session_state.data_file = st.file_uploader(
            "📊 Data", type=["csv", "xlsx", "json"], key="data_sidebar", label_visibility="visible"
        )

# --- Main Header ---
st.title("🔍 Data Profiler with AI Chat Assistant")

# --- Upload Section Before Chat Starts ---
if not st.session_state.chat_mode:
    rules_file = st.file_uploader("Upload Data Profiling Rules", type=["txt", "pdf", "json", "csv"], key="rules_upload")
    data_file = st.file_uploader("Upload Data", type=["csv", "xlsx", "json"], key="data_upload")

    if rules_file and data_file:
        st.session_state.rules_file = rules_file
        st.session_state.data_file = data_file
        st.success("✅ Both files uploaded successfully!")
        st.session_state.chat_mode = True
        st.rerun()

# --- Chat Interface ---
if st.session_state.chat_mode:
    st.markdown("## 💬 AI Assistant")

    # Show chat history
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["message"])

    # Chat input
    prompt = st.chat_input("Ask about the data profiling rules or uploaded data...")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "message": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Gemini is thinking..."):
                try:
                    response = model.generate_content(prompt)
                    answer = response.text
                except Exception as e:
                    answer = f"❌ Error from Gemini API: {e}"

                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "message": answer})
