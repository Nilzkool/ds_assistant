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
        temperature=0.7,
    )

    message = response["choices"][0]["message"]["content"]
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

csv_upload_file_added_to_conversation = False

def on_change():
    global csv_upload_file_added_to_conversation
    if st.session_state.user_input:
        if "graph" in st.session_state.user_input.lower():
            random_response = random_scatter_plot()
            st.session_state.conversation_history.append((st.session_state.user_input, random_response))
        
        elif (st.session_state.csv_uploaded) and (csv_upload_file_added_to_conversation==False):
            st.session_state.conversation_history.append(("Uploaded a CSV file", st.session_state.random_sample))
            csv_upload_file_added_to_conversation = True
       
        else:
            # Use ChatGPT to generate a response considering conversation history
            random_response = generate_chatgpt_response(st.session_state.user_input, st.session_state.conversation_history, st.session_state.system_prompt)

        # Add the user prompt and response to the conversation history
            st.session_state.conversation_history.append((st.session_state.user_input, random_response))

        # Add the CSV upload message only once
        #if st.session_state.csv_uploaded:
        #   st.session_state.conversation_history.append(("Uploaded a CSV file", st.session_state.random_sample))
            #st.write(st.session_state.random_sample) 
            #st.session_state.csv_uploaded = False

        # Clear the input field by updating the text input widget's key
        unique_key = f"user_input_{time.time()}"
        st.session_state.user_input = ""
        st.experimental_rerun()


if "csv_uploaded" not in st.session_state:
        st.session_state.csv_uploaded = False

def main():
    st.title("Simple Chatbot")

    # Initialize conversation history
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = "You are a helpful assistant. Answer concisely"
    
    #if "csv_uploaded" not in st.session_state:
    #    st.session_state.csv_uploaded = False

    # File uploader

    #if st.session_state.csv_uploaded == False:
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    # Process the uploaded CSV file
    if (uploaded_file is not None) and (st.session_state.csv_uploaded == False):
        df = pd.read_csv(uploaded_file)
        random_sample = df.sample(n=5)
        st.session_state.conversation_history.append(("Uploaded CSV file", random_sample))

        st.session_state.random_sample = random_sample

        df_str = df.to_string(header=True,
                              index=False,
                              index_names=False).split('\n')
        
        df_str = repr([','.join(ele.split()) for ele in df_str])
        #print(df_str)

        st.session_state.system_prompt = f"You are a helpful assistant. Answer concisely. The user has uploaded a CSV file. The data is:\n\n {df_str}"

        st.session_state.csv_uploaded = True

        print('I am here again')

    # Display conversation history
    for entry in st.session_state.conversation_history:
        display_entry(entry)

    # Input prompt placeholder
    user_input_placeholder = st.empty()

    # Add the text input widget to the placeholder, with on_change=True
    user_input = user_input_placeholder.text_input("Enter your prompt:", key="user_input", on_change=on_change, args=[])
    print()

if __name__ == "__main__":
    main()
