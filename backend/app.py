from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (keep this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 GLOBALS (start as None)
model = None
df = None
embeddings = None

# 🔥 LAZY LOADER
def load_resources():
    global model, df, embeddings

    if model is None:
        print("Loading model...")
        model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    if df is None:
        print("Loading dataset...")
        df = pd.read_excel("ua_resources_filled.xlsx")

    if embeddings is None:
        print("Loading embeddings...")
        embeddings = np.load("embeddings.npy")

# Request schema
class Query(BaseModel):
    question: str

# Health check
@app.get("/")
def root():
    return {"status": "running"}

# 🔥 SEARCH ENDPOINT
@app.post("/search")
def search(query: Query):
    load_resources()  

    q_embedding = model.encode(query.question)

    scores = np.dot(embeddings, q_embedding)
    top_indices = np.argsort(scores)[-5:][::-1]

    results = []
    for i in top_indices:
        results.append({
            "name": df.iloc[i]["resource_name"],
            "description": df.iloc[i]["description"],
            "url": df.iloc[i]["url"],
            "score": float(scores[i])
        })

    return {"results": results}
