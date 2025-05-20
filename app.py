import streamlit as st
from recipe import render_recipe_page
from chatbot import render_chatbot_page
import login

st.session_state.openai_key = ""

# --------------------------
# Login Section
# --------------------------
login.login()

# --------------------------
# Page Configuration & CSS
# --------------------------
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    body {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .right-col {
        margin-left: 100px;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Initialize Session State
# --------------------------
if 'recipe' not in st.session_state:
    st.session_state.recipe = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": "You are a helpful assistant that provides insights."
        }
    ]

if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = True

# --------------------------
# Page Title & Layout
# --------------------------
st.title("Spare Parts Inventory Assistant")

if st.session_state.get("show_add_form", True):
    with st.expander("What is this?", expanded=False):
        st.write(
            "This is a quick PoC built for a spare parts inventory assistant using a state-of-the-art reasoning model (e.g., GPT-4) combined with file-based data retrieval."
        )
        st.write("**What is this data?**")
        st.write("- The uploaded Excel file contains real or simulated data about inventory levels, stock parameters, open purchase orders, and material reservations.")
        st.write("**What tools are being used?**")
        st.write("- This assistant leverages an OpenAI language model with file search and analysis capabilities for Excel documents.")
        st.write("**What is it capable of?**")
        st.write("- It can answer questions about current stock status, detect shortages or overstock, and suggest actions like creating purchase orders, initiating internal transfers, or suspending existing orders based on predefined logic.")

render_chatbot_page()
