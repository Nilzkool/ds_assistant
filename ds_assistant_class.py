import time
import base64
import re
import pandas as pd
import streamlit as st
from python_code_execution import execute_python_statement, is_single_line_python_code
from chatgpt_api_utils import generate_chatgpt_response
from system_prompt import system_prompt

class DataScienceAssistant:
    def __init__(self):
        """
        Initializes the DataScienceAssistant with an empty conversation history,
        an empty local variables dictionary, and the system prompt.
        """
        self.conversation_history = []
        self.locals_dict = {}
        self.system_prompt = system_prompt()
    
    def handle_file_upload(self, file):
        """
        Load a CSV file into a pandas dataframe and store it in the assistant's locals_dict.
        
        Args:
            file (UploadedFile): A Streamlit UploadedFile object containing the CSV file.
        """
        if file:
            df = pd.read_csv(file)
            self.locals_dict['df'] = df
            self.conversation_history.append(("Upload CSV", "The columns of the uploaded dataframe are " + repr(list(df.columns))))
            return df
    
    def display_conversation(self):
        """
        Display the conversation history, including user inputs, assistant outputs, and generated plots.
        
        Args:
            assistant (DataScienceAssistant): The DataScienceAssistant object.
        """
        st.markdown("**Conversation History:**")
        for entry in self.conversation_history:
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

    def on_change(self, user_input):
        """
        Process user input and update the conversation history.
        If the user input is a single line of Python code, execute it and store the output.
        If it's a question or a statement, use the ChatGPT API to generate a response.
        
        Args:
            user_input (str): The user's input (Python code or a question).
        """
        if user_input:
            output = ""
            plot = None
            print('***User input')
            print(user_input)
            if is_single_line_python_code(user_input):
                output, plot,_ = execute_python_statement(user_input, self.locals_dict)
            else:
                try:
                    print('calling chatgpt api...')
                    output = generate_chatgpt_response(user_input, self.conversation_history, self.system_prompt)
                    print('Received response...')
                    code_snippet = re.search(r'<\s*(.*?)\s*>', output, re.DOTALL) or re.search(r'```python\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```\n?(.*?)\n?```', output, re.DOTALL) or re.search(r'```(?:python)?\n?(.*?)(?:\n?```)?', output, re.DOTALL)

                    if code_snippet:
                        print('Extracted code...')
                        try:
                            code = code_snippet.group(1)
                            print('Executing python code...')
                            output, plot, _ = execute_python_statement(code, self.locals_dict)
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
            self.conversation_history.append((user_input, output))
            unique_key = f"user_input_{time.time()}"
            st.session_state.user_input = ''
            st.experimental_rerun()