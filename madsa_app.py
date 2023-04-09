import io
import time
from io import StringIO, BytesIO
import sys
import base64
import os
import re

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure
import streamlit as st
import openai


from chatgpt_api_utils import generate_chatgpt_response
from system_prompt import system_prompt
from app_utils import is_single_line_python_code, handle_file_upload, display_conversation


# Load OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

def execute_python_statement(statement):
    """
    Execute a Python statement and capture its output, plot, and error (if any).
    
    Args:
        statement (str): A Python statement to be executed.
        
    Returns:
        output (str): The captured output from the executed statement.
        plot (str): Base64 encoded plot image, if a plot was generated.
        error (str): The error message, if an error occurred during execution.
    """
    original_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}

    plot = None

    try:
        exec(statement, globals(), st.session_state.locals_dict)
        if "plt" in st.session_state.locals_dict:
            plt = st.session_state.locals_dict["plt"]
            buf = BytesIO()
            plt.savefig(buf, format="png")
            plot = base64.b64encode(buf.getbuffer()).decode("ascii")
            plt.clf()
            plt.close()
            del st.session_state.locals_dict["plt"]  # Add this line to remove the plt object from the session state
    except Exception as e:
        sys.stdout = original_stdout
        return f"Error executing extracted code: {e}. Original code: {statement}", None, None

    sys.stdout = original_stdout
    output = captured_output.getvalue().strip()
    if output == "":
        output = None

    return output, plot, None

def on_change():
    """
    Process user input and update the conversation history.
    If the user input is a single line of Python code, execute it and store the output.
    If it's a question or a statement, use the ChatGPT API to generate a response.
    
    Args:
        user_input (str): The user's input (Python code or a question).
    """
    if st.session_state.user_input:
        output = ""
        plot = None
        print('***User input')
        print(st.session_state.user_input)
        if is_single_line_python_code(st.session_state.user_input):
            output, plot,_ = execute_python_statement(st.session_state.user_input)
        else:
            try:
                print('calling chatgpt api...')
                output = generate_chatgpt_response(st.session_state.user_input, st.session_state.conversation_history, st.session_state.system_prompt)
                print('Received response...')
                code_snippet = re.search(r'<\s*(.*?)\s*>', output, re.DOTALL) or re.search(r'```python\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```(?:python)?\n?(.*?)(?:\n?```)?', output, re.DOTALL)

                if code_snippet:
                    print('Extracted code...')
                    try:
                        code = code_snippet.group(1)
                        print('Executing python code...')
                        output, plot, _ = execute_python_statement(code)
                        if plot:
                            print('Plot found...')
                            output = f"```python\n{code.strip()}\n```"
                        else:
                            output = f"{output}. \n```python\n{code.strip()}\n```"
                    except Exception as e:
                        output = f"Error executing extracted code: {e}. Original ChatGPT response: {output}"
                else:
                    print('No extractable code...')
                    plot = None
            except Exception as e:
                output = f"Error: {e}"

        if plot:
            output = (output if output else "Here's the requested plot:", plot)
        st.session_state.conversation_history.append((st.session_state.user_input, output))
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()

def initialize_app():
    """
    Intializes app session variables
    """
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt =system_prompt()

    if 'df' not in st.session_state.locals_dict:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="csv_uploader")
        if uploaded_file:
            handle_file_upload(uploaded_file)
    else:
        st.write("CSV file has been loaded into a pandas dataframe df")

def main():
    st.title("My awesome data science assistant (Madsa)")
    initialize_app()
    display_conversation()
    user_input_placeholder = st.empty()
    user_input = user_input_placeholder.text_input("Enter your Python statement or ask a question:", key="user_input", on_change=on_change, args=[])


if __name__ == "__main__":
    main()
 
