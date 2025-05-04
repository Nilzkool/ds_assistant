def system_prompt():
    """
    Define the system prompt text for initializing the conversation with ChatGPT.
    
    Returns:
        str: The system prompt text.
    """
    sys_prompt = (
                    "You are a data science assistant called Madsa. Assume that a csv file has been loaded into a pandas dataframe variable called df in your python environment. The main libraries in your environment are sklearn, numpy, pandas and matplotlib."
                    "All the user prompts will be related to the dataframe df. "
    
                )
    return sys_prompt
