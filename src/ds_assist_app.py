import streamlit as st
import random
import string
import time
import numpy as np
import matplotlib.pyplot as plt

# Function to generate a random string
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_scatter_plot():
    N = 50
    x = np.random.rand(N)
    y = np.random.rand(N)
    colors = np.random.rand(N)
    area = (30 * np.random.rand(N))**2
    
    fig, ax = plt.subplots()
    ax.scatter(x, y, s=area, c=colors, alpha=0.5)
    
    return fig

def display_entry(entry):
    user_prompt, response = entry
    st.markdown(f"**User**: {user_prompt}")
    if isinstance(response, str):
        st.markdown(f"**Bot**: {response}")
    else:
        st.write("**Bot**: Here's your random scatter plot:")
        st.pyplot(response)
    st.markdown("---")

def on_change():
    if st.session_state.user_input:
        if "graph" in st.session_state.user_input.lower():
            random_response = random_scatter_plot()
        else:
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
    for entry in st.session_state.conversation_history:
        display_entry(entry)

    # Input prompt placeholder
    user_input_placeholder = st.empty()

    # Add the text input widget to the placeholder, with on_change=True
    user_input = user_input_placeholder.text_input("Enter your prompt:", key="user_input", on_change=on_change, args=[])

if __name__ == "__main__":
    main()
