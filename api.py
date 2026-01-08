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
    
    # Process directly from DataFrame (no temp file needed)
    preprocessed_df = preprocess_transactions(df=raw_df)

    enriched_df = enrich_transactions(df=preprocessed_df)

    return {
        "enriched_transactions": enriched_df.to_dict(orient="records")
    }
