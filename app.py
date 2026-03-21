from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data + model ONCE
df = pd.read_excel("ua_resources_filled.xlsx")

model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
embeddings = np.load("embeddings.npy")  # precomputed

class Query(BaseModel):
    question: str

@app.post("/search")
def search(query: Query):
    q_embedding = model.encode(query.question)

    print("Query embedding shape:", q_embedding.shape)
    print("Embeddings shape:", embeddings.shape)

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
