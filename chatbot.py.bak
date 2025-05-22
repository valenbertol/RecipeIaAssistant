import streamlit as st
import streamlit.components.v1 as components
import json, time, pathlib
from openai import OpenAI, NotFoundError


# --------------------------------------------------
# ⚙️  CONFIG
# --------------------------------------------------
FILE_ID = "file-VFsR3BNvQS7SPykyySRFiq"  # Excel ya subido en tu cuenta
MODEL_NAME = "gpt-4o"               # Cambiá a gpt-4o si querés más potencia
ASSISTANT_CACHE = pathlib.Path(".assistant_id")

# ----------------------------------------------------------------------------
# 🔧 CONFIGURACIÓN
# ----------------------------------------------------------------------------
MODEL_NAME = "gpt-4o-mini"  # cambia a gpt-4o si querés más potencia
ASSISTANT_CACHE = pathlib.Path(".assistant_id")

# ----------------------------------------------------------------------------
# 🛠 UTILIDADES
# ----------------------------------------------------------------------------

def log_js(msg: str):
    components.html(f"<script>console.log({json.dumps(msg)});</script>", height=0, width=0)


def get_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, timeout=60)


# ----------------------------------------------------------------------------
# 🧠 ASSISTANT & THREAD HELPERS
# ----------------------------------------------------------------------------

INSTRUCTIONS = (
    "You are **Spare Parts Bot**, an expert spare‑parts inventory assistant. "
    "All inventory data is contained in the 'Mod01' sheet of the uploaded Excel file; "
    "the 'Library' sheet only describes each parameter. "
    "Use Python with Code Interpreter for calculations, statistics, and to extract precise data when needed. "
    "Respond in the same language the user writes (English or Spanish). "
    "Provide clear, informative answers and **never fabricate information** that you cannot derive from the file."
) 


def create_assistant(client: OpenAI, file_id: str) -> str:
    assistant = client.beta.assistants.create(
        name="Spare Parts Bot",
        model=MODEL_NAME,
        instructions=INSTRUCTIONS,
        tools=[{"type": "code_interpreter"}],
        tool_resources={"code_interpreter": {"file_ids": [file_id]}},
    )
    ASSISTANT_CACHE.write_text(assistant.id)
    return assistant.id


def get_linked_file_ids(assistant) -> list[str]:
    """Devuelve la lista de file_ids asociados al Code Interpreter del assistant"""
    try:
        return list(assistant.tool_resources.code_interpreter.file_ids)  # SDK ≥1.15
    except AttributeError:
        # Fallback para versiones previas donde es dict-like
        try:
            return assistant.tool_resources["code_interpreter"]["file_ids"]
        except Exception:
            return []


def get_assistant_id(client: OpenAI, file_id: str) -> str:
    cached_id = ASSISTANT_CACHE.read_text().strip() if ASSISTANT_CACHE.exists() else None
    if cached_id:
        try:
            assistant = client.beta.assistants.retrieve(cached_id)
            if file_id in get_linked_file_ids(assistant):
                return cached_id
        except NotFoundError:
            pass  # ID inválido: recreamos
    return create_assistant(client, file_id)


def get_thread_id(client: OpenAI) -> str:
    if "thread_id" in st.session_state:
        return st.session_state.thread_id
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    return thread.id


# ----------------------------------------------------------------------------
# 💬 UI PRINCIPAL
# ----------------------------------------------------------------------------

def render_chatbot_page():
    st.title("📦 Spare Parts Bot (PoC)")

    api_key = st.sidebar.text_input("🔑 OpenAI API Key", type="password", value=st.session_state.get("OPENAI_TOKEN", ""))
    if not api_key:
        st.info("Introduce tu API key para comenzar.")
        st.stop()
    st.session_state.OPENAI_TOKEN = api_key
    client = get_client(api_key)

    # --- Archivo ---
    st.markdown("### 1️⃣ Subí tu Excel / CSV de inventario")
    up_file = st.file_uploader("Archivo", type=["xlsx", "xls", "csv"])
    if up_file is None:
        st.stop()

    # Subir a OpenAI si es nuevo
    if st.session_state.get("file_name") != up_file.name:
        with st.spinner("Subiendo archivo a OpenAI…"):
            file_resp = client.files.create(file=up_file, purpose="assistants")
        st.session_state.update({"file_id": file_resp.id, "file_name": up_file.name})
        # invalida caches
        ASSISTANT_CACHE.unlink(missing_ok=True)
        st.session_state.pop("assistant_id", None)
        st.session_state.pop("thread_id", None)

    file_id = st.session_state.file_id
    assistant_id = get_assistant_id(client, file_id)
    thread_id = get_thread_id(client)

    # --- History ---
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for m in st.session_state.chat_history:
        st.chat_message(m["role"]).markdown(m["content"])

    prompt = st.chat_input("Escribí tu consulta…")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)

        client.beta.threads.messages.create(thread_id=thread_id, role="user", content=prompt)
        run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

        with st.spinner("Pensando…"):
            while run.status not in {"completed", "failed"}:
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        if run.status == "failed":
            st.error("La ejecución falló. Intentá de nuevo.")
            return

        reply_msg = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1).data[0]
        reply = reply_msg.content[0].text.value
        st.session_state.chat_history.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").markdown(reply)

