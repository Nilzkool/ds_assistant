import ast
import base64
import sys
from io import BytesIO, StringIO


def is_valid_python(code: str) -> bool:
    """
    Check whether the given string parses as valid Python code.

    Args:
        code (str): A string containing Python code.

    Returns:
        bool: True if the code parses successfully, False otherwise.
    """
    try:
        ast.parse(code)
        return True
    except Exception:
        return False


def execute_python_statement(statement: str, locals_dict: dict):
    """
    Execute a Python statement and capture its output, plot, and error (if any).

    Args:
        statement (str): A Python statement to be executed.
        locals_dict (dict): The local namespace to execute the statement against. Mutated
            in place, matching the semantics of `exec`.

    Returns:
        tuple: (output, plot, error) where `output` is the captured stdout (or None),
            `plot` is a base64-encoded PNG of a matplotlib figure (or None), and `error`
            is always None on success or a string describing the failure.
    """
    original_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()

    plot = None

    try:
        exec(statement, globals(), locals_dict)
        if "plt" in locals_dict:
            plt = locals_dict["plt"]
            buf = BytesIO()
            plt.savefig(buf, format="png")
            plot = base64.b64encode(buf.getbuffer()).decode("ascii")
            plt.clf()
            plt.close()
            del locals_dict["plt"]
    except Exception as e:
        sys.stdout = original_stdout
        return f"Error executing extracted code: {e}. Original code: {statement}", None, None

    sys.stdout = original_stdout
    output = captured_output.getvalue().strip()
    if output == "":
        output = None

    return output, plot, None
