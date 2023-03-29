import sys
import ast
import streamlit as st
from io import BytesIO, StringIO
import base64
import re


def execute_python_statement(statement, locals_dict):
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
    plot=None

    try:
        exec(statement, globals(), locals_dict)
        if "plt" in locals_dict:
            plt = locals_dict["plt"]
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