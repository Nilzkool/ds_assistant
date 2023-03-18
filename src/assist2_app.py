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

    plot = None

    try:
        exec(statement, globals(), st.session_state.locals_dict)
        if "plt" in st.session_state.locals_dict:
            plt = st.session_state.locals_dict["plt"]
            buf = BytesIO()
            plt.savefig(buf, format="png")
            plot = base64.b64encode(buf.getbuffer()).decode("ascii")
            plt.clf()
            del st.session_state.locals_dict["plt"]  # Add this line to remove the plt object from the session state
    except Exception as e:
        sys.stdout = original_stdout
        return f"Error executing extracted code: {e}. Original code: {statement}", None, None

    sys.stdout = original_stdout
    output = captured_output.getvalue().strip()
    if output == "":
        output = None

    return output, plot, None

def is_single_line_python_code(code):
    try:
        ast.parse(code)
        return True
    except:
        return False


def on_change():
    if st.session_state.user_input:
        output = ""

        if is_single_line_python_code(st.session_state.user_input):
            output, plot,_ = execute_python_statement(st.session_state.user_input)
        else:
            try:
                output = generate_chatgpt_response(st.session_state.user_input, st.session_state.conversation_history, st.session_state.system_prompt)
                code_snippet = re.search(r'<\s*(.*?)\s*>', output, re.DOTALL) or re.search(r'```python\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```(?:python)?\n?(.*?)(?:\n?```)?', output, re.DOTALL)

                if code_snippet:
                    try:
                        code = code_snippet.group(1)
                        output, plot, _ = execute_python_statement(code)
                        if plot:
                            output = f"```python\n{code.strip()}\n```"
                        else:
                            output = f"{output}. \n```python\n{code.strip()}\n```"
                    except Exception as e:
                        output = f"Error executing extracted code: {e}. Original ChatGPT response: {output}"
                else:
                    plot = None
            except Exception as e:
                output = f"Error: {e}"

        if plot:
            output = (output if output else "Here's the requested plot:", plot)
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

def display_conversation():
    st.markdown("**Conversation History:**")
    for entry in st.session_state.conversation_history:
        user_prompt, response = entry
        if isinstance(response, tuple):
            response_text, plot = response
        else:
            response_text, plot = response, None
        st.markdown(f"**In**: {user_prompt}")
        if plot:
            code_block = re.search(r'```python\n?(.*?)\n?```', response_text, re.DOTALL)
            if code_block:
                code = code_block.group(1)
                response_text = response_text.replace(f"```python\n{code}\n```", "")
        st.markdown(f"**Out**: {response_text}")
        if plot:
            st.image(base64.b64decode(plot), caption="Generated plot", use_column_width=True)
            st.code(code, language='python')




def system_prompt_text():
    sys_prompt = (
                    "You are a data science assistant. Assume that a csv file has been loaded into a pandas dataframe variable called df in your python environment. The main libraries are sklearn, numpy, pandas and matplotlib."
                    "All the user prompts will be related to the dataframe df. "
                    "Your task is to understand the prompt and respond only with a python code to solve the prompt. Be very concise in your response. "
                    "The python code must include a print statement to output the solution. "
                    "Your Python code must be wrapped inside < >. Nothing else will do. "
                    "If the prompt consists of executable python code, respond by returning the same code wrapped inside < >, and do not modify the prompt."
                    "If you cannot respond only with a python code in the correct format, say I am sorry for now. "
                )
    return sys_prompt

def main():
    st.title("My awesome data science assistant")

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt =system_prompt_text()

    if 'df' not in st.session_state.locals_dict:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="csv_uploader")
        if uploaded_file:
            handle_file_upload(uploaded_file)
    else:
        st.write("CSV file has been loaded into a pandas dataframe df")

    display_conversation()

    user_input_placeholder = st.empty()
    user_input = user_input_placeholder.text_input("Enter your Python statement or ask a question:", key="user_input", on_change=on_change, args=[])


if __name__ == "__main__":
    main()
