import streamlit as st
import time
from io import StringIO
import sys
import pandas as pd
import openai
import os

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
        max_tokens=50,
        n=1,
        temperature=0.7)

    text_output = response["choices"][0]["message"]["content"]
    return text_output

def execute_python_statement(statement):
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



def on_change():
    if st.session_state.user_input:
        try:
            output = execute_python_statement(st.session_state.user_input)
        except:
            output = generate_chatgpt_response(st.session_state.user_input, st.session_state.conversation_history, st.session_state.system_prompt)

        st.session_state.conversation_history.append((st.session_state.user_input, output))
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()

def handle_file_upload(file):
    if file:
        df = pd.read_csv(file)
        st.session_state.locals_dict['df'] = df
        st.session_state.conversation_history.append(("Upload CSV", "A csv has been uploaded into a pandas dataframe object called df"))
        st.experimental_rerun()

def main():
    st.title("My awesome data science assistant")

    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    if "locals_dict" not in st.session_state:
        st.session_state.locals_dict = {}
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a data science assistant. Answer concisely and factually"

    if 'df' not in st.session_state.locals_dict:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="csv_uploader")
        if uploaded_file:
            handle_file_upload(uploaded_file)
    else:
        st.write("CSV file has been uploaded. File uploader is now disabled.")

    st.markdown("**Conversation History:**")
    for entry in st.session_state.conversation_history:
        user_prompt, response = entry
        st.markdown(f"**In**: {user_prompt}")
        if isinstance(response, pd.DataFrame):
            st.dataframe(response)
        else:
            st.markdown(f"**Out**: {response}")

    user_input_placeholder = st.empty()

    user_input = user_input_placeholder.text_input("Enter your Python statement or ask a question:", key="user_input", on_change=on_change, args=[])

if __name__ == "__main__":
    main()
