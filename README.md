# My Awesome Data Science Assistant (Madsa)

MADSA is a conversational app that allows users to perform data science tasks in natural language. With Madsa, one can:

- Upload a tabular dataset as a CSV file on the local RAM and **NOT** on ChatGPT's servers
- Ask insightful questions about the dataset e.g. *What was the survivor rate for each gender in the titanic?*
- Generate plots by prompting in natural language e.g. *Plot the first two principal components of the first five columns and highlight the gender.*
- Train machine learning models and/or explore model parameters e.g. *Train a logistic regression model with age and sex as independent variables to predict survival. Which parameter contributed the most?*

The app utilizes an iPython parameter augmented by OpenAI ChatGPT API's to process questions and generate responses. Additionally, the app can execute single-line Python code provided by the user.

**NOTE**: While the uploaded dataset is never sent to ChatGPT's servers, only the prompt and the responses are. 

## Repository structure
1. madsa_app.py: The main Streamlit application file.
2. app_utils.py: Utility functions to support the Streamlit app.
3. chatgpt_api_utils.py: Utility functions to interact with the OpenAI ChatGPT API.
4. system_prompt.py: Defines the system prompt for the ChatGPT API.
5. requirements.txt: Lists the required Python packages to run the app.
6. test_datasets: A folder containing sample datasets to test the app.
7. R&D: An old folder containing research and development code.

## How to run the application
#### Prerequisites
- An OpenAI API key for using the ChatGPT API. Click [here](https://platform.openai.com/account/api-keys) to know more.
- Conda package manager

#### Installation

1. Clone this repo
```bash
git clone git@github.com:Nilzkool/ds_assistant.git
cd ds_assistant
```
2. Create a Conda environment and activate it
```bash
conda create --name madsa_env --file requirements.txt
conda activate madsa_env
```
3. Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key"  # Linux/Mac
set OPENAI_API_KEY="your-api-key"  # Windows
```

#### Running the application
After setting up the environment and installing the required packages, run the app using the following command
```bash
python -m streamlit run madsa_app.py
```

## Usage
1. Upload a CSV file using the file uploader in the app.
2. Enter your Python statement or ask a question in the text input field.
   Press Enter to submit your input. 
3. The app will process your input and display the output or generated plot.

## Tips and tricks

Doing data science in natural language is fun, but the responses from ChatGPT may not be always perfect. Here are a few tips to get higher-quality responses

1. Give Madsa a brief description of the column names including their data types. e.g.
```
Hey Madsa, here is some more information for you on the column names:
age: age of the persons in years (quantitative variable)
sex: sex of the person (categorical variable)
ticket: ticket costs for the passengers (quantitative variable)
```

2. Make the prompt concrete and specific e.g. 

Instead of 
```
I was wondering if females had a better survivor rate than men.
```
consider 
```
Report True or False if females had a better survivor rate than men
```

3. Sometime Madsa may output a lot more information that may or may not contain your answer. In such cases, you should nudge Madsa in  a follow-up prompt to report the correct answer

4. Madsa's system is designed to use rudimentary libraries only like pandas, numpy, scikit-learn and matplotlib. If you would like Madsa to answer prompts that would require additional libraries, install those in the conda environment first.  Then in the prompt, you can specify to Madsa to use this library e.g.
```
Plot a histogram of passenger age. Use the package Seaborn
```

5. Here is the system prompt:
```
You are a data science assistant named Madsa. A CSV file has already been loaded into a pandas DataFrame named `df`. You have access to the libraries: pandas, numpy, sklearn, and matplotlib. All user prompts will relate to the DataFrame `df`. Your job is to understand the prompt and respond only with Python code to solve it. Be concise. Always include a `print` statement in your code to display the output. Wrap your entire Python code inside angle brackets like this: < your_code_here >. Do not return anything else. If the user prompt contains valid Python code, return the exact same code wrapped in < > without modification. If you cannot respond with a Python code block in the correct format, reply with: I am sorry for now.
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
