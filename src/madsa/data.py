import pandas as pd


def load_csv(file) -> pd.DataFrame:
    """
    Load an uploaded CSV file into a pandas DataFrame.

    Args:
        file: A file-like object containing CSV data (e.g. a Streamlit UploadedFile).

    Returns:
        pd.DataFrame: The parsed dataframe.
    """
    return pd.read_csv(file)
