import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
df = pd.read_excel("ua_resources_filled.xlsx")

# Load model
print("Loading model...")

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

# Create embeddings
print("Generating embeddings...")
embeddings = np.load("embeddings.npy")

def expand_query(query):
    query = query.lower()

    expansions = []

    if "grade" in query:
        expansions.append("check grades blackboard grades assignments")
    if "class" in query or "course" in query:
        expansions.append("schedule classes degreeworks courses")
    if "email" in query or "contact" in query:
        expansions.append("email professor contact faculty directory")
    if "scholarship" in query:
        expansions.append("apply scholarships financial aid funding")

    return query + " " + " ".join(expansions)

print("\n🚀 Semantic Search Ready!\n")

# Search loop
while True:
    user_input = input("Enter your question: ")
    query = expand_query(user_input)	

    if query.lower() == "exit":
        break

    # Encode query
    query_embedding = model.encode([query])

    # Compute similarity
    scores = cosine_similarity(query_embedding, embeddings)[0]

    # Get top results
    top_indices = scores.argsort()[-5:][::-1]

    print("\nTop Results:\n")

    for idx in top_indices:
        print(f"🔹 {df.loc[idx, 'resource_name']}")
        print(f"   {df.loc[idx, 'description']}")
        print(f"   Link: {df.loc[idx, 'url']}")
        print(f"   Score: {scores[idx]:.4f}\n")

    print("-" * 50)
