from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi.middleware.cors import CORSMiddleware
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# CORS configuration to allow requests from any origin (for development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GLOBALS set as none because they are large and we want to load them only when needed (lazy loading
model = None
df = None
embeddings = None

# LAZY LOADER
def load_resources():
    global model, df, embeddings

    if model is None:
        print("Loading model...")
        model = SentenceTransformer("/app/model", device="cpu")

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


# loads the model, dataset, and embeddings when the application starts up, ensuring enpoints are ready with first request without delay
@app.on_event("startup")
def startup_event():
    load_resources()


# SEARCH ENDPOINT
@app.post("/search")
def search(query: Query):

    q_embedding = model.encode([query.question]) # converts text to a vector representation (embedding) using the loaded model
    scores = cosine_similarity(q_embedding, embeddings)[0] # computes the cosine similarity between the query embedding and all resource embeddings, resulting in a score for each resource

    top_indices = np.argsort(scores)[-5:][::-1] # identifies the indices of the top 5 resources based on their similarity scores

    results = []
    # this for loop is assigning actual resource information (name, description, url) to the results list based on the top indices
    for i in top_indices:
        results.append({
            "name": df.iloc[i]["resource_name"],
            "description": df.iloc[i]["description"],
            "url": df.iloc[i]["url"],
            "score": float(scores[i])
        })

    return {"results": results}
