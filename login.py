import streamlit as st

OPENAI_TOKEN = ""

# --------------------------
# Login Section
# --------------------------

def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Initialize a place for the key in session_state
    if "OPENAI_TOKEN" not in st.session_state:
        st.session_state.OPENAI_TOKEN = ""

    if not st.session_state.authenticated:
        st.title("Login")
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        openai = st.text_input("OpenAI API Key", type="password", key="openai")

        if st.button("Login"):
            if username == "chef" and password == "bakerychef" and openai:
                st.session_state.authenticated = True
                # Optionally, also update the config variable in memory.
                st.session_state.OPENAI_TOKEN = openai
                st.rerun()  # Refresh the page to load the main app.
            else:
                st.error("Invalid username, password, or missing API key")
        st.stop()  # Stop the rest of the app if not logged in.
