import openai
# Hello world update
def generate_chatgpt_response(prompt, conversation_history, system_prompt, model_engine = 'gpt-3.5-turbo', temperature = 0):
    """
    Generate a response from ChatGPT for a given prompt and conversation history.
    
    Args:
        prompt (str): The current user prompt.
        conversation_history (list): A list of tuples containing the conversation history.
        system_prompt (str): The system message to initialize the conversation with ChatGPT.
        model_engine (str): The pre-trained GPT model from OpenAI. Defaults to gpt-3.5-turbo
        temperature (int): Controls randomness of generated text
        
    Returns:
        str: The text output from ChatGPT.
    """

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
        max_tokens=1000,
        n=1,
        temperature=temperature)

    text_output = response["choices"][0]["message"]["content"]
    
    return text_output
