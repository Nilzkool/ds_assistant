import os

import openai
import streamlit as st
from dotenv import load_dotenv

from madsa.data import load_csv
from madsa.execution import execute_python_statement, is_valid_python
from madsa.llm import extract_code_block, generate_chatgpt_response
from madsa.prompts import system_prompt
from madsa.ui import display_conversation

load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai.api_key = openai_api_key


def on_change():
    """
    Process user input and update the conversation history.

    If the user input is valid Python code, execute it directly and store the output.
    Otherwise, send it to ChatGPT, extract any generated code from the response, and
    execute that instead.
    """
    if not st.session_state.user_input:
        return

    plot = None
    if is_valid_python(st.session_state.user_input):
        output, plot, _ = execute_python_statement(
            st.session_state.user_input, st.session_state.locals_dict
        )
    else:
        try:
            response = generate_chatgpt_response(
                st.session_state.user_input,
                st.session_state.conversation_history,
                st.session_state.system_prompt,
            )
            code = extract_code_block(response)

            if code:
                try:
                    output, plot, _ = execute_python_statement(
                        code, st.session_state.locals_dict
                    )
                    if plot:
                        output = f"```python\n{code.strip()}\n```"
                    else:
                        output = f"{output}. \n```python\n{code.strip()}\n```"
                except Exception as e:
                    output = f"Error executing extracted code: {e}. Original ChatGPT response: {response}"
            else:
                output = response
        except Exception as e:
            output = f"Error: {e}"

    if plot:
        output = (output if output else "Here's the requested plot:", plot)
    st.session_state.conversation_history.append((st.session_state.user_input, output))
    st.session_state.user_input = ""
    st.rerun()


def initialize_app():
    """Initialize app session state and render the CSV uploader."""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}

    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = system_prompt()

    if "df" not in st.session_state.locals_dict:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="csv_uploader")
        if uploaded_file:
            df = load_csv(uploaded_file)
            st.session_state.locals_dict["df"] = df
            st.session_state.conversation_history.append(
                ("Upload CSV", "The columns of the uploaded dataframe are " + repr(list(df.columns)))
            )
            st.rerun()
    else:
        st.write("CSV file has been loaded into a pandas dataframe df")


def main():
    st.title("My awesome data science assistant (Madsa)")

    if not openai_api_key:
        st.error(
            "OPENAI_API_KEY is not set. Export it as an environment variable or add it to a "
            ".env file before running the app."
        )
        return

    initialize_app()
    display_conversation(st.session_state.conversation_history)
    user_input_placeholder = st.empty()
    user_input_placeholder.text_input(
        "Enter your Python statement or ask a question:",
        key="user_input",
        on_change=on_change,
    )


if __name__ == "__main__":
    main()
