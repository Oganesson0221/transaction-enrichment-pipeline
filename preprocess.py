import pandas as pd
import numpy as np
import re

def preprocess_transactions(input_file: str = None, output_file: str = None, df: pd.DataFrame = None):
    """
    Preprocess transactions from either an Excel file or a DataFrame.
    
    Args:
        input_file: Path to Excel file (used when processing files)
        output_file: Path to output Excel file (optional)
        df: DataFrame to process directly (used by API)
    
    Returns:
        Processed DataFrame
    """
    if df is None:
        df = pd.read_excel(input_file)
        # Rename columns only when reading from file (original Excel format)
        df = df.rename(columns={
            'TransactionDate': 'TransactionDate',
            'TransactionAmountUSD': 'AmountUSD',
            'TransactionClassification': 'Category',
            'TransactionName': 'Description',
        })

    # Ensure AmountUSD is numeric
    df['AmountUSD'] = df['AmountUSD'].astype(str).str.replace(',', '', regex=False).astype(float)

    # Add Balance column if not present
    if 'Balance' not in df.columns:
        df['Balance'] = np.nan

    df['TransactionDate'] = pd.to_datetime(df['TransactionDate']).dt.strftime('%Y-%m-%d')

    df['Description'] = df['Description'].astype(str).str.lower()
    df['Description'] = df['Description'].apply(lambda x: re.sub(r'\b\d{10,}\b', '', str(x)).strip())

    # Add Category column if not present
    if 'Category' not in df.columns:
        df['Category'] = 'Unknown'

    df = df[['TransactionDate', 'Description', 'Category', 'AmountUSD', 'Balance']]

    if output_file:
        df.to_excel(output_file, index=False)
        print(f"Processed data written to {output_file}")
    
    return df

if __name__ == "__main__":
    input_excel_file = "Data.xlsx"
    output_excel_file = "data/processed/transactions_cleaned.xlsx"
    preprocess_transactions(input_excel_file, output_excel_file)
