import base64
import re

import streamlit as st


def display_conversation(conversation_history: list) -> None:
    """
    Display the conversation history, including user inputs, assistant outputs, and
    generated plots.

    Args:
        conversation_history (list): A list of (user_prompt, response) tuples, where
            `response` is either a string or a (text, base64_plot) tuple.
    """
    st.markdown("**Conversation History:**")
    for user_prompt, response in conversation_history:
        if isinstance(response, tuple):
            response_text, plot = response
        else:
            response_text, plot = response, None

        st.markdown(f"**In**: {user_prompt}")

        code = None
        if plot:
            code_block = re.search(r"```python\n?(.*?)\n?```", response_text, re.DOTALL)
            if code_block:
                code = code_block.group(1)
                response_text = response_text.replace(f"```python\n{code}\n```", "")

        st.markdown(f"**Out**: {response_text}")
        if plot:
            st.image(base64.b64decode(plot), caption="Generated plot", use_container_width=True)
            if code:
                st.code(code, language="python")
