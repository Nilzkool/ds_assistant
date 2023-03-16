import os
import streamlit as st
import random
import string
import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import openai


# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to generate response using ChatGPT API
def generate_chatgpt_response(prompt, conversation_history):
    model_engine = "gpt-3.5-turbo"

    # Construct the list of messages for the API
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
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
        temperature=0.7,
    )

    print(response)
    message = response["choices"][0]["message"]["content"]
    #message = response.choices[0].text.strip()
    return message



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
    elif isinstance(response, pd.DataFrame):
        st.write("**Bot**: Here are 5 randomly selected rows from the uploaded CSV file:")
        st.write(response)
    else:
        st.write("**Bot**: Here's your random scatter plot:")
        st.pyplot(response)
    st.markdown("---")

def on_change():
    if st.session_state.user_input:
        if "graph" in st.session_state.user_input.lower():
            random_response = random_scatter_plot()
        else:
            # Use ChatGPT to generate a response considering conversation history
            random_response = generate_chatgpt_response(st.session_state.user_input, st.session_state.conversation_history)

        # Add the user prompt and response to the conversation history
        st.session_state.conversation_history.append((st.session_state.user_input, random_response))

        # Clear the input field by updating the text input widget's key
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()

def main():
    st.title("Simple Chatbot")

    # Initialize conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []

    # File uploader
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    # Process the uploaded CSV file
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        random_sample = df.sample(n=5)
        st.session_state.conversation_history.append(("Uploaded CSV file", random_sample))

    # Display conversation history
    for entry in st.session_state.conversation_history:
        display_entry(entry)

    # Input prompt placeholder
    user_input_placeholder = st.empty()

    # Add the text input widget to the placeholder, with on_change=True
    user_input = user_input_placeholder.text_input("Enter your prompt:", key="user_input", on_change=on_change, args=[])

if __name__ == "__main__":
    main()
