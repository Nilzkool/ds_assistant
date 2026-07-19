import re

import openai

_CODE_BLOCK_PATTERNS = (
    re.compile(r"<\s*(.*?)\s*>", re.DOTALL),
    re.compile(r"```python\n?(.*?)\n?```", re.DOTALL),
    re.compile(r"```\n?(.*?)\n?```", re.DOTALL),
    re.compile(r"```(?:python)?\n?(.*?)(?:\n?```)?", re.DOTALL),
)


def generate_chatgpt_response(
    prompt: str,
    conversation_history: list,
    system_prompt: str,
    model_engine: str = "gpt-3.5-turbo",
    temperature: int = 0,
) -> str:
    """
    Generate a response from ChatGPT for a given prompt and conversation history.

    Args:
        prompt (str): The current user prompt.
        conversation_history (list): A list of (user_prompt, response) tuples.
        system_prompt (str): The system message to initialize the conversation with ChatGPT.
        model_engine (str): The OpenAI chat model to use. Defaults to gpt-3.5-turbo.
        temperature (int): Controls randomness of generated text.

    Returns:
        str: The text output from ChatGPT.
    """
    messages = [{"role": "system", "content": system_prompt}]
    for user_prompt, response in conversation_history:
        messages.append({"role": "user", "content": user_prompt})
        if isinstance(response, str):
            messages.append({"role": "assistant", "content": response})

    messages.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages,
        max_tokens=1000,
        n=1,
        temperature=temperature,
    )

    return response["choices"][0]["message"]["content"]


def extract_code_block(response_text: str) -> str | None:
    """
    Extract a Python code snippet from an LLM response.

    Tries an angle-bracket wrapped snippet first (the format Madsa is instructed to
    use), then falls back to progressively looser Markdown fenced-code patterns.

    Args:
        response_text (str): The raw text returned by the LLM.

    Returns:
        str | None: The extracted code, or None if nothing matched.
    """
    for pattern in _CODE_BLOCK_PATTERNS:
        match = pattern.search(response_text)
        if match:
            return match.group(1)
    return None
