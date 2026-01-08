import pandas as pd
import numpy as np
import re

def preprocess_transactions(input_file: str, output_file: str=None):
    df = pd.read_excel(input_file)

    df = df.rename(columns={
        'TransactionDate': 'TransactionDate',
        'TransactionAmountUSD': 'AmountUSD',
        'TransactionClassification': 'Category',
        'TransactionName': 'Description',
    })

    df['AmountUSD'] = df['AmountUSD'].astype(str).str.replace(',', '', regex=False).astype(float)

    df['Balance'] = np.nan

    df['TransactionDate'] = pd.to_datetime(df['TransactionDate']).dt.strftime('%Y-%m-%d')

    df['Description'] = df['Description'].astype(str).str.lower()
    df['Description'] = df['Description'].apply(lambda x: re.sub(r'\b\d{10,}\b', '', str(x)).strip())

    df = df[['TransactionDate', 'Description', 'Category', 'AmountUSD', 'Balance']]

    df.to_excel(output_file, index=False)
    print(f"Processed data written to {output_file}")

if __name__ == "__main__":
    input_excel_file = "Data.xlsx"
    output_excel_file = "data/processed/transactions_cleaned.xlsx"
    preprocess_transactions(input_excel_file, output_excel_file)
