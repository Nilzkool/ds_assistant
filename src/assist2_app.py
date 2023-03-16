import streamlit as st
import random
import string
import time

# Function to generate a random string
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def on_change():
    if st.session_state.user_input:
        # Random response generation
        response_length = random.randint(5, 15)
        random_response = random_string(response_length)

        # Add the user prompt and response to the conversation history
        st.session_state.conversation_history.append((st.session_state.user_input, random_response))

        # Clear the input field by updating the text input widget's key
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()

# Streamlit app
def main():
    st.title("Simple Chatbot")

    # Initialize conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # Display conversation history
    st.markdown("**Conversation History:**")
    for entry in st.session_state.conversation_history:
        user_prompt, response = entry
        st.markdown(f"- **User**: {user_prompt}")
        st.markdown(f"- **Bot**: {response}")

    # Input prompt placeholder
    user_input_placeholder = st.empty()

    # Add the text input widget to the placeholder, with on_change=True
    user_input = user_input_placeholder.text_input("Enter your prompt:", key="user_input", on_change=on_change, args=[])

if __name__ == "__main__":
    main()
