import os
import streamlit as st
import openai
from ds_assistant_class import DataScienceAssistant

# loads api ket from env
openai.api_key = os.environ["OPENAI_API_KEY"]


def main():
    """
    The main function of the data science assistant Streamlit app.
    This function initializes the assistant, handles file uploads, displays the conversation,
    and takes user input to process Python code or answer questions using the ChatGPT API.
    """
     
    st.title("My awesome data science assistant (Madsa)")

    if 'assistant' not in st.session_state:
        st.session_state.assistant = DataScienceAssistant()

    assistant = st.session_state.assistant

    if 'df' not in st.session_state:
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"], key="csv_uploader")
        if uploaded_file:
            st.session_state.df = assistant.handle_file_upload(uploaded_file)
    else:
        st.write("CSV file has been loaded into a pandas dataframe df")

    assistant.display_conversation()

    if 'last_user_input' not in st.session_state:
        st.session_state.last_user_input = ""

    query_params = st.experimental_get_query_params()
    user_input = query_params.get("user_input", [""])[0]

    user_input = st.text_input("Enter your Python statement or ask a question:", value=user_input, key="user_input")
    submit_button = st.button("Submit")

    if submit_button and user_input and user_input != st.session_state.last_user_input:
        st.session_state.last_user_input = user_input
        assistant.on_change(user_input)
        st.experimental_set_query_params(user_input="")

if __name__ == "__main__":
    main()
