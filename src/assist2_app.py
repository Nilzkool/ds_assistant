import streamlit as st
import io
import time
from io import StringIO
import sys
import pandas as pd
import openai
import os
import re
import ast
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib.figure

# Fetch openai api key
openai.api_key = os.environ["OPENAI_API_KEY"]

def generate_chatgpt_response(prompt, conversation_history, system_prompt):
    model_engine = "gpt-3.5-turbo"

    # Construct the list of messages for the API
    messages = [{"role": "system", "content": system_prompt}]
    for entry in conversation_history:
        user_prompt, response = entry
        messages.append({"role": "user", "content": user_prompt})
        if isinstance(response, str):
            messages.append({"role": "assistant", "content": response})

    # Add the current prompt
    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages,
        max_tokens=1000,
        n=1,
        temperature=0.20)

    text_output = response["choices"][0]["message"]["content"]
    
    return text_output

# working code without plots
def execute_python_statement(statement):
    original_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}

    lines = statement.split('\n')

    for line in lines:
        try:
            exec(line, globals(), st.session_state.locals_dict)
        except Exception as e:
            sys.stdout = original_stdout
            return f"Error executing extracted code: {e}. Original code: {statement}"

    sys.stdout = original_stdout
    output = captured_output.getvalue().strip()
    if output == "":
        output = None

    return output

def on_change():
    if st.session_state.user_input:
        output = ""
        try:
            # Try to parse the user input as Python code
            ast.parse(st.session_state.user_input)
            is_python_code = True
            output = execute_python_statement(st.session_state.user_input)
        except:
            is_python_code = False

        if not is_python_code:
            try:
                output = generate_chatgpt_response(st.session_state.user_input, st.session_state.conversation_history, st.session_state.system_prompt)
                code_snippet = re.search(r'<\s*(.*?)\s*>', output, re.DOTALL) or re.search(r'```python\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```(?:python)?\n?(.*?)(?:\n?```)?', output, re.DOTALL)
                
                if code_snippet:
                    try:
                        code = code_snippet.group(1)
                        output = execute_python_statement(code)
                        output = f"{output}. \n```python\n{code.strip()}\n```"
                    except Exception as e:
                        output = f"Error executing extracted code: {e}. Original ChatGPT response: {output}"
            except Exception as e:
                output = f"Error: {e}"

        st.session_state.conversation_history.append((st.session_state.user_input, output))
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()

def handle_file_upload(file):
    if file:
        df = pd.read_csv(file)
        st.session_state.locals_dict['df'] = df
        st.session_state.conversation_history.append(("Upload CSV", "The columns of the uploaded dataframe are " + repr(list(df.columns))))
        st.experimental_rerun()

def main():
    st.title("My awesome data science assistant")

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = (
            "You are a data science assistant. Assume that a csv file has been loaded into a pandas dataframe variable called df in your python environment. "
            "All the user prompts will be related to the dataframe df. "
            "Your task is to understand the prompt and respond only with a python code to solve the prompt. Be very concise in your response. "
            "The python code must include a print statement to output the solution. "
            "Your Python code must be wrapped inside < >. Nothing else will do. "
            "If you cannot respond only with a python code in the correct format, say I am sorry for now. "
        )

    if 'df' not in st.session_state.locals_dict:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="csv_uploader")
        if uploaded_file:
            handle_file_upload(uploaded_file)
    else:
        st.write("CSV file has been loaded into a pandas dataframe df")

    st.markdown("**Conversation History:**")
    for entry in st.session_state.conversation_history:
        user_prompt, response = entry
        st.markdown(f"**In**: {user_prompt}")
        st.markdown(f"**Out**: {response}")

    user_input_placeholder = st.empty()
    user_input = user_input_placeholder.text_input("Enter your Python statement or ask a question:", key="user_input", on_change=on_change, args=[])


if __name__ == "__main__":
    main()
