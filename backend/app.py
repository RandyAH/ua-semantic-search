from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from semantic_search import get_search_engine

app = FastAPI()

# CORS for local frontend / dev tooling
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "running"}


@app.on_event("startup")
def startup_event():
    # Warm-load model, embeddings, and cleaned dataframe once (not per request)
    get_search_engine()


@app.post("/search")
def search(query: Query):
    return get_search_engine().search_dict(query.question)
