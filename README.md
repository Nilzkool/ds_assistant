# My Awesome Data Science Assistant (Madsa)

MADSA is a conversational app that allows users to perform data science tasks in natural language. With Madsa, one can:

- Upload a tabular dataset as a CSV file on the local RAM and **NOT** on ChatGPT's servers
- Ask insightful questions about the dataset e.g. *What was the survivor rate for each gender in the titanic?*
- Generate plots by prompting in natural language e.g. *Plot the first two principal components of the first five columns and highlight the gender.*
- Train machine learning models and/or explore model parameters e.g. *Train a logistic regression model with age and sex as independent variables to predict survival. Which parameter contributed the most?*

The app utilizes an iPython-like execution environment augmented by OpenAI's ChatGPT API to process questions and generate responses. Additionally, the app can execute single-line Python code provided by the user directly.

**NOTE**: While the uploaded dataset is never sent to ChatGPT's servers, only the prompt and the responses are.

## Repository structure

```
src/madsa/
├── app.py          # Streamlit entrypoint
├── execution.py     # Sandboxed exec + stdout/plot capture
├── llm.py            # OpenAI ChatCompletion call + code extraction
├── prompts.py        # System prompt (single source of truth)
├── data.py           # CSV upload handling
└── ui.py              # Conversation rendering
test_datasets/         # Sample datasets and prompts to try the app with
pyproject.toml          # Package metadata and pinned dependencies
Dockerfile               # Container build
```

## How to run the application

### Prerequisites
- An OpenAI API key. Click [here](https://platform.openai.com/account/api-keys) to know more.
- Either **Python 3.11+** (to run locally) or **Docker** (to run in a container) — you don't need both.

### Option 1: Run locally with pip

1. Clone this repo
```bash
git clone git@github.com:Nilzkool/ds_assistant.git
cd ds_assistant
```
2. Create a virtual environment (must be Python 3.11+) and install the package
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```
3. Provide your OpenAI API key, either as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key"  # Linux/Mac
set OPENAI_API_KEY="your-api-key"     # Windows
```
or by copying `.env.example` to `.env` and filling in your key:
```bash
cp .env.example .env  # then edit .env with your key
```
4. Run the app
```bash
streamlit run src/madsa/app.py
```
5. Streamlit will print a local URL (typically [http://localhost:8501](http://localhost:8501)) — open it in your browser.

### Option 2: Run with Docker

No local Python setup required — just Docker.

1. Clone this repo (see step 1 above) and `cd` into it.
2. Copy `.env.example` to `.env` and fill in your `OPENAI_API_KEY`.
```bash
cp .env.example .env  # then edit .env with your key
```
3. Build the image
```bash
docker build -t madsa .
```
4. Run the container
```bash
docker run -p 8501:8501 --env-file .env madsa
```
5. Open [http://localhost:8501](http://localhost:8501) in your browser.

## Usage
1. Upload a CSV file using the file uploader in the app.
2. Enter your Python statement or ask a question in the text input field. Press Enter to submit your input.
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

3. Sometimes Madsa may output a lot more information that may or may not contain your answer. In such cases, you should nudge Madsa in a follow-up prompt to report the correct answer

4. Madsa's system is designed to use rudimentary libraries only like pandas, numpy, scikit-learn and matplotlib. If you would like Madsa to answer prompts that would require additional libraries, install those first. Then in the prompt, you can specify to Madsa to use this library e.g.
```
Plot a histogram of passenger age. Use the package Seaborn
```

5. The exact system prompt Madsa is initialized with lives in [`src/madsa/prompts.py`](src/madsa/prompts.py), if you'd like to see or tweak how it's instructed.

You can try the app quickly using the sample datasets and prompts in [`test_datasets/`](test_datasets/) (`Iris.csv`, `titanic_train.csv`, `sample_prompts.txt`).

## License

[MIT](LICENSE)
