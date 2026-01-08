from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

from preprocess import preprocess_transactions
from enrich import enrich_transactions

app = FastAPI(title="Transaction Enrichment API")

class TransactionInput(BaseModel):
    transactions: list[dict]

class EnrichmentResponse(BaseModel):
    enriched_transactions: list[dict]

@app.post("/enrich", response_model=EnrichmentResponse)
def enrich_endpoint(payload: TransactionInput):
    # Immutability preserved: copy into DF
    raw_df = pd.DataFrame(payload.transactions)
    tmp_file = "tmp.xlsx"
    raw_df.to_excel(tmp_file, index=False)
    preprocessed_df = preprocess_transactions(tmp_file, output_file=None)

    enriched_df = enrich_transactions(preprocessed_df)

    return {
        "enriched_transactions": enriched_df.to_dict(orient="records")
    }
