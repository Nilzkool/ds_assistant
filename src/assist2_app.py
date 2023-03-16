import streamlit as st
import time
from io import StringIO
import sys
import pandas as pd

def execute_python_statement(statement):
    try:
        original_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        if "locals_dict" not in st.session_state:
            st.session_state.locals_dict = {}

        output = eval(statement, globals(), st.session_state.locals_dict)
        if output is None:
            exec(statement, globals(), st.session_state.locals_dict)
            sys.stdout = original_stdout
            output = captured_output.getvalue().strip()

        return output

    except Exception as e:
        return str(e)

def on_change():
    if st.session_state.user_input:
        output = execute_python_statement(st.session_state.user_input)
        st.session_state.conversation_history.append((st.session_state.user_input, output))
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()

def handle_file_upload(file):
    if file:
        df = pd.read_csv(file)
        st.session_state.locals_dict['df'] = df
        st.session_state.conversation_history.append(("Upload CSV", "The DataFrame has been uploaded"))
        st.experimental_rerun()

def main():
    st.title("Python Statement Executor")

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}

    if 'df' not in st.session_state.locals_dict:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="csv_uploader")
        if uploaded_file:
            handle_file_upload(uploaded_file)
    else:
        st.write("CSV file has been uploaded. File uploader is now disabled.")

    st.markdown("**Conversation History:**")
    for entry in st.session_state.conversation_history:
        user_prompt, response = entry
        st.markdown(f"- **Input**: {user_prompt}")
        if isinstance(response, pd.DataFrame):
            st.dataframe(response)
        else:
            st.markdown(f"- **Output**: {response}")

    user_input_placeholder = st.empty()

    user_input = user_input_placeholder.text_input("Enter your Python statement:", key="user_input", on_change=on_change, args=[])

if __name__ == "__main__":
    main()
