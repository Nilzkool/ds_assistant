import pandas as pd
import streamlit as st
import base64
import re
import ast
#dummy change
def handle_file_upload(file):
    """
    Load a CSV file into a pandas dataframe and store it in the assistant's locals_dict.
    
    Args:
        file (UploadedFile): A Streamlit UploadedFile object containing the CSV file.
    """
    if file:
        df = pd.read_csv(file)
        st.session_state.locals_dict['df'] = df
        st.session_state.conversation_history.append(("Upload CSV", "The columns of the uploaded dataframe are " + repr(list(df.columns))))
        st.experimental_rerun()

def display_conversation():
    """
    Display the conversation history, including user inputs, assistant outputs, and generated plots.
    
    Args:
        assistant (DataScienceAssistant): The DataScienceAssistant object.
    """
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

def is_single_line_python_code(code):
    """
    Check if the given code is a valid single-line Python code.
    
    Args:
        code (str): A string containing Python code.
        
    Returns:
        bool: True if the code is a valid single-line Python code, False otherwise.
    """
    try:
        ast.parse(code)
        return True
    except:
        return False

def dummy():
    pass
