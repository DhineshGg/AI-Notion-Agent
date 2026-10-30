import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Notion AI Agent",
    page_icon="✦",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #888888;
        margin-bottom: 25px;
    }

    .action-title {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .chat-container {
        max-width: 900px;
        margin: auto;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "selected_action" not in st.session_state:

    st.session_state.selected_action = None


if "input_text" not in st.session_state:

    st.session_state.input_text = ""


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">✦ Notion Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Manage your Notion workspace using natural language.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ✦ Notion Agent")

    st.markdown("---")

    st.markdown("### Workspace")

    st.write("🏠 Home")
    st.write("📄 Pages")
    st.write("🔍 Search")

    st.markdown("---")

    st.markdown("### Connection")

    try:

        response = requests.get(
            f"{BACKEND_URL}/health",
            timeout=3
        )

        if response.ok:

            st.success("Backend connected")

        else:

            st.error("Backend unavailable")

    except Exception:

        st.error(
            "Backend not running"
        )


# ============================================================
# ACTION BUTTONS
# ============================================================

st.markdown(
    '<div class="action-title">What would you like to do?</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)


with col1:

    if st.button(
        "➕ Create Page",
        use_container_width=True
    ):

        st.session_state.selected_action = (
            "create"
        )

        st.session_state.input_text = (
            "Create a Notion page about "
        )

        st.rerun()


with col2:

    if st.button(
        "🔍 Search Pages",
        use_container_width=True
    ):

        st.session_state.selected_action = (
            "search"
        )

        st.session_state.input_text = (
            "Search my Notion pages for "
        )

        st.rerun()


with col3:

    if st.button(
        "📖 Read Page",
        use_container_width=True
    ):

        st.session_state.selected_action = (
            "read"
        )

        st.session_state.input_text = (
            "Read my Notion page about "
        )

        st.rerun()


# ============================================================
# SELECTED ACTION
# ============================================================

if st.session_state.selected_action:

    action_names = {

        "create": "➕ Create Page",

        "search": "🔍 Search Pages",

        "read": "📖 Read Page"
    }

    action_name = action_names[
        st.session_state.selected_action
    ]

    st.info(
        f"Selected action: **{action_name}**"
    )


# ============================================================
# CHAT HISTORY
# ============================================================

st.markdown("---")

chat_container = st.container()

with chat_container:

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask your Notion agent..."
)


# ============================================================
# HANDLE ACTION INPUT
# ============================================================

if prompt:

    # --------------------------------------------------------
    # If an action was selected, prepend the action context.
    # --------------------------------------------------------

    user_message = prompt

    action = st.session_state.selected_action

    if action == "create":

        user_message = (
            "The user wants to create a Notion page. "
            "Create it based on this request:\n\n"
            f"{prompt}"
        )

    elif action == "search":

        user_message = (
            "The user wants to search their Notion pages. "
            "Search based on this request:\n\n"
            f"{prompt}"
        )

    elif action == "read":

        user_message = (
            "The user wants to read a Notion page. "
            "Find the relevant page and return its content "
            "based on this request:\n\n"
            f"{prompt}"
        )

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # --------------------------------------------------------
    # Send to backend
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Thinking..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={
                        "message": user_message
                    },
                    timeout=120
                )

                if response.ok:

                    data = response.json()

                    assistant_message = data.get(
                        "response",
                        "No response received."
                    )

                else:

                    try:
                        error_data = response.json()

                        assistant_message = (
                            "Backend error: "
                            f"{error_data.get('detail', response.text)}"
                        )

                    except Exception:

                        assistant_message = (
                            "Backend error: "
                            f"{response.text}"
                        )

            except requests.exceptions.ConnectionError:

                assistant_message = (
                    "I could not connect to the FastAPI backend. "
                    "Make sure the backend is running on "
                    f"{BACKEND_URL}."
                )

            except Exception as e:

                assistant_message = (
                    f"Error: {str(e)}"
                )

        st.markdown(
            assistant_message
        )

    # --------------------------------------------------------
    # Save assistant message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_message
        }
    )

    # --------------------------------------------------------
    # Reset selected action
    # --------------------------------------------------------

    st.session_state.selected_action = None