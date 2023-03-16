import streamlit as st
import time
from io import StringIO
import sys

def execute_python_statement(statement):
    try:
        # Redirect stdout to a StringIO object
        original_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        if "locals_dict" not in st.session_state:
            st.session_state.locals_dict = {}

        exec(statement, globals(), st.session_state.locals_dict)

        # Restore original stdout
        sys.stdout = original_stdout

        output = captured_output.getvalue()
        return output.strip()

    except Exception as e:
        return str(e)

def on_change():
    if st.session_state.user_input:
        # Execute the Python statement and get the output
        output = execute_python_statement(st.session_state.user_input)

        # Add the user prompt and response to the conversation history
        st.session_state.conversation_history.append((st.session_state.user_input, output))

        # Clear the input field by updating the text input widget's key
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()

# Streamlit app
def main():
    st.title("Python Statement Executor")

    # Initialize conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # Display conversation history
    st.markdown("**Conversation History:**")
    for entry in st.session_state.conversation_history:
        user_prompt, response = entry
        st.markdown(f"- **Input**: {user_prompt}")
        st.markdown(f"- **Output**: {response}")

    # Input prompt placeholder
    user_input_placeholder = st.empty()

    # Add the text input widget to the placeholder, with on_change=True
    user_input = user_input_placeholder.text_input("Enter your Python statement:", key="user_input", on_change=on_change, args=[])

if __name__ == "__main__":
    main()
