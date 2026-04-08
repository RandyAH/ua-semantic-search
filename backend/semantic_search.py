import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
df = pd.read_excel("ua_resources_filled.xlsx")

# Lazy-load model
model = None

def get_model():
    """Load embedding model once and reuse it."""
    global model
    if model is None:
        print("Loading model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

# Load precomputed embeddings
print("Loading embeddings...")
embeddings = np.load("embeddings.npy")


def expand_query(query):
    """Expand query with related keywords to improve recall."""
    query = query.lower()
    expansions = []

    if "grade" in query:
        expansions.append("check grades blackboard assignments")
    if "class" in query or "course" in query:
        expansions.append("schedule classes degreeworks")
    if "email" in query or "contact" in query:
        expansions.append("email professor faculty directory")
    if "scholarship" in query:
        expansions.append("apply scholarships financial aid")

    return query + " " + " ".join(expansions)


print("\nSemantic Search Ready!\n")

while True:
    user_input = input("Enter your question: ")

    if user_input.lower() == "exit":
        break

    query = expand_query(user_input)

    # Get model (ensures it's loaded)
    model = get_model()

    # Encode query
    query_embedding = model.encode([query])

    # Compute similarity
    scores = cosine_similarity(query_embedding, embeddings)[0]

    # Get top 5 results
    top_indices = scores.argsort()[-5:][::-1]

    print("\nTop Results:\n")

    for idx in top_indices:
        print(f"- {df.loc[idx, 'resource_name']}")
        print(f"  {df.loc[idx, 'description']}")
        print(f"  Link: {df.loc[idx, 'url']}")
        print(f"  Score: {scores[idx]:.4f}\n")

    print("-" * 50)