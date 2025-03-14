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
            "content": "You are a helpful assistant that provides advice on the current recipe ingredients."
        }
    ]

if 'show_add_form' not in st.session_state:
    st.session_state.show_add_form = True

# --------------------------
# Page Title & Layout
# --------------------------
st.title("Recipe Creator with Chatbot")

if st.session_state.get("show_add_form", True):
    with st.expander("What is this?", expanded=False):
        st.write(
            "This is a small PoC built in one day for a recipe assistant using a state-of-the-art reasoning model (o3-mini) with information retrieval tools."
        )
        st.write("**What is this data?**")
        st.write("- All the data in this PoC is simulated from a bakery and is invented for the purpose of this demo.")
        st.write("**What tools are being used here?**")
        st.write("- We are using the latest o3-mini from OpenAI with a file search tool (OpenAI responses API). This is great for this use case because this small reasoning model can quantify ingredients in a considerable amount of time.")
        st.write("**What is capable of ?**")
        st.write("- This assistant can suggest (add, edit or delete) ingredients from the database depending on the chef's needs. It has creativity and is precise with quantities. You can ask it to suggest something vegan, 'fun', or 'trendy' and it will know what you mean :)")

left_col, right_col = st.columns([2, 2])

with left_col:
    render_recipe_page()
    
with right_col:
    render_chatbot_page()
